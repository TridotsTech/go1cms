// Copyright (c) 2026, Tridots Tech and contributors
frappe.ui.form.on("S3 File Attachment", {
	async test_connection(frm) {
		if (frm.is_dirty()) await frm.save();
		frappe.call({
			method: "go1_cms.go1_cms.s3_attachment.test_connection",
			freeze: true,
			freeze_message: __("Testing connection..."),
			callback(r) {
				if (r.message) frappe.msgprint(__("Connected: a test file was written, read back and removed."), __("S3 Connection"));
			},
		});
	},
	migrate_existing_files(frm) {
		frappe.confirm(
			__("Copy existing local files to S3? Files used on pages stay local, and nothing is deleted from this server."),
			() => {
				frappe.call({
					method: "go1_cms.go1_cms.s3_attachment.migrate_existing_files",
					callback(r) {
						if (r.message) {
							frappe.msgprint(__("Local files are being migrated. You will get a message when it finishes."), __("S3 Migration"));
						} else {
							frappe.msgprint(__("Retry"));
						}
					},
				});
			}
		);
	},
});
