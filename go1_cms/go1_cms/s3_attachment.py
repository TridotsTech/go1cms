"""Files on S3, configured in the single doctype "S3 File Attachment".

A port of shridarpatil/Frappe-attachments-s3 with the same settings and the same URLs
and key layout ({folder}/{year}/{month}/{day}/{doctype}/{random}_{file name}). With no
bucket name saved, nothing changes: files stay on this server.

Amazon S3 needs only the original settings. Any other S3-compatible provider (Wasabi, Cloudflare
R2, DigitalOcean Spaces, Backblaze B2, Contabo, Hetzner, MinIO...) also needs Endpoint URL, and
Public Base URL when public files are served from another address.

Public files get a direct S3 URL; private files get /api/method/...generate_file, which
checks the File's permission and redirects to a signed URL. As in the original, the File's
content_hash holds the S3 key.

Where this differs from the original, because this CMS needs it:
- It runs after cms_frontend's image_compress, so S3 receives the final bytes.
- A file keeps its media library folder (the original moved all to Home/Attachments).
- Migrating skips files in use and never deletes local copies: pages hold /files/ URLs
  inside their layouts, so moving those files would break the pages.
- An S3 object is deleted only with the last File row that uses it.
- Fonts stay local: a browser refuses @font-face from another origin without bucket CORS.

S3 files have no web sizes, poster or MP4 (image_variants and video_processing work from
files on disk), and the image editor cannot open them.
"""
import datetime
import mimetypes
import os
import random
import re
import string
from urllib.parse import quote, urlencode, urlsplit, urlunsplit

import boto3
import frappe
from boto3.exceptions import S3UploadFailedError
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from frappe import _
from frappe.utils import cint

SETTINGS = "S3 File Attachment"
GENERATE_FILE = "/api/method/go1_cms.go1_cms.s3_attachment.generate_file"
LOCAL_PREFIXES = ("/files/", "/private/files/")
# Read back from disk by Frappe, so they stay local (conf: ignore_s3_upload_for_doctype).
IGNORED_DOCTYPES = ["Data Import", "Prepared Report"]
FONT_TYPES = (".woff", ".woff2", ".ttf", ".otf", ".eot")
MAX_KEY = 140  # content_hash is a Data field
DEFAULT_EXPIRY = 120
# How a provider says it has no ACLs, or refuses to set one; public access then comes from its bucket settings.
ACL_REFUSED = ("AccessControlListNotSupported", "NotImplemented", "InvalidArgument", "AccessDenied")
MAX_FAILURES = 20  # wrong credentials fail every file: stop instead of logging thousands


def is_configured():
	# Read from Singles: uploads must not fail between a code update and the migrate
	# that creates this doctype.
	rows = frappe.db.sql("SELECT value FROM `tabSingles` WHERE doctype = %s AND field = 'bucket_name'", SETTINGS)
	return bool(rows and rows[0][0])


