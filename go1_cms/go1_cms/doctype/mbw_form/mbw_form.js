// Copyright (c) 2024, Tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on("MBW Form", {
  refresh: function (frm) {
    if (frm.doc.__unsaved) {
      frm.set_value("__newname", "SYS-F-");
    }
  },
  is_template: function (frm) {
    if (frm.doc.__unsaved) {
      if (frm.doc.is_template == 1) {
        frm.set_value("__newname", "SYS-F-");
      } else {
        frm.set_value("__newname", "US-F-");
      }
    }
  },
});
