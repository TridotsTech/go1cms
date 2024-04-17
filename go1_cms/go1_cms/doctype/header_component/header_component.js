// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt
frappe.require("assets/go1_cms/js/jquery.ui.min.js");
frappe.require("assets/go1_cms/js/uppy.min.css");
frappe.require("assets/go1_cms/js/uppy.min.js");
frappe.require("assets/go1_cms/css/jodit.min.css");
frappe.require("assets/go1_cms/js/jodit.min.js");
frappe.require("assets/go1_cms/js/jquery.slimscroll.min.js");
var is_row_updated = 0;
frappe.ui.form.on("Header Component", {
  refresh: function (frm) {
    if (!frm.__islocal) {
      frm.trigger("web_section_html");
      if (frm.doc.page_type == "Adaptive") {
        frm.trigger("mobile_section_html");
      }
      if (is_row_updated == 1) {
        $('[data-label="Reload"]').parent().click();
        is_row_updated = 0;
      }
    }
    frm.trigger("render_image_preview");
  },
  web_section_html: function (frm) {
    frm.events.section_html(frm, "web_section", "web_section_html", "Web");
  },
  section_html: function (frm, field, html, device_type) {
    let wrapper = $(frm.get_field(html).wrapper).empty();
    let table = $(`<table class="table table-bordered">
            <thead>
                <tr>
                    <th>${__("Section")}</th>
                   <th>${__("Column Index")}</th>
                    <th></th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>`).appendTo(wrapper);
    /* <style>
            div[data-fieldname="${html}"] table td .copied{
                background: grey; color: #fff; padding: 5px 10px; border-radius: 5px; right: 0; 
                position: absolute; bottom: 0px; display: none;
            }
        </style>*/
    if (frm.doc[field] && frm.doc[field].length > 0) {
      frm.doc[field].map((f) => {
        let section_data = "";
        if (has_common(frappe.user_roles, ["System Manager"])) {
          section_data = `<a href="/app/page-section/${f.section}">${f.section}</a>`;
          if (f.section != f.section_title) {
            if (f.section_name) {
              section_data += `<br><span style="float: left;margin-left: 43px;">${f.section_name}</span>`;
            } else {
              section_data += `<br><span style="float: left;margin-left: 43px;">${f.section_title}</span>`;
            }
          }
        } else {
          // section_data = `${f.section_title}`;
          if (f.section_name) {
            section_data += `<br><span style="float: left;margin-left: 43px;">${f.section_name}</span>`;
          } else {
            section_data += `<br><span style="float: left;margin-left: 43px;">${f.section_title}</span>`;
          }
        }
        let route = "";
        if (!has_common([f.section_type], ["Slider", "Static Section"])) {
          route = f.route ? f.route : "";
        }
        let row = $(`<tr data-id="${f.name}">
                    <td style="width: 50%;"><img src="/assets/go1_cms/images/section-icon.svg" style="height:30px;cursor: all-scroll;position: relative;top: 8px;margin-right: 10px;"> ${section_data}</td>
                    <td style="width: 20%;" class="col-idx"></td>
                    <td class="btns" style="width:50%;"></td></tr>`).appendTo(
          table
        );
        // <span class="copied">Copied!</span>
        var col_sec = $(
          `<input type="number" class="form-control" data-index="${f.idx}" value="${f.column_index}"/>`
        );
        $(row).find(".col-idx").append(col_sec);
        col_sec.change(() => {
          var p_type = frm.doc.page_type;
          var idx = $(col_sec).attr("data-index");
          cur_frm.get_field("web_section").grid.data[idx - 1].column_index =
            $(col_sec).val();
          cur_frm.refresh_field("web_section");
          if (p_type != "Adoptive") {
            cur_frm.set_value("page_type", "Adoptive");
          } else {
            cur_frm.set_value("page_type", "Responsive");
          }
          cur_frm.refresh_field("page_type");
        });

        let allow = false;
        if (f.section_type != "Slider") allow = true;
        else {
          let slider_link = $(
            `<button class="btn btn-primary btn-xs" style="margin-right: 10px;"><span class="fa fa-edit"></span></button>`
          );
          $(row).find(".btns").append(slider_link);
          slider_link.click(function () {
            frappe.set_route("List", "Slider");
          });
        }
        if (allow) {
          let modify_data = $(
            `<button class="btn btn-primary btn-xs" style="margin-right: 10px;"><span class="fa fa-edit"></span></button>`
          );
          $(row).find(".btns").append(modify_data);
          modify_data.click(() => {
            new modify_section_data({
              section: f.section,
              content_type: "Data",
            });
          });
        }
        if (device_type == "Mobile") {
          let modify_design = $(
            `<button class="btn btn-info btn-xs" style="margin-right: 10px;"><span class="fa fa-code"></span></button>`
          );
          $(row).find(".btns").append(modify_design);
          modify_design.click(() => {
            new modify_section_data({
              section: f.section,
              content_type: "Design",
            });
          });
        }
        let delete_section = $(
          `<button class="btn btn-danger btn-xs"><span class="fa fa-trash"></span></button>`
        );
        $(row).find(".btns").append(delete_section);
        delete_section.click(() => {
          frm.events.delete_sections(frm, f.name, f.parentfield);
        });
      });
    } else {
      $(table)
        .find("tbody")
        .append(`<tr><td colspan="2">No Records Found!</td></tr>`);
    }
    // let add_section = $(`<button class="btn btn-primary">Add Existing Section</button>`).appendTo(wrapper);
    let create_section = $(
      `<button class="btn btn-sm btn-primary" style="margin-left: 15px;">Add New Section</button>`
    ).appendTo(wrapper);
    // add_section.click(()=>{
    //     new add_new_section({
    //         parentfield: field,
    //         doctype: 'Mobile Page Section',
    //         section_type: 'existing',
    //         frm: frm
    //     });
    // })
    create_section.click(() => {
      new add_new_section({
        parentfield: field,
        doctype: "Mobile Page Section",
        section_type: "new",
        frm: frm,
        device_type: device_type,
      });
    });
    setTimeout(function () {
      $(cur_frm.$wrapper)
        .find('div[data-fieldname="' + html + '"] table tbody')
        .sortable({
          items: "tr",
          opacity: 0.7,
          distance: 20,
          update: function (e, ui) {
            $(cur_frm.$wrapper)
              .find('div[data-fieldname="' + html + '"] table tbody tr')
              .each(function (k, v) {
                frappe.model.set_value(
                  "Mobile Page Section",
                  $(this).attr("data-id"),
                  "idx",
                  k + 1
                );
                refresh_field("mobile_section");
                refresh_field("web_section");
                is_row_updated = 1;
              });
          },
        });
    }, 1000);
  },
  delete_sections: function (frm, name, parentfield) {
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.delete_section",
      args: {
        name: name,
        parentfield: parentfield,
      },
      callback: function (r) {
        cur_frm.reload_doc();
      },
    });
  },
  pick_layout(frm) {
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.header_component.header_component.get_header_layouts",
      args: {},
      freeze: true,
      callback: (res) => {
        // console.log(">> footer layout api response <<",res)
        if (res && res.message && res.message.length > 0) {
          frm.events.open_footer_popoup(frm, res.message);
          frm.footer_layout_api_data = res.message;
          frm.r___id = Math.floor(Math.random() * 100);
        } else {
          frappe.throw("There is no layout to view..!");
        }
      },
    });
  },
  open_footer_popoup(frm, layouts) {
    let layout_dialogs = new frappe.ui.Dialog({
      title: "Pick Layout",
      fields: [{ fieldname: "layout_html", fieldtype: "HTML" }],
    });
    let layout_wrapper = layout_dialogs.fields_dict.layout_html.$wrapper;
    $(layout_dialogs.$wrapper)
      .find(".modal-dialog")
      .css({ "min-width": "70%" });
    layout_dialogs.show();
    // empty seleted palette colour id
    cur_frm.selected_palette_id = "";
    // end
    layout_dialogs.set_primary_action("Save", () => {
      frm.events.save_update_layout(frm, layout_dialogs);
    });
    let p_add_html = "";
    layouts.map((each_p) => {
      p_add_html += `<div class="each-palette-div" style="flex:0 0 calc(33.33% - 20px);position:relative;">
		<label style="cursor:pointer;width:100%;" value="${each_p.name}">
			<div style="width:80%;height:80px;margin:auto;
				background-image: url(${
          each_p.preview
            ? "'" + each_p.preview.replace(" ", "%20") + "'"
            : "/files/no-img.jpg"
        });
				background-size:cover;
				background-repeat: no-repeat;
				background-position:top;
				border: 1px solid #e5e5e5;">
			</div>
			<div class="palette" style="width:100%;">
				<p style="margin: 0;font-size: 15px;font-weight: bold;
					margin-top: 10px;color: #222;white-space: nowrap;
					overflow: hidden;text-overflow: ellipsis;text-align:center">${each_p.title}
				</p>
			</div>
			<input type="radio" value="${
        each_p.name
      }" name="theme_radio" onclick="select_unselect_layout($(this))" style="position:absolute;top:6px;right:30px;z-index:99;">
		</label></div>`;
    });

    let p_html = `<div class="palette-main-div" id=${cur_frm.r___id}>
						<div class="palatte-sub-div" style="display:flex;flex-wrap:wrap;gap:20px;">
							${p_add_html}
						</div>
					</div>`;
    $(layout_wrapper).html(p_html);
  },
  save_update_layout(frm, dialog) {
    if (frm.selected_layout_id) {
      // console.log(">>seleted layout id<<",frm.selected_layout_id)
      frm.footer_layout_api_data.map((res) => {
        if (frm.selected_layout_id == res.name) {
          cur_frm.set_value("preview", res.preview);
          refresh_field("preview");
          cur_frm.set_value("layout_json", JSON.stringify(res.layout_json));
          refresh_field("layout_json");
          dialog.hide();
          frm.trigger("render_image_preview");
        }
      });
    }
  },
  render_image_preview(frm) {
    frm.image_pre_wrapper = frm.get_field("preview_html").$wrapper;
    $(frm.image_pre_wrapper).empty();
    if (frm.doc.preview) {
      let html = `<div class="img-previw-tag id="${frm.r___id}">
							<div class="img-subcontainer">
								<div class="preview-img"></div>
							</div>
						<style>
						.preview-img{
									width: 100%;
									height: 130px;
									background-image: url('${frm.doc.preview.replace(" ", "%20")}');
									background-size: contain;
									background-repeat: no-repeat;
									padding: 5px;
									background-position: top;
									}
						</style>
						</div>`;
      frm.image_pre_wrapper.html(html);
      refresh_field("preview");
    }
  },
});