class S3Operations:
	def __init__(self):
		self.s3_settings_doc = frappe.get_doc(SETTINGS, SETTINGS)
		credentials = {}
		if self.s3_settings_doc.aws_key and self.s3_settings_doc.get_password("aws_secret", raise_exception=False):
			credentials = {
				"aws_access_key_id": self.s3_settings_doc.aws_key,
				"aws_secret_access_key": self.s3_settings_doc.get_password("aws_secret"),
			}
		self.endpoint_url = (self.s3_settings_doc.endpoint_url or "").strip().rstrip("/")
		self.addressing_style = (self.s3_settings_doc.addressing_style or "Auto").lower()
		if self.addressing_style == "auto" and self.endpoint_url:
			self.addressing_style = "path"
		self.S3_CLIENT = boto3.client(
			"s3",
			# Signing needs a region; providers without regions accept this one.
			region_name=self.s3_settings_doc.region_name or ("us-east-1" if self.endpoint_url else None),
			endpoint_url=self.endpoint_url or None,
			config=Config(signature_version="s3v4", s3={"addressing_style": self.addressing_style}),
			**credentials,
		)
		self.BUCKET = self.s3_settings_doc.bucket_name
		self.folder_name = (self.s3_settings_doc.folder_name or "").strip("/")

	def strip_special_chars(self, file_name):
		return re.sub(r"[^0-9a-zA-Z._-]", "", file_name)

	def key_generator(self, file_name, parent_doctype, parent_name):
		"""The S3 key of a new object. An app can supply its own with the s3_key_generator hook."""
		hook_cmd = frappe.get_hooks().get("s3_key_generator")
		if hook_cmd:
			try:
				key = frappe.get_attr(hook_cmd[0])(
					file_name=file_name, parent_doctype=parent_doctype, parent_name=parent_name
				)
				if key:
					return key.strip("/")
			except Exception:
				frappe.log_error(title="s3_key_generator failed", message=frappe.get_traceback())

		file_name = self.strip_special_chars(file_name.replace(" ", "_"))
		random_part = "".join(random.choice(string.ascii_uppercase + string.digits) for _i in range(8))
		parts = [datetime.datetime.now().strftime("%Y/%m/%d"), parent_doctype, f"{random_part}_"]
		if self.folder_name:
			parts.insert(0, self.folder_name)
		prefix = "/".join(parts)
		return prefix + file_name[-(MAX_KEY - len(prefix)):]

	def upload_files_to_s3_with_key(self, file_path, file_name, is_private, parent_doctype, parent_name):
		content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
		key = self.key_generator(file_name, parent_doctype, parent_name)
		args = {"ContentType": content_type, "Metadata": {"ContentType": content_type}}
		if is_private:
			args["Metadata"]["file_name"] = quote(file_name)
		else:
			args["ACL"] = "public-read"
		try:
			try:
				self.S3_CLIENT.upload_file(file_path, self.BUCKET, key, ExtraArgs=args)
			except S3UploadFailedError as e:
				if "ACL" not in args or not any(reason in str(e) for reason in ACL_REFUSED):
					raise
				args.pop("ACL", None)
				self.S3_CLIENT.upload_file(file_path, self.BUCKET, key, ExtraArgs=args)
		except S3UploadFailedError:
			frappe.log_error(title=f"S3 upload failed: {file_name}", message=frappe.get_traceback())
			frappe.throw(_("File Upload Failed. Please try again."))
		return key

	def delete_from_s3(self, key):
		if not self.s3_settings_doc.delete_file_from_cloud:
			return
		try:
			self.S3_CLIENT.delete_object(Bucket=self.BUCKET, Key=key)
		except ClientError:
			frappe.throw(_("Access denied: Could not delete file"))

	def public_url(self, key):
		base = (self.s3_settings_doc.public_base_url or "").strip().rstrip("/")
		if base:
			return f"{base}/{quote(key)}"
		endpoint = self.S3_CLIENT.meta.endpoint_url.rstrip("/")
		if self.addressing_style == "virtual":
			url = urlsplit(endpoint)
			endpoint = urlunsplit((url.scheme, f"{self.BUCKET}.{url.netloc}", url.path, "", ""))
			return f"{endpoint}/{quote(key)}"
		return f"{endpoint}/{self.BUCKET}/{quote(key)}"

	def get_url(self, key, file_name=None):
		params = {"Bucket": self.BUCKET, "Key": key}
		if file_name:
			params["ResponseContentDisposition"] = 'filename="{}"'.format(file_name.replace('"', ""))
		return self.S3_CLIENT.generate_presigned_url(
			"get_object",
			Params=params,
			ExpiresIn=cint(self.s3_settings_doc.signed_url_expiry_time) or DEFAULT_EXPIRY,
		)


def _parent(doc):
	return doc.attached_to_doctype or "File", doc.attached_to_name


def _skipped(file_url, file_name, parent_doctype):
	"""True for what stays local whatever the settings."""
	if not file_url or not file_url.startswith(LOCAL_PREFIXES):
		return True
	if (file_name or "").lower().endswith(FONT_TYPES):
		return True
	return parent_doctype in (frappe.local.conf.get("ignore_s3_upload_for_doctype") or IGNORED_DOCTYPES)


def _send(doc, s3):
	"""Upload doc's file and point every File row with its URL at S3. Returns the local path,
	or None when the file is not on disk."""
	path = doc.get_full_path()
	if not os.path.isfile(path):
		return None
	parent_doctype, parent_name = _parent(doc)
	key = s3.upload_files_to_s3_with_key(path, doc.file_name, cint(doc.is_private), parent_doctype, parent_name)
	if cint(doc.is_private):
		file_url = f"{GENERATE_FILE}?{urlencode({'key': key, 'file_name': doc.file_name})}"
	else:
		file_url = s3.public_url(key)
	frappe.db.sql("UPDATE `tabFile` SET file_url = %s, content_hash = %s WHERE file_url = %s", (file_url, key, doc.file_url))
	doc.file_url, doc.content_hash = file_url, key
	return path


def _repoint_attachment(doc, old_url):
	"""Frappe's after_insert already wrote the attachment comment with the local URL, and
	the attached record's field may hold it too."""
	doctype, name = doc.attached_to_doctype, doc.attached_to_name
	if not (doctype and name):
		return
	frappe.db.sql(
		"""UPDATE `tabComment` SET content = REPLACE(content, %s, %s)
		WHERE reference_doctype = %s AND reference_name = %s AND comment_type = 'Attachment'""",
		(old_url, doc.file_url, doctype, name),
	)
	for field in {doc.attached_to_field, frappe.get_meta(doctype).get("image_field")}:
		if field and frappe.db.get_value(doctype, name, field) == old_url:
			frappe.db.set_value(doctype, name, field, doc.file_url, update_modified=False)


