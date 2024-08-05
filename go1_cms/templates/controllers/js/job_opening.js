frappe.ui.form.on("Job Opening", {
  refresh: function (frm) {
    frm.add_custom_button(__("CMS settings web view"), function () {
      frappe.db
        .get_value("Job Opening Website", { job_opening: frm.doc.name }, [
          "name",
        ])
        .then(function (data) {
          window.location.href = `/app/job-opening-website/${data.message?.name}`;
        });
    });
  },
});