var add_new_section = Class.extend({
  init: function (opts) {
    this.parentfield = opts.parentfield;
    this.doctype = opts.doctype;
    this.section_type = opts.section_type;
    this.frm = opts.frm;
    this.device_type = opts.device_type;

    this.make();
  },
  make: function () {
    let me = this;
    frappe.run_serially([
      () => {
        if (me.section_type == "existing") me.get_all_sections();
        else if (me.section_type == "new") me.get_section_templates();
      },
      () => {
        if (
          (me.section_type == "existing" && me.sections) ||
          (me.section_type == "new" && me.templates)
        )
          me.make_dialog();
        else {
          frappe.msgprint(
            "No sections are available. Please create a new section."
          );
        }
      },
    ]);
  },
  get_all_sections: function () {
    let me = this;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_sections",
      args: {
        device_type: me.device_type,
      },
      async: false,
      callback: function (r) {
        me.sections = r.message;
      },
    });
  },
  get_section_templates: function () {
    let me = this;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_header_section_templates",
      args: {
        device_type: me.device_type,
      },
      async: false,
      callback: function (r) {
        me.groups = r.message.template_groups;
        me.templates = r.message.templates;
      },
    });
  },
  make_dialog: function () {
    let me = this;
    let title = "Pick a section";
    if (this.section_type == "new") title = "Create New section";
    this.dialog = new frappe.ui.Dialog({
      title: __(title),
      // fields: [{ "label": __("Enter Section Title"), "fieldname": "title_name", "fieldtype": "Data" }, { "fieldname": "section_html", "fieldtype": "HTML" }]
      fields: [{ fieldname: "section_html", fieldtype: "HTML" }],
    });
    this.selected_section = [];
    this.dialog.set_primary_action(__("Save"), function () {
      if (me.section_type == "existing") {
        if (me.selected_section.length > 0) {
          $(me.selected_section).each(function (k, v) {
            let row = frappe.model.add_child(
              me.frm.doc,
              me.doctype,
              me.parentfield
            );
            row.section = v.section;
            row.section_type = v.section_type;
            row.content_type = v.content_type;
          });
          me.frm.save();
          me.dialog.hide();
        } else {
          frappe.throw("Please pick any section");
        }
      } else {
        if (me.selected_section.length > 0) {
          let titles = "";
          let val = me.dialog.get_values();
          if (val) {
            titles = val.title_name;
          }
          frappe.call({
            method:
              "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.convert_template_to_section",
            args: {
              template: me.selected_section[0].template,
              business: cur_frm.doc.business,
              section_name: titles,
            },
            callback: function (r) {
              if (r.message) {
                let row = frappe.model.add_child(
                  me.frm.doc,
                  me.doctype,
                  me.parentfield
                );
                row.section = r.message.name;
                row.section_type = r.message.section_type;
                row.content_type = r.message.content_type;
                row.section_name = r.message.section_name;
                me.frm.save();
                me.dialog.hide();
              }
            },
          });
        } else {
          frappe.throw("Please pick any section");
        }
      }
    });
    this.dialog.show();
    this.section_html();
    this.dialog.$wrapper.find(".form-column.col-sm-12").css("padding", "0");
    this.dialog.$wrapper
      .find(".form-section")
      .attr(
        "style",
        "width: calc(100% + 6px);margin-left: -7px;padding-top: 0;margin-top: 0;"
      );
    this.dialog.$wrapper
      .find('[data-fieldname="section_html"]')
      .attr("style", "margin-bottom: 0;");
    this.dialog.$wrapper.find(".modal-dialog").css("width", "90%");
    this.dialog.$wrapper.find(".modal-dialog").css("max-width", "1000px");
    this.dialog.$wrapper.find(".modal-content").css("height", "600px");
  },

  section_html: function () {
    let me = this;
    let wrapper = this.dialog.fields_dict.section_html.$wrapper.empty();
    let html = $(`<div class="row" id="SectionList"></div>
            <style>
                div[data-fieldname="section_html"] #SectionList .section-title{
                    padding: 42% 2%; text-align: center; height: 205px;
                }
                div[data-fieldname="section_html"] #SectionList .section-item.active{
                    border: 1px solid #0c9e0c; background: #efefef1f; color: #0c9e0c;
                }
                div[data-fieldname="section_html"] #SectionList .section-img{
                    position: relative; height: 165px;
                }
                div[data-fieldname="section_html"] #SectionList .section-img img{
                    position: absolute; top: 50%; left: 50%; max-height: 160px;
                    transform: translate(-50%, -50%); vertical-align: middle;
                }
                div[data-fieldname="section_html"] #SectionList .section-item{
                    margin-bottom: 10px; border: 1px solid #ddd; background: #f3f3f3; cursor:pointer;
                }
                div[data-fieldname="section_html"] #SectionList .section-item p{
                    text-align: center;
                }
                li.active{background-color:#f3f3f3;}
                </style>`).appendTo(wrapper);
    if (me.groups.length > 0) {
      section_groups = me.groups;
    }
    let data = me.sections ? me.sections : me.templates;
    if (me.groups.length > 0) {
      wrapper
        .find("#SectionList")
        .append(
          "<div class='col-md-3' id='sec-left-content' style='background-color: #fff;min-height: 547px;margin-left: -15px;position: fixed;left: 1.5%;border-right: 1px solid #ddd;'></div>"
        );
      wrapper
        .find("#SectionList")
        .append(
          "<div class='col-md-9' id='sec-right-content' style='padding-top:20px;margin-left:25%'></div>"
        );
      var group_html =
        "<span style='background: #f3f3f3;float: left;width: calc(100% + 32px);margin-left: -18px;padding: 10px 15px;font-size: 15px;font-weight: bold;border-bottom: 1px solid #ddd;'>Filter By Section Group</span>";
      group_html +=
        "<ul style='float: left;width: 100%;padding: 0;margin: 0;'><li style='list-style:none;float: left;width: calc(100% + 30px);padding: 10px 15px;border-bottom: 1px solid #ddd;margin-left: -15px;'><a class='group-link' onclick=filter_section('All')>All</a></li>";
      for (var i = 0; i < me.groups.length; i++) {
        group_html +=
          '<li style="list-style:none;float: left;width: calc(100% + 30px);padding: 10px 15px;border-bottom: 1px solid #ddd;margin-left: -15px;"><a class="group-link" style="float: left;width: 100%;text-decoration: none;"';
        group_html +=
          'data-group="' +
          me.groups[i].group_name +
          '" id="dtgroup' +
          i +
          '" onclick=filter_section(' +
          i +
          ")>" +
          me.groups[i].group_name +
          "</a></li>";
      }
      group_html += "</ul>";
      wrapper.find("#SectionList").find("#sec-left-content").append(group_html);
    } else {
      wrapper
        .find("#SectionList")
        .append(
          "<div class='col-md-12' id='sec-right-content' style='padding-top:20px'></div>"
        );
    }
    data.map((f) => {
      let template = `<div class="section-title" data-group='${f.section_group}'>${f.name}</div>`;
      if (f.image) {
        template = `<div class="section-img"><img src="${f.image}" /></div><p>${f.name}</p>`;
      }
      let item = $(`<div class="col-md-4 col-sm-6 col-xs-6" style="float:left">
                    <div class="section-item">${template}</div>
                </div>`);
      if (me.groups.length == 0) {
        item = $(`<div class="col-md-3 col-sm-6 col-xs-6" style="float:left">
                    <div class="section-item">${template}</div>
                </div>`);
      }
      wrapper.find("#SectionList").find("#sec-right-content").append(item);
      item.click(function () {
        if (me.section_type == "existing") {
          let check = me.selected_section.find((obj) => obj.section == f.name);
          if (check) {
            me.selected_section = me.selected_section.filter(
              (obj) => obj.section != f.name
            );
            $(item).find(".section-item").removeClass("active");
          } else {
            me.selected_section.push({
              section: f.name,
              section_type: f.section_type,
              content_type: f.content_type,
            });
            $(item).find(".section-item").addClass("active");
          }
        } else {
          me.selected_section = [{ template: f.name }];
          $(html).find(".section-item").removeClass("active");
          $(item).find(".section-item").addClass("active");
        }
      });
    });

    // wrapper.find('#SectionList').slimScroll({
    //     height: 540
    // })
  },
});

