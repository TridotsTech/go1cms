let template_json = [];
let layout_json = [];
let origin = location.origin;
let section_type = "speciality_section";
let page_route = "";
let page_title = "";
let page_sections = [];
let component_count = 0;
let pages_html = "";
frappe.pages["go1cms-builder"].on_page_load = function (wrapper) {
  $("head").append(
    '<style>[data-route="go1cms-builder"] button.btn {padding: 5px 10px;}</style>'
  );
  var hash = "";
  var hashes = window.location.href
    .slice(window.location.href.indexOf("?") + 1)
    .split("&");
  for (var i = 0; i < hashes.length; i++) {
    hash = hashes[i].split("=");
  }
  page_route = hash[1];
  if (page_route) {
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_builder_data",
      args: {
        page_route: page_route,
      },
      freeze: true,
      callback: function (r) {
        if (r.message) {
          if (r.message.page_sections && r.message.page_sections != null) {
            page_sections = r.message.page_sections;
          }
          if (r.message.cid && r.message.cid != null) {
            component_count = parseInt(r.message.cid);
          }
          if (r.message.title && r.message.title != null) {
            page_title = r.message.title;
          }
          if (r.message.pages_list && r.message.pages_list != null) {
            pages_html =
              "<div class='page-list'> <div class='list-head'>Pages</div><ul>";
            for (var i = 0; i < r.message.pages_list.length; i++) {
              pages_html +=
                "<li><a onclick=change_page_route('" +
                r.message.pages_list[i].route +
                "')>" +
                r.message.pages_list[i].name +
                "</a></li>";
            }
            pages_html += "</ul></div>";
          }
        }
        frappe.Go1_CMS_Builder = new frappe.Go1CmsBuilder(
          wrapper,
          page_sections,
          page_title
        );
      },
    });
  }
};
frappe.Go1CmsBuilder = class Go1CmsBuilder {
  constructor(parent, page_sections, title) {
    this.parent = parent;
    this.page_sections = page_sections;
    this.title = title;
    // this.get_sections()
    this.make();
    this.refresh();
  }

  async get_sections() {}

  refresh() {
    $(document.body).on("change", "#sections", function (e) {
      //doStuff
      var optVal = $("#sections option:selected").val();
      // console.log(optVal);
    });
    this.render_layout();

    if (this.page_sections) {
      for (var i = 0; i < page_sections.length; i++) {
        this.render_existing_section(this.page_sections[i], i);
      }
    }
  }
  render_existing_section(page_section_obj, section_index) {
    if (
      page_section_obj.layout_json != undefined &&
      page_section_obj.layout_json != null
    ) {
      template_json.push(page_section_obj);

      if (page_section_obj.layout_type == "Speciality Section") {
        this.addTemplate(page_section_obj);
      } else {
        this.addrow_template(page_section_obj);
      }
      // this.addTemplate(page_section_obj);
      layout_json.push(page_section_obj.layout_json);
      this.page_section = page_section_obj.page_section;

      for (var i = 0; i < page_section_obj.layout_json.length; i++) {
        // console.log(page_section_obj.layout_json[i])
        // for (var j = 0; j < page_section_obj.layout_json[i].length; j++) {
        if (
          page_section_obj.layout_json[i].components &&
          page_section_obj.layout_json[i].components.length > 0
        ) {
          var section = $(
            "#" +
              page_section_obj.page_section +
              " #" +
              page_section_obj.layout_json[i].u_id
          );
          // $(section).find(".add_button").append(frappe.render_template("components",{cid:page_section_obj.layout_json[i].components[i].cid,ele_id:page_section_obj.layout_json[i].u_id,parent_idx:section_index,data:page_section_obj.layout_json[i].components[0].component_title,cmpt_id:page_section_obj.layout_json[i].u_id}));
          // this.renderComponent(page_section_obj.layout_json[i].components[0].component_title,page_section_obj.layout_json[i].u_id)
          for (
            var cp = 0;
            cp < page_section_obj.layout_json[i].components.length;
            cp++
          ) {
            $(section)
              .find(".add_button")
              .append(
                frappe.render_template("components", {
                  ele_id: page_section_obj.layout_json[i].u_id,
                  parent_idx: section_index,
                  data: page_section_obj.layout_json[i].components[cp]
                    .component_title,
                  cid: page_section_obj.layout_json[i].components[cp].cid,
                  cmpt_id: page_section_obj.layout_json[i].u_id,
                })
              );
          }
        } else {
          var cols = page_section_obj.layout_json[i].columns;
          if (cols != undefined) {
            for (var c = 0; c < cols.length; c++) {
              if (cols[c].components && cols[c].components.length > 0) {
                // this.renderComponent(cols[c].components[0].component_title,cols[c].u_id)
                var section = $(
                  "#" + page_section_obj.page_section + " #" + cols[c].u_id
                );
                // $(section).find(".add_button").append(frappe.render_template("components",{ele_id:cols[c].u_id,parent_idx:section_index,data:cols[c].components[0].component_title,cmpt_id:cols[c].u_id}));
                for (var cp = 0; cp < cols[c].components.length; cp++) {
                  $(section)
                    .find(".add_button")
                    .append(
                      frappe.render_template("components", {
                        ele_id: cols[c].u_id,
                        parent_idx: section_index,
                        data: cols[c].components[cp].component_title,
                        cid: cols[c].components[cp].cid,
                        cmpt_id: cols[c].u_id,
                      })
                    );
                }
              } else {
                if (cols[c].rows) {
                  var f_rows = cols[c].rows;
                  for (var r = 0; r < f_rows.length; r++) {
                    if (
                      f_rows[r].components &&
                      f_rows[r].components.length > 0
                    ) {
                      // this.renderComponent(f_rows[r].components[0].component_title,f_rows[r].u_id)
                      var section = $(
                        "#" +
                          page_section_obj.page_section +
                          " #" +
                          f_rows[r].u_id
                      );
                      // $(section).find(".add_button").append(frappe.render_template("components",{ele_id:f_rows[r].u_id,parent_idx:section_index,data:f_rows[r].components[0].component_title,cmpt_id:f_rows[r].u_id}));
                      for (var cp = 0; cp < f_rows[r].components.length; cp++) {
                        $(section)
                          .find(".add_button")
                          .append(
                            frappe.render_template("components", {
                              ele_id: f_rows[r].u_id,
                              parent_idx: section_index,
                              data: f_rows[r].components[cp].component_title,
                              cid: f_rows[r].components[cp].cid,
                              cmpt_id: f_rows[r].u_id,
                            })
                          );
                      }
                    }
                    var f_row_cols = f_rows[r].columns;
                    for (var rc = 0; rc < f_row_cols.length; rc++) {
                      if (
                        f_row_cols[rc].components &&
                        f_row_cols[rc].components.length > 0
                      ) {
                        // this.renderComponent(,$("#"+f_row_cols[rc].u_id))
                        var section = $(
                          "#" +
                            page_section_obj.page_section +
                            " #" +
                            f_row_cols[rc].u_id
                        );
                        for (
                          var cp = 0;
                          cp < f_row_cols[rc].components.length;
                          cp++
                        ) {
                          $(section)
                            .find(".add_button")
                            .append(
                              frappe.render_template("components", {
                                ele_id: f_row_cols[rc].u_id,
                                parent_idx: section_index,
                                data: f_row_cols[rc].components[cp]
                                  .component_title,
                                cid: f_row_cols[rc].components[cp].cid,
                                cmpt_id: f_row_cols[rc].u_id,
                              })
                            );
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        // }
      }
    } else {
      $(".print-format-builder-layout").append(
        frappe.render_template("predefined_section", {
          title: page_section_obj.section_title,
          page_section: page_section_obj.page_section,
        })
      );
    }
  }
  make() {
    this.page = frappe.ui.make_app_page({
      parent: this.parent,
      title: __(this.title),
    });
    this.page.main.css({ "border-color": "transparent" });
    $(".page-actions").append(
      '<a class="btn btn-primary preview-btn" onclick="preview_page()">Preview</a>'
    );
    $(".title-area")
      .find(".whitespace-nowrap")
      .addClass("fa fa-chevron-down")
      .attr("onclick", "change_page()")
      .attr("id", "page-link")
      .attr("style", "cursor:pointer;margin-top: 4px;");
    $(".title-area").append(pages_html);
    // console.log(this.page.main);
    // bind only once
    this.handle_drag();
    this.setup_section_settings();
    this.add_component();
    this.add_row();
    this.remove_component();
    this.delete_row();
    this.delete_section();
    this.edit_component_block();
    this.style_component_block();
    this.clone_component();
    this.clone_row();
    this.clone_section();
    $(this.page.sidebar).css({ position: "fixed" });
    this.layout_json = [];
  }
  // ADD Components function

  async get_components() {
    await frappe.call({
      method:
        "go1_cms.go1_cms.doctype.section_template_layout.section_template_layout.get_layout_section_template_data",
      args: {},
      freeze: true,
      callback: function (r) {
        // console.log(r)
      },
    });
  }
  add_component() {
    var me = this;
    this.page.main.on("click", ".add_component", function () {
      var section = $(this);
      //   me.get_components()
      // new dialog

      frappe.call({
        method:
          "go1_cms.go1_cms.doctype.section_component.section_component.get_component_details",
        args: {},
        freeze: true,
        callback: function (r) {
          // console.log(">> Components Response <<",r)
          new add_new_section({
            component_data: r,
            section: section,
            page_section: $(section)
              .parent()
              .closest("div.page_section")
              .attr("id"),
          });
        },
      });
    });
    this.page.main.on("click", ".edit_settings", function () {
      var section = $(this);
      me.edit_styles_columns(
        $(section).parent().closest("div.page_section").attr("id"),
        $(this).parent().closest("div.paceHolder_").attr("id")
      );
    });
  }
  renderComponent(component_name, col_id) {
    // console.log(col_id);
    // console.log(col_id.parent());
    $(col_id.parent()).append(
      frappe.render_template("components", { data: component_name, me: this })
    );
  }

  setup_section_settings() {
    var me = this;
    this.page.main.on("click", ".section-settings", function () {
      var section = $(this);
      me.edit_styles_sections(
        $(section).parent().closest("div.page_section").attr("id")
      );
    });
  }
  edit_styles_sections(page_section) {
    var id = page_section;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_page_section_properties",
      args: { section_name: page_section },
      async: false,
      callback: function (r) {
        if (r.message.styles) {
          var data = r.message.styles;
          var json_data = {};
          var fonts_data = [];
          // var fonts_data = [" ","Primary(Font Family)","Secondary(Font Family)","Text(Font Family)","Accent(Font Family)"]
          if (r.message.fonts_list) {
            for (var i = 0; i < r.message.fonts_list.length; i++) {
              fonts_data.push(r.message.fonts_list[i].name);
            }
          }
          if (
            r.message.css_json != null &&
            r.message.css_json != undefined &&
            r.message.css_json != ""
          ) {
            json_data = r.message.css_json;
          }
          var filelist = data;
          var fields = [];
          var child_sections = [];
          var units_sections = [];
          for (var i = 0; i < filelist.length; i++) {
            if (filelist[i].child_properties) {
              var child_properties = filelist[i].child_properties;
              var is_collapse = 0;
              if (filelist[i].collapse) {
                if (filelist[i].collapse == 1) {
                  is_collapse = 1;
                }
              }
              fields.push({
                fieldtype: "Section Break",
                fieldname: "sb_childs",
                label: filelist[i].label,
                collapsible: is_collapse,
              });
              for (var k = 0; k < child_properties.length; k++) {
                if (k == 0) {
                  child_sections.push(child_properties[k].fieldname);
                }
                for (const [key, value] of Object.entries(json_data)) {
                  if (key == child_properties[k].fieldname) {
                    child_properties[k].default = value;
                  }
                }
                if (child_properties[k].fieldname != "font-family") {
                  fields.push(child_properties[k]);
                } else {
                  fields.push({
                    fieldtype: "Select",
                    fieldname: child_properties[k].fieldname,
                    label: child_properties[k].label,
                    default: child_properties[k].default,
                    options: fonts_data,
                  });
                }
                if (k != child_properties.length - 1) {
                  // fields.push({ 'fieldtype': 'Column Break', 'fieldname': 'cb_childs'+k, 'label': '', 'collapsible': 0 })
                } else {
                  fields.push({
                    fieldtype: "Section Break",
                    fieldname: "sb_childs_next",
                    collapsible: 0,
                  });
                }
                if (child_properties[k].allow_units) {
                  if (child_properties[k].allow_units == 1) {
                    units_sections.push(child_properties[k].fieldname);
                  }
                }
              }
            } else {
              for (const [key, value] of Object.entries(json_data)) {
                if (key == filelist[i].fieldname) {
                  filelist[i].default = value;
                }
              }
              if (filelist[i].fieldname != "font-family") {
                fields.push(filelist[i]);
              } else {
                fields.push({
                  fieldtype: "Select",
                  fieldname: filelist[i].fieldname,
                  label: filelist[i].label,
                  default: filelist[i].default,
                  options: fonts_data,
                });
              }
              if (filelist[i].allow_units) {
                if (filelist[i].allow_units == 1) {
                  units_sections.push(filelist[i].fieldname);
                }
              }
            }
          }

          var styledialog = new frappe.ui.Dialog({
            title: "Edit Section Style",
            fields: fields,
          });
          styledialog.show();
          styledialog.$wrapper.find(".modal-dialog").attr("id", id);
          styledialog.set_primary_action(__("Save"), function () {
            let values = styledialog.get_values();
            let style_json = {};
            let is_full_width = 0;
            let css_design = "." + r.message.class_name + "{";
            for (let k in values) {
              if (values[k] != "" && values[k] != "0px" && values[k] != "0") {
                style_json[k] = values[k];
                if (k == "background-image") {
                  css_design += k + ":url('" + values[k] + "') !important;";
                } else if (k == "font-family") {
                  let font_famil_name = r.message.fonts_list.find(
                    (o) => o.name === values[k]
                  );
                  if (font_famil_name) {
                    css_design +=
                      k + ":" + font_famil_name.font_family + " !important;";
                  }
                } else if (k == "is_full_width") {
                  is_full_width = values[k];
                } else {
                  var is_allow_units = 0;
                  if (
                    styledialog.$wrapper
                      .find(".form-control[data-fieldname='" + k + "']")
                      .attr("allow-units")
                  ) {
                    if (
                      styledialog.$wrapper
                        .find(".form-control[data-fieldname='" + k + "']")
                        .attr("allow-units") == "1"
                    ) {
                      is_allow_units = 1;
                    }
                  }
                  var units = "";
                  if (is_allow_units == 1) {
                    units = styledialog.$wrapper
                      .find(".form-control[data-fieldname='" + k + "']")
                      .parent()
                      .find("select.unit")
                      .val();
                  }
                  css_design += k + ":" + values[k] + units + " !important;";
                }
              }
            }
            css_design += "}";
            $('[data-fieldname="' + id + '"]').attr("css_design", css_design);
            $('[data-fieldname="' + id + '"]').attr(
              "style_json",
              JSON.stringify(style_json)
            );
            frappe.call({
              method:
                "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_page_section_properties",
              args: {
                is_full_width: is_full_width,
                section_name: page_section,
                css_design: css_design,
                style_json: style_json,
              },
              async: false,
              callback: function (r) {
                styledialog.hide();
                setTimeout(function () {
                  $(".modal-dialog[id='" + id + "']")
                    .parent()
                    .remove();
                }, 1000);
              },
            });
          });
          styledialog.$wrapper
            .find(".modal-body")
            .attr(
              "style",
              "max-height:calc(100vh - 100px);min-height:calc(100vh - 100px);overflow-y: auto;overflow-x: hidden;"
            );
          styledialog.$wrapper.find(".modal-dialog").css("max-width", "700px");
          for (var i = 0; i < child_sections.length; i++) {
            styledialog.$wrapper
              .find(
                ".frappe-control[data-fieldname='" + child_sections[i] + "']"
              )
              .parent()
              .parent()
              .parent()
              .parent()
              .attr(
                "style",
                "margin-bottom:10px;border-top:none !important;margin-top: -20px;width: calc(100% + 40px);margin-left: -20px;padding-left: 20px;padding-right: 20px;margin-bottom: 0;position: relative;    min-height: 62px;"
              ); //modfied by boopathy
            styledialog.$wrapper
              .find(
                ".frappe-control[data-fieldname='" + child_sections[i] + "']"
              )
              .parent()
              .parent()
              .parent()
              .parent()
              .find(".section-head")
              .attr(
                "style",
                "font-weight: 600;margin-bottom: 20px;margin-top: 0;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;    min-height: 43px;"
              );
            styledialog.$wrapper
              .find(
                ".frappe-control[data-fieldname='" + child_sections[i] + "']"
              )
              .parent()
              .parent()
              .parent()
              .parent()
              .find(".section-body")
              .attr("style", "margin-top:60px");
            if (i == 0) {
              styledialog.$wrapper
                .find(
                  ".frappe-control[data-fieldname='" + child_sections[i] + "']"
                )
                .parent()
                .parent()
                .parent()
                .parent()
                .find(".section-head")
                .attr(
                  "style",
                  "font-weight: 600;margin-bottom: 20px;margin-top: 4px;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;    min-height: 43px;"
                );
            }
          }
          for (var i = 0; i < units_sections.length; i++) {
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .attr(
                "style",
                " box-shadow: none;flex: 0 0 60%;  border-top-right-radius: 0; border-bottom-right-radius: 0; border-right: 1px solid #ddd;"
              );
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .attr("type", "number");
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .attr("allow-units", "1");
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .parent()
              .attr(
                "style",
                "display: flex;position: relative;max-width: 140px;"
              );
            var select_html =
              '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
            select_html +=
              '<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 12px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .parent()
              .append(select_html);
          }
        }
      },
    });
  }
  edit_styles_columns(page_section, column) {
    var id = page_section;
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_column_properties",
      args: { section_name: page_section, column: column },
      async: false,
      callback: function (r) {
        if (r.message.styles) {
          var data = r.message.styles;
          var json_data = {};
          var fonts_data = [];
          // var fonts_data = [" ","Primary(Font Family)","Secondary(Font Family)","Text(Font Family)","Accent(Font Family)"]
          if (r.message.fonts_list) {
            for (var i = 0; i < r.message.fonts_list.length; i++) {
              fonts_data.push(r.message.fonts_list[i].name);
            }
          }
          if (
            r.message.css_json != null &&
            r.message.css_json != undefined &&
            r.message.css_json != ""
          ) {
            json_data = r.message.css_json;
          }
          var filelist = data;
          var fields = [];
          var child_sections = [];
          var units_sections = [];
          for (var i = 0; i < filelist.length; i++) {
            if (filelist[i].child_properties) {
              var child_properties = filelist[i].child_properties;
              var is_collapse = 0;
              if (filelist[i].collapse) {
                if (filelist[i].collapse == 1) {
                  is_collapse = 1;
                }
              }
              fields.push({
                fieldtype: "Section Break",
                fieldname: "sb_childs",
                label: filelist[i].label,
                collapsible: is_collapse,
              });
              for (var k = 0; k < child_properties.length; k++) {
                if (k == 0) {
                  child_sections.push(child_properties[k].fieldname);
                }
                for (const [key, value] of Object.entries(json_data)) {
                  if (key == child_properties[k].fieldname) {
                    child_properties[k].default = value;
                  }
                }
                if (child_properties[k].fieldname != "font-family") {
                  fields.push(child_properties[k]);
                } else {
                  fields.push({
                    fieldtype: "Select",
                    fieldname: child_properties[k].fieldname,
                    label: child_properties[k].label,
                    default: child_properties[k].default,
                    options: fonts_data,
                  });
                }
                if (k != child_properties.length - 1) {
                  // fields.push({ 'fieldtype': 'Column Break', 'fieldname': 'cb_childs'+k, 'label': '', 'collapsible': 0 })
                } else {
                  fields.push({
                    fieldtype: "Section Break",
                    fieldname: "sb_childs_next",
                    collapsible: 0,
                  });
                }
                if (child_properties[k].allow_units) {
                  if (child_properties[k].allow_units == 1) {
                    units_sections.push(child_properties[k].fieldname);
                  }
                }
              }
            } else {
              for (const [key, value] of Object.entries(json_data)) {
                if (key == filelist[i].fieldname) {
                  filelist[i].default = value;
                }
              }
              if (filelist[i].fieldname != "font-family") {
                fields.push(filelist[i]);
              } else {
                fields.push({
                  fieldtype: "Select",
                  fieldname: filelist[i].fieldname,
                  label: filelist[i].label,
                  default: filelist[i].default,
                  options: fonts_data,
                });
              }
              if (filelist[i].allow_units) {
                if (filelist[i].allow_units == 1) {
                  units_sections.push(filelist[i].fieldname);
                }
              }
            }
          }

          var styledialog = new frappe.ui.Dialog({
            title: "Edit Column Style",
            fields: fields,
          });
          styledialog.show();
          styledialog.$wrapper.find(".modal-dialog").attr("id", id);
          styledialog.set_primary_action(__("Save"), function () {
            let values = styledialog.get_values();
            let style_json = {};
            let is_full_width = 0;
            let css_design = "." + r.message.class_name + "{";
            for (let k in values) {
              if (
                values[k] != "" &&
                values[k] != "0px" &&
                values[k] != "0" &&
                k != "background_options"
              ) {
                style_json[k] = values[k];
                if (k == "background-image") {
                  css_design += k + ":url('" + values[k] + "') !important;";
                } else if (k == "font-family") {
                  let font_famil_name = r.message.fonts_list.find(
                    (o) => o.name === values[k]
                  );
                  if (font_famil_name) {
                    css_design +=
                      k + ":" + font_famil_name.font_family + " !important;";
                  }
                } else if (k == "is_full_width") {
                  is_full_width = values[k];
                } else {
                  var is_allow_units = 0;
                  if (
                    styledialog.$wrapper
                      .find(".form-control[data-fieldname='" + k + "']")
                      .attr("allow-units")
                  ) {
                    if (
                      styledialog.$wrapper
                        .find(".form-control[data-fieldname='" + k + "']")
                        .attr("allow-units") == "1"
                    ) {
                      is_allow_units = 1;
                    }
                  }
                  var units = "";
                  if (is_allow_units == 1) {
                    units = styledialog.$wrapper
                      .find(".form-control[data-fieldname='" + k + "']")
                      .parent()
                      .find("select.unit")
                      .val();
                  }
                  css_design += k + ":" + values[k] + units + " !important;";
                }
              }
            }
            css_design += "}";
            $('[data-fieldname="' + id + '"]').attr("css_design", css_design);
            $('[data-fieldname="' + id + '"]').attr(
              "style_json",
              JSON.stringify(style_json)
            );
            frappe.call({
              method:
                "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_page_section_column_properties",
              args: {
                is_full_width: is_full_width,
                column: column,
                section_name: page_section,
                css_design: css_design,
                style_json: style_json,
              },
              async: false,
              callback: function (r) {
                styledialog.hide();
                setTimeout(function () {
                  $(".modal-dialog[id='" + id + "']")
                    .parent()
                    .remove();
                }, 1000);
              },
            });
          });
          styledialog.$wrapper
            .find(".modal-body")
            .attr(
              "style",
              "max-height:calc(100vh - 100px);min-height:calc(100vh - 100px);overflow-y: auto;overflow-x: hidden;"
            );
          styledialog.$wrapper.find(".modal-dialog").css("max-width", "700px");
          for (var i = 0; i < child_sections.length; i++) {
            styledialog.$wrapper
              .find(
                ".frappe-control[data-fieldname='" + child_sections[i] + "']"
              )
              .parent()
              .parent()
              .parent()
              .parent()
              .attr(
                "style",
                "margin-bottom:10px;border-top:none !important;margin-top: -20px;width: calc(100% + 40px);margin-left: -20px;padding-left: 20px;padding-right: 20px;margin-bottom: 0;position: relative;    min-height: 62px;"
              ); //modfied by boopathy
            styledialog.$wrapper
              .find(
                ".frappe-control[data-fieldname='" + child_sections[i] + "']"
              )
              .parent()
              .parent()
              .parent()
              .parent()
              .find(".section-head")
              .attr(
                "style",
                "font-weight: 600;margin-bottom: 20px;margin-top: 0;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;    min-height: 43px;"
              );
            styledialog.$wrapper
              .find(
                ".frappe-control[data-fieldname='" + child_sections[i] + "']"
              )
              .parent()
              .parent()
              .parent()
              .parent()
              .find(".section-body")
              .attr("style", "margin-top:60px");
            if (i == 0) {
              styledialog.$wrapper
                .find(
                  ".frappe-control[data-fieldname='" + child_sections[i] + "']"
                )
                .parent()
                .parent()
                .parent()
                .parent()
                .find(".section-head")
                .attr(
                  "style",
                  "font-weight: 600;margin-bottom: 20px;margin-top: 4px;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;    min-height: 43px;"
                );
            }
          }
          for (var i = 0; i < units_sections.length; i++) {
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .attr(
                "style",
                " box-shadow: none;flex: 0 0 60%;  border-top-right-radius: 0; border-bottom-right-radius: 0; border-right: 1px solid #ddd;"
              );
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .attr("type", "number");
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .attr("allow-units", "1");
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .parent()
              .attr(
                "style",
                "display: flex;position: relative;max-width: 140px;"
              );
            var select_html =
              '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
            select_html +=
              '<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 12px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
            styledialog.$wrapper
              .find(".form-control[data-fieldname='" + units_sections[i] + "']")
              .parent()
              .append(select_html);
          }
        }
      },
    });
  }

  render_layout() {
    // console.log(this.page.main[0]);
    var main_page = this.page.main[0];

    $(
      frappe.render_template("builder_layout", {
        data: [],
        me: this,
      })
    ).appendTo(main_page);
    this.setup_add_section();
  }

  addTemplate(template) {
    // console.log("template",template);
    var me = this;
    $(
      frappe.render_template("templates", {
        section: template,
        me: me,
      })
    ).appendTo(me.page.main.find(".print-format-builder-layout"));
  }
  // add Template
  async setup_add_section() {
    var seleted_layout_id = "";
    var me = this;
    this.page.main
      .find(".print-format-builder-add-section")
      .on("click", function () {
        // boostrap new section info
        // new dialog
        section_type = "speciality_section";
        var length = template_json.length;
        var section_id = "id" + length;
        // console.log(section_id);
        frappe.call({
          method:
            "go1_cms.go1_cms.doctype.section_template_layout.section_template_layout.get_layout_data",
          args: {},
          freeze: true,
          callback: function (r) {
            // console.log(">> api response <<",r)
            if (r && r.message) {
              pop_up_layout_dialog(r.message);
            }
          },
        });

        function pop_up_layout_dialog(layout_data) {
          var r___id = Math.floor(Math.random() * 1000);
          let layout_dialog = new frappe.ui.Dialog({
            title: "Choose Section Layout",
            fields: [{ fieldname: "layout_html", fieldtype: "HTML" }],
          });
          let layout_dialog_wrapper =
            layout_dialog.fields_dict.layout_html.$wrapper;
          $(layout_dialog.$wrapper)
            .find(".modal-dialog")
            .css({ "min-width": "70%" });
          layout_dialog.show();
          layout_dialog.$wrapper.addClass("in");
          layout_dialog.set_primary_action("Save", () => {
            // console.log(">> values <<",layout_dialog.get_values())
            get_each_layout_data(seleted_layout_id);
            layout_dialog.hide();
          });
          let sp_add_html = "";
          let r_add_html = "";
          let st_add_html = "";
          if (
            layout_data &&
            layout_data.Speciality_Section &&
            layout_data.Speciality_Section.length > 0
          ) {
            layout_data.Speciality_Section.map((each_p) => {
              sp_add_html += `<div class="each-specality-div" style="flex:0 0 calc(33.33% - 20px);position:relative;">
				<label style="cursor:pointer;width:100%;" value="${each_p.unique_id}">
					<div style="width:80%;height:80px;margin:auto;
						background-image: url(${
              each_p.preview_image
                ? "'" + each_p.preview_image.replace(" ", "%20") + "'"
                : "/files/no-img.jpg"
            });
						border-radius: 3%;
						background-size:cover;
						background-repeat: no-repeat;
						background-position:top;
						border: 1px solid #e5e5e5;">
					</div>
					<div class="palette" style="width:100%;">
						<p style="margin: 0;font-size: 15px;font-weight: 500;
							margin-top: 10px;color: #222;white-space: nowrap;
							overflow: hidden;text-overflow: ellipsis;text-align:center">${each_p.title}
						</p>
					</div>
					<input type="radio"  value="${
            each_p.unique_id
          }" name="theme_radio" style="position:absolute;top:6px;right:30px;z-index:99;" ${
            each_p.unique_id == seleted_layout_id
          }?"checked":"">
				</label></div>`;
            });
          }

          if (
            layout_data &&
            layout_data.Regular_Section &&
            layout_data.Regular_Section.length > 0
          ) {
            layout_data.Regular_Section.map((each_p) => {
              r_add_html += `<div class="each-specality-div" style="flex:0 0 calc(33.33% - 20px);position:relative;">
				<label style="cursor:pointer;width:100%;" value="${each_p.unique_id}">
					<div style="width:80%;height:80px;margin:auto;
						background-image: url(${
              each_p.preview_image
                ? "'" + each_p.preview_image.replace(" ", "%20") + "'"
                : "/files/no-img.jpg"
            });
						border-radius: 3%;
						background-size:cover;
						background-repeat: no-repeat;
						background-position:top;
						border: 1px solid #e5e5e5;">
					</div>
					<div class="palette" style="width:100%;">
						<p style="margin: 0;font-size: 15px;font-weight: 500;
							margin-top: 10px;color: #222;white-space: nowrap;
							overflow: hidden;text-overflow: ellipsis;text-align:center">${each_p.title}
						</p>
					</div>
					<input type="radio"  value="${
            each_p.unique_id
          }" name="theme_radio" style="position:absolute;top:6px;right:30px;z-index:99;" ${
            each_p.unique_id == seleted_layout_id
          }?"checked":"">
				</label></div>`;
            });
          }

          if (
            layout_data &&
            layout_data.section_template &&
            layout_data.section_template.templates &&
            layout_data.section_template.templates.length > 0
          ) {
            layout_data.section_template.templates.map((each_p) => {
              st_add_html += `<div class="each-specality-div" style="max-width: calc(33.33% - 20px);flex:0 0 calc(33.33% - 20px);position:relative;">
			<label style="cursor:pointer;width:100%;" value="${each_p.name}">
				<div style="width:80%;height:80px;margin:auto;
					background-image: url(${
            each_p.image
              ? "'" + each_p.image.replace(" ", "%20") + "'"
              : "/files/no-img.jpg"
          });
					border-radius: 3%;
					background-size:cover;
					background-repeat: no-repeat;
					background-position:top;
					border: 1px solid #e5e5e5;">
				</div>
				<div class="palette" style="width:100%;">
					<p style="margin: 0;font-size: 15px;font-weight: 500;
						margin-top: 10px;color: #222;white-space: nowrap;
						overflow: hidden;text-overflow: ellipsis;text-align:center">${each_p.name}
					</p>
				</div>
				<input type="radio"  value="${
          each_p.name
        }" name="theme_radio" style="position:absolute;top:6px;right:30px;z-index:99;" ${
          each_p.unique_id == seleted_layout_id
        }?"checked":"">
			</label></div>`;
            });
          }

          let p_html = `<div class="full-container" id=${r___id}>
							<div class="tabs-container">
								<div class="tabs-sub-container">
									<div class="speciality-section-tab active" value="Speciality Section">Speciality Section</div>
									<div class="regular-section-tab" value="Regular Section">Regular Section</div>
									<div class="section-template-tab" value="Predefined Section">Predefined Section</div>
								</div>
							</div>
							<div class="specality-main-div " style="display: block;width: 75%;float: left;border-left: 1px solid var(--border-color);margin-top: -15px;padding-top: 15px;min-height: 420px;max-height: 420px;overflow-y: auto;margin-bottom: -10px;" id=sp_${r___id} >
							<div class="specality-sub-div" style="display:flex;flex-wrap:wrap;gap:20px;">
								${sp_add_html}
							</div>
						</div>
						<div class="regular-main-div" id=r_${r___id} style="display:none;width: 75%;float: left;border-left: 1px solid var(--border-color);margin-top: -15px;padding-top: 15px;min-height: 420px;max-height: 420px;overflow-y: auto;margin-bottom: -10px;">
							<div class="regular-sub-div" style="display:flex;flex-wrap:wrap;gap:20px;">
								${r_add_html}
							</div>
						</div>
						<div class="template-main-div" id=st_${r___id} style="display:none;width: 75%;float: left;border-left: 1px solid var(--border-color);margin-top: -15px;padding-top: 15px;min-height: 420px;max-height: 420px;overflow-y: auto;margin-bottom: -10px;">
							<div class="template-sub-div" style="display:flex;flex-wrap:wrap;gap:20px;">
								${st_add_html}
							</div>
						</div>
						</div>
						<style>
							.tabs-sub-container{
						float: left;
    display: block;
    width: calc(100% + 21px);
    margin-top: -15px;
    margin-left: -20px;
							}
							.tabs-container{
								width: 25%;
    float: left;
							}
							.section-template-tab,.regular-section-tab,.speciality-section-tab{
								cursor: pointer;border-bottom: 1px solid var(--border-color);
    font-size: 14px;
    float: left;
    width: 100%;
    padding: 10px 15px;
							}
							.regular-section-tab.active,.speciality-section-tab.active,.section-template-tab.active {
    background-color: var(--border-color);font-weight:600;
}
						</style>`;
          $(layout_dialog_wrapper).html(p_html);

          layout_dialog_wrapper
            .find(`#${r___id}`)
            .find("input")
            .on("click", (e) => {
              // console.log(">> selected layout id <<",$(e.target).val())
              seleted_layout_id = $(e.target).val();
            });

          layout_dialog_wrapper
            .find(`#${r___id}`)
            .find(".speciality-section-tab")
            .on("click", (e) => {
              // console.log(">> selected layout id <<",$(e.target).attr("value"))
              section_type = "speciality_section";
              // console.log(section_type);
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#st_${r___id}`)
                .hide();
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#r_${r___id}`)
                .hide();
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#sp_${r___id}`)
                .show();
              $(".regular-section-tab").removeClass("active");
              $(".section-template-tab").removeClass("active");
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(".speciality-section-tab")
                .addClass("active");
            });

          layout_dialog_wrapper
            .find(`#${r___id}`)
            .find(".regular-section-tab")
            .on("click", (e) => {
              // console.log(">> selected layout id <<",$(e.target).attr("value"))
              section_type = "regular_section";
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#st_${r___id}`)
                .hide();
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#sp_${r___id}`)
                .hide();
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#r_${r___id}`)
                .show();
              $(".speciality-section-tab").removeClass("active");
              $(".section-template-tab").removeClass("active");
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(".regular-section-tab")
                .addClass("active");
            });

          layout_dialog_wrapper
            .find(`#${r___id}`)
            .find(".section-template-tab")
            .on("click", (e) => {
              // console.log(">> selected layout id <<",$(e.target).attr("value"))
              section_type = "predefined_section";
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#r_${r___id}`)
                .hide();
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#sp_${r___id}`)
                .hide();
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(`#st_${r___id}`)
                .show();
              $(".speciality-section-tab").removeClass("active");
              $(".regular-section-tab").removeClass("active");
              layout_dialog_wrapper
                .find(`#${r___id}`)
                .find(".section-template-tab")
                .addClass("active");
            });
        }
      });

    function get_each_layout_data(layout_id) {
      // console.log(">> seleted layout id on save <<",layout_id)
      if (section_type == "predefined_section") {
        frappe.call({
          method:
            "go1_cms.go1_cms.doctype.section_template_layout.section_template_layout.save_predefined_section",
          args: { layout_id: layout_id, page_route: page_route },
          freeze: true,
          callback: function (r) {
            // console.log(">> api response <<",r)
            // console.log(section_type);
            if (r && r.message && r.message.length > 0) {
              $(".print-format-builder-layout").append(
                frappe.render_template("predefined_section", {
                  title: r.message[0].title,
                  page_section: r.message[0].page_section,
                })
              );
              me.page_section = r.message[0].page_section;
            }
          },
        });
      } else {
        frappe.call({
          method:
            "go1_cms.go1_cms.doctype.section_template_layout.section_template_layout.get_each_layout_data",
          args: { layout_id: layout_id, page_route: page_route },
          freeze: true,
          callback: function (r) {
            // console.log(">> api response <<",r)
            // console.log(section_type);
            if (r && r.message && r.message.length > 0) {
              template_json.push(r.message[0]);

              if (section_type == "speciality_section") {
                me.addTemplate(r.message[0]);
              } else {
                me.addrow_template(r.message[0]);
              }

              var obj = {};
              obj[layout_id] = r.message[0].layout_json;
              layout_json.push(r.message[0].layout_json);
              me.page_section = r.message[0].page_section;
            }
          },
        });
      }
    }
  }

  add_row() {
    var seleted_layout_id = "";
    var me = this;
    this.page.main.on("click", ".add_row_button", function () {
      // boostrap new section info
      // new dialog
      let elem = $(this);
      frappe.call({
        method:
          "go1_cms.go1_cms.doctype.section_template_layout.section_template_layout.get_layout_data",
        args: {},
        freeze: true,
        callback: function (r) {
          // console.log(">> api response <<",r)
          if (r && r.message && r.message.Regular_Section.length > 0) {
            // console.log("enter");
            pop_up_layout_dialog(r.message.Regular_Section);
          }
        },
      });

      function pop_up_layout_dialog(layout_data) {
        // console.log("////",layout_data);
        var r___id = Math.floor(Math.random() * 1000);
        let layout_dialog = new frappe.ui.Dialog({
          title: "Add New Section",
          fields: [{ fieldname: "layout_html", fieldtype: "HTML" }],
        });
        let layout_dialog_wrapper =
          layout_dialog.fields_dict.layout_html.$wrapper;
        $(layout_dialog.$wrapper)
          .find(".modal-dialog")
          .css({ "min-width": "70%" });
        layout_dialog.show();
        layout_dialog.$wrapper.addClass("in");
        layout_dialog.set_primary_action("Save", () => {
          // console.log(">> values <<",layout_dialog.get_values())
          get_each_layout_data(seleted_layout_id, elem);
          layout_dialog.hide();
        });
        let p_add_html = "";
        layout_data.map((each_p) => {
          p_add_html += `<div class="each-palette-div" style="flex:0 0 calc(33.33% - 20px);position:relative;">
				<label style="cursor:pointer;width:100%;" value="${each_p.unique_id}">
					<div style="width:80%;height:80px;margin:auto;
						background-image: url(${
              each_p.preview_image
                ? "'" + each_p.preview_image.replace(" ", "%20") + "'"
                : "/files/no-img.jpg"
            });
						border-radius: 3%;
						background-size:cover;
						background-repeat: no-repeat;
						background-position:top;
						border: 1px solid #e5e5e5;">
					</div>
					<div class="palette" style="width:100%;">
						<p style="margin: 0;font-size: 15px;font-weight: 500;
							margin-top: 10px;color: #222;white-space: nowrap;
							overflow: hidden;text-overflow: ellipsis;text-align:center">${each_p.title}
						</p>
					</div>
					<input type="radio"  value="${
            each_p.unique_id
          }" name="theme_radio" style="position:absolute;top:6px;right:30px;z-index:99;" ${
            each_p.unique_id == seleted_layout_id
          }?"checked":"">
				</label></div>`;
        });

        let p_html = `<div class="palette-main-div" id=${r___id}>
								<div class="palatte-sub-div" style="display:flex;flex-wrap:wrap;gap:20px;">
									${p_add_html}
								</div>
							</div>`;
        $(layout_dialog_wrapper).html(p_html);

        layout_dialog_wrapper
          .find(`#${r___id}`)
          .find("input")
          .on("click", (e) => {
            // console.log(">> selected layout id <<",$(e.target).val())
            seleted_layout_id = $(e.target).val();
          });
      }
    });

    function get_each_layout_data(layout_id, elem) {
      // console.log(">> seleted layout id on save <<",layout_id)
      frappe.call({
        method:
          "go1_cms.go1_cms.doctype.section_template_layout.section_template_layout.get_each_layout_data",
        args: { layout_id: layout_id, page_route: page_route },
        freeze: true,
        callback: function (r) {
          // console.log(">> api response <<",r)
          if (r && r.message && r.message.length > 0) {
            me.addrow_action(r.message[0], elem);
          }
        },
      });
    }
  }
  addrow_action(column, section) {
    // console.log(column,section)
    var parent = section.parent().parent();
    // console.log(parent,column);
    $(parent).append(
      frappe.render_template("regular", { data: column, type: "add", me: this })
    );
  }

  addrow_template(regular_json) {
    var row = $(".print-format-builder-layout");
    // console.log("row template", regular_json);

    $(".print-format-builder-layout").append(
      frappe.render_template("regular", {
        data: regular_json,
        type: "new",
        me: this,
      })
    );
  }

  // delete functions
  remove_component() {
    var me = this;
    this.page.main.on("click", ".remove_parent", function () {
      var section = $(this);
      var page_section = section.parent().closest(".page_section").attr("id");
      var uid = section.parent().parent().attr("data-id");
      var cid = section.parent().parent().attr("data-cid");
      frappe.confirm(
        "Are you sure you want to remove component?",
        () => {
          frappe.call({
            method:
              "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.remove_page_section_component",
            args: { page_section: page_section, uid: uid, cid: cid },
            freeze: true,
            callback: function (r) {
              if (r.message) {
                var page_layout_json = r.message.layout_json;
                var u_json = [];
                for (var i = 0; i < page_layout_json.length; i++) {
                  if (page_layout_json[i].u_id == uid) {
                    if (page_layout_json[i].components) {
                      for (
                        var cp = 0;
                        cp < page_layout_json[i].components.length;
                        cp++
                      ) {
                        if (page_layout_json[i].components[cp].cid == cid) {
                          page_layout_json[i].components.splice(cp, 1);
                        }
                      }
                    }
                    // page_layout_json[i].components = []
                  } else {
                    var cols = page_layout_json[i].columns;
                    if (cols != undefined) {
                      for (var c = 0; c < cols.length; c++) {
                        if (cols[c].u_id == uid) {
                          // cols[c].components = []
                          if (cols[c].components) {
                            for (
                              var cp = 0;
                              cp < cols[c].components.length;
                              cp++
                            ) {
                              if (cols[c].components[cp].cid == cid) {
                                cols[c].components.splice(cp, 1);
                              }
                            }
                          }
                        } else {
                          var f_rows = cols[c].rows;
                          for (var r = 0; r < f_rows.length; r++) {
                            if (f_rows[r].u_id == uid) {
                              // f_rows[r].components = []
                              if (f_rows[r].components) {
                                for (
                                  var cp = 0;
                                  cp < f_rows[r].components.length;
                                  cp++
                                ) {
                                  if (f_rows[r].components[cp].cid == cid) {
                                    f_rows[r].components.splice(cp, 1);
                                  }
                                }
                              }
                            }
                            var f_row_cols = f_rows[r].columns;
                            for (var rc = 0; rc < f_row_cols.length; rc++) {
                              if (f_row_cols[rc].u_id == uid) {
                                // f_row_cols[rc].components = []
                                if (f_row_cols[rc].components) {
                                  for (
                                    var cp = 0;
                                    cp < f_row_cols[rc].components.length;
                                    cp++
                                  ) {
                                    if (
                                      f_row_cols[rc].components[cp].cid == cid
                                    ) {
                                      f_row_cols[rc].components.splice(cp, 1);
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                  u_json.push(page_layout_json[i]);
                }

                frappe.call({
                  method:
                    "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_page_section_layout_json",
                  args: {
                    page_section: page_section,
                    layout_json: JSON.stringify(u_json),
                  },
                  freeze: true,
                  callback: function (r) {
                    $(section.parent().parent()).remove();
                  },
                });
              }
            },
          });
        },
        () => {}
      );
    });
  }
  delete_row() {
    var me = this;
    this.page.main.on("click", ".delete_row", function () {
      var section = $(this);
      // console.log(section.parent().parent().parent());
      $(section.parent().parent().parent().parent()).remove();
    });
  }
  delete_section() {
    var me = this;
    this.page.main.on("click", ".delete_section", function () {
      var section = $(this);
      var p_section = $(this).parent().closest("div.page_section").attr("id");
      frappe.confirm(
        "Are you sure you want to remove section?",
        () => {
          frappe.call({
            method:
              "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.remove_page_section",
            args: { page_section: p_section, page_route: page_route },
            freeze: true,
            callback: function (r) {
              $(section.parent().parent().parent()).remove();
            },
          });
        },
        () => {}
      );
    });
  }
  // dublicate element
  clone_component() {
    this.page.main.on("click", ".clone_component", function () {
      var section = $(this);
      // console.log(section.parent());
      $(section.parent().parent())
        .clone()
        .insertAfter(section.parent().parent());
    });
  }
  clone_row() {
    this.page.main.on("click", ".clone_row", function () {
      var section = $(this);
      // console.log(section.parent());
      $(section.parent().parent().parent().parent())
        .clone()
        .insertAfter(section.parent().parent().parent().parent());
    });
  }
  clone_section() {
    var me = this;
    this.page.main.on("click", ".clone_section", function () {
      var section = $(this);
      // console.log(section.parent().parent().parent());
      $(section.parent().parent().parent())
        .clone()
        .insertAfter(section.parent().parent().parent());
    });
  }
  handle_drag() {
    var me = this;
    this.page.main.find(".add_button").each(function () {
      me.setup_sortable_for_column(this);
    });
  }

  setup_sortable_for_column(col) {
    var me = this;
    Sortable.create(col, {
      group: {
        name: "field",
        put: true,
        pull: true,
      },
      onAdd: function (evt) {
        // on drop, change the HTML

        var $item = $(evt.item);
        if (!$item.hasClass("component_label")) {
          var html = frappe.render_template("components", {
            me: me,
          });

          $item.replaceWith(html);
        }
      },
    });
  }

  // edit component
  edit_component_block() {
    var me = this;
    this.page.main.on("click", ".edit_component_block", function () {
      // var d = new frappe.ui.Dialog({
      // 	title: "Edit Component",
      // 	fields: [
      // 		{
      // 			label: __("Cancel"),
      // 			fieldname: "remove_section",
      // 			fieldtype: "Button",
      // 			click: function () {
      // 				d.hide();
      // 			},
      // 			input_class: "btn-danger",
      // 			input_css: {
      // 				"margin-top": "20px",
      // 			},
      // 		},
      // 	],
      // 	primary_action_label: 'Submit',
      // 	primary_action() {
      // 		d.hide();
      // 	}
      // });
      // d.show();
      // d.$wrapper.addClass("in")
      // console.log($(this).parent().parent().html())
      new modify_section_data({
        page_section: $(this).parent().closest("div.page_section").attr("id"),
        section: me.section,
        comp_id: $(this).parent().parent().attr("data-ele-id"),
        cid: $(this).parent().parent().attr("data-cid"),
        parent_idx: $(this).parent().parent().attr("data-parent-idx"),
        content_type: "Data",
      });
    });
    this.page.main.on("click", ".edit_predifined_block", function () {
      new modify_section_data({
        page_section: $(this).parent().closest("div.page_section").attr("id"),
        section: me.section,
        comp_id: "",
        cid: 0,
        parent_idx: 0,
        content_type: "Data",
      });
    });
  }
  style_component_block() {
    var me = this;
    this.page.main.on("click", ".style_component_block", function () {
      frappe.call({
        method:
          "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_component_properties",
        args: {
          comp_ref: $(this).parent().parent().attr("data-id"),
          page_section: $(this)
            .parent()
            .parent()
            .closest("div.page_section")
            .attr("id"),
          cid: $(this).parent().parent().attr("data-cid"),
        },
        callback: function (r) {},
      });
    });
  }
};

var custom_title = "";
var add_new_section = Class.extend({
  init: function (opts) {
    this.component_data = opts.component_data;
    this.page_section = opts.page_section;
    this.section_type = "new";
    this.section = opts.section;
    this.make();
    // console.log(this.page_section)
  },
  make: function () {
    let me = this;
    me.groups = me.component_data.message.template_groups;
    me.templates = me.component_data.message.templates;
    frappe.run_serially([
      () => {
        if (me.templates) me.make_dialog();
        else {
          frappe.msgprint(
            "No sections are available. Please create a new section."
          );
        }
      },
    ]);
  },

  make_dialog: function () {
    let me = this;
    let title = "Pick a Component";
    this.dialog = new frappe.ui.Dialog({
      title: __(title),
      fields: [{ fieldname: "section_html", fieldtype: "HTML" }],
    });
    this.selected_section = [];
    this.dialog.show();
    this.section_html();
    this.dialog.$wrapper.find(".form-column.col-sm-12").css("padding", "0");
    this.dialog.$wrapper
      .find(".form-section")
      .attr(
        "style",
        "width: calc(100%);margin-left: 0px;padding-top: 0;margin-top: 0px;border-radius: 0;"
      );
    this.dialog.$wrapper
      .find('[data-fieldname="section_html"]')
      .attr("style", "margin-bottom: 0;");
    this.dialog.$wrapper.find(".modal-dialog").css("width", "90%");
    this.dialog.$wrapper.find(".modal-dialog").css("max-width", "1400px");
    this.dialog.$wrapper.find(".modal-content").css("height", "527px");
  },

  section_html: function () {
    let me = this;
    let wrapper = this.dialog.fields_dict.section_html.$wrapper.empty();
    let html = $(`<div class="row" id="SectionList"></div>
            <style>
                div[data-fieldname="section_html"] #SectionList .section-title{
                    padding: 35% 2%; text-align: center; height: 175px;
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
                        min-height: 175px;
                    margin-bottom: 10px; border: 1px solid #ddd; cursor:pointer;
                }
                div[data-fieldname="section_html"] #SectionList .section-item p{
                    text-align: center;
    min-height: 60px;
    background: #f3f3f3;
    padding-bottom: 10px;
    padding-top: 10px;
    margin-bottom: 0;
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
          "<div class='col-md-3' id='sec-left-content' style='background-color: #fff;    height: 462px;margin-left: -21px;position: absolute;left: 0;border-right: 1px solid #ddd;overflow-y: auto;overflow-x: hidden;margin-top: -15px;width: 25%;'></div>"
        );
      wrapper
        .find("#SectionList")
        .append(
          "<div class='col-md-9' id='sec-right-content' style='padding-top:20px;margin-left:25%;max-height: 445px;overflow-y: scroll;'></div>"
        );
      var group_html =
        "<span style='background: #f3f3f3;float: left;width: calc(100% + 32px);margin-left: -18px;padding: 10px 15px;font-size: 15px;font-weight: bold;border-bottom: 1px solid #ddd;'>Filter By Section Group</span>";
      group_html +=
        "<ul style='float: left;width: 100%;padding: 0;margin: 0;'><li style='list-style:none;float: left;width: calc(100% + 33px);border-bottom: 1px solid #ddd;margin-left: -18px;' class='active'><a class='group-link' id='dtgroupAll' style='float: left;width: 100%;text-decoration: none;padding: 10px 15px;' onclick=filter_section('All')>All</a></li>";
      for (var i = 0; i < me.groups.length; i++) {
        group_html +=
          '<li style="list-style:none;float: left;width: calc(100% + 33px);border-bottom: 1px solid #ddd;margin-left: -18px;"><a class="group-link" style="float: left;width: 100%;text-decoration: none;padding: 10px 15px;"';
        group_html +=
          'data-group="' +
          me.groups[i].group_name +
          '" id="dtgroup' +
          i +
          '" onclick=filter_section(' +
          i +
          ")>" +
          me.groups[i].group_name +
          ' <i class="fa fa-chevron-right" style="float: right;padding-top: 2px;font-size: 13px;color: #9e9e9e;font-weight: normal;font:normal normal normal 14px/1 FontAwesome"></i></a></li>';
      }
      group_html += "</ul>";
      wrapper.find("#SectionList").find("#sec-left-content").append(group_html);
    } else {
      wrapper
        .find("#SectionList")
        .append(
          "<div class='col-md-12' id='sec-right-content' style='padding-top:20px;max-height: 500px;overflow-y: scroll;'></div>"
        );
    }
    data.map((f) => {
      var bg_color = "style='background: #f3f3f3;'";
      let template = `<div class="section-title" data-group='${f.group_name}'>${f.name}</div>`;
      if (f.image) {
        template = `<div class="section-img" style="height:115px;"><img src="${f.image}" /></div><p style="display: flex;align-items: center;justify-content: center;">${f.name}</p>`;
        bg_color = "";
      }
      let item =
        $(`<div class="col-md-3 col-sm-6 col-xs-6" style="float:left;padding: 0 15px;" data-group='${f.group_name}'>
                    <div class="section-item" ${bg_color}>${template}</div>
                </div>`);
      wrapper.find("#SectionList").find("#sec-right-content").append(item);
      item.click(function () {
        var comp_id = $(me.section.parent().parent()).attr("id");
        // console.log(component_count);
        var cid = component_count + 1;
        component_count = component_count + 1;

        frappe.call({
          method:
            "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_component_page_section",
          args: {
            comp_id: comp_id,
            page_section: me.page_section,
            comp_uuid: f.unique_id,
            cid: cid,
          },
          callback: function (r) {
            me.dialog.hide();
            var comp_info = r.message.comp_info;
            var section_index = $(me.section)
              .parent()
              .closest("div.page_section")
              .index();
            $(me.section.parent()).append(
              frappe.render_template("components", {
                cid: cid,
                ele_id: comp_id,
                parent_idx: section_index,
                data: f.name,
                css_attrs: comp_info.css_field_list,
                cmpt_id: comp_info.name,
                me: this,
                templates: me.templates,
              })
            );
            var ps_layout_json = r.message.layout_json;
            var u_json = [];
            var ps_layout_json = r.message.layout_json;
            var eleid = comp_id;
            var comp_info = comp_info;
            var u_data = {};
            if (comp_info.content) {
              for (var i = 0; i < comp_info.content.length; i++) {
                if (comp_info.content[i].name != undefined) {
                  u_data[comp_info.content[i].field_key] =
                    comp_info.content[i].content;
                }
              }
            }
            for (var i = 0; i < ps_layout_json.length; i++) {
              if (ps_layout_json[i].u_id == eleid) {
                if (ps_layout_json[i].components != undefined) {
                  var is_exist = 0;
                  for (
                    var p = 0;
                    p < ps_layout_json[i].components.length;
                    p++
                  ) {
                    if (ps_layout_json[i].components.cid == me.cid) {
                      is_exist = 1;
                      ps_layout_json[i].components[p].data = u_data;
                      ps_layout_json[i].components[p].component_type =
                        comp_info.component_type;
                      ps_layout_json[i].components[p].component_title =
                        comp_info.title;
                    }
                  }
                  if (is_exist == 0) {
                    var cm_list = ps_layout_json[i].components;

                    cm_list.push({
                      cid: cid,
                      data: u_data,
                      component_type: comp_info.component_type,
                      component_title: comp_info.title,
                    });
                    ps_layout_json[i]["components"] = cm_list;
                  }
                } else {
                  var cm_list = [];
                  cm_list.push({
                    cid: cid,
                    data: u_data,
                    component_type: comp_info.component_type,
                    component_title: comp_info.title,
                  });
                  ps_layout_json[i]["components"] = cm_list;
                }
              } else {
                var cols = ps_layout_json[i].columns;
                if (cols != undefined) {
                  for (var c = 0; c < cols.length; c++) {
                    if (cols[c].u_id == eleid) {
                      if (cols[c].components != undefined) {
                        var is_exist = 0;
                        for (var p = 0; p < cols[c].components.length; p++) {
                          if (cols[c].components.cid == cid) {
                            is_exist = 1;
                            cols[c].components[p].data = u_data;
                            cols[c].components[p].component_type =
                              comp_info.component_type;
                            cols[c].components[p].component_title =
                              comp_info.title;
                          }
                        }
                        if (is_exist == 0) {
                          var cm_list = cols[c].components;
                          // console.log(cm_list);
                          cm_list.push({
                            cid: cid,
                            data: u_data,
                            component_type: comp_info.component_type,
                            component_title: comp_info.title,
                          });
                          cols[c]["components"] = cm_list;
                        }
                      } else {
                        var cm_list = [];
                        cm_list.push({
                          cid: cid,
                          data: u_data,
                          component_type: comp_info.component_type,
                          component_title: comp_info.title,
                        });
                        cols[c]["components"] = cm_list;
                      }
                    } else {
                      if (cols[c].rows) {
                        var f_rows = cols[c].rows;
                        for (var r = 0; r < f_rows.length; r++) {
                          if (f_rows[r].u_id == eleid) {
                            if (f_rows[r].components != undefined) {
                              var is_exist = 0;
                              for (
                                var p = 0;
                                p < f_rows[r].components.length;
                                p++
                              ) {
                                if (f_rows[r].components.cid == cid) {
                                  is_exist = 1;
                                  f_rows[r].components[p].data = u_data;
                                  f_rows[r].components[p].component_type =
                                    comp_info.component_type;
                                  f_rows[r].components[p].component_title =
                                    comp_info.title;
                                }
                              }
                              if (is_exist == 0) {
                                var cm_list = f_rows[r].components;
                                // console.log(cm_list);
                                cm_list.push({
                                  cid: cid,
                                  data: u_data,
                                  component_type: comp_info.component_type,
                                  component_title: comp_info.title,
                                });
                                f_rows[r]["components"] = cm_list;
                              }
                            } else {
                              var cm_list = [];
                              cm_list.push({
                                cid: cid,
                                data: u_data,
                                component_type: r.message.component_type,
                                component_title: comp_info.title,
                              });
                              f_rows[r]["components"] = cm_list;
                            }
                          }
                          var f_row_cols = f_rows[r].columns;
                          for (var rc = 0; rc < f_row_cols.length; rc++) {
                            if (f_row_cols[rc].u_id == eleid) {
                              if (f_row_cols[rc].components != undefined) {
                                var is_exist = 0;
                                for (
                                  var p = 0;
                                  p < f_row_cols[rc].components.length;
                                  p++
                                ) {
                                  if (f_row_cols[rc].components[p].cid == cid) {
                                    is_exist = 1;
                                    f_row_cols[rc].components[p].data = u_data;
                                    f_row_cols[rc].components[
                                      p
                                    ].component_type = comp_info.component_type;
                                    f_row_cols[rc].components[
                                      p
                                    ].component_title = comp_info.title;
                                  }
                                }
                                if (is_exist == 0) {
                                  var cm_list = f_row_cols[rc].components;
                                  // console.log(cm_list);
                                  cm_list.push({
                                    cid: cid,
                                    data: u_data,
                                    component_type: comp_info.component_type,
                                    component_title: comp_info.title,
                                  });
                                  f_row_cols[rc]["components"] = cm_list;
                                }
                              } else {
                                var cm_list = [];
                                cm_list.push({
                                  cid: cid,
                                  data: u_data,
                                  component_type: comp_info.component_type,
                                  component_title: comp_info.title,
                                });
                                f_row_cols[rc]["components"] = cm_list;
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }

              u_json.push(ps_layout_json[i]);
            }
            frappe.call({
              method:
                "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_page_section_layout_json",
              args: {
                page_section: me.page_section,
                layout_json: JSON.stringify(u_json),
              },
              freeze: true,
              callback: function (r) {
                me.dialog.hide();
              },
            });
          },
        });
      });
    });
  },
});

// Edit Section Data
let reference_name_val;
let no_of_records_val;
let is_dynamic_data_val;
var modify_section_data = Class.extend({
  init: function (opts) {
    this.section = opts.section;
    this.page_section = opts.page_section;
    this.parent_idx = opts.parent_idx;
    this.cid = opts.cid;
    this.comp_id = opts.comp_id;
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
    // console.log(me.section,"me----")
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_page_component_content",
      args: {
        section: me.page_section,
        comp_id: me.comp_id,
        cid: me.cid,
        content_type: me.content_type,
      },
      async: false,
      callback: function (r) {
        if (r.message) {
          me.fields = r.message;
          var fonts_data = [];
          if (me.fields.fonts_list) {
            for (var i = 0; i < me.fields.fonts_list.length; i++) {
              fonts_data.push(me.fields.fonts_list[i].name);
            }
          }
          me.fields.fonts_data = fonts_data;
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
        // console.log("----------sec--------")
        // console.log(r.message)
        if (r.message) {
          let value;
          if (r.message.section_name) title = r.message.section_name;
          else if (r.message.section_title) title = r.message.section_title;
        }
      },
    });
    let fields = [];
    // console.log(this.content_type)
    if (this.content_type == "Data") fields = this.get_fields_list();
    else fields = [{ fieldname: "pattern_html", fieldtype: "HTML" }];
    if (this.content_type == "Data" && fields.length == 0)
      frappe.throw("There is no editable part available for this section.");
    this.dialog = new frappe.ui.Dialog({
      title: __("Edit Content"),
      fields: fields,
    });

    this.dialog.set_primary_action(__("Save"), function () {
      if (me.content_type == "Data") me.save_data();
      else me.update_design();
    });
    // let css_html = this.dialog.fields_dict.css_setting_html.$wrapper.empty();
    // $(`<p>hi</p>`).appendTo(css_html)

    this.dialog.show();
    // this.dialog.$wrapper.find('input[data-fieldtype="Data"],input[data-fieldtype="Link"],input[data-fieldtype="Select"],input[data-fieldtype="Int"]').css("max-width", "330px");
    this.dialog.$wrapper.find(".modal-dialog").css("width", "1000px");
    this.dialog.$wrapper.find(".modal-dialog").css("max-width", "750px");
    this.dialog.$wrapper.find(".ace-tomorrow").css("max-height", "200px");

    this.dialog.$wrapper
      .find(".modal-body")
      .attr(
        "style",
        "max-height:calc(100vh - 100px);overflow-y: auto;overflow-x: hidden;"
      );

    for (var value of this.fields.content) {
      if (value["allow_update_to_style"] == 1) {
        // console.log(value)
        // console.log(this.dialog.$wrapper.find('[data-fieldname="'+value.name+'"]').find(".control-label").text())
        // if(value['css_properties_list'].length>0){
        var label = value.field_label;
        if (
          value.image_dimension != "" &&
          value.image_dimension != undefined &&
          value.image_dimension != null
        ) {
          label = value.field_label + " (" + value.image_dimension + ")";
        }
        this.dialog.$wrapper
          .find('[data-fieldname="' + value.name + '"]')
          .find(".control-label")
          .html(
            label +
              "<a style='margin-left: 10px;background: #fff;padding: 2px 7px;text-transform: capitalize;color: #308fdb;font-size: 12px;border: 1px solid #308fdb;border-radius: 3px;font-weight: 600;' onclick=show_element_style('" +
              value.name +
              "')><i class='fa fa-cog' style='margin-right:5px'></i>Edit Styles</a>"
          );
        if (value.field_type == "Border") {
          // this.dialog.$wrapper.find('.frappe-control[data-fieldname="'+value.name+'"]').attr("style","margin-bottom:-15px");
          this.dialog.$wrapper
            .find('[data-fieldname="' + value.name + '"]')
            .find(".control-input")
            .attr("style", "display:none");
          // this.dialog.$wrapper.find('[data-fieldname="'+value.name+'"]').find(".control-label").attr("style"," padding-right: 0px;font-weight: bold;color: #666666 !important;text-transform: uppercase;");
        }
      }
    }

    if (this.content_type != "Design") {
      this.check_image_field();
      this.check_fieldtype_lists();
      this.check_fieldtype_button();
    }
    if (this.fields && this.fields.section_type == "Custom Section") {
      // console.log(this.fields)
      if (this.fields.reference_document != "Blog Category") {
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
      } else {
        me.dialog.fields_dict.reference_name.$wrapper.removeClass(
          "hide-control"
        );
      }
      if (this.fields.reference_document == "Product Category") {
        this.get_category_products("data");
      }
      if (this.fields.reference_document == "Blog Category") {
        this.get_blog_category("data");
      }
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
        } else if (me.fields.reference_document == "Blog Category") {
          field_name = "title";
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
        } else if (me.fields.reference_document == "Blog Category") {
          field_name = "title";
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
  get_blog_category: function (type) {
    let me = this;
    if (type == "shuffle") {
      if (is_dynamic_data_val == 0 && reference_name_val != "") {
        frappe.call({
          method:
            "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_shuffled_blog_category",
          args: {
            category: reference_name_val,
            no_of_records: no_of_records_val,
          },
          async: false,
          callback: function (r) {
            // console.log(r)
            me.dialog.$wrapper
              .find('[data-fieldname="blog_category_html"]')
              .html("");
            if (r.message) {
              let p_html =
                me.dialog.fields_dict.blog_category_html.$wrapper.empty();

              let btns = $(`<div>
                                         <button class="btn btn-primary">${__(
                                           "Shuffle Data"
                                         )}</button>
                                    </div>`).appendTo(p_html);
              btns.find(".btn-primary").click(function () {
                me.get_blog_category("shuffle");
              });

              var t_html = $(
                `<table class="table table-bordered"><thead><tr><th style="width:65px"></th><th style="width:200px">ID</th><th>Category Name</th></tr></thead><tbody></tbody></table>`
              );
              for (var i = 0; i < r.message.length; i++) {
                var row = "";
                var image_html = "";
                if (
                  r.message[i].thumbnail_image != null &&
                  r.message[i].thumbnail_image != undefined
                ) {
                  image_html =
                    "<img src='" +
                    r.message[i].thumbnail_image +
                    "' style='height: 50px;margin-right: 10px;'/>";
                }
                row =
                  "<tr><td><img src='/assets/go1_cms/images/section-icon.svg' style='height:30px;cursor: all-scroll;position: relative;top: 0;margin-right: 10px;text-align: center;left: 10px;'></td><td style='width:200px'>" +
                  r.message[i].name +
                  "</td><td>" +
                  image_html +
                  r.message[i].title +
                  "</td></tr>";
                t_html.append(row);
              }
              t_html.appendTo(p_html);
              // console.log(me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').parent().parent().parent().parent())
              me.dialog.$wrapper
                .find('[data-fieldname="blog_category_html"]')
                .parent()
                .parent()
                .parent()
                .parent()
                .show();
              // me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').html(p_html);
              me.categoryblogs = r.message;
            }
          },
        });
      } else {
        me.dialog.$wrapper
          .find('[data-fieldname="blog_category_html"]')
          .html("");
        me.dialog.$wrapper
          .find('[data-fieldname="blog_category_html"]')
          .parent()
          .parent()
          .parent()
          .parent()
          .hide();
        me.category_products = "";
      }
    } else {
      setTimeout(function () {
        let p_html = me.dialog.fields_dict.blog_category_html.$wrapper.empty();
        let btns = $(`<div>
                     <button class="btn btn-primary">${__(
                       "Shuffle Data"
                     )}</button>
                </div>`).appendTo(p_html);
        btns.find(".btn-primary").click(function () {
          me.get_blog_category("shuffle");
        });

        var t_html = $(
          `<table class="table table-bordered"><thead><tr><th style="width:65px"></th><th style="width:200px">ID</th><th>Category Name</th></tr></thead><tbody></tbody></table>`
        );
        var json_data = JSON.parse(me.fields.custom_section_data);
        for (var i = 0; i < json_data.length; i++) {
          var row = "";
          var image_html = "";
          if (
            json_data[i].thumbnail_image != null &&
            json_data[i].thumbnail_image != undefined
          ) {
            image_html =
              "<img src='" +
              json_data[i].thumbnail_image +
              "' style='height: 50px;margin-right: 10px;'/>";
          }
          row =
            "<tr><td><img src='/assets/go1_cms/images/section-icon.svg' style='height:30px;cursor: all-scroll;position: relative;top: 0;margin-right: 10px;text-align: center;left: 10px;'></td><td style='width:200px'>" +
            json_data[i].name +
            "</td><td>" +
            image_html +
            json_data[i].title +
            "</td></tr>";
          t_html.append(row);
        }
        t_html.appendTo(p_html);
        me.dialog.$wrapper
          .find('[data-fieldname="blog_category_html"]')
          .parent()
          .parent()
          .parent()
          .parent()
          .show();
        // me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').html(p_html);
        me.category_products = json_data;
      }, 1000);
    }
    setTimeout(function () {
      me.dialog.$wrapper
        .find('[data-fieldname="blog_category_html"]')
        .find("tbody")
        .sortable({
          items: "tr",
          opacity: 0.7,
          distance: 20,
          update: function (e, ui) {},
        });
    }, 1000);
  },
  get_category_products: function (type) {
    let me = this;
    if (type == "shuffle") {
      if (is_dynamic_data_val == 0 && reference_name_val != "") {
        frappe.call({
          method:
            "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_shuffled_category_products",
          args: {
            category: reference_name_val,
            no_of_records: no_of_records_val,
          },
          async: false,
          callback: function (r) {
            me.dialog.$wrapper
              .find('[data-fieldname="category_products_html"]')
              .html("");
            if (r.message) {
              let p_html =
                me.dialog.fields_dict.category_products_html.$wrapper.empty();

              let btns = $(`<div>
                                         <button class="btn btn-primary">${__(
                                           "Shuffle Data"
                                         )}</button>
                                    </div>`).appendTo(p_html);
              btns.find(".btn-primary").click(function () {
                me.get_category_products("shuffle");
              });

              var t_html = $(
                `<table class="table table-bordered"><thead><tr><th style="width:65px"></th><th style="width:200px">ID</th><th>Item Name</th></tr></thead><tbody></tbody></table>`
              );
              for (var i = 0; i < r.message.length; i++) {
                var row = "";
                var image_html = "";
                if (
                  r.message[i].product_image != null &&
                  r.message[i].product_image != undefined
                ) {
                  image_html =
                    "<img src='" +
                    r.message[i].product_image +
                    "' style='height: 50px;margin-right: 10px;'/>";
                }
                row =
                  "<tr><td><img src='/assets/go1_cms/images/section-icon.svg' style='height:30px;cursor: all-scroll;position: relative;top: 0;margin-right: 10px;text-align: center;left: 10px;'></td><td style='width:200px'>" +
                  r.message[i].name +
                  "</td><td>" +
                  image_html +
                  r.message[i].item +
                  "</td></tr>";
                t_html.append(row);
              }
              t_html.appendTo(p_html);
              me.dialog.$wrapper
                .find('[data-fieldname="category_products_html"]')
                .parent()
                .parent()
                .parent()
                .parent()
                .show();
              // me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').html(p_html);
              me.category_products = r.message;
            }
          },
        });
      } else {
        me.dialog.$wrapper
          .find('[data-fieldname="category_products_html"]')
          .html("");
        me.dialog.$wrapper
          .find('[data-fieldname="category_products_html"]')
          .parent()
          .parent()
          .parent()
          .parent()
          .hide();
        me.category_products = "";
      }
    } else {
      setTimeout(function () {
        let p_html =
          me.dialog.fields_dict.category_products_html.$wrapper.empty();
        let btns = $(`<div>
                     <button class="btn btn-primary">${__(
                       "Shuffle Data"
                     )}</button>
                </div>`).appendTo(p_html);
        btns.find(".btn-primary").click(function () {
          me.get_category_products("shuffle");
        });

        var t_html = $(
          `<table class="table table-bordered"><thead><tr><th style="width:65px"></th><th style="width:200px">ID</th><th>Item Name</th></tr></thead><tbody></tbody></table>`
        );
        var json_data = JSON.parse(me.fields.custom_section_data);
        for (var i = 0; i < json_data.length; i++) {
          var row = "";
          var image_html = "";
          if (
            json_data[i].product_image != null &&
            json_data[i].product_image != undefined
          ) {
            image_html =
              "<img src='" +
              json_data[i].product_image +
              "' style='height: 50px;margin-right: 10px;'/>";
          }
          row =
            "<tr><td><img src='/assets/go1_cms/images/section-icon.svg' style='height:30px;cursor: all-scroll;position: relative;top: 0;margin-right: 10px;text-align: center;left: 10px;'></td><td style='width:200px'>" +
            json_data[i].name +
            "</td><td>" +
            image_html +
            json_data[i].item +
            "</td></tr>";
          t_html.append(row);
        }
        t_html.appendTo(p_html);
        me.dialog.$wrapper
          .find('[data-fieldname="category_products_html"]')
          .parent()
          .parent()
          .parent()
          .parent()
          .show();
        // me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').html(p_html);
        me.category_products = json_data;
      }, 1000);
    }
    setTimeout(function () {
      me.dialog.$wrapper
        .find('[data-fieldname="category_products_html"]')
        .find("tbody")
        .sortable({
          items: "tr",
          opacity: 0.7,
          distance: 20,
          update: function (e, ui) {},
        });
    }, 1000);
  },
  get_fields_list: function () {
    let me = this;
    let field_list = [];
    if (this.content_type == "Design") {
      field_list.push({});
    }

    if (this.fields.section_type == "Predefined Section")
      field_list.push({
        fieldtype: "Section Break",
        fieldname: "sb_design1",
        label: "Design",
        collapsible: 0,
      });
    // me.dialog.fields_dict.section_type.set_value("Static Links")
    // console.log("============this.fields.reference_document=========")
    // console.log(this.fields.reference_document)
    if (
      this.fields.section_type == "Custom Section" &&
      this.fields.reference_document == "Blog Category"
    ) {
      reference_name_val = this.fields.reference_name;
      no_of_records_val = this.fields.no_of_records;
      is_dynamic_data_val = this.fields.dynamic_data;

      field_list.push({
        fieldname: "reference_name",
        fieldtype: "Link",
        label: __(this.fields.reference_document),
        options: this.fields.reference_document,
        reqd: 1,
        default: this.fields.reference_name || "",
        onchange: function () {
          reference_name_val = this.get_value();
          if (reference_name_val) {
            me.get_blog_category("shuffle");
          }
        },
      });
      field_list.push({
        fieldname: "dynamic_data",
        fieldtype: "Check",
        label: __("Fecth Data Dynamically"),
        default: this.fields.dynamic_data || 0,
        depends_on: "eval: doc.fetch_product == 1",
        onchange: function () {
          let val = this.get_value();
          is_dynamic_data_val = val;
          me.get_category_products("shuffle");
        },
      });
      field_list.push({
        fieldname: "display_randomly",
        fieldtype: "Check",
        label: __("Display Data Randomly"),
        default: this.fields.display_randomly || 0,
        depends_on: "eval: doc.dynamic_data == 1",
      });
      field_list.push({
        fieldname: "fetch_product",
        fieldtype: "Check",
        default: 1,
        label: __("Get Data From Blogs"),
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

      field_list.push({
        fieldtype: "Section Break",
        fieldname: "sec_category_blogs",
        depends_on: "eval: doc.reference_name!='' ",
      });
      field_list.push({
        fieldname: "blog_category_html",
        fieldtype: "HTML",
        // "depends_on": "eval: {{doc.dynamic_data == 0}}",
      });
      if (this.fields.content.length > 0) {
        field_list.push({ fieldtype: "Section Break", fieldname: "sec_b0" });
      }
    }

    if (
      this.fields.section_type == "Custom Section" &&
      this.fields.reference_document != "Blog Category"
    ) {
      reference_name_val = this.fields.reference_name;
      no_of_records_val = this.fields.no_of_records;
      is_dynamic_data_val = this.fields.dynamic_data;

      // field_list.push({
      //     "fieldname": "fetch_product",
      //     "fieldtype": "Check",
      //     "default": (this.fields.fetch_product),
      //     "label": __("Get Data From Products")
      // })
      // field_list.push({
      //     "fieldname": "reference_name",
      //     "fieldtype": "Link",
      //     "label": __(this.fields.reference_document),
      //     "options": this.fields.reference_document,
      //     "reqd": 1,
      //     "default": (this.fields.reference_name || ""),
      //     "depends_on": "eval: doc.fetch_product == 1",
      //     onchange:function(){
      //         reference_name_val = this.get_value();
      //         me.get_category_products('shuffle');
      //     }
      // });
      // field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'col_br' })
      field_list.push({
        fieldname: "no_of_records",
        fieldtype: "Int",
        label: __("No. Of Records"),
        options: this.fields.no_of_records,
        reqd: 1,
        default: this.fields.no_of_records || "",
      });
      field_list.push({
        fieldname: "dynamic_data",
        fieldtype: "Check",
        label: __("Fecth Data Dynamically"),
        default: this.fields.dynamic_data || 0,

        onchange: function () {
          let val = this.get_value();
          is_dynamic_data_val = val;
          me.get_category_products("shuffle");
        },
      });
      // field_list.push({
      //     "fieldname": "display_randomly",
      //     "fieldtype": "Check",
      //     "label": __("Display Data Randomly"),
      //     "default": (this.fields.display_randomly || 0),
      //     "depends_on": "eval: doc.dynamic_data == 1",
      // });
      field_list.push({
        fieldtype: "Section Break",
        fieldname: "sec_category_products",
        depends_on: "eval: doc.fetch_product == 1",
      });
      field_list.push({
        fieldname: "category_products_html",
        fieldtype: "HTML",
        // "depends_on": "eval: {{doc.dynamic_data == 0}}",
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
        // field_list.push({ 'fieldtype': 'HTML', 'fieldname': 'css_setting_html','label': 'CSS Setting HTML'})
      }

      $(fields).each(function (k, v) {
        // console.log(k,v,"kv")
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
        } else if (v.field_type == "Button") {
          field.fieldtype = "Button";
        } else if (v.field_type == "Border") {
          field.fieldtype = "Data";
          field.label = __(v.field_label);
          field.default = 1;
        } else {
          field.fieldtype = "HTML Editor";
        }

        if (v.content && v.content != "") field.default = v.content;

        if (v.image_dimension != "" && v.image_dimension != undefined) {
          field.label = __(v.field_label) + "(" + v.image_dimension + ")";
        } else {
          field.label = __(v.field_label);
        }
        field_list.push(field);
        //   if(v.field_type == 'Button') {
        //      field_list.push({ 'fieldtype': 'Data', 'fieldname': 'btn_text','label':"Button Text" })
        //      field_list.push({ 'fieldtype': 'Data', 'fieldname': 'btn_redirect_url','label':"Button Link" })
        //      field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'btn_clbr1' })
        //      field_list.push({ 'fieldtype': 'Data', 'fieldname': 'btn_bg_color','label':"Button Background Color" })
        //      field_list.push({ 'fieldtype': 'Data', 'fieldname': 'btn_color','label':"Button Text Color" })
        // }
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
      //     method: 'go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_featured_products',
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
            return {
              filters: {
                is_active: 1,
              },
            };
          } else if (me.fields.reference_document == "Product Brand") {
            filtercond = "published";
            return {
              filters: {
                published: 1,
              },
            };
          } else if (me.fields.reference_document == "Product") {
            filtercond = "is_active";
            return {
              filters: {
                is_active: 1,
              },
            };
          }
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
    // console.log(field_list)
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
    let style_json = {};
    let css_design = "";

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
      if (v.fieldtype == "Button") {
        var section_obj = {};
        var code_json = {};
        $('[data-key="' + v.fieldname + '"]').each(function () {
          code_json[$(this).attr("data-fieldname")] = $(this).val();
        });
        section_obj = {
          name: v.fieldname,
          content: JSON.stringify(code_json),
          doctype: "Section Content",
          parent: me.section,
        };
        if (
          $('[data-fieldname="' + v.fieldname + '"]').attr("css_design") !=
            undefined &&
          $('[data-fieldname="' + v.fieldname + '"]').attr("css_design") != ""
        ) {
          section_obj = {
            name: v.fieldname,
            doctype: "Section Content",
            parent: me.section,
          };
          section_obj["css_text"] = $(
            '[data-fieldname="' + v.fieldname + '"]'
          ).attr("css_design");
        }
        if (
          $('[data-fieldname="' + v.fieldname + '"]').attr("style_json") !=
            undefined &&
          $('[data-fieldname="' + v.fieldname + '"]').attr("style_json") != ""
        ) {
          section_obj["css_json"] = $(
            '[data-fieldname="' + v.fieldname + '"]'
          ).attr("style_json");
        }
        results.push(section_obj);
      } else if (v.fieldtype != "Section Break") {
        var section_obj = {};
        if (jQuery.inArray(v.fieldname, dialog_fields) === -1) {
          if (
            me.fields.section_type != "Lists" &&
            me.fields.section_type != "Tabs"
          )
            section_obj = {
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            };
          else if (
            me.fields.section_type == "Lists" &&
            !has_common(
              [k],
              ["item", "item_title", "is_edit", "image_type", "image_ref_doc"]
            )
          )
            section_obj = {
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            };
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
            section_obj = {
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            };
          } else if (
            me.fields.section_type == "Predefined Section" &&
            !has_common([k], ["preitem", "pre_title"])
          ) {
            section_obj = {
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            };
          } else if (me.fields.section_type == "Collections") {
            section_obj = {
              name: v.fieldname,
              content: "",
              doctype: "Section Content",
              parent: me.section,
            };
          }
        }
        if (
          $('[data-fieldname="' + v.fieldname + '"]').attr("css_design") !=
            undefined &&
          $('[data-fieldname="' + v.fieldname + '"]').attr("css_design") != ""
        ) {
          section_obj = {
            name: v.fieldname,
            doctype: "Section Content",
            parent: me.section,
          };
          section_obj["css_text"] = $(
            '[data-fieldname="' + v.fieldname + '"]'
          ).attr("css_design");
        }
        if (
          $('[data-fieldname="' + v.fieldname + '"]').attr("style_json") !=
            undefined &&
          $('[data-fieldname="' + v.fieldname + '"]').attr("style_json") != ""
        ) {
          section_obj["css_json"] = $(
            '[data-fieldname="' + v.fieldname + '"]'
          ).attr("style_json");
        }
        if (v.fieldname == "category_products_html") {
          var c_products = [];
          var table_html = $(
            me.dialog.fields_dict["category_products_html"].$wrapper.find(
              "table tbody"
            )
          );
          table_html.find("tr").each(function () {
            c_products.push({ name: $(this).find("td:eq(1)").text() });
          });
          section_obj = {
            name: v.fieldname,
            content: JSON.stringify(c_products),
            doctype: "Section Content",
            parent: me.section,
          };
        }
        if (v.fieldname == "blog_category_html") {
          var c_products = [];
          var table_html = $(
            me.dialog.fields_dict["blog_category_html"].$wrapper.find(
              "table tbody"
            )
          );
          table_html.find("tr").each(function () {
            c_products.push({ name: $(this).find("td:eq(1)").text() });
          });
          section_obj = {
            name: v.fieldname,
            content: JSON.stringify(c_products),
            doctype: "Section Content",
            parent: me.section,
          };
        }
        results.push(section_obj);
      }
    });
    if (css_design != "") {
      results.push({ name: "section_css_json", content: style_json });
      results.push({ name: "section_css_text", content: css_design });
    }
    if (results.length > 0 || me.list_section_data.length > 0) {
      frappe.call({
        method:
          "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_section_content",
        args: {
          docs: results,
          lists_data: JSON.stringify(me.list_section_data),
          section: me.page_section,
        },
        freeze: true,
        callback: function (r) {
          if (r.message.status == "Success") {
            frappe.show_alert("Section updated!", 5);
            var eleid = me.comp_id.split("-")[0];
            var parent_idx = me.parent_idx;
            var r_data = r.message.data;
            var u_data = {};
            for (var i = 0; i < r_data.length; i++) {
              if (r_data[i].name != undefined) {
                u_data[r_data[i].field_key] = r_data[i].content;
              }
            }
            var ps_layout_json = r.message.layout_json;
            var u_json = [];

            for (var i = 0; i < ps_layout_json.length; i++) {
              if (ps_layout_json[i].u_id == eleid) {
                if (ps_layout_json[i].components != undefined) {
                  var is_exist = 0;
                  for (
                    var p = 0;
                    p < ps_layout_json[i].components.length;
                    p++
                  ) {
                    if (ps_layout_json[i].components.cid == me.cid) {
                      is_exist = 1;
                      ps_layout_json[i].components[p].data = u_data;
                      ps_layout_json[i].components[p].component_type =
                        r_data[0].component_type;
                      ps_layout_json[i].components[p].component_title =
                        r_data[0].component_title;
                    }
                  }
                  if (is_exist == 0) {
                    var cm_list = ps_layout_json[i].components;

                    cm_list.push({
                      cid: me.cid,
                      data: u_data,
                      component_type: r_data[0].component_type,
                      component_title: r_data[0].component_title,
                    });
                    ps_layout_json[i]["components"] = cm_list;
                  }
                } else {
                  var cm_list = [];
                  cm_list.push({
                    cid: me.cid,
                    data: u_data,
                    component_type: r_data[0].component_type,
                    component_title: r_data[0].component_title,
                  });
                  ps_layout_json[i]["components"] = cm_list;
                }
              } else {
                var cols = ps_layout_json[i].columns;
                if (cols != undefined) {
                  for (var c = 0; c < cols.length; c++) {
                    if (cols[c].u_id == eleid) {
                      if (cols[c].components != undefined) {
                        var is_exist = 0;
                        for (var p = 0; p < cols[c].components.length; p++) {
                          if (cols[c].components.cid == me.cid) {
                            is_exist = 1;
                            cols[c].components[p].data = u_data;
                            cols[c].components[p].component_type =
                              r_data[0].component_type;
                            cols[c].components[p].component_title =
                              r_data[0].component_title;
                          }
                        }
                        if (is_exist == 0) {
                          var cm_list = cols[c].components;
                          // console.log(cm_list);
                          cm_list.push({
                            cid: me.cid,
                            data: u_data,
                            component_type: r_data[0].component_type,
                            component_title: r_data[0].component_title,
                          });
                          cols[c]["components"] = cm_list;
                        }
                      } else {
                        var cm_list = [];
                        cm_list.push({
                          cid: me.cid,
                          data: u_data,
                          component_type: r_data[0].component_type,
                          component_title: r_data[0].component_title,
                        });
                        cols[c]["components"] = cm_list;
                      }
                    } else {
                      if (cols[c].rows) {
                        var f_rows = cols[c].rows;
                        for (var r = 0; r < f_rows.length; r++) {
                          if (f_rows[r].u_id == eleid) {
                            if (f_rows[r].components != undefined) {
                              var is_exist = 0;
                              for (
                                var p = 0;
                                p < f_rows[r].components.length;
                                p++
                              ) {
                                if (f_rows[r].components.cid == me.cid) {
                                  is_exist = 1;
                                  f_rows[r].components[p].data = u_data;
                                  f_rows[r].components[p].component_type =
                                    r_data[0].component_type;
                                  f_rows[r].components[p].component_title =
                                    r_data[0].component_title;
                                }
                              }
                              if (is_exist == 0) {
                                var cm_list = f_rows[r].components;
                                // console.log(cm_list);
                                cm_list.push({
                                  cid: me.cid,
                                  data: u_data,
                                  component_type: r_data[0].component_type,
                                  component_title: r_data[0].component_title,
                                });
                                f_rows[r]["components"] = cm_list;
                              }
                            } else {
                              var cm_list = [];
                              cm_list.push({
                                cid: me.cid,
                                data: u_data,
                                component_type: r_data[0].component_type,
                                component_title: r_data[0].component_title,
                              });
                              f_rows[r]["components"] = cm_list;
                            }
                          }
                          var f_row_cols = f_rows[r].columns;
                          for (var rc = 0; rc < f_row_cols.length; rc++) {
                            if (f_row_cols[rc].u_id == eleid) {
                              if (f_row_cols[rc].components != undefined) {
                                var is_exist = 0;
                                for (
                                  var p = 0;
                                  p < f_row_cols[rc].components.length;
                                  p++
                                ) {
                                  if (
                                    f_row_cols[rc].components[p].cid == me.cid
                                  ) {
                                    is_exist = 1;
                                    f_row_cols[rc].components[p].data = u_data;
                                    f_row_cols[rc].components[
                                      p
                                    ].component_type = r_data[0].component_type;
                                    f_row_cols[rc].components[
                                      p
                                    ].component_title =
                                      r_data[0].component_title;
                                  }
                                }
                                if (is_exist == 0) {
                                  var cm_list = f_row_cols[rc].components;
                                  // console.log(cm_list);
                                  cm_list.push({
                                    cid: me.cid,
                                    data: u_data,
                                    component_type: r_data[0].component_type,
                                    component_title: r_data[0].component_title,
                                  });
                                  f_row_cols[rc]["components"] = cm_list;
                                }
                              } else {
                                var cm_list = [];
                                cm_list.push({
                                  cid: me.cid,
                                  data: u_data,
                                  component_type: r_data[0].component_type,
                                  component_title: r_data[0].component_title,
                                });
                                f_row_cols[rc]["components"] = cm_list;
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }

              u_json.push(ps_layout_json[i]);
            }

            // console.log(u_json);
            frappe.call({
              method:
                "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.update_page_section_layout_json",
              args: {
                page_section: me.page_section,
                layout_json: JSON.stringify(u_json),
              },
              freeze: true,
              callback: function (r) {
                me.dialog.hide();
              },
            });
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
                   
                    <div style='border: 1px solid #ddd;margin-top: 15px;margin-bottom: -21px;padding: 10px;font-weight: bold;'>List Items  <button class="btn btn-sm btn-primary add-list-item" style="float:right;margin-top: -5px;">Add Item</button></div>
                    <table class="table table-bordered table-striped">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody></tbody>
                    </table></div>`).appendTo(list_html);
        // list_html.find('thead tr').append(`<th>Items</th>`);
        let values = [];
        if (v.content) {
          values = JSON.parse(v.content) || [];
          me.dialog.set_value(v.name, v.content);
        }
        var display_fileds_count = 1;
        if (fields.length > 0) {
          list_html.find("thead").append("<tr id='head-cols'></tr>");

          for (var i = 0; i < fields.length; i++) {
            // if(fields[i].field_type!="Attach"){
            list_html
              .find("thead #head-cols")
              .append(
                `<th style='border-bottom-width: 1px;border-color: #ddd;'>` +
                  fields[i].field_label +
                  `</th>`
              );
            display_fileds_count += 1;
            // }
          }
          list_html
            .find("thead #head-cols")
            .append(
              `<th style='border-color: #ddd;border-bottom: 0;'>Actions</th>`
            );
        }

        if (values.length > 0) {
          values.map((f) => {
            var row_html = "<tr>";
            for (var i = 0; i < fields.length; i++) {
              if (fields[i].field_type != "Attach") {
                row_html +=
                  '<td style="border-color: #ddd;word-break: break-word;">' +
                  f[fields[i].field_key] +
                  "</td>";
              } else {
                row_html +=
                  '<td style="border-color: #ddd;word-break: break-word;"><img src="' +
                  f[fields[i].field_key] +
                  '" style="height:50px"/></td>';
              }
            }
            row_html += ' <td style="width: 25%;border-color: #ddd;">';
            row_html +=
              ' <button class="btn btn-sm btn-primary"><span class="fa fa-edit"></span></button>';
            row_html +=
              ' <button class="btn btn-sm btn-danger"><span class="fa fa-trash"></span></button>';
            row_html += " </td>";
            row_html += "</tr>";

            let row = $(row_html);
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
            .html(
              `<tr><td style='border-color: #ddd;word-break: break-word;' colspan="` +
                display_fileds_count +
                `">No records found!</td></tr>`
            );
        }
        list_html.find(".add-list-item").click(function () {
          me.show_list_modal(index, v, "add");
        });
      }
    });
  },
  check_fieldtype_button: function () {
    let me = this;
    let list_fields = this.fields.content.filter(
      (obj) => obj.field_type == "Button"
    );

    $(list_fields).each(function (k, v) {
      let list_html = me.dialog.fields_dict[v.name].$wrapper.empty();
      var btn_url = "";
      var btn_txt = "";
      var edit_style = "";
      if (v.allow_update_to_style == 1) {
        edit_style =
          '<a style="margin-left: 10px;background: #fff;padding: 2px 7px;color: #308fdb;font-size: 12px;border: 1px solid #308fdb;border-radius: 3px;font-weight: 600;" onclick=show_element_style("' +
          v.name +
          '")><i class="fa fa-cog" style="margin-right:5px"></i>Edit Styles</a>';
      }
      if (v.content) {
        var json_data = JSON.parse(v.content);
        for (const [key, value] of Object.entries(json_data)) {
          if (key == "btn_text") {
            btn_txt = value;
          }
          if (key == "btn_redirect_url") {
            btn_url = value;
          }
        }
      }
      let appendHtml =
        '<div class="row"> <div class="section-head" style="margin: 0 15px 15px"><a class="h6 uppercase">Button' +
        edit_style +
        "</a></div>";
      appendHtml +=
        '<div class="col-md-6"><div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="' +
        v.name +
        '" title="c1abe1bcce"><div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Button Text</label>                    </div>                    <div class="control-input-wrapper">                        <div class="control-input" style="display: block;"><input type="text" value="' +
        btn_txt +
        '" autocomplete="off" class="input-with-feedback form-control" maxlength="140" data-fieldtype="Data" data-fieldname="btn_text" data-key="' +
        v.name +
        '" placeholder=""></div><div class="control-value like-disabled-input" style="display: none;">#</div><p class="help-box small text-muted hidden-xs"></p></div></div></div></div>';
      appendHtml +=
        '<div class="col-md-6"><div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="' +
        v.name +
        '" title="c1abe1bcce"><div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Button Redirect Url</label></div><div class="control-input-wrapper"><div class="control-input" style="display: block;"><input type="text" value="' +
        btn_url +
        '" autocomplete="off" class="input-with-feedback form-control" maxlength="140" data-fieldtype="Data" data-fieldname="btn_redirect_url" data-key="' +
        v.name +
        '" placeholder=""></div><div class="control-value like-disabled-input" style="display: none;">#</div><p class="help-box small text-muted hidden-xs"></p></div></div></div></div>';
      // appendHtml+='<div class="col-md-6"><div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="'+v.name+'" title="c1abe1bcce"><div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Button Background Color</label>                    </div>                    <div class="control-input-wrapper"><div class="control-input" style="display: block;"><input type="text" autocomplete="off" class="input-with-feedback form-control" maxlength="140" data-fieldtype="Data" data-fieldname="btn_bg_color" data-key="'+v.name+'" placeholder=""></div><div class="control-value like-disabled-input" style="display: none;">#</div><p class="help-box small text-muted hidden-xs"></p></div></div></div></div>'
      // appendHtml+='<div class="col-md-6"><div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="'+v.name+'" title="c1abe1bcce"><div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Button Text Color</label>                    </div>                    <div class="control-input-wrapper"><div class="control-input" style="display: block;"><input type="text" autocomplete="off" class="input-with-feedback form-control" maxlength="140" data-fieldtype="Data" data-fieldname="btn_text_color" data-key="'+v.name+'" placeholder=""></div><div class="control-value like-disabled-input" style="display: none;">#</div><p class="help-box small text-muted hidden-xs"></p></div></div></div></div>'
      list_html.append(appendHtml);
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
            // console.log(val.idx)
            // console.log(edit_data.idx)

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
      // console.log(val,"-----save_btns1-----")
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
      // console.log(val,"-----predefined_save_btns-----")
      if (!val.preitem || !val.pre_title) {
        frappe.throw("Please fill all columns");
      }

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
      // console.log(val,"-----save_btns-----")
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
function preview_page() {
  frappe.db.get_doc("CMS Settings", "CMS Settings", {}).then((res) => {
    if (res.use_other_domain == 1) {
      window.open(
        res.domain + "/c/" + page_route,
        "_blank" // <- This is what makes it open in a new window.
      );
    } else {
      window.open(
        window.location.origin + "/" + page_route,
        "_blank" // <- This is what makes it open in a new window.
      );
    }
  });
}
function change_page() {
  $(".page-list").show();
}
function change_page_route(route) {
  window.location.href = "/app/go1cms-builder?route=" + route;
}
$(document).ready(function () {
  $("body").click(function (event) {
    if (event.target.id == "page-link") {
      return;
    }
    $(".page-list").hide();
  });
});
