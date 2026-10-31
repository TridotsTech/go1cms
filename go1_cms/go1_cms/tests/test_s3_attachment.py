# Copyright (c) 2026, Tridots Tech and contributors
"""S3 attachments, against a fake S3 client: uploads, deletes, private access and migration.

bench --site go1cms.com run-tests --module go1_cms.go1_cms.tests.test_s3_attachment
"""
import os
from unittest import mock

import frappe
from boto3.exceptions import S3UploadFailedError
from frappe.tests.utils import FrappeTestCase

from go1_cms.go1_cms import s3_attachment as s3

ENDPOINT = "https://s3.ap-south-1.amazonaws.com"
PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
       b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND\xaeB`\x82")


def _client():
	client = mock.MagicMock()
	client.meta.endpoint_url = ENDPOINT
	client.generate_presigned_url.return_value = "https://signed.example/object"
	return client


def _file(name, content=None, private=0, **values):
	return frappe.get_doc({
		"doctype": "File", "file_name": name, "content": content or frappe.generate_hash().encode(),
		"is_private": private, **values,
	}).insert(ignore_permissions=True)


class TestS3Attachment(FrappeTestCase):
	def setUp(self):
		self.client = _client()
		patcher = mock.patch.object(s3.boto3, "client", return_value=self.client)
		patcher.start()
		self.addCleanup(patcher.stop)
		self.addCleanup(frappe.set_user, "Administrator")
		frappe.db.delete("Singles", {"doctype": s3.SETTINGS})
		self.addCleanup(frappe.db.delete, "Singles", {"doctype": s3.SETTINGS})

	def configure(self, **values):
		frappe.get_doc(s3.SETTINGS).update({
			"bucket_name": "bucket", "aws_key": "key", "aws_secret": "secret", "region_name": "ap-south-1",
			"folder_name": "cms", "delete_file_from_cloud": 1, **values,
		}).save(ignore_permissions=True)

	def test_no_bucket_leaves_files_local(self):
		doc = _file("s3-off.txt")
		self.assertTrue(doc.file_url.startswith("/files/"))
		self.assertTrue(os.path.isfile(doc.get_full_path()))
		self.client.upload_file.assert_not_called()
		doc.delete()

	def test_public_upload(self):
		self.configure()
		doc = _file("my photo.txt", folder="Home/Attachments")
		path, bucket, key = self.client.upload_file.call_args.args[:3]
		args = self.client.upload_file.call_args.kwargs["ExtraArgs"]
		self.assertEqual(bucket, "bucket")
		self.assertRegex(key, r"^cms/\d{4}/\d{2}/\d{2}/File/[A-Z0-9]{8}_my_photo\.txt$")
		self.assertEqual(args["ACL"], "public-read")
		self.assertEqual(args["ContentType"], "text/plain")
		self.assertEqual(doc.file_url, f"{ENDPOINT}/bucket/{key}")
		saved = frappe.db.get_value("File", doc.name, ["file_url", "content_hash", "folder"], as_dict=True)
		self.assertEqual((saved.file_url, saved.content_hash, saved.folder), (doc.file_url, key, "Home/Attachments"))
		self.assertFalse(os.path.exists(path))

	def test_compressed_bytes_are_what_s3_gets(self):
		self.configure()
		seen = {}
		self.client.upload_file.side_effect = lambda path, *a, **k: seen.update(size=os.path.getsize(path))
		with mock.patch("cms_frontend.image_compress.compress_file") as compress:
			def smaller(path, private=False):
				with open(path, "wb") as handle:
					handle.write(b"small")
			compress.side_effect = smaller
			_file("compressed.png", PNG + frappe.generate_hash().encode())
		self.assertEqual(seen["size"], 5)

	def test_key_fits_content_hash(self):
		self.configure()
		doc = _file("x" * 130 + ".txt")
		self.assertLessEqual(len(doc.content_hash), s3.MAX_KEY)
		self.assertTrue(doc.content_hash.endswith(".txt"))

	def test_bucket_with_acls_off(self):
		self.configure()
		self.client.upload_file.side_effect = [S3UploadFailedError("AccessControlListNotSupported"), None]
		_file("no-acl.txt")
		self.assertEqual(self.client.upload_file.call_count, 2)
		self.assertNotIn("ACL", self.client.upload_file.call_args.kwargs["ExtraArgs"])

	def test_failed_upload_keeps_nothing(self):
		self.configure()
		self.client.upload_file.side_effect = S3UploadFailedError("denied")
		with self.assertRaises(frappe.ValidationError):
			_file("failed.txt")

	def test_private_file_needs_permission(self):
		self.configure()
		doc = _file("secret.txt", private=1)
		self.assertTrue(doc.file_url.startswith(s3.GENERATE_FILE))
		self.assertNotIn("ACL", self.client.upload_file.call_args.kwargs["ExtraArgs"])

		s3.generate_file(key=doc.content_hash)
		self.assertEqual(frappe.local.response["location"], "https://signed.example/object")

		frappe.local.response.pop("location")
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			s3.generate_file(key=doc.content_hash)
		self.assertNotIn("location", frappe.local.response)

	def test_fonts_and_ignored_doctypes_stay_local(self):
		self.configure()
		font = _file("site.woff2")
		self.assertTrue(font.file_url.startswith("/files/"))
		self.client.upload_file.assert_not_called()
		font.delete()

	def test_delete_keeps_shared_object(self):
		self.configure()
		doc = _file("shared.txt")
		copy = frappe.copy_doc(doc).insert(ignore_permissions=True)
		self.assertEqual(copy.file_url, doc.file_url)
		frappe.delete_doc("File", copy.name, ignore_permissions=True)
		self.client.delete_object.assert_not_called()
		frappe.delete_doc("File", doc.name, ignore_permissions=True)
		self.client.delete_object.assert_called_once_with(Bucket="bucket", Key=doc.content_hash)

	def test_delete_off_keeps_object(self):
		self.configure(delete_file_from_cloud=0)
		frappe.delete_doc("File", _file("kept.txt").name, ignore_permissions=True)
		self.client.delete_object.assert_not_called()

	def test_migration_skips_files_in_use(self):
		used, unused = _file("used.txt"), _file("unused.txt")
		before = {doc.file_url: doc.get_full_path() for doc in (used, unused)}
		self.configure()
		rows = [r for r in s3._file_rows() if r.file_url in before]
		with mock.patch.object(s3, "_in_use_urls", return_value={used.file_url}), \
			mock.patch.object(frappe.db, "commit"), mock.patch.object(s3, "_file_rows", return_value=rows):
			result = s3.migrate_existing_files_job()
		self.assertEqual(result, {"moved": 1, "failed": 0})
		self.assertEqual(frappe.db.get_value("File", used.name, "file_url"), used.file_url)
		self.assertTrue(frappe.db.get_value("File", unused.name, "file_url").startswith(ENDPOINT))
		# The local copy stays, for anything the usage index does not count.
		self.assertTrue(all(os.path.isfile(path) for path in before.values()))

	def test_migration_stops_on_repeated_failures(self):
		self.configure()
		self.client.upload_file.side_effect = S3UploadFailedError("denied")
		rows = [frappe._dict(name=f"f{i}", file_url=f"/files/f{i}.txt", file_name=f"f{i}.txt") for i in range(s3.MAX_FAILURES + 5)]
		with mock.patch.object(s3, "_in_use_urls", return_value=set()), mock.patch.object(s3, "_file_rows", return_value=rows), \
			mock.patch.object(frappe.db, "commit"), mock.patch.object(frappe.db, "rollback"), mock.patch.object(frappe, "log_error"):
			result = s3.migrate_existing_files_job()
		self.assertEqual(result["failed"], s3.MAX_FAILURES)

	def test_migration_needs_a_bucket(self):
		with mock.patch.object(s3, "_in_use_urls") as in_use:
			self.assertEqual(s3.migrate_existing_files_job(), {"moved": 0, "failed": 0})
		in_use.assert_not_called()

	def test_amazon_needs_no_provider_settings(self):
		self.configure()
		kwargs = s3.boto3.client.call_args if s3.S3Operations() else None
		self.assertIsNone(kwargs.kwargs["endpoint_url"])
		self.assertEqual(kwargs.kwargs["region_name"], "ap-south-1")
		self.assertEqual(s3.S3Operations().public_url("a b/c.txt"), f"{ENDPOINT}/bucket/a%20b/c.txt")

	def test_custom_endpoint_uses_path_style(self):
		self.configure(endpoint_url="https://s3.example.com/", region_name="")
		self.client.meta.endpoint_url = "https://s3.example.com"
		ops = s3.S3Operations()
		kwargs = s3.boto3.client.call_args.kwargs
		self.assertEqual(kwargs["endpoint_url"], "https://s3.example.com")
		self.assertEqual(kwargs["region_name"], "us-east-1")
		self.assertEqual(kwargs["config"].s3["addressing_style"], "path")
		self.assertEqual(ops.public_url("k.txt"), "https://s3.example.com/bucket/k.txt")

	def test_virtual_style_url(self):
		self.configure(endpoint_url="https://s3.example.com", addressing_style="Virtual")
		self.client.meta.endpoint_url = "https://s3.example.com"
		self.assertEqual(s3.S3Operations().public_url("k.txt"), "https://bucket.s3.example.com/k.txt")

	def test_public_base_url_wins_and_delete_still_finds_the_object(self):
		self.configure(endpoint_url="https://s3.example.com", public_base_url="https://cdn.example.com/")
		doc = _file("cdn.txt")
		self.assertTrue(doc.file_url.startswith("https://cdn.example.com/cms/"))
		frappe.delete_doc("File", doc.name, ignore_permissions=True)
		self.client.delete_object.assert_called_once_with(Bucket="bucket", Key=doc.content_hash)

	def test_provider_without_acls(self):
		self.configure()
		self.client.upload_file.side_effect = [S3UploadFailedError("NotImplemented"), None]
		_file("r2.txt")
		self.assertNotIn("ACL", self.client.upload_file.call_args.kwargs["ExtraArgs"])

	def test_private_upload_failure_is_not_retried(self):
		self.configure()
		self.client.upload_file.side_effect = S3UploadFailedError("AccessDenied")
		with self.assertRaises(frappe.ValidationError):
			_file("denied.txt", private=1)
		self.assertEqual(self.client.upload_file.call_count, 1)

	def test_connection_reports_the_providers_error(self):
		self.configure()
		self.assertTrue(s3.test_connection())
		self.client.delete_object.assert_called_once()
		self.client.put_object.side_effect = s3.ClientError({"Error": {"Code": "InvalidAccessKeyId", "Message": "no"}}, "PutObject")
		with self.assertRaises(frappe.ValidationError):
			s3.test_connection()

	def test_migrate_is_system_manager_only(self):
		self.configure()
		frappe.set_user("Guest")
		with mock.patch.object(frappe, "enqueue") as enqueue, mock.patch.dict(frappe.local.flags, {"in_test": False}):
			with self.assertRaises(frappe.PermissionError):
				s3.migrate_existing_files()
		enqueue.assert_not_called()