var modify_section_data = Class.extend({
  init: function (opts) {
    this.section = opts.section;
    this.content_type = opts.content_type;
    this.list_section_data =
      this.random_lists =
      this.predefined_lists =
      this.collection_lists =
      this.patterns =
        [];

    this.make();
  },
  make: function () {
    let me = this;
    frappe.run_serially([
      () => {
        if (me.content_type == "Data") {
          me.get_data_fields();
        } else {
          me.patterns = me.get_patterns();
        }
      },
      () => {
        me.make_dialog();
      },
    ]);
  },
  get_data_fields: function () {
    let me = this;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_section_content",
      args: {
        section: me.section,
        content_type: me.content_type,
      },
      async: false,
      callback: function (r) {
        if (r.message) {
          me.fields = r.message;
        }
      },
    });
  },
  get_patterns: function () {
    let patterns = [];
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_patterns_list",
      args: {},
      async: false,
      callback: function (r) {
        if (r.message) {
          patterns = r.message;
        }
      },
    });
    return patterns;
  },
  make_dialog: function () {
    let me = this;
    let title = "Section Data";
    frappe.call({
      method: "frappe.client.get_value",
      args: {
        doctype: "Page Section",
        filters: {
          name: me.section,
        },
        fieldname: ["section_name", "section_title"],
      },
      async: false,
      callback: function (r) {
        if (r.message) {
          let value;
          if (r.message.section_name) title = r.message.section_name;
          else if (r.message.section_title) title = r.message.section_title;
        }
      },
    });
    let fields = [];
    // console.log(this.content_type);
    if (this.content_type == "Data") fields = this.get_fields_list();
    else fields = [{ fieldname: "pattern_html", fieldtype: "HTML" }];
    if (this.content_type == "Data" && fields.length == 0)
      frappe.throw("There is no editable part available for this section.");
    this.dialog = new frappe.ui.Dialog({
      title: __(title),
      fields: fields,
    });

    this.dialog.set_primary_action(__("Save"), function () {
      if (me.content_type == "Data") me.save_data();
      else me.update_design();
    });

    this.dialog.show();
    // this.dialog.$wrapper.find('input[data-fieldtype="Data"],input[data-fieldtype="Link"],input[data-fieldtype="Select"],input[data-fieldtype="Int"]').css("max-width", "330px");
    this.dialog.$wrapper.find(".modal-dialog").css("width", "1000px");
    // if(this.fields.allow_update_to_style==1){
    //     this.dialog.$wrapper.find('.form-page.form-page-section').css("width", "70%");
    //     this.dialog.$wrapper.find('.form-page.form-page-section').css("float", "left");
    //     this.dialog.$wrapper.find('.form-layout').css("width", "calc(100% + 30px)");
    //     this.dialog.$wrapper.find('.form-layout').css("float", "left");
    //     this.dialog.$wrapper.find('.form-layout').css("background", "#fff");
    //     this.dialog.$wrapper.find('.form-section').css("margin-left", "0");

    // }
    if (this.fields.allow_update_to_style == 1) {
      if (this.fields.styles.length > 1) {
        this.dialog.$wrapper.find(".form-layout").css("float", "left");
        this.dialog.$wrapper.find(".form-section").css("margin-left", "0");
        this.dialog.$wrapper.find(".form-layout").css("background", "#fff");
        this.dialog.$wrapper
          .find(".form-layout")
          .css("width", "calc(100% + 30px)");
        this.dialog.$wrapper
          .find(".row.form-section.visible-section")
          .css("width", "70%");
        this.dialog.$wrapper
          .find(".row.form-section.visible-section")
          .css("float", "left");
        this.dialog.$wrapper
          .find(".row.form-section.visible-section:first-child")
          .css("width", "30%");
        this.dialog.$wrapper
          .find(".row.form-section.visible-section:first-child")
          .css("border-right", "1px solid #ddd");
        this.dialog.$wrapper
          .find(".row.form-section.visible-section:first-child")
          .css("min-height", "720px");
        this.dialog.$wrapper
          .find(".row.form-section.visible-section:first-child")
          .find("h6")
          .attr(
            "style",
            "margin-left: -20px;margin-top: -15px;background-color: #f5f5f5;width: calc(100% + 42px);padding: 10px 15px;"
          );
      }
    }
    if (this.content_type != "Design") {
      this.check_image_field();
      this.check_fieldtype_lists();
    }
    if (this.fields && this.fields.section_type == "Custom Section") {
      if (this.fields.fetch_product == 1) {
        this.dialog.fields_dict.reference_name.$wrapper.removeClass(
          "hide-control"
        );
      } else {
        this.dialog.fields_dict.reference_name.$wrapper.addClass(
          "hide-control"
        );
      }
      this.dialog.fields_dict.fetch_product.input.onchange = function () {
        if (me.dialog.fields_dict.fetch_product.input.checked) {
          me.dialog.fields_dict.reference_name.$wrapper.removeClass(
            "hide-control"
          );
        } else {
          me.dialog.fields_dict.reference_name.$wrapper.addClass(
            "hide-control"
          );
        }
      };
    }
    if (
      this.fields &&
      this.fields.section_type == "Tabs" &&
      this.fields.reference_document != "Custom Query"
    ) {
      this.list_fields();
      this.dialog.fields_dict.item1.onchange = function () {
        let field_name = "";
        if (me.fields.reference_document == "Product Category") {
          field_name = "category_name";
        } else if (me.fields.reference_document == "Product Brand") {
          field_name = "brand_name";
        } else if (me.fields.reference_document == "Product") {
          field_name = "item";
        }
        frappe.call({
          method: "frappe.client.get_value",
          args: {
            doctype: me.fields.reference_document,
            filters: {
              name: me.dialog.fields_dict.item1.value,
            },
            fieldname: [field_name],
          },
          callback: function (r) {
            if (r.message) {
              let value;
              if (r.message.category_name) value = r.message.category_name;
              else if (r.message.brand_name) value = r.message.brand_name;
              else if (r.message.item) value = r.message.item;
              if (value) me.dialog.fields_dict.item_title1.set_value(value);
            }
          },
        });
      };
    }
    if (
      this.fields &&
      this.fields.section_type == "Predefined Section" &&
      this.fields.predefined_section != ""
    ) {
      this.list_fields();
      this.dialog.fields_dict.preitem.onchange = function () {
        let field_name = "name";
        if (me.fields.reference_document == "Product") {
          field_name = "item";
        }
        frappe.call({
          method: "frappe.client.get_value",
          args: {
            doctype: me.fields.reference_document,
            filters: {
              name: me.dialog.fields_dict.preitem.value,
              display_home_page: 0,
            },
            fieldname: [field_name],
          },
          callback: function (r) {
            if (r.message) {
              let value;
              if (r.message.item) value = r.message.item;
              if (value) me.dialog.fields_dict.pre_title.set_value(value);
            }
          },
        });
      };
    }
    if (this.fields && this.fields.section_type == "Collections") {
      this.list_fields();
      // this.dialog.fields_dict.collections.onchange = function() {
      //     this.list_fields()
      // }
    }

    if (
      this.fields &&
      this.fields.section_type == "Tabs" &&
      this.fields.reference_document == "Custom Query"
    ) {
      this.list_fields();
      this.dialog.fields_dict.tab_item.onchange = function () {
        let field_name = "";
        if (me.fields.reference_document == "Custom Query") {
          field_name = "name";
        }
        frappe.call({
          method: "frappe.client.get_value",
          args: {
            doctype: me.fields.reference_document,
            filters: {
              name: me.dialog.fields_dict.tab_item.value,
            },
            fieldname: [field_name],
          },
          callback: function (r) {
            if (r.message) {
              let value;
              if (r.message.name) value = r.message.name;
              if (value) me.dialog.fields_dict.tab_title.set_value(value);
            }
          },
        });
      };
    }
    if (this.fields && this.fields.section_type == "Lists") {
      this.list_fields();
      this.dialog.fields_dict.item.onchange = function () {
        let field_name = "";
        if (me.fields.reference_document == "Product Category") {
          field_name = "category_name";
        } else if (me.fields.reference_document == "Product Brand") {
          field_name = "brand_name";
        } else if (me.fields.reference_document == "Product") {
          field_name = "item";
        }
        frappe.call({
          method: "frappe.client.get_value",
          args: {
            doctype: me.fields.reference_document,
            filters: {
              name: me.dialog.fields_dict.item.value,
            },
            fieldname: [field_name],
          },
          callback: function (r) {
            if (r.message) {
              let value;
              if (r.message.category_name) value = r.message.category_name;
              else if (r.message.brand_name) value = r.message.brand_name;
              else if (r.message.item) value = r.message.item;
              if (value) me.dialog.fields_dict.item_title.set_value(value);
            }
          },
        });
      };
    }
    if (this.content_type == "Design") {
      this.pattern_html();
    }
  },
  get_fields_list: function () {
    let me = this;
    let field_list = [];
    if (this.content_type == "Design") {
      field_list.push({});
    }
    if (this.fields.allow_update_to_style == 1) {
      if (this.fields.styles.length > 1) {
        var styles = this.fields.styles;
        field_list.push({
          fieldtype: "Section Break",
          fieldname: "sb_design",
          label: "Design",
          collapsible: 0,
        });
        for (var i = 0; i < styles.length; i++) {
          field_list.push({
            fieldtype: styles[i].fieldtype,
            fieldname: styles[i].fieldname,
            label: styles[i].label,
            default: styles[i].default,
          });
        }
      }
    }
    if (this.fields.section_type == "Custom Section") {
      field_list.push({
        fieldname: "fetch_product",
        fieldtype: "Check",
        default: this.fields.fetch_product,
        label: __("Get Data From Products"),
      });
      field_list.push({
        fieldname: "reference_name",
        fieldtype: "Link",
        label: __(this.fields.reference_document),
        options: this.fields.reference_document,
        reqd: 1,
        default: this.fields.reference_name || "",
        depends_on: "eval: {{doc.fetch_product == 1}}",
      });
      field_list.push({ fieldtype: "Column Break", fieldname: "col_br" });
      field_list.push({
        fieldname: "no_of_records",
        fieldtype: "Int",
        label: __("No. Of Records"),
        options: this.fields.no_of_records,
        reqd: 1,
        default: this.fields.no_of_records || "",
      });
      if (this.fields.content.length > 0) {
        field_list.push({ fieldtype: "Section Break", fieldname: "sec_br" });
      }
    }
    let distinct_groups = [
      ...new Set(this.fields.content.map((obj) => obj.group_name)),
    ];
    $(distinct_groups).each(function (key, value) {
      let fields = me.fields.content.filter((obj) => obj.group_name == value);
      if (distinct_groups.length > 1) {
        field_list.push({
          fieldtype: "Section Break",
          fieldname: "sb" + key,
          label: value,
          collapsible: 1,
        });
      }

      $(fields).each(function (k, v) {
        let field = {};
        field.fieldname = v.name;
        field.fieldtype = v.field_type;
        if (v.field_type == "Attach") {
          field.fieldtype = "Attach Image";
        } else if (v.field_type == "Text") {
          field.fieldtype = "Data";
        } else if (v.fieldtype == "Small Text") {
          field.fieldtype = "Small Text";
        } else if (v.fieldtype == "List") {
          field.fieldtype = "Code";
          field.options = v.fields_json;
        } else if (v.field_type == "Attach Video") {
          field.fieldtype = "Attach";
        } else {
          field.fieldtype = "HTML Editor";
        }
        if (v.content && v.content != "") field.default = v.content;
        field.label = __(v.field_label);
        field_list.push(field);
        if (distinct_groups.length == 1) {
          if (me.fields.content.length > 5) {
            if ((k + 1) % 3 != 0) {
              field_list.push({
                fieldtype: "Column Break",
                fieldname: "cb" + k,
              });
            } else {
              field_list.push({
                fieldtype: "Section Break",
                fieldname: "sb" + k,
              });
            }
          }
        } else {
          if (fields.length > 5 && (k + 1) % 3 != 0) {
            field_list.push({ fieldtype: "Column Break", fieldname: "cb" + k });
          } else if (
            fields.length <= 5 &&
            fields.length > 1 &&
            k % 2 != 0 &&
            k + 1 != fields.length
          ) {
            field_list.push({ fieldtype: "Column Break", fieldname: "cb" + k });
          }
        }
      });
    });
    if (
      this.fields.section_type == "Tabs" &&
      this.fields.reference_document != "Custom Query"
    ) {
      field_list.push({ fieldtype: "Section Break", fieldname: "sec_br_11" });
      field_list.push({
        fieldname: "table_html1",
        fieldtype: "HTML",
      });
      field_list.push({ fieldtype: "Section Break", fieldname: "sec_br_22" });
      field_list.push({
        fieldtype: "Link",
        fieldname: "item1",
        label: __(this.fields.reference_document),
        options: this.fields.reference_document,
        onchange: function () {
          let val = this.get_value();
        },
      });
      field_list.push({
        fieldtype: "Data",
        fieldname: "item_title1",
        label: __("Title"),
      });
      field_list.push({
        fieldname: "no_of_records",
        fieldtype: "Int",
        label: __("No. Of Records"),
        options: this.fields.no_of_records,
        default: this.fields.no_of_records || "",
      });
      field_list.push({ fieldtype: "HTML", fieldname: "save_records" });
      field_list.push({
        fieldtype: "Data",
        fieldname: "is_edit1",
        hidden: 1,
        default: "0",
      });
    }
    if (
      this.fields.section_type == "Tabs" &&
      this.fields.reference_document == "Custom Query"
    ) {
      field_list.push({
        fieldtype: "Section Break",
        fieldname: "tab_sec_br_1",
      });
      field_list.push({
        fieldname: "tab_table_html",
        fieldtype: "HTML",
      });
      field_list.push({
        fieldtype: "Section Break",
        fieldname: "tab_sec_br_2",
      });
      field_list.push({
        fieldtype: "Link",
        fieldname: "tab_item",
        label: __(this.fields.reference_document),
        options: this.fields.reference_document,
        onchange: function () {
          let val = this.get_value();
        },
      });
      field_list.push({
        fieldtype: "Data",
        fieldname: "tab_title",
        label: __("Title"),
      });
      field_list.push({
        fieldname: "no_of_records",
        fieldtype: "Int",
        label: __("No. Of Records"),
        options: this.fields.no_of_records,
        default: this.fields.no_of_records || "",
      });
      field_list.push({ fieldtype: "HTML", fieldname: "tab_save_record" });
      field_list.push({
        fieldtype: "Data",
        fieldname: "is_edit_tab",
        hidden: 1,
        default: "0",
      });
    }
    if (
      this.fields.section_type == "Predefined Section" &&
      !this.fields.dynamic_data &&
      !this.fields.is_login_required
    ) {
      // field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'predefined_sec_br_11' });
      // let data = ''
      field_list.push({
        fieldtype: "Column Break",
        fieldname: "predefined_col_br_1",
      });
      // frappe.call({
      //     method: 'ecommerce_business_store.cms.doctype.web_page_builder.web_page_builder.get_featured_products',
      //     args: {},
      //     async: false,
      //     callback: function(r) {
      //         data = r.message
      //     }
      // })
      let label_name = this.fields.reference_document;
      field_list.push({
        label: __("Add " + label_name),
        fieldtype: "Section Break",
        fieldname: "predefined_sec_br_1",
      });

      field_list.push({
        fieldtype: "Link",
        fieldname: "preitem",
        label: __("Select " + label_name),
        options: this.fields.reference_document,
        get_query: function () {
          let filtercond = "published";
          if (me.fields.reference_document == "Product Category") {
            filtercond = "is_active";
          } else if (me.fields.reference_document == "Product Brand") {
            filtercond = "published";
          } else if (me.fields.reference_document == "Product") {
            filtercond = "is_active";
          }
          return {
            filters: {
              filtercond: 1,
            },
          };
        },
        onchange: function () {
          let val = this.get_value();
          let fieldname = "name";
          if (me.fields.reference_document == "Product Category") {
            fieldname = "category_name";
          } else if (me.fields.reference_document == "Product Brand") {
            fieldname = "brand_name";
          } else if (me.fields.reference_document == "Product") {
            fieldname = "item";
          }
          if (val) {
            frappe.call({
              method: "frappe.client.get_value",
              args: {
                doctype: me.fields.reference_document,
                filters: {
                  name: val,
                },
                fieldname: fieldname,
              },
              async: false,
              callback: function (r) {
                if (r.message) {
                  let value;
                  if (r.message.item) value = r.message.item;
                  if (value) me.dialog.fields_dict.pre_title.set_value(value);
                }
              },
            });
          } else {
            me.dialog.fields_dict.pre_title.set_value("");
          }
        },
      });
      field_list.push({
        fieldtype: "Column Break",
        fieldname: "predefined_col_br_1",
      });
      field_list.push({
        fieldtype: "Data",
        fieldname: "pre_title",
        label: __("Name"),
        read_only: 1,
      });
      field_list.push({
        fieldtype: "Column Break",
        fieldname: "predefined_col_br_1",
      });
      field_list.push({ fieldtype: "HTML", fieldname: "save_prerecords" });
      field_list.push({
        fieldtype: "Section Break",
        fieldname: "predefined_sec_br_22",
      });
      field_list.push({
        fieldname: "predefined_table_html",
        fieldtype: "HTML",
      });

      // field_list.push({
      //     "fieldname": "no_of_records",
      //     "fieldtype": "Int",
      //     "label": __("No. Of Records"),
      //     "options": this.fields.no_of_records,
      //     "default": (this.fields.no_of_records || "")
      // });

      // field_list.push({
      //     "fieldtype": "Data",
      //     "fieldname": "is_edit1",
      //     "hidden": 1,
      //     "default": "0"
      // });
    }
    if (this.fields.section_type == "Lists") {
      field_list.push({ fieldtype: "Column Break", fieldname: "col_br_1" });
      field_list.push({
        fieldname: "no_of_records",
        fieldtype: "Int",
        label: __("No. Of Records"),
        options: this.fields.no_of_records,
        reqd: 1,
        default: this.fields.no_of_records || "",
      });
      field_list.push({ fieldtype: "Section Break", fieldname: "sec_br_1" });
      field_list.push({
        fieldname: "table_html",
        fieldtype: "HTML",
      });
      field_list.push({ fieldtype: "Section Break", fieldname: "sec_br_2" });
      field_list.push({
        fieldtype: "Link",
        fieldname: "item",
        label: __(this.fields.reference_document),
        options: this.fields.reference_document,
        onchange: function () {
          let val = this.get_value();
        },
      });
      field_list.push({
        fieldtype: "Data",
        fieldname: "item_title",
        label: __("Title / Subtitle"),
        description:
          "Enter title, subtitle with a pipe symbol as seperator. Eg. Top Offer | Explore Now!",
      });
      let ecommerce = frappe.get_module("Ecommerce Business Store");
      let default_val = "";
      let options = [
        "Upload image",
        "Image attached to document",
        "Random image from linked document",
        "Pick image from linked document",
      ];
      if (!ecommerce) default_val = "Image attached to document";
      let dt_options = [];
      if (this.fields.image_link_documents) {
        let opts = JSON.parse(this.fields.image_link_documents);
        $(opts).each(function (a, b) {
          dt_options.push(b.document_name);
        });
      }

      field_list.push({
        fieldtype: "Select",
        fieldname: "image_type",
        label: __("Image Type"),
        options: options,
        // "options": "\nRandom images from associated products\nPick / Upload specified image",
        default: default_val,
      });
      field_list.push({
        fieldname: "image_ref_doc",
        fieldtype: "Select",
        options: dt_options,
        label: __("Reference Document"),
        depends_on:
          "eval: {{doc.image_type == 'Random image from linked document' || doc.image_type =='Pick image from linked document'}}",
      });
      field_list.push({ fieldtype: "HTML", fieldname: "img" });
      field_list.push({ fieldtype: "HTML", fieldname: "save_record" });
      field_list.push({
        fieldtype: "Data",
        fieldname: "is_edit",
        hidden: 1,
        default: "0",
      });
      field_list.push({ fieldtype: "Column Break", fieldname: "col_br_2" });
      field_list.push({ fieldtype: "HTML", fieldname: "suggestions" });
    }
    if (this.fields.section_type == "Collections") {
      field_list.push({
        fieldtype: "Link",
        fieldname: "collections",
        label: __("Select Collection List"),
        options: "Collections",
        default: this.fields.collections || "",
        onchange: function () {
          let val = this.get_value();
          if (val) {
            me.list_fields();
          }
        },
      });
      field_list.push({ fieldtype: "Column Break", fieldname: "coll_col_br" });
      field_list.push({ fieldtype: "Section Break", fieldname: "coll_sec_br" });
      field_list.push({
        fieldname: "collections_table_html",
        fieldtype: "HTML",
      });
    }
    if (this.fields.section_type == "Menu") {
      field_list.push({
        fieldtype: "Link",
        fieldname: "menu",
        label: __("Select Menu"),
        options: "Menu",
        default: this.fields.menu || "",
        onchange: function () {},
      });
    }

    return field_list;
  },
  pattern_html: function () {
    let me = this;
    let html = this.dialog.fields_dict.pattern_html.$wrapper.empty();
    $(`<div class="patterns row"></div><style>
            div[data-fieldname="pattern_html"] .patterns .img-list{min-height: 50px;margin-bottom: 10px;padding: 10px;border: 2px solid transparent;}
            div[data-fieldname="pattern_html"] .patterns .img-list.active{border-color: #0bc50b;}
            </style>`).appendTo(html);

    me.patterns.map((f) => {
      let row = $(
        `<div class="col-md-3 img-list"><img src="${f.background_image}" /></div>`
      );
      html.find(".patterns").append(row);
      row.click(function () {
        html.find(".patterns .img-list").removeClass("active");
        row.addClass("active");
        me.selected_pattern = f;
      });
    });
  },
  save_data: function () {
    let me = this;
    let values = me.dialog.get_values();

    var dialog_fields = [];
    let results = [];
    $.each(values, function (k, v) {
      dialog_fields.push(k);
      if (me.fields.section_type != "Lists" && me.fields.section_type != "Tabs")
        results.push({
          name: k,
          content: v,
          doctype: "Section Content",
          parent: me.section,
        });
      else if (
        me.fields.section_type == "Lists" &&
        !has_common(
          [k],
          ["item", "item_title", "is_edit", "image_type", "image_ref_doc"]
        )
      )
        results.push({
          name: k,
          content: v,
          doctype: "Section Content",
          parent: me.section,
        });
      else if (
        me.fields.section_type == "Tabs" &&
        !has_common(
          [k],
          [
            "tab_item",
            "tab_title",
            "is_edit_tab",
            "no_of_records",
            "item1",
            "item_title1",
            "is_edit1",
          ]
        )
      ) {
        results.push({
          name: k,
          content: v,
          doctype: "Section Content",
          parent: me.section,
        });
      } else if (
        me.fields.section_type == "Predefined Section" &&
        !has_common([k], ["preitem", "pre_title"])
      ) {
        results.push({
          name: k,
          content: v,
          doctype: "Section Content",
          parent: me.section,
        });
      } else if (me.fields.section_type == "Collections") {
        results.push({
          name: k,
          content: v,
          doctype: "Section Content",
          parent: me.section,
        });
      }
    });
    $.each(me.dialog.fields, function (k, v) {
      if (v.fieldtype != "Section Break") {
        if (jQuery.inArray(v.fieldname, dialog_fields) === -1) {
          if (
            me.fields.section_type != "Lists" &&
            me.fields.section_type != "Tabs"
          )
            results.push({
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            });
          else if (
            me.fields.section_type == "Lists" &&
            !has_common(
              [k],
              ["item", "item_title", "is_edit", "image_type", "image_ref_doc"]
            )
          )
            results.push({
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            });
          else if (
            me.fields.section_type == "Tabs" &&
            !has_common(
              [k],
              [
                "tab_item",
                "tab_title",
                "is_edit_tab",
                "no_of_records",
                "item1",
                "item_title1",
                "is_edit1",
              ]
            )
          ) {
            results.push({
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            });
          } else if (
            me.fields.section_type == "Predefined Section" &&
            !has_common([k], ["preitem", "pre_title"])
          ) {
            results.push({
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            });
          } else if (me.fields.section_type == "Collections") {
            results.push({
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            });
          }
        }
      }
    });

    if (results.length > 0 || me.list_section_data.length > 0) {
      frappe.call({
        method:
          "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_section_content",
        args: {
          docs: results,
          lists_data: JSON.stringify(me.list_section_data),
          section: me.section,
          business: cur_frm.doc.business,
        },
        freeze: true,
        callback: function (r) {
          if (r.message.status == "Success") {
            frappe.show_alert("Section updated!", 5);
            // me.dialog.hide();
            cur_frm.save();
          }
        },
      });
    } else {
      frappe.throw("Please fill any field");
    }
  },
  update_design: function () {
    let me = this;
    if (this.selected_pattern) {
      this.selected_pattern.section = me.section;
      frappe.call({
        method:
          "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_patterns",
        args: me.selected_pattern,
        callback: function (r) {
          if (r.message.status == "Success") {
            frappe.show_alert("Section updated!", 5);
            me.dialog.hide();
            cur_frm.save();
          }
        },
      });
    }
  },
  check_image_field: function () {
    let me = this;
    let image_fields = this.fields.content.filter(
      (obj) => obj.field_type == "Attach"
    );
    $(image_fields).each(function (k, v) {
      if (v.content != "" && v.content != null && v.content != undefined) {
        me.dialog.fields_dict[v.name].$wrapper
          .find(".img-container")
          .css("display", "block");
        me.dialog.fields_dict[v.name].$wrapper
          .find(".img-container img")
          .attr("src", v.content);
        me.dialog.fields_dict[v.name].$wrapper
          .find(".missing-image")
          .css("display", "none");
        me.dialog.set_value(v.name, v.content);
      }
    });
  },
  check_fieldtype_lists: function () {
    let me = this;
    let list_fields = this.fields.content.filter(
      (obj) => obj.field_type == "List"
    );
    let names_list = [];
    this.fields.content.map((c) => {
      names_list.push(c.name);
    });
    $(list_fields).each(function (k, v) {
      if (v.fields_json) {
        let index = names_list.indexOf(v.name);
        let fields = JSON.parse(v.fields_json) || [];
        let list_html = me.dialog.fields_dict[v.name].$wrapper.empty();
        $(`<div>
                    <button class="btn btn-primary add-list-item">Add Item</button>
                    <table class="table table-bordered">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody></tbody>
                    </table></div>`).appendTo(list_html);
        list_html.find("thead tr").append(`<th>Records</th>`);
        list_html.find("thead tr").append(`<th></th>`);
        let values = [];
        if (v.content) {
          values = JSON.parse(v.content) || [];
          me.dialog.set_value(v.name, v.content);
        }
        if (values.length > 0) {
          values.map((f) => {
            let row = $(`<tr>
                                <td>Row ${f.idx}</td>
                                <td style="width: 25%;">
                                    <button class="btn btn-primary"><span class="fa fa-edit"></span></button>
                                    <button class="btn btn-danger"><span class="fa fa-trash"></span></button>
                                </td>
                            </tr>`);
            row.find(".btn-primary").click(function () {
              me.show_list_modal(index, v, "edit", f);
            });
            row.find(".btn-danger").click(function () {
              let content = values.filter((obj) => obj.idx != f.idx);
              $(content).each(function (i, j) {
                j.idx = i + 1;
              });
              me.fields.content[index].content = JSON.stringify(content);
              me.check_fieldtype_lists();
            });
            list_html.find("tbody").append(row);
          });
        } else {
          list_html
            .find("tbody")
            .html(`<tr><td colspan="2">No records found!</td></tr>`);
        }
        list_html.find(".add-list-item").click(function () {
          me.show_list_modal(index, v, "add");
        });
      }
    });
  },
  show_list_modal: function (index, data, type, edit_data) {
    let me = this;
    let title = type == "add" ? "Add New Item" : "Edit Item";
    let fields = [];
    let fields_list = JSON.parse(data.fields_json) || [];
    $(fields_list).each(function (k, v) {
      let obj = {};
      obj.fieldname = v.field_key;
      obj.label = v.field_label;
      if (v.field_type == "Attach") obj.fieldtype = "Attach";
      else if (v.field_type == "Text") obj.fieldtype = "Data";
      else if (v.field_type == "Small Text") obj.fieldtype = "Text";
      else if (v.field_type == "Attach Video") obj.fieldtype = "Attach";
      else obj.fieldtype = "HTML Editor";
      fields.push(obj);
    });
    let list_dialog = new frappe.ui.Dialog({
      title: title,
      fields: fields,
      primary_action_label: __("Save"),
      primary_action(values) {
        let content = JSON.parse(data.content || "[]");
        if (type == "add") {
          values.idx = content.length + 1;
          content.push(values);
        } else {
          let keys = Object.keys(values);
          $(content).each(function (key, val) {
            if (val.idx == edit_data.idx) {
              $(keys).each(function (i, j) {
                val[j] = values[j];
              });
            }
          });
        }
        me.fields.content[index].content = JSON.stringify(content);
        list_dialog.hide();
        me.check_fieldtype_lists();
      },
    });
    list_dialog.show();
    if (type == "edit") {
      let keys = Object.keys(edit_data);
      $(keys).each(function (k, v) {
        list_dialog.set_value(v, edit_data[v]);
      });
    }
  },
  list_fields: function () {
    let me = this;
    if (this.fields.section_type == "Lists") {
      this.table_html(this.fields.custom_section_data);
      this.suggestion_html();
      this.save_btns();
      this.dialog.fields_dict.sec_br_2.wrapper.hide();
    } else if (
      this.fields.section_type == "Tabs" &&
      this.fields.reference_document != "Custom Query"
    ) {
      this.table_html1(this.fields.custom_section_data);
      this.save_btns1();
      this.dialog.fields_dict.sec_br_22.wrapper.hide();
    } else if (
      this.fields.section_type == "Tabs" &&
      this.fields.reference_document == "Custom Query"
    ) {
      this.tab_table_html(this.fields.custom_section_data);
      this.tab_save_btns();
      this.dialog.fields_dict.tab_sec_br_2.wrapper.hide();
    } else if (
      this.fields.section_type == "Predefined Section" &&
      this.fields.predefined_section != ""
    ) {
      me.predefined_items();
      // this.predefined_table_html(this.fields.custom_section_data);
      this.predefined_save_btns();
      // this.dialog.fields_dict.predefined_sec_br_22.wrapper.hide();
    } else if (this.fields.section_type == "Collections") {
      me.collection_items();
      // this.collections_save_btns();
    }
  },
  table_html1: function (section_data) {
    let me = this;
    let html = this.dialog.fields_dict.table_html1.$wrapper.empty();
    let btns = $(`<div>
                <button class="btn btn-primary">${__("Add Record")}</button>
            </div>`).appendTo(html);

    btns.find(".btn-primary").click(function () {
      me.dialog.fields_dict.sec_br_22.wrapper.show();
      me.dialog.fields_dict.sec_br_11.wrapper.hide();
      me.dialog.fields_dict.is_edit1.set_value("0");
      me.dialog.fields_dict.item1.set_value("");
      me.dialog.fields_dict.item_title1.set_value("");
      me.dialog.fields_dict.no_of_records.set_value("");
    });
    let table = $(`<div class="scroll-item"><table class="table table-bordered">
                <thead>
                    <tr>
                        <td>${__("Item")}</td>
                        <td>${__("Title")}</td>
                        <td>${__("No Of Item")}</td>
                        <td></td>
                    </tr>
                </thead>
                <tbody></tbody>
            </table></div>`).appendTo(html);
    table.slimScroll({
      height: 350,
    });
    let no_record = false;
    if (!section_data || section_data == "") no_record = true;
    else {
      let data = JSON.parse(section_data);
      if (data && data.length > 0) {
        me.list_section_data = data;
        data.map((f) => {
          let hide = "";

          let row = $(`<tr>
                            <td>${f.item1}</td>
                             <td>${f.item_title1}</td>
                             <td>${f.no_of_records}</td>
                           <td>
                            <button class="btn btn-xs btn-primary"><span class="fa fa-edit"></span></button>
                            <button class="btn btn-xs btn-danger"><span class="fa fa-trash"></span></button>
                            </td>
                        </tr>`);
          table.find("tbody").append(row);
          row.find(".btn-primary").click(function () {
            me.dialog.fields_dict.is_edit1.set_value(f.idx1);
            me.dialog.fields_dict.item1.set_value(f.item1);
            me.dialog.fields_dict.item_title1.set_value(f.item_title1);
            me.dialog.fields_dict.no_of_records.set_value(f.no_of_records);
            me.dialog.fields_dict.sec_br_22.wrapper.show();
            me.dialog.fields_dict.sec_br_11.wrapper.hide();
          });
          row.find(".btn-danger").click(function () {
            let obj = me.list_section_data.filter((o) => o.idx1 != f.idx1);
            $(obj).each(function (k, v) {
              v.idx1 = k + 1;
            });
            me.list_section_data = obj;
          });
        });
      } else {
        no_record = true;
      }
    }
    if (no_record) {
      table
        .find("tbody")
        .append(`<tr><td colspan="3">No Records Found!</td></tr>`);
    }
  },
  tab_table_html: function (section_data) {
    let me = this;
    let html = this.dialog.fields_dict.tab_table_html.$wrapper.empty();
    let btns = $(`<div>
                <button class="btn btn-primary">${__("Add Record")}</button>
            </div>`).appendTo(html);

    btns.find(".btn-primary").click(function () {
      me.dialog.fields_dict.tab_sec_br_2.wrapper.show();
      me.dialog.fields_dict.tab_sec_br_1.wrapper.hide();
      me.dialog.fields_dict.is_edit_tab.set_value("0");
      me.dialog.fields_dict.tab_item.set_value("");
      me.dialog.fields_dict.tab_title.set_value("");
      me.dialog.fields_dict.no_of_records.set_value("");
    });
    let table = $(`<div class="scroll-item"><table class="table table-bordered">
                <thead>
                    <tr>
                        <td>${__("Item")}</td>
                        <td>${__("Title")}</td>
                        <td>${__("No Of Records")}</td>
                        <td></td>
                    </tr>
                </thead>
                <tbody></tbody>
            </table></div>`).appendTo(html);
    table.slimScroll({
      height: 350,
    });
    let no_record = false;
    if (!section_data || section_data == "") no_record = true;
    else {
      let data = JSON.parse(section_data);
      if (data && data.length > 0) {
        me.list_section_data = data;
        data.map((f) => {
          let hide = "";

          let row = $(`<tr>
                            <td>${f.tab_item}</td>
                             <td>${f.tab_title}</td>
                             <td>${f.no_of_records}</td>
                           <td>
                            <button class="btn btn-xs btn-primary"><span class="fa fa-edit"></span></button>
                            <button class="btn btn-xs btn-danger"><span class="fa fa-trash"></span></button>
                            </td>
                        </tr>`);
          table.find("tbody").append(row);
          row.find(".btn-primary").click(function () {
            me.dialog.fields_dict.is_edit_tab.set_value(f.idx);
            me.dialog.fields_dict.tab_item.set_value(f.tab_item);
            me.dialog.fields_dict.tab_title.set_value(f.tab_title);
            me.dialog.fields_dict.no_of_records.set_value(f.no_of_records);
            me.dialog.fields_dict.tab_sec_br_2.wrapper.show();
            me.dialog.fields_dict.tab_sec_br_1.wrapper.hide();
          });
          row.find(".btn-danger").click(function () {
            let obj = me.list_section_data.filter((o) => o.idx != f.idx);
            $(obj).each(function (k, v) {
              v.idx = k + 1;
            });
            me.list_section_data = obj;
          });
        });
      } else {
        no_record = true;
      }
    }
    if (no_record) {
      table
        .find("tbody")
        .append(`<tr><td colspan="3">No Records Found!</td></tr>`);
    }
  },
  predefined_table_html: function (section_data) {
    let me = this;
    let html = this.dialog.fields_dict.predefined_table_html.$wrapper.empty();
    // let btns = $(`<div>
    //         <button class="btn btn-primary">${__("Add Record")}</button>
    //     </div>`).appendTo(html);

    // btns.find('.btn-primary').click(function() {
    //     // me.dialog.fields_dict.predefined_sec_br_22.wrapper.show();
    //     // me.dialog.fields_dict.predefined_sec_br_11.wrapper.hide();
    //     // me.dialog.fields_dict.is_edit_tab.set_value('0');
    //     me.dialog.fields_dict.preitem.set_value("");
    //     me.dialog.fields_dict.pre_title.set_value("");
    //     // me.dialog.fields_dict.no_of_records.set_value("");
    // })
    var doclabel = me.fields.reference_document;
    let table = $(`<div class="scroll-item"><table class="table table-bordered">
                <thead>
                    <tr>
                        <td>${__("ID")}</td>
                        <td>${__(doclabel + " Name")}</td>
                        <td>${__(doclabel + " Image")}</td>
                        <td>${__("Price")}</td>
                        <td></td>
                    </tr>
                </thead>
                <tbody></tbody>
            </table></div>`).appendTo(html);
    table.slimScroll({
      height: 350,
    });
    let no_record = false;
    if (!section_data || section_data == "") no_record = true;
    else {
      let data = JSON.parse(section_data);
      if (data && data.length > 0) {
        me.list_section_data = data;
        data.map((f) => {
          let hide = "";
          let image = "";
          if (f.product_image) {
            image = f.product_image;
          }
          let fieldname = "name";
          if (me.fields.reference_document == "Product Category") {
            fieldname = "category_name";
          } else if (me.fields.reference_document == "Product Brand") {
            fieldname = "brand_name";
          } else if (me.fields.reference_document == "Product") {
            fieldname = "item";
          }
          let item = "";
          let price = "";

          if (f[fieldname]) {
            item = f[fieldname];
          }
          if (f.price) {
            price = f.price;
          }
          let row = $(`<tr>
                    <td>${f.name}</td>
                     <td>${item}</td>
                     <td><img src="${image}" style="max-height: 30px;max-width: 100%;"></td>
                     <td>${price}</td>
                   <td data-id="${f.name}">
                    <button class="btn btn-xs btn-danger"><span class="fa fa-trash"></span></button>
                    </td>
                </tr>`);
          table.find("tbody").append(row);
          // row.find('.btn-primary').click(function() {
          //     me.dialog.fields_dict.is_edit_pre.set_value(f.idx);
          //     me.dialog.fields_dict.pre_item.set_value(f.pre_item);
          //     me.dialog.fields_dict.pre_title.set_value(f.pre_title);
          //     me.dialog.fields_dict.no_of_records.set_value(f.no_of_records);
          //     me.dialog.fields_dict.predefined_sec_br_2.wrapper.show();
          //     me.dialog.fields_dict.predefine_sec_br_1.wrapper.hide();

          // });
          row.find(".btn-danger").click(function () {
            var name = $(this).parent().attr("data-id");
            let obj = me.list_section_data.filter((o) => o.idx != f.idx);

            let cond = "display_home_page";
            if (me.fields.reference_document == "Product Category") {
              cond = "display_on_home_page";
            } else if (me.fields.reference_document == "Product Brand") {
              cond = "is_active";
            } else if (me.fields.reference_document == "Product") {
              cond = "display_home_page";
            }
            frappe.call({
              method:
                "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_featured_item",
              args: {
                doctype: me.fields.reference_document,
                name: val.preitem,
                checked: 1,
                conditionfield: cond,
              },
              async: false,
              callback: function (r) {},
            });
            me.predefined_items();
          });
        });
      } else {
        no_record = true;
      }
    }
    if (no_record) {
      table
        .find("tbody")
        .append(`<tr><td colspan="3">No Records Found!</td></tr>`);
    }
  },
  collections_table_html: function (section_data) {
    let me = this;
    let html = this.dialog.fields_dict.collections_table_html.$wrapper.empty();
    let table = $(`<div class="scroll-item"><table class="table table-bordered">
                <thead>
                    <tr>
                        <td>${__("ID")}</td>
                        <td>${__("Product Name")}</td>
                    </tr>
                </thead>
                <tbody></tbody>
            </table></div>`).appendTo(html);
    table.slimScroll({
      height: 350,
    });
    let no_record = false;
    if (!section_data || section_data == "") no_record = true;
    else {
      let data = JSON.parse(section_data);
      if (data && data.length > 0) {
        me.list_section_data = data;
        data.map((f) => {
          let hide = "";
          let image = "";
          if (f.product_image) {
            image = f.product_image;
          }
          let row = $(`<tr>
                            <td>${f.name}</td>
                             <td>${f.item}</td>
                        </tr>`);
          table.find("tbody").append(row);
          // row.find('.btn-danger').click(function() {
          //     var name = $(this).parent().attr('data-id')
          //     let obj = me.list_section_data.filter(o => o.idx != f.idx);
          //     frappe.call({
          //         method: 'ecommerce_business_store.cms.doctype.web_page_builder.web_page_builder.update_featured_item',
          //         args: {
          // doctype:me.fields.reference_document,
          //             name: name,
          //             checked: 0
          //         },
          //         async: false,
          //         callback: function(r) {
          //
          //         }
          //     })
          //     me.predefined_items()
          // });
        });
      } else {
        no_record = true;
      }
    }
    if (no_record) {
      table
        .find("tbody")
        .append(`<tr><td colspan="3">No Records Found!</td></tr>`);
    }
  },
  table_html: function (section_data) {
    let me = this;
    let html = this.dialog.fields_dict.table_html.$wrapper.empty();
    let btns = $(`<div>
                <button class="btn btn-warning">${__(
                  "Auto Generate Records"
                )}</button>
                <button class="btn btn-primary">${__(
                  "Add Record Manually"
                )}</button>
            </div>`).appendTo(html);
    btns.find(".btn-warning").click(function () {
      me.random_items();
    });
    btns.find(".btn-primary").click(function () {
      me.dialog.fields_dict.sec_br_2.wrapper.show();
      me.dialog.fields_dict.sec_br_1.wrapper.hide();
      me.dialog.fields_dict.is_edit.set_value("0");
      me.dialog.fields_dict.item.set_value("");
      me.dialog.fields_dict.item_title.set_value("");
      me.dialog.fields_dict.image_type.set_value("");
      let img_html = me.dialog.fields_dict.img.$wrapper.empty();
    });
    let table = $(`<div class="scroll-item"><table class="table table-bordered">
                <thead>
                    <tr>
                        <td>${__("Item")}</td>
                        <td>${__("Title / Subtitle")}</td>
                        <td></td>
                    </tr>
                </thead>
                <tbody></tbody>
            </table></div>`).appendTo(html);
    table.slimScroll({
      height: 350,
    });
    let no_record = false;
    if (!section_data || section_data == "") no_record = true;
    else {
      let data = JSON.parse(section_data);
      if (data && data.length > 0) {
        me.list_section_data = data;
        data.map((f) => {
          let titles = f.item_title.split(" | ");
          let t = titles[0];
          if (titles[1]) t += "<br>" + titles[1];
          if (titles[2]) t += "<br>" + titles[2];
          let hide = "";
          if (
            f.image_type &&
            f.image_type != "Pick / Upload specified image" &&
            f.image_type != "Upload image"
          )
            hide = "hidden";
          let row = $(`<tr>
                            <td>${f.item}</td>
                            <td>${t}</td>
                            <td>
                                <button class="btn btn-xs btn-primary"><span class="fa fa-edit"></span></button>
                                <button class="btn btn-xs btn-info ${hide}"><span class="fa fa-camera"></span></button>
                                <button class="btn btn-xs btn-danger"><span class="fa fa-trash"></span></button>
                            </td>
                        </tr>`);
          table.find("tbody").append(row);
          row.find(".btn-primary").click(function () {
            me.dialog.fields_dict.is_edit.set_value(f.idx);
            me.dialog.fields_dict.item.set_value(f.item);
            me.dialog.fields_dict.item_title.set_value(f.item_title);
            me.dialog.fields_dict.image_type.set_value(f.image_type);
            me.dialog.fields_dict.sec_br_2.wrapper.show();
            me.dialog.fields_dict.sec_br_1.wrapper.hide();
            let img_html = me.dialog.fields_dict.img.$wrapper.empty();
            if (f.image) {
              img_html.append(
                `<div><img src="${f.image}" style="height: 75px;" /></div>`
              );
            }
          });
          row.find(".btn-danger").click(function () {
            let obj = me.list_section_data.filter((o) => o.idx != f.idx);
            $(obj).each(function (k, v) {
              v.idx = k + 1;
            });
            me.list_section_data = obj;
            row.remove();
          });
          row.find(".btn-info").click(function () {
            me.image_dialog(f);
          });
        });
      } else {
        no_record = true;
      }
    }
    if (no_record) {
      table
        .find("tbody")
        .append(`<tr><td colspan="3">No Records Found!</td></tr>`);
    }
  },
  suggestion_html: function () {
    let html = this.dialog.fields_dict.suggestions.$wrapper.empty();
    $(`<div style="background: #ddd;border: 1px solid #ccc;padding: 10px;">
                <h4 style="margin-top: 0;">${__(
                  "Suggestions for Title / Subtitle"
                )}</h4>
                <ul></ul>
            </div>`).appendTo(html);
    let suggestions = [
      "Best Selling",
      "Mega Sale! Limited Stock!",
      "Discover Now!",
      "Shop Now!",
      "Grab Now!",
      "Great Savings!",
      "Explore Now!",
      "Hurry!",
      "Buy Now!",
      "Top Picks",
      "Bestsellers",
      "Hot Picks",
      "Most Popular!",
    ];
    suggestions.map((f) => {
      html.find("ul").append(`<li>${f}</li>`);
    });
  },
  save_btns1: function () {
    let me = this;
    let html = this.dialog.fields_dict.save_records.$wrapper.empty();
    $(`<div>
                <button class="btn btn-sm btn-primary">${__("Save")}</button>
                <button class="btn btn-sm btn-danger">${__("Cancel")}</button>
                </div>`).appendTo(html);
    html.find(".btn-primary").click(function () {
      let val = me.dialog.get_values();
      if (!val.item1 || !val.item_title1)
        frappe.throw("Please fill all columns");
      if (val.is_edit1 == 0) {
        me.list_section_data.push({
          item1: val.item1,
          no_of_records: val.no_of_records,
          item_title1: val.item_title1,
          idx1: me.list_section_data.length + 1,
        });
      } else {
        $(me.list_section_data).each(function (k, v) {
          if (k + 1 == parseInt(val.is_edit1)) {
            v.item1 = val.item1;
            v.item_title1 = val.item_title1;
            v.no_of_records = val.no_of_records;
          }
        });
      }
      me.table_html1(JSON.stringify(me.list_section_data));
      me.dialog.fields_dict.sec_br_22.wrapper.hide();
      me.dialog.fields_dict.sec_br_11.wrapper.show();
    });
    html.find(".btn-danger").click(function () {
      me.dialog.fields_dict.sec_br_22.wrapper.hide();
      me.dialog.fields_dict.sec_br_11.wrapper.show();
    });
  },
  predefined_save_btns: function () {
    let me = this;
    let html = this.dialog.fields_dict.save_prerecords.$wrapper.empty();
    $(`<div>
                <button class="btn btn-sm btn-primary" style="margin-top:25px;padding: 8px 23px !important;">${__(
                  "Add"
                )}</button>
                </div>`).appendTo(html);
    html.find(".btn-primary").click(function () {
      let val = me.dialog.get_values();
      if (!val.preitem || !val.pre_title) {
        frappe.throw("Please fill all columns");
      }
      // frappe.db.set_value('Product',val.preitem,'display_home_page',1)
      // $(me.list_section_data).each(function(k, v) {
      //     v.name = val.preitem;
      //     v.item = val.pre_title;
      // })
      // if (val.is_edit1 == 0) {
      //     me.list_section_data.push({
      //         "name": val.preitem,
      //         "item": val.pre_title,
      //         "idx1": (me.list_section_data.length + 1)
      //     });
      // } else {
      //     $(me.list_section_data).each(function(k, v) {
      //         // if ((k + 1) == parseInt(val.is_edit1)) {
      //             v.item1 = val.item1;
      //             v.item_title1 = val.item_title1;
      //             // v.no_of_records = val.no_of_records;
      //         // }
      //     })
      // }
      // me.predefined_table_html(JSON.stringify(me.list_section_data));

      let cond = "display_home_page";
      if (me.fields.reference_document == "Product Category") {
        cond = "display_on_home_page";
      } else if (me.fields.reference_document == "Product Brand") {
        cond = "is_active";
      } else if (me.fields.reference_document == "Product") {
        cond = "display_home_page";
      }
      frappe.call({
        method:
          "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_featured_item",
        args: {
          doctype: me.fields.reference_document,
          name: val.preitem,
          checked: 1,
          conditionfield: cond,
        },
        async: false,
        callback: function (r) {},
      });
      me.dialog.fields_dict.preitem.set_value("");
      me.dialog.fields_dict.pre_title.set_value("");
      me.predefined_items();

      // me.predefined_table_html(JSON.stringify(me.predefined_lists))
      // me.dialog.fields_dict.predefined_sec_br_22.wrapper.hide();
      // me.dialog.fields_dict.predefined_sec_br_11.wrapper.show();
    });
    // html.find('.btn-danger').click(function() {
    //     me.dialog.fields_dict.predefined_sec_br_22.wrapper.hide();
    //     me.dialog.fields_dict.predefined_sec_br_11.wrapper.show();
    // })
  },
  tab_save_btns: function () {
    let me = this;
    let html = this.dialog.fields_dict.tab_save_record.$wrapper.empty();
    $(`<div>
                <button class="btn btn-sm btn-primary">${__("Save")}</button>
                <button class="btn btn-sm btn-danger">${__("Cancel")}</button>
                </div>`).appendTo(html);
    html.find(".btn-primary").click(function () {
      let val = me.dialog.get_values();
      if (!val.tab_item || !val.tab_title)
        frappe.throw("Please fill all columns");
      if (val.is_edit_tab == 0) {
        me.list_section_data.push({
          tab_item: val.tab_item,
          tab_title: val.tab_title,
          no_of_records: val.no_of_records,
          idx: me.list_section_data.length + 1,
        });
      } else {
        $(me.list_section_data).each(function (k, v) {
          if (k + 1 == parseInt(val.is_edit_tab)) {
            v.tab_item = val.tab_item;
            v.tab_title = val.tab_title;
            v.no_of_records = val.no_of_records;
          }
        });
      }
      me.tab_table_html(JSON.stringify(me.list_section_data));
      me.dialog.fields_dict.tab_sec_br_2.wrapper.hide();
      me.dialog.fields_dict.tab_sec_br_1.wrapper.show();
    });
    html.find(".btn-danger").click(function () {
      me.dialog.fields_dict.tab_sec_br_2.wrapper.hide();
      me.dialog.fields_dict.tab_sec_br_1.wrapper.show();
    });
  },
  save_btns: function () {
    let me = this;
    let html = this.dialog.fields_dict.save_record.$wrapper.empty();
    $(`<div>
                <button class="btn btn-sm btn-primary">${__("Save")}</button>
                <button class="btn btn-sm btn-danger">${__("Cancel")}</button>
                </div>`).appendTo(html);
    html.find(".btn-primary").click(function () {
      let val = me.dialog.get_values();
      if (!val.item || !val.item_title) frappe.throw("Please fill all columns");
      if (val.is_edit == 0) {
        me.list_section_data.push({
          item: val.item,
          item_title: val.item_title,
          idx: me.list_section_data.length + 1,
          image: null,
          image_type: val.image_type,
        });
      } else {
        $(me.list_section_data).each(function (k, v) {
          if (k + 1 == parseInt(val.is_edit)) {
            v.item = val.item;
            v.item_title = val.item_title;
            v.image_type = val.image_type;
          }
        });
      }
      me.table_html(JSON.stringify(me.list_section_data));
      me.dialog.fields_dict.sec_br_2.wrapper.hide();
      me.dialog.fields_dict.sec_br_1.wrapper.show();
    });
    html.find(".btn-danger").click(function () {
      me.dialog.fields_dict.sec_br_2.wrapper.hide();
      me.dialog.fields_dict.sec_br_1.wrapper.show();
    });
  },
  random_items: function () {
    let me = this;
    frappe.run_serially([
      () => {
        me.get_random_records(
          me.fields.reference_document,
          me.dialog.get_value("no_of_records")
        );
      },
      () => {
        me.table_html(JSON.stringify(me.random_lists));
      },
    ]);
  },
  predefined_items: function () {
    let me = this;
    frappe.run_serially([
      () => {
        me.get_predefined_records(
          me.fields.name,
          me.fields.reference_document,
          me.fields.no_of_records,
          me.fields.business
        );
      },
      () => {
        me.predefined_table_html(JSON.stringify(me.predefined_lists));
      },
    ]);
  },
  collection_items: function () {
    let me = this;
    frappe.run_serially([
      () => {
        me.get_collections_records(me.dialog.get_value("collections"));
      },
      () => {
        me.collections_table_html(JSON.stringify(me.collection_lists));
      },
    ]);
  },
  get_random_records: function (dt, records) {
    let me = this;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_random_records",
      args: {
        dt: dt,
        records: records,
        business: cur_frm.doc.business,
      },
      async: false,
      callback: function (r) {
        if (r.message) {
          me.random_lists = r.message;
        }
      },
    });
  },
  get_predefined_records: function (name, dt, no_of_records, business) {
    let me = this;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_predefined_records",
      args: {
        dt: dt,
        records: no_of_records,
        business: cur_frm.doc.business,
        name: name,
      },
      async: false,
      callback: function (r) {
        if (r.message) {
          me.predefined_lists = r.message;
        }
      },
    });
  },
  get_collections_records: function (collections) {
    let me = this;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_collection_records",
      args: {
        collections: collections,
      },
      async: false,
      callback: function (r) {
        if (r.message) {
          me.collection_lists = r.message;
        }
      },
    });
  },
  image_dialog: function (rec) {
    let me = this;
    frappe.run_serially([
      () => {
        me.get_image_album(me.fields.reference_document, rec.item);
      },
      () => {
        me.show_img_dialog(rec);
      },
    ]);
  },
  show_img_dialog: function (rec) {
    let me = this;
    this.imagedialog = new frappe.ui.Dialog({
      title: __("Pick Image"),
      fields: [
        { fieldname: "tab_html", fieldtype: "HTML" },
        { fieldname: "sec_1", fieldtype: "Section Break" },
        { fieldname: "upload_img", fieldtype: "HTML" },
        { fieldname: "sec_2", fieldtype: "Section Break" },
        { fieldname: "image_gallery", fieldtype: "HTML" },
      ],
    });
    this.imagedialog.set_primary_action(__("Save"), function () {
      let active_tab = me.imagedialog.fields_dict.tab_html.$wrapper
        .find("li.active")
        .attr("data-id");
      let image = "";
      if (active_tab == "2") {
        image = me.picked_image;
      } else if (active_tab == "1") {
        image = me.uploaded_image;
      }
      $(me.list_section_data).each(function (k, v) {
        if (v.idx == rec.idx) {
          v.image = image;
        }
      });
      me.imagedialog.hide();
    });
    this.imagedialog.show();
    this.gallery_tab_html();
    this.uploader_component();
    this.gallery_html();
    this.imagedialog.$wrapper.find(".modal-dialog").css("width", "800px");
    this.imagedialog.$wrapper.find(".form-section").css("border-bottom", "0");
  },
  get_image_album: function (dt, dn) {
    let me = this;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_image_album",
      args: {
        dt: dt,
        dn: dn,
        business: cur_frm.doc.business,
      },
      async: false,
      callback: function (r) {
        if (r.message) {
          me.gallery = r.message;
        } else {
          me.gallery = [];
        }
      },
    });
  },
  gallery_tab_html: function () {
    let me = this;
    let tab_html = this.imagedialog.fields_dict.tab_html.$wrapper.empty();
    $(`<div class="gal-tabs">
            <ul>
                <li class="active" data-id="1">${__("Upload Image")}</li>
                <li data-id="2">${__("Pick Image")}</li>
            </ul>
        </div>
        <style>
            div[data-fieldname="tab_html"]{ margin-bottom: 0; }
            div[data-fieldname="tab_html"] .gal-tabs{ text-align: center; }
            div[data-fieldname="tab_html"] .gal-tabs ul{display: inline-flex;list-style:none;}
            div[data-fieldname="tab_html"] .gal-tabs ul li{padding: 5px 25px;cursor: pointer;font-size: 15px;font-weight: 500;}
            div[data-fieldname="tab_html"] .gal-tabs ul li.active{border-bottom: 2px solid #1b8fdb}
        </style>`).appendTo(tab_html);
    this.imagedialog.fields_dict.sec_2.wrapper.hide();
    tab_html.find("li").click(function () {
      tab_html.find("li").removeClass("active");
      if ($(this).attr("data-id") == "1") {
        me.imagedialog.fields_dict.sec_2.wrapper.hide();
        me.imagedialog.fields_dict.sec_1.wrapper.show();
        tab_html.find('li[data-id="1"]').addClass("active");
      } else {
        me.imagedialog.fields_dict.sec_1.wrapper.hide();
        me.imagedialog.fields_dict.sec_2.wrapper.show();
        tab_html.find('li[data-id="2"]').addClass("active");
      }
    });
  },
  gallery_html: function () {
    let me = this;
    let gallery_html =
      this.imagedialog.fields_dict.image_gallery.$wrapper.empty();
    if (this.gallery && this.gallery.length > 0) {
      $(`<div class="gallery row"></div>
                <style>
                div[data-fieldname="image_gallery"] .gallery .gal-items{position: relative;}
                div[data-fieldname="image_gallery"] .gallery .gal-items img{
                    position: absolute; top: 50%; left: 50%; vertical-align: middle;
                    transform: translate(-50%, -50%); width: auto; height: 90%;
                }
                div[data-fieldname="image_gallery"] .gallery .gal-items.active{border: 2px solid #0bc50b;}
                </style>`).appendTo(gallery_html);
      this.gallery.map((f) => {
        let row = $(
          `<div class="col-md-3 gal-items" style="margin-bottom: 10px; height: 100px;"><img src="${f.thumbnail}" /></div>`
        );
        gallery_html.find(".gallery").append(row);
        row.click(function () {
          gallery_html.find(".gal-items").removeClass("active");
          row.addClass("active");
          me.picked_image = f.list_image;
        });
      });
      gallery_html.find(".gallery").slimScroll({
        height: 300,
      });
    } else {
      gallery_html.append(
        `<div style="text-align: center;background: #ddd;padding: 10%;font-size: 20px;border: 1px solid #ccc;border-radius: 4px;">No images found!</div>`
      );
    }
  },
  uploader_component: function () {
    let me = this;
    let uploader = this.imagedialog.fields_dict.upload_img.$wrapper.empty();
    let random = parseInt(Math.random() * 10000);
    uploader.append(
      `<div id="uploader${random}"></div><div id="progress${random}"></div>`
    );
    setTimeout(function () {
      me.upload_component(`#uploader${random}`, `#progress${random}`);
    }, 500);
  },
  upload_component: function (target, progress) {
    let me = this;
    var uppy = Uppy.Core({
      restrictions: {
        maxFileSize: 250000,
        maxNumberOfFiles: 1,
        allowedFileTypes: ["image/*", ".jpg", ".png", ".jpeg", ".gif"],
      },
      meta: {
        doctype: "Page Section",
        docname: me.section,
      },
    })
      .use(Uppy.DragDrop, {
        target: target,
        inline: true,
        note: "Image only up to 250 KB",
      })
      .use(Uppy.XHRUpload, {
        endpoint:
          window.location.origin +
          "/api/method/go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.upload_img",
        method: "post",
        formData: true,
        fieldname: "file",
        headers: {
          "X-Frappe-CSRF-Token": frappe.csrf_token,
        },
      })
      .use(Uppy.StatusBar, {
        target: progress,
        hideUploadButton: false,
        hideAfterFinish: false,
      })
      .on("upload-success", function (file, response) {
        if (response.status == 200) {
          me.uploaded_image = response.body.message.file_url;
          me.imagedialog.$wrapper
            .find(".modal-header .btn-primary")
            .trigger("click");
        }
      });
  },
});