def file_upload_to_s3(doc, method=None):
	"""File after_insert (after image_compress): move the new file to S3."""
	if cint(doc.is_folder) or not is_configured() or _skipped(doc.file_url, doc.file_name, _parent(doc)[0]):
		return
	if frappe.db.count("File", {"file_url": doc.file_url, "name": ["!=", doc.name]}):
		# Frappe reused an older local file with the same bytes; it stays where it is.
		return
	old_url = doc.file_url
	path = _send(doc, S3Operations())
	if path:
		_repoint_attachment(doc, old_url)
		os.remove(path)


@frappe.whitelist()
def generate_file(key=None, file_name=None):
	"""Send the user to a signed S3 URL of a private file they may read."""
	if not key:
		frappe.local.response["body"] = "Key not found."
		return
	name = frappe.db.get_value("File", {"content_hash": key}, "name")
	if not name:
		raise frappe.DoesNotExistError
	doc = frappe.get_doc("File", name)
	if not doc.is_downloadable():
		raise frappe.PermissionError
	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = S3Operations().get_url(key, doc.file_name)


def _in_use_urls():
	if "cms_frontend" not in frappe.get_installed_apps():
		return set()
	from cms_frontend.media_usage import USAGE_DOCTYPE, rebuild_usage_index

	rebuild_usage_index()
	return set(frappe.get_all(USAGE_DOCTYPE, pluck="file_url", distinct=True, limit_page_length=0))


def _file_rows():
	return frappe.get_all(
		"File", filters={"is_folder": 0}, fields=["name", "file_url", "file_name", "attached_to_doctype"], limit_page_length=0
	)


def migrate_existing_files_job(user=None):
	if not is_configured():
		return {"moved": 0, "failed": 0}
	in_use = _in_use_urls()
	s3 = S3Operations()
	moved = failed = 0
	seen = set()
	for row in _file_rows():
		if failed >= MAX_FAILURES:
			break
		url = row.file_url
		if url in seen or url in in_use or _skipped(url, row.file_name, row.attached_to_doctype or "File"):
			continue
		seen.add(url)
		try:
			doc = frappe.get_doc("File", row.name)
			if _send(doc, s3):
				_repoint_attachment(doc, url)
				moved += 1
			frappe.db.commit()
		except Exception:
			frappe.db.rollback()
			failed += 1
			frappe.log_error(title=f"S3 migration failed: {row.file_name}", message=frappe.get_traceback())
	if user:
		frappe.publish_realtime(
			"msgprint",
			_("S3 migration finished: {0} files copied, {1} failed, {2} in use and left local.").format(moved, failed, len(in_use)),
			user=user,
		)
	return {"moved": moved, "failed": failed}


@frappe.whitelist()
def migrate_existing_files():
	"""Copy existing local files to S3, in the background (a site can hold thousands)."""
	frappe.only_for("System Manager")
	if not is_configured():
		frappe.throw(_("Save a bucket name first."))
	frappe.enqueue(
		"go1_cms.go1_cms.s3_attachment.migrate_existing_files_job", user=frappe.session.user, queue="long", timeout=14400,
		job_id=f"cms-s3-migrate:{frappe.local.site}", deduplicate=True,
	)
	return True


@frappe.whitelist()
def test_connection():
	"""Write, read back and remove a small object, which is what uploads need the key to do."""
	frappe.only_for("System Manager")
	if not is_configured():
		frappe.throw(_("Save a bucket name first."))
	s3 = S3Operations()
	key = "/".join(filter(None, [s3.folder_name, ".go1cms-connection-test"]))
	try:
		s3.S3_CLIENT.put_object(Bucket=s3.BUCKET, Key=key, Body=b"ok")
		s3.S3_CLIENT.get_object(Bucket=s3.BUCKET, Key=key)["Body"].read()
		s3.S3_CLIENT.delete_object(Bucket=s3.BUCKET, Key=key)
	except (BotoCoreError, ClientError) as e:
		frappe.throw(_("Could not connect: {0}").format(frappe.utils.escape_html(str(e))), title=_("S3 Connection"))
	return True


def delete_from_cloud(doc, method=None):
	"""File on_trash: remove the object, unless another File row still uses it."""
	if cint(doc.is_folder) or not doc.file_url or doc.file_url.startswith(LOCAL_PREFIXES) or not is_configured():
		return
	s3 = S3Operations()
	if not doc.content_hash or not doc.file_url.startswith((GENERATE_FILE, s3.public_url(""))):
		return
	if frappe.db.count("File", {"file_url": doc.file_url, "name": ["!=", doc.name]}):
		return
	s3.delete_from_s3(doc.content_hash)
