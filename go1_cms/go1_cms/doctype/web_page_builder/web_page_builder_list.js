frappe.listview_settings["Web Page Builder"] = {
  // onload(listview) {
  //   listview.page.set_secondary_action(
  //     "Load Sample Pages",
  //     () => load_sample_data(),
  //     "refresh"
  //   );
  // },
};
function load_sample_data() {
  frappe.call({
    method: "go1_cms.go1_cms.after_install.load_sample_pages",
    args: {},
    freeze: true,
    callback: function (r) {},
  });
}
