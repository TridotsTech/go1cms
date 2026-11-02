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
		# Nothing here may reach the real queue (a stray job once ran a real migration).
		enqueue = mock.patch("frappe.enqueue")
		self.enqueue = enqueue.start()
		self.addCleanup(enqueue.stop)
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
		self.assertRegex(key, r"^cms/common/documents/[A-Z0-9]{8}_my_photo\.txt$")
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

	def test_everything_is_public(self):
		self.configure()
		doc = _file("contract.csv", private=1)
		self.assertEqual(doc.file_url, f"{ENDPOINT}/bucket/{doc.content_hash}")
		self.assertEqual(frappe.db.get_value("File", doc.name, "is_private"), 0)
		self.assertEqual(self.client.upload_file.call_args.kwargs["ExtraArgs"]["ACL"], "public-read")

	@mock.patch.object(s3, "ALL_PUBLIC", False)
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

	@mock.patch.object(s3, "ALL_PUBLIC", False)
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

	def test_files_go_to_their_websites_folder(self):
		self.configure()
		project = frappe.get_all("CMS Project", fields=["name", "project_slug"], filters={"project_slug": ["is", "set"]}, limit=1)[0]
		attached = _file("brand.png", PNG + frappe.generate_hash().encode(), attached_to_doctype="CMS Project", attached_to_name=project.name)
		self.assertTrue(attached.content_hash.startswith(f"cms/{project.project_slug}/images/"))
		with mock.patch.dict(frappe.local.form_dict, {"cms_project": project.name}):
			sent = _file("clip.mp4")
		self.assertTrue(sent.content_hash.startswith(f"cms/{project.project_slug}/videos/"))
		with mock.patch.dict(frappe.local.form_dict, {"cms_project": "No Such Website"}):
			stray = _file("notes.csv")
		self.assertTrue(stray.content_hash.startswith("cms/common/documents/"))

	@mock.patch.object(s3, "ALL_PUBLIC", False)
	def test_images_are_always_public(self):
		self.configure()
		image = _file("private-photo.png", PNG + frappe.generate_hash().encode(), private=1)
		self.assertEqual(image.file_url, f"{ENDPOINT}/bucket/{image.content_hash}")
		self.assertEqual(frappe.db.get_value("File", image.name, "is_private"), 0)
		self.assertEqual(self.client.upload_file.call_args.kwargs["ExtraArgs"]["ACL"], "public-read")
		document = _file("private.csv", private=1)
		self.assertTrue(document.file_url.startswith(s3.GENERATE_FILE))
		self.assertEqual(frappe.db.get_value("File", document.name, "is_private"), 1)

	def test_folders(self):
		self.configure()
		self.enqueue.assert_called()
		project = frappe.get_all("CMS Project", fields=["name", "project_slug"], filters={"project_slug": ["is", "set"]}, limit=1)[0]
		s3.make_folders([project.name])
		self.client.put_object.assert_called_once_with(Bucket="bucket", Key=f"cms/{project.project_slug}/", Body=b"")
		self.client.put_object.reset_mock()
		s3.make_folders()
		keys = {c.kwargs["Key"] for c in self.client.put_object.call_args_list}
		self.assertTrue({"cms/common/", "cms/template_images/", f"cms/{project.project_slug}/"} <= keys)
		self.assertEqual(len(keys), self.client.put_object.call_count)

	def test_new_website_queues_its_folder(self):
		self.configure()
		self.enqueue.reset_mock()
		s3.on_project_insert(frappe._dict(name="Some Website"))
		self.enqueue.assert_called_once_with("go1_cms.go1_cms.s3_attachment.make_folders_job", projects=["Some Website"],
			enqueue_after_commit=True)

	def test_template_images(self):
		self.configure()
		self.client.head_object.side_effect = s3.ClientError({"Error": {"Code": "404"}}, "HeadObject")
		ops = s3.S3Operations()
		s3.put_template_media(ops, "aura/hero 1.jpg", b"jpeg")
		self.client.put_object.assert_called_once_with(Bucket="bucket", Key="cms/template_images/aura/hero 1.jpg", Body=b"jpeg",
			ContentType="image/jpeg", ACL="public-read")
		self.client.head_object.side_effect = None
		self.client.head_object.return_value = {"ContentLength": 4}
		s3.put_template_media(ops, "aura/hero 1.jpg", b"jpeg")
		self.assertEqual(self.client.put_object.call_count, 1)

		from cms_frontend import template_store

		base = s3.template_media_base(ops)
		self.assertEqual(base, f"{ENDPOINT}/bucket/cms/template_images/")
		text = '{"src": "https://store.example/assets/go1_templates/media/aura/hero%201.jpg", "api": "/assets/go1_templates/media/aura/team.json"}'
		self.assertEqual(template_store._site_media(text, base),
			'{"src": "' + base + 'aura/hero%201.jpg", "api": "/files/go1-templates/aura/team.json"}')
		self.assertEqual(template_store._site_media(text), text.replace("https://store.example/assets/go1_templates/media/", "/files/go1-templates/")
			.replace("/assets/go1_templates/media/", "/files/go1-templates/"))

	def test_taken_template_images_go_to_s3(self):
		self.configure()
		from cms_frontend import template_store

		self.client.head_object.side_effect = s3.ClientError({"Error": {"Code": "404"}}, "HeadObject")
		data = {"library_id": "s3-test-template", "media": ["hero.png", "team.json"]}
		bodies = {"s3-test-template/hero.png": b"png", "s3-test-template/team.json": b'{"img": "/assets/go1_templates/media/s3-test-template/hero.png"}'}
		with mock.patch.object(template_store, "_store_file", side_effect=bodies.get):
			base = template_store._copy_media(data)
		root = frappe.get_site_path("public", "files", "go1-templates", "s3-test-template")
		self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
		self.assertEqual(base, f"{ENDPOINT}/bucket/cms/template_images/")
		self.assertEqual([c.kwargs["Key"] for c in self.client.put_object.call_args_list], ["cms/template_images/s3-test-template/hero.png"])
		self.assertFalse(os.path.exists(os.path.join(root, "hero.png")))
		with open(os.path.join(root, "team.json")) as handle:
			self.assertEqual(handle.read(), '{"img": "' + base + 's3-test-template/hero.png"}')

	def test_store_previews_link_uploaded_images(self):
		self.configure()
		from go1_templates import template_api

		frappe.cache().set_value(s3.TEMPLATE_MEDIA_CACHE, {"base": "https://s3.example/b/cms/template_images/", "paths": {"aura/a b.jpg"}})
		self.addCleanup(frappe.cache().delete_value, s3.TEMPLATE_MEDIA_CACHE)
		text = '"/assets/go1_templates/media/aura/a%20b.jpg" "/assets/go1_templates/media/aura/new.jpg" "/assets/go1_templates/media/aura/d.json"'
		store = frappe.utils.get_url() + "/assets/go1_templates/media/"
		self.assertEqual(template_api._linked(text, previews=True),
			f'"https://s3.example/b/cms/template_images/aura/a%20b.jpg" "{store}aura/new.jpg" "{store}aura/d.json"')
		self.assertNotIn("s3.example", template_api._linked(text))

	def test_migrate_is_system_manager_only(self):
		self.configure()
		frappe.set_user("Guest")
		with mock.patch.object(frappe, "enqueue") as enqueue, mock.patch.dict(frappe.local.flags, {"in_test": False}):
			with self.assertRaises(frappe.PermissionError):
				s3.migrate_existing_files()
		enqueue.assert_not_called()
