# Copyright (c) 2026, Tridots Tech and contributors
from frappe.model.document import Document


class S3FileAttachment(Document):
	def on_update(self):
		from go1_cms.go1_cms.s3_attachment import on_settings_update

		on_settings_update()
