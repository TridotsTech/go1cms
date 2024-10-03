frappe.ui.form.on("Section Content", "form_render", function (frm, cdt, cdn) {
  var d = locals[cdt][cdn];
  // let wrapper = frm.fields_dict[d.parentfield].grid.grid_rows_by_docname[cdn].grid_form.fields_dict['fields_json'].wrapper
  if (d.field_type == "List") {
    setTimeout(() => {
      let wrapper =
        frm.fields_dict[d.parentfield].grid.grid_rows_by_docname[cdn].grid_form
          .fields_dict["fields_json"].wrapper;
      fields_json(d, wrapper);
    }, 500);
  }
  $('.btn-default[data-fieldname="choose_style_properties"]').css(
    "border",
    "1px solid #ddd"
  );
  $('.btn-default[data-fieldname="setup_defaults"]').css(
    "border",
    "1px solid #ddd"
  );
});

frappe.ui.form.on("Section Content", {
  field_type: function (frm, cdt, cdn) {
    let item = locals[cdt][cdn];
    if (item.field_type == "List") {
      setTimeout(() => {
        let wrapper =
          frm.fields_dict[item.parentfield].grid.grid_rows_by_docname[cdn]
            .grid_form.fields_dict["fields_json"].wrapper;
        fields_json(item, wrapper);
      }, 500);
    }
  },
  content: function (frm, cdt, cdn) {
    let item = locals[cdt][cdn];
    if (item.field_type == "List") {
      console.log(item.content);
    }
  },
  setup_defaults: function (frm, cdt, cdn) {
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_section_element_properties",
      args: { id: cdn },
      async: false,
      callback: function (r) {
        if (r.message.css_properties_list) {
          var data = r.message.css_properties_list;
          var json_data = {};
          if (r.message.css_json != null && r.message.css_json != undefined) {
            json_data = JSON.parse(r.message.css_json);
          }
          var fonts_data = [];
          if (r.message.fonts_list) {
            for (var i = 0; i < r.message.fonts_list.length; i++) {
              fonts_data.push(r.message.fonts_list[i].name);
            }
          }
          var filelist = JSON.parse(data);
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
            title: "Edit Style",
            fields: fields,
          });
          styledialog.show();
          styledialog.$wrapper.find(".modal-dialog").attr("id", cdn);
          styledialog.set_primary_action(__("Save"), function () {
            let values = styledialog.get_values();
            let style_json = {};
            let css_design =
              "." + r.message.class_name + " ." + r.message.field_key + "{";
            for (let k in values) {
              if (values[k] != "" && values[k] != "0px") {
                style_json[k] = values[k];
              }
            }
            // console.log(style_json)
            styledialog.hide();
            frappe.model.set_value(
              cdt,
              cdn,
              "css_json",
              JSON.stringify(style_json)
            );
            // $(".modal-dialog[id='"+cdn+"']").parent().remove();
          });
          for (var i = 0; i < child_sections.length; i++) {
            // if(i!=child_sections.length-1){
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
                "margin-bottom:10px;border-top:none !important;margin-top: -20px;"
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
              .attr("style", "font-weight: 600;margin-bottom:0px");
            // }
            // styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find("h6.form-section-heading.uppercase").attr("style","font-weight: 400;color: #222 !important;text-transform: capitalize;font-size: 14px;");
            // styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom:0px");
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
                  "font-weight: 600;margin-bottom:0px;margin-top:15px;"
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
          styledialog.$wrapper.find(".modal-dialog").css("max-width", "700px");
        }
      },
    });
  },
  //created by boopathy-30/06/2022

  choose_style_properties: function (frm, cdt, cdn) {
    // console.log(frm, cdt, cdn,"frm, cdt, cdn")
    frappe.call({
      method:
        "go1_cms.go1_cms.doctype.section_template.section_template.get_css_fields",
      args: {},
      callback: function (r) {
        console.log(r.message, "r.message");
        let dialog = new frappe.ui.Dialog({
          title: __("Choose Properties"),
          fields: [{ fieldname: "css_fields_html", fieldtype: "HTML" }],
        });
        dialog.set_primary_action(__("Update"), function () {
          let selected_fields = [];
          $(wrapper)
            .find('.fields-list input[type="checkbox"]:checked')
            .each(function () {
              let obj = r.message.find((o) => o.fieldname === $(this).val());
              selected_fields.push(obj);
            });
          // frm.set_value('css_properties_list', JSON.stringify(selected_fields));
          frappe.model.set_value(
            cdt,
            cdn,
            "css_properties_list",
            JSON.stringify(selected_fields)
          );
          dialog.hide();
          frm.save();
        });
        let wrapper = dialog.fields_dict.css_fields_html.$wrapper.empty();

        $(`<div class="row">
                    <div class="col-md-12 col-xs-12">
                        <label>${__("Select fields to display")}</label>
                    </div>
                    <div class="fields-list"></div>
                </div>`).appendTo(wrapper);
        let existing_fields = [];
        if (frm.doc.css_properties_list) {
          existing_fields = JSON.parse(frm.doc.css_field_list);
        }
        r.message.map((f, index) => {
          if (!has_common([f.fieldtype], ["Column Break", "Section Break"])) {
            let checked = "";
            let obj = existing_fields.find((o) => o.fieldname === f.fieldname);
            if (obj) checked = 'checked="checked"';
            let css_html = $(`<div class="col-md-6" style="float:left;">
                            <div class="checkbox" style="margin-top: 0px !important;">
                                <label>
                                    <span class="input-area">
                                        <input type="checkbox" autocomplete="off" class="input-with-feedback" name="ftd" label="Name" value="${f.fieldname}"  ${checked} />
                                    </span>
                                    <span class="disp-area" style="display:none">
                                        <i class="octicon octicon-check" style="margin-right: 3px;"></i>
                                    </span>
                                    <span class="label-area small">${f.label}</span>
                                </label>
                                <p class="help-box small text-muted"></p>
                            </div>
                        </div>`);
            $(wrapper).find(".fields-list").append(css_html);
          }
        });
        dialog.show();
      },
    });
  },

  //end by boopathy
});

function fields_json(item, html) {
  let wrapper = $(html).empty();
  // $(`<div><button class="btn btn-sm btn-primary">${__("Add Fields")}</button><button class="btn btn-sm btn-warning btn-add-edit-data" style="margin-left:15px">${__("Add / View Data")}</button><button class="btn btn-sm btn-warning btn-add-data" style="margin-left:15px">${__("Add Data")}</button><button class="btn btn-sm btn-default btn-view-data" style="margin-left:15px;border:1px solid #ddd">${__("View Data")}</button></div>
  $(`<div><button class="btn btn-sm btn-primary">${__(
    "Add Fields"
  )}</button><button class="btn btn-sm btn-warning btn-add-edit-data" style="margin-left:15px">${__(
    "Add / View Data"
  )}</button></div>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>${__("Field Label")}</th>
                <th>${__("Field Key")}</th>
                <th>${__("Field Type")}</th>
                <th></th>
            </tr>
        </thead>
        <tbody></tbody>
    </table>`).appendTo(wrapper);
  let fields_list = [];
  if (item.fields_json) {
    fields_list = JSON.parse(item.fields_json);
  }
  if (fields_list && fields_list.length > 0) {
    fields_list.map((f) => {
      let row = $(`<tr>
                <td>${f.field_label}</td>
                <td>${f.field_key}</td>
                <td>${f.field_type}</td>
                <td>
                    <button class="btn btn-xs btn-info"><span class="fa fa-edit"></span></button>
                    <button class="btn btn-xs btn-danger"><span class="fa fa-trash"></span></button>
                </td>
            </tr>`);
      $(wrapper).find("tbody").append(row);

      row.find(".btn-info").click(() => {
        get_fields_list(html, item, "Edit", f);
      });
      row.find(".btn-danger").click(() => {
        let new_list = fields_list.filter((obj) => obj.idx != f.idx);
        $(new_list).each(function (k, v) {
          v.idx = k + 1;
        });
        frappe.model.set_value(
          item.doctype,
          item.name,
          "fields_json",
          JSON.stringify(new_list)
        );
        if (!cur_frm.__islocal) cur_frm.save();
        else fields_json(item, html);
      });
    });
  } else {
    $(wrapper)
      .find("tbody")
      .append(`<tr><td colspan="4">${__("No records found!")}</td></tr>`);
  }

  wrapper.find(".btn-primary").click(() => {
    get_fields_list(html, item, "Add");
  });
  wrapper.find(".btn-add-data").click(() => {
    if (JSON.parse(item.fields_json).length > 0) {
      add_new_list_item(html, item);
    } else {
      frappe.msgprint(__("Please Add Fields"));
    }
  });
  wrapper.find(".btn-view-data").click(() => {
    if (JSON.parse(item.content).length > 0) {
      view_list_item(html, item);
    } else {
      frappe.msgprint(__("There is no data"));
    }
  });
  wrapper.find(".btn-add-edit-data").click(() => {
    // if(JSON.parse(item.content).length>0){
    view_list_items(html, item);
    view_data_dialog.show();
    // }
    // else{
    //     frappe.msgprint(__('There is no data'));
    // }
  });
}
function get_items_html(wrapper, doc) {}
let view_data_dialog = new frappe.ui.Dialog({
  title: __("List Items"),
  fields: [
    {
      fieldname: "list_html",
      fieldtype: "HTML",
      label: "Items",
    },
  ],
});
view_data_dialog.$wrapper.find(".modal-dialog").css("max-width", "900px");

function view_list_items(wrapper, doc) {
  var fields = [];
  let list_html;
  var values = [];
  if (doc.content) {
    values = JSON.parse(doc.content);
  }
  var fieldslist = JSON.parse(doc.fields_json);
  if (fieldslist) {
    let fields = fieldslist || [];
    list_html = $(`<div>
                    <button class="btn btn-sm btn-primary add-list-item">Add Item</button>
                    <div style='border: 1px solid #ddd;margin-top: 15px;margin-bottom: -21px;padding: 10px;font-weight: bold;'>Items</div>
                    <table class="table table-bordered table-striped" id="list_html_table">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                    </div>`);
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
        // else{

        //     }
      }
      list_html
        .find("thead #head-cols")
        .append(
          `<th style='border-color: #ddd;border-bottom: 0;'>Actions</th>`
        );
    }

    if (values.length > 0) {
      values.map((f, index) => {
        var row_html = "<tr>";
        for (var i = 0; i < fields.length; i++) {
          if (fields[i].field_type != "Attach") {
            row_html +=
              '<td style="border-color: #ddd;word-break: break-word;">' +
              f[fields[i].field_key] +
              "</td>";
          } else {
            row_html +=
              '<td style="border-color: #ddd;word-break: break-word;"><img style="max-height:50px" src="' +
              f[fields[i].field_key] +
              '"/></td>';
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
          edit_list_item(wrapper, doc, index);
        });
        row.find(".btn-danger").click(function () {
          var updated_date = [];
          // let content = values.filter((obj) => obj.idx != index);
          // $(content).each(function(i, j) {
          //     console.log(j)
          //     j.idx = (i + 1);
          // });
          let idx = 1;
          for (var i = 0; i < values.length; i++) {
            if (i != index) {
              values[i]["idx"] = idx;
              updated_date.push(values[i]);
              idx++;
            }
          }
          // console.log(updated_date);
          doc.content = JSON.stringify(updated_date);
          frappe.model.set_value(
            "Section Content",
            doc.name,
            "content",
            JSON.stringify(updated_date)
          );
          view_data_dialog.$wrapper
            .find("#list_html_table tbody tr:eq(" + index + ")")
            .remove();

          cur_frm.set_value("route", "");
          view_list_items(wrapper, doc);
        });
        list_html.find("tbody").append(row);
      });
    } else {
      list_html
        .find("tbody")
        .html(
          `<tr><td style='border-color: #ddd;word-break: break-word;' colspan="` +
            display_fileds_count +
            `;word-break: break-word;">No records found!</td></tr>`
        );
    }
    list_html.find(".add-list-item").click(function () {
      add_new_list_item(wrapper, doc);
    });
  }
  // view_data_dialog = new frappe.ui.Dialog({
  //   title: __("List Items"),
  //   fields: [
  //     {
  //       fieldname: "list_html",
  //       fieldtype: "HTML",
  //       label: "Items",
  //     },
  //   ],
  // });
  // view_data_dialog.show();
  // cur_frm.set_value("route", "");
  view_data_dialog.fields_dict.list_html.$wrapper.html(list_html);
}
function view_list_item(wrapper, doc) {
  var fields = [];
  let list_html;
  var values = JSON.parse(doc.content);
  var fieldslist = JSON.parse(doc.fields_json);
  if (fieldslist) {
    let fields = fieldslist || [];
    list_html = $(`<div>
                    
                    <div style='border: 1px solid #ddd;margin-top: 15px;margin-bottom: -21px;padding: 10px;font-weight: bold;'>Items</div>
                    <table class="table table-bordered table-striped" id="list_html_table">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody></tbody>
                    </table></div>`);
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
        // else{

        //     }
      }
      list_html
        .find("thead #head-cols")
        .append(
          `<th style='border-color: #ddd;border-bottom: 0;'>Actions2</th>`
        );
    }

    if (values.length > 0) {
      values.map((f, index) => {
        var row_html = "<tr>";
        for (var i = 0; i < fields.length; i++) {
          if (fields[i].field_type != "Attach") {
            row_html +=
              '<td style="border-color: #ddd;word-break: break-word;">' +
              f[fields[i].field_key] +
              "</td>";
          } else {
            row_html +=
              '<td style="border-color: #ddd;word-break: break-word;"><img style="max-height:50px" src="' +
              f[fields[i].field_key] +
              '"/></td>';
          }
        }
        row_html += ' <td style="width: 25%;border-color: #ddd;">';
        // row_html+=' <button class="btn btn-sm btn-primary"><span class="fa fa-edit"></span></button>';
        row_html +=
          ' <button class="btn btn-sm btn-danger"><span class="fa fa-trash"></span></button>';
        row_html += " </td>";
        row_html += "</tr>";

        let row = $(row_html);
        row.find(".btn-danger").click(function () {
          var updated_date = [];
          let content = values.filter((obj) => obj.idx != index);
          // $(content).each(function(i, j) {
          //     console.log(j)
          //     j.idx = (i + 1);
          // });
          var j = 0;
          for (var i = 0; i < values.length; i++) {
            if (i != index) {
              updated_date.idx = j + 1;
              updated_date.push(values[i]);
              j = j + 1;
            }
          }

          doc.content = JSON.stringify(updated_date);
          frappe.model.set_value(
            "Section Content",
            doc.name,
            "content",
            JSON.stringify(updated_date)
          );
          view_data_dialog.$wrapper
            .find("#list_html_table tbody tr:eq(" + index + ")")
            .remove();
        });
        list_html.find("tbody").append(row);
      });
    } else {
      list_html
        .find("tbody")
        .html(
          `<tr><td style='border-color: #ddd;word-break: break-word;' colspan="` +
            display_fileds_count +
            `;word-break: break-word;">No records found!</td></tr>`
        );
    }
  }
  view_data_dialog = new frappe.ui.Dialog({
    title: __("View List Items"),
    fields: [
      {
        fieldname: "list_html",
        fieldtype: "HTML",
        label: "Items",
      },
    ],
  });
  view_data_dialog.show();
  view_data_dialog.fields_dict.list_html.$wrapper.html(list_html);
}
function add_new_list_item(wrapper, doc) {
  var fieldslist = JSON.parse(doc.fields_json);
  var fields = [];
  for (var i = 0; i < fieldslist.length; i++) {
    if (["Text", "Attach"].includes(fieldslist[i].field_type)) {
      fields.push({
        fieldname: fieldslist[i].field_key,
        fieldtype: "Data",
        label: fieldslist[i].field_label,
        reqd: 1,
      });
    } else {
      fields.push({
        fieldname: fieldslist[i].field_key,
        fieldtype: fieldslist[i].field_type,
        label: fieldslist[i].field_label,
        reqd: 1,
      });
    }
  }
  let data_dialog = new frappe.ui.Dialog({
    title: __("Add List Item"),
    fields: fields,
  });
  data_dialog.show();
  data_dialog.set_primary_action(__("Save"), () => {
    let values = data_dialog.get_values();
    if (doc.content) {
      var old_content = JSON.parse(doc.content);
      values.idx = old_content.length + 1;
      old_content.push(values);
      doc.content = JSON.stringify(old_content);
    } else {
      var ct_arry = [];
      values.idx = 1;
      ct_arry.push(values);
      doc.content = JSON.stringify(ct_arry);
    }
    frappe.model.set_value("Section Content", doc.name, "content", doc.content);
    data_dialog.hide();
    cur_frm.set_value("route", "");
    // update_list_items(wrapper, doc);
    view_list_items(wrapper, doc);
  });
}
function edit_list_item(wrapper, doc, index) {
  var fieldslist = JSON.parse(doc.fields_json);
  fieldslist.unshift({
    field_label: "STT",
    field_key: "idx",
    field_type: "Int",
    idx: fieldslist.length + 1,
  });
  var fields = [];
  for (var i = 0; i < fieldslist.length; i++) {
    if (["Text", "Attach"].includes(fieldslist[i].field_type)) {
      fields.push({
        fieldname: fieldslist[i].field_key,
        fieldtype: "Data",
        label: fieldslist[i].field_label,
        // reqd: 1,
      });
    } else {
      fields.push({
        fieldname: fieldslist[i].field_key,
        fieldtype: fieldslist[i].field_type,
        label: fieldslist[i].field_label,
        // reqd: 1,
      });
    }
  }
  let data_dialog = new frappe.ui.Dialog({
    title: __("Edit List Item"),
    fields: fields,
  });
  var old_content = JSON.parse(doc.content);
  let content = old_content.find((obj) => obj.idx == index + 1);

  $(fieldslist).each(function (k, v) {
    data_dialog.set_value(v.field_key, content[v.field_key]);
  });
  data_dialog.show();
  data_dialog.set_primary_action(__("Save"), () => {
    let values = data_dialog.get_values();
    if (doc.content) {
      if (content.idx != values.idx) {
        for (var idx = index; idx >= values.idx; idx--) {
          let new_content = old_content[idx - 1];
          new_content["idx"] = idx + 1;
          old_content[idx] = new_content;
        }
      }
      old_content[values.idx - 1] = values;
      doc.content = JSON.stringify(old_content);
    } else {
      var ct_arry = [];
      values.idx = 1;
      ct_arry.push(values);
      doc.content = JSON.stringify(ct_arry);
    }
    frappe.model.set_value("Section Content", doc.name, "content", doc.content);
    data_dialog.hide();
    cur_frm.set_value("route", "");
    // update_list_items(wrapper, doc);
    view_list_items(wrapper, doc);
  });
}
function update_list_items(wrapper, doc) {
  var fields = [];
  let list_html;
  var values = JSON.parse(doc.content);
  var fieldslist = JSON.parse(doc.fields_json);
  if (fieldslist) {
    let fields = fieldslist || [];
    list_html = $(`<div>
                    <button class="btn btn-sm btn-primary add-list-item">Add Item</button>
                    <div style='border: 1px solid #ddd;margin-top: 15px;margin-bottom: -21px;padding: 10px;font-weight: bold;'>Items</div>
                    <table class="table table-bordered table-striped" id="list_html_table">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody></tbody>
                    </table></div>`);
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
        // else{

        //     }
      }
      list_html
        .find("thead #head-cols")
        .append(
          `<th style='border-color: #ddd;border-bottom: 0;'>Actions3</th>`
        );
    }

    if (values.length > 0) {
      values.map((f, index) => {
        var row_html = "<tr>";
        for (var i = 0; i < fields.length; i++) {
          if (fields[i].field_type != "Attach") {
            row_html +=
              '<td style="border-color: #ddd;word-break: break-word;">' +
              f[fields[i].field_key] +
              "</td>";
          } else {
            row_html +=
              '<td style="border-color: #ddd;word-break: break-word;"><img style="max-height:50px" src="' +
              f[fields[i].field_key] +
              '"/></td>';
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
        row.find(".btn-danger").click(function () {
          var updated_date = [];
          let content = values.filter((obj) => obj.idx != index);
          // $(content).each(function(i, j) {
          //     console.log(j)
          //     j.idx = (i + 1);
          // });
          for (var i = 0; i < values.length; i++) {
            if (i != index) {
              updated_date.push(values[i]);
            }
          }

          doc.content = JSON.stringify(updated_date);
          frappe.model.set_value(
            "Section Content",
            doc.name,
            "content",
            JSON.stringify(updated_date)
          );
          view_data_dialog.$wrapper
            .find("#list_html_table tbody tr:eq(" + index + ")")
            .remove();
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
  }
  list_html.find(".add-list-item").click(function () {
    add_new_list_item(wrapper, doc);
  });
  view_data_dialog.fields_dict.list_html.$wrapper.html(list_html);
}

function get_fields_list(wrapper, doc, frm_type, edit_doc) {
  let dialog = new frappe.ui.Dialog({
    title: frm_type == "Add" ? __("Add Field") : __("Edit Field"),
    fields: [
      {
        fieldname: "field_label",
        fieldtype: "Data",
        label: __("Field Label"),
        default: (edit_doc && edit_doc.field_label) || "",
        reqd: 1,
      },
      {
        fieldname: "field_key",
        fieldtype: "Data",
        label: __("Field Key"),
        default: (edit_doc && edit_doc.field_key) || "",
      },
      {
        fieldname: "field_type",
        fieldtype: "Select",
        label: __("Field Type"),
        default: (edit_doc && edit_doc.field_type) || "",
        options: ["Text", "Int", "Long Text", "Small Text", "Attach"],
        reqd: 1,
      },
      {
        fieldtype: "Column Break",
        fieldname: "cb_1",
      },
      {
        fieldtype: "Code",
        fieldname: "content",
        label: __("Content"),
        default: (edit_doc && edit_doc.content) || "",
      },
    ],
  });
  dialog.show();
  dialog.set_primary_action(__("Save"), () => {
    let values = dialog.get_values();
    let prev_vals = [];
    if (!values.field_key || values.field_key == "") {
      let field_key = values.field_label.toLowerCase().replace(/ /g, "_");
      values.field_key = field_key;
    }
    if (doc.fields_json) prev_vals = JSON.parse(doc.fields_json);
    if (frm_type == "Add") {
      if (prev_vals && prev_vals.length > 0) {
        values.idx = prev_vals.length + 1;
        prev_vals.push(values);
      } else {
        values.idx = 1;
        prev_vals = [values];
      }
    } else {
      $(prev_vals).each(function (k, v) {
        if (v.idx == edit_doc.idx) {
          v.field_label = values.field_label;
          v.field_key = values.field_key;
          v.content = values.content;
          v.field_type = values.field_type;
        }
      });
    }
    frappe.model.set_value(
      doc.doctype,
      doc.name,
      "fields_json",
      JSON.stringify(prev_vals)
    );
    dialog.hide();
    if (!cur_frm.doc.__islocal) {
      cur_frm.save();
    } else {
      fields_json(doc, wrapper);
    }
  });
  dialog.$wrapper.find(".modal-dialog").css("width", "75%");
}

frappe.provide("cms");
frappe.require("/assets/go1_cms/css/jodit.min.css");
frappe.require("/assets/go1_cms/js/jodit.min.js");
cms.TextEditorView = Class.extend({
  init: function (opts) {
    this.field_name = opts.fieldname;
    this.frm = opts.frm;

    this.make();
  },

  make: function () {
    let me = this;
    let wrapper = $(this.frm.get_field(this.field_name).wrapper).empty();
    this.element = document.createElement("textarea");
    $(wrapper).append(me.element);

    var editor = new Jodit(me.element);

    // this.editor = Jodit.instances.jeditor_webform;
    if (editor) {
      editor.value = me.frm.doc[me.field_name] || "";
    }

    this.element.addEventListener("change", function () {
      me.frm.set_value(me.field_name, this.value);
    });
  },
});

cms.SectionBuilder = Class.extend({
  init: function (opts) {
    this.field_name = opts.fieldname;
    this.frm = opts.frm;
    this.from_form = opts.from_form;
    this.wrapper = opts.wrapper;
    this.title_field = opts.title_field;
    this.title = opts.title;

    this.section_template = opts.template;
    this.style_template = document.createElement("style");
    if (!this.section_template || this.section_template == "") {
      this.section_template = $(`<div class="sectiontemplate"></div>`);
    } else {
      let template = this.section_template.split("<style>")[0];
      this.section_template = $(template);
      if (opts.template.indexOf("<style>") > -1) {
        let styles = opts.template.split("<style>")[1].split("</style>")[0];
        let styles_list = styles.split("#{{section}}");
        this.create_style_elements(styles_list);
      }
    }

    this.make();
  },
  make: function () {
    this.get_layouts();
    this.get_components();
    this.get_css_properties();

    this.make_section_layout();
  },
  get_layouts: function () {
    let me = this;
    frappe.call({
      method: "go1_cms.go1_cms.api.get_section_layouts",
      args: {},
      callback: function (r) {
        if (r.message) {
          me.layouts = r.message;
        }
      },
    });
  },
  get_components: function () {
    let me = this;
    frappe.call({
      method: "go1_cms.go1_cms.api.get_section_components",
      args: {},
      callback: function (r) {
        if (r.message) {
          me.components = r.message;
        }
      },
    });
  },
  get_css_properties: function () {
    let me = this;
    frappe.call({
      method: "go1_cms.go1_cms.api.get_styles_list",
      args: {},
      callback: function (r) {
        if (r.message) {
          me.css_groups = r.message;
        }
      },
    });
  },
  make_section_layout: function () {
    let title = "";
    if (this.from_form == 1 && this.title_field) title = this.title_field;
    else if (this.title) title = this.title;
    $(`<div class="section-layout">
            <div class="section-inner-layout">
                <div class="row">
                    <div class="col-md-3 section-settings"><ul></ul></div>
                    <div class="col-md-6" style="float:left;">
                        <div class="section-title">${__(title)}</div>
                    </div>
                    <div class="col-md-3"></div>
                </div>
            </div>
            <div class="section-row-layout"></div>
        </div>
        <style>
            div[data-fieldname="${this.field_name}"] .section-layout{
                border: 1px solid #ddd;
            }
            div[data-fieldname="${this.field_name}"] .section-inner-layout{
                color: #fff;
                background: #444343;
            }
            div[data-fieldname="${this.field_name}"] .section-title,
            div[data-fieldname="${this.field_name}"] .row-title,
            div[data-fieldname="${this.field_name}"] .comp-title{
                text-align: center;
                padding: 10px;
            }
            div[data-fieldname="${this.field_name}"] .section-row-layout{
                min-height: 120px;
                padding: 10px;
            }
            div[data-fieldname="${this.field_name}"] .section-settings ul,
            div[data-fieldname="${this.field_name}"] .row-settings ul,
            div[data-fieldname="${this.field_name}"] .comp-settings ul{
                list-style: none;
                margin:0;
                display: flex;
                padding-left: 0;
            }
            div[data-fieldname="${this.field_name}"] .section-settings ul li,
            div[data-fieldname="${this.field_name}"] .row-settings ul li,
            div[data-fieldname="${this.field_name}"] .comp-settings ul li{
                padding: 10px;
            }
            div[data-fieldname="${
              this.field_name
            }"] .section-row-layout .new-row-div{
                text-align: center;
                padding: 10px;
                margin: 10px;
            }
            div[data-fieldname="${
              this.field_name
            }"] .section-row-layout .add-row{
                padding: 5px 10px;
                background: #4d8a4d;
                border-radius: 50%;
                color: #fff;
            }
            div[data-fieldname="${this.field_name}"] .row-head{
                background: #6a619e;
                color: #fff;
            }
            div[data-fieldname="${this.field_name}"] .row-body-layout{
                border: 1px solid #ddd;
                margin-bottom: 10px;
            }
            div[data-fieldname="${this.field_name}"] .row-layout{
                min-height: 100px;
                padding: 10px;
            }
            div[data-fieldname="${this.field_name}"] .new-comp{
                text-align: center;
                margin-top: 10px;
            }
            div[data-fieldname="${this.field_name}"] .new-comp .add-comp{
                background: #6c24a2;
                color: #fff;
                padding: 5px 10px;
                border-radius: 50%;
            }
            div[data-fieldname="${this.field_name}"] .comp-head{
                background: #53b772;
                color: #fff;
                margin-bottom: 10px;
            }
        </style>`).appendTo(this.wrapper);
    let settings_wrapper = this.wrapper.find(".section-settings");
    this.make_settings(
      settings_wrapper,
      ["Settings"],
      "Section",
      "#{{section}} .sectiontemplate"
    );
    this.make_row();
  },
  make_settings: function (
    wrapper,
    settings_list,
    type,
    selector,
    row_count,
    column_count,
    component_class
  ) {
    let me = this;
    if (settings_list && settings_list.length > 0) {
      $(settings_list).each(function (k, v) {
        let icon, cls;
        if (v == "Settings") {
          icon = "fa fa-cog";
          cls = "settings";
        } else if (v == "Copy") {
          icon = "fa fa-clone";
          cls = "copy";
        } else if (v == "Delete") {
          icon = "fa fa-trash";
          cls = "delete";
        } else if (v == "Move") {
          icon = "fa fa-arrows";
          cls = "move";
        }
        let row = $(`<li><span class="${icon}"></span></li>`);
        $(wrapper).find("ul").append(row);
        row.click(() => {
          if (v == "Settings") {
            me.settings_modal(type, selector);
          }
          if (v == "Copy") {
            me.copy_element(
              wrapper,
              type,
              selector,
              row_count,
              column_count,
              component_class
            );
          }
          if (v == "Delete") {
            me.delete_element(
              wrapper,
              type,
              selector,
              row_count,
              column_count,
              component_class
            );
          }
        });
      });
    }
  },
  settings_modal: function (type, selector) {
    let me = this;
    this.settings_dialog = new frappe.ui.Dialog({
      title: `${type} Settings`,
      fields: me.settings_dialog_fields(type),
    });
    this.settings_dialog.show();
    this.settings_dialog.set_primary_action(__("Update"), function () {
      let values = me.settings_dialog.get_values();
      let styles = "";
      $.each(values, function (k, v) {
        let field_info = me.settings_dialog.fields.find(
          (obj) => obj.fieldname == k
        );
        if (has_common([field_info.fieldtype], ["Attach", "Attach Image"])) {
          styles += k.replace(/_/g, "-") + ": url(" + v + ");";
        } else {
          styles += k.replace(/_/g, "-") + ":" + v + ";";
        }
      });
      if (me.style_template.textContent.indexOf(selector) != -1) {
        me.style_template.childNodes.forEach(function (i, j) {
          if (i.data.indexOf(selector) != -1) {
            me.style_template.removeChild(me.style_template.childNodes[j]);
          }
        });
      }
      me.style_template.appendChild(
        document.createTextNode(selector + " {" + styles + "}")
      );
      me.save_template();
      me.settings_dialog.hide();
    });
    this.settings_dialog.$wrapper.find(".modal-dialog").css("width", "60%");
    this.set_settings_dialog_values(type, selector);
  },
  settings_dialog_fields: function (type) {
    let me = this;
    let fields = [];
    $(me.css_groups).each(function (k, v) {
      if (v.style_elements && v.style_elements.length > 0) {
        fields.push({
          fieldname: "cssgrp" + (k + 1),
          fieldtype: "Section Break",
          label: __(v.name),
          collapsible: 1,
        });
        $(v.style_elements).each(function (key, val) {
          let field = {};
          field.fieldtype = val.value_type;
          if (val.value_type == "Number") field.fieldtype = "Float";
          if (val.value_type == "Attach") field.fieldtype = "Attach Image";
          if (val.value_type == "Select") {
            if (val.options_json) {
              field.options = JSON.parse(val.options_json);
            }
          }
          field.fieldname = val.property_name.replace(/-/g, "_");
          field.label = __(val.name);
          fields.push(field);
          if ((key + 1) % 3 == 0) {
            fields.push({
              fieldname: "colbr" + (k + 1),
              fieldtype: "Column Break",
            });
          }
        });
        if (v.style_elements.length < 3) {
          fields.push({
            fieldname: "colbr" + (k + 1),
            fieldtype: "Column Break",
          });
        }
      }
    });
    return fields;
  },
  set_settings_dialog_values: function (type, selector) {
    let me = this;
    if (this.style_template.textContent.indexOf(selector) != -1) {
      this.style_template.childNodes.forEach(function (k, v) {
        if (k.data.indexOf(selector) != -1) {
          let styles = k.data.split(selector)[1].split("{")[1].split("}")[0];
          let style_list = styles.split(";");
          $(style_list).each(function (i, j) {
            let splits = j.split(":");
            let key = splits[0].trim().replace(/-/g, "_");
            try {
              if (splits[1].indexOf("url") > -1) {
                me.settings_dialog.set_value(
                  key,
                  splits[1].split("(")[1].split(")")
                );
              } else {
                me.settings_dialog.set_value(key, splits[1]);
              }
            } catch (e) {}
          });
        }
      });
    }
  },
  make_row: function () {
    let me = this;
    $(me.wrapper).find(".section-row-layout").html("");
    if ($(this.section_template).children().length > 0) {
      let child_node = $(me.section_template).children();
      for (var i = 0; i < child_node.length; i++) {
        let node = $(child_node)[i];
        let node_html;
        if (node.className.indexOf("row") != -1) {
          node_html = $(`<div class="row-body-layout">
                        <div class="row-head">
                            <div class="row">
                                <div class="col-md-3 row-settings"><ul></ul></div>
                                <div class="col-md-6 row-title">${__(
                                  "Row"
                                )}</div>
                                <div class="col-md-3"></div>
                            </div>
                        </div>
                        <div class="row-layout"></div>
                    </div>`);
          let row_html = $(`<div class="${node.className}"></div>`);
          if ($(node)[0].children.length > 0) {
            for (var j = 0; j < $(node)[0].children.length; j++) {
              let col_html = "";
              if (
                $(node)[0].children[j].className.indexOf("section-col") != -1
              ) {
                let col_node = $(node)[0].children[j];
                col_html = $(`<div class="${col_node.className}"></div>`);
                if ($(col_node)[0].children.length > 0) {
                  for (var k = 0; k < $(col_node)[0].children.length; k++) {
                    let component = $(col_node)[0].children[k];
                    if (component.className.indexOf("section-comp") != -1) {
                      let comp_html = $(`<div class="comp-head">
                                                <div class="row">
                                                    <div class="col-md-3 comp-settings"><ul></ul></div>
                                                    <div class="col-md-6 comp-title">${__(
                                                      $(component).attr(
                                                        "data-component"
                                                      )
                                                    )}</div>
                                                    <div class="col-md-3"></div>
                                                </div>
                                                <div class="comp-layout">
                                                    <div class="${
                                                      component.className
                                                    }"></div>
                                                </div>
                                            </div>`);
                      $(col_html).append(comp_html);
                      let comp_settings = $(comp_html).find(".comp-settings");
                      let cls = `.sec-row${i + 1}-col${j + 1}`;
                      let component_cls = `.sr${i + 1}c${j + 1}-com${k + 1}`;
                      me.make_settings(
                        comp_settings,
                        ["Settings", "Copy", "Delete"],
                        "Component",
                        "#{{section}} " + cls + " " + component_cls,
                        i + 1,
                        j + 1,
                        component_cls
                      );
                    }
                  }
                }
                let new_comp = $(`<div class="new-comp">
                                    <a class="add-comp"><span class="fa fa-plus"></span></a>
                                </div>`);
                new_comp.find("a").click(() => {
                  me.add_new_component(col_node.className, i, j);
                });
                $(col_html).append(new_comp);
              }
              $(row_html).append(col_html);
            }
          }
          $(node_html).find(".row-layout").append(row_html);
          let row_settings = $(node_html).find(".row-settings");
          me.make_settings(
            row_settings,
            ["Settings", "Copy", "Delete"],
            "Row",
            "#{{section}} .section-row",
            i + 1
          );
        }
        $(me.wrapper).find(".section-row-layout").append(node_html);
      }
    }
    let html = $(`<div class="row">
            <div class="col-md-12">
                <div class="new-row-div"><a class="add-row"><span class="fa fa-plus"></span></a></div>
            </div>
        </div>`);
    $(this.wrapper).find(".section-row-layout").append(html);
    html.find("a").click(() => {
      me.layout_dialog(1);
    });
  },
  layout_dialog: function (row_count) {
    let me = this;
    this.layout = new frappe.ui.Dialog({
      title: __("Choose Layout"),
      fields: [{ fieldname: "layout_section", fieldtype: "HTML" }],
    });
    let layout_wrapper =
      this.layout.fields_dict.layout_section.$wrapper.empty();
    $(`<div class="row layoutsdiv"></div>
        <style>
            .layoutsdiv .row{
                margin-top: 5px;
                margin-right: -5px;
                margin-left: -5px;
                border: 1px solid #fff;
            }
            .layoutsdiv .col-div div{
                min-height: 15px;
                background: #ddd;
                border-radius: 5px;
            }
            .layoutsdiv .col-div{
                padding-left: 5px;
                padding-right: 5px;
            }
            .layoutsdiv .selectedDiv .col-div div{
                background: #63c463;
            }
        </style>`).appendTo(layout_wrapper);
    let selected_layout;
    this.layouts.map((f) => {
      let html = $(
        `<div class="col-md-6" style="float:left;"><div class="row"></div></div>`
      );
      let cols = f.web_layout.split("x");
      $(cols).each(function (k, v) {
        $(html)
          .find(".row")
          .append(`<div class="col-div col-md-${v.trim()}"><div></div></div>`);
      });
      $(layout_wrapper).find(".layoutsdiv").append(html);
      html.click(() => {
        $(layout_wrapper).find(".selectedDiv").removeClass("selectedDiv");
        $(html).find(".row").addClass("selectedDiv");
        selected_layout = f;
      });
    });
    this.layout.set_primary_action(__("Save"), function () {
      if (selected_layout) {
        let new_row = $(
          `<div><div class="row section-row sec-row${row_count}"></div></div>`
        );
        let cols = selected_layout.web_layout.split("x");
        $(cols).each(function (k, v) {
          let div = `<div class="col-md-${v.trim()} section-col sec-row${row_count}-col${
            k + 1
          }"></div>`;
          $(new_row).find(".row").append(div);
        });
        let innerHTML = $(me.section_template)[0].innerHTML;
        innerHTML += $(new_row)[0].innerHTML;
        $(me.section_template)[0].innerHTML = innerHTML;
        $(me.wrapper)
          .find(".section-row-layout")
          .find(".new-row-div")
          .parent()
          .parent()
          .remove();
        me.save_template();
        me.make_row();
        me.layout.hide();
      } else {
        frappe.msgprint("Please select any layout");
      }
    });
    this.layout.show();
  },
  save_template: function () {
    if (this.from_form) {
      let new_div = document.createElement("div");
      $(new_div).append(this.section_template);
      $(new_div).append(this.style_template);
      this.frm.set_value(this.field_name, $(new_div)[0].innerHTML);
    }
  },
  add_new_component: function (class_name, row_count, column_count) {
    let me = this;
    this.components_dialog = new frappe.ui.Dialog({
      title: __("Add Component"),
      fields: [{ fieldname: "component_html", fieldtype: "HTML" }],
    });

    let component_wrapper =
      this.components_dialog.fields_dict.component_html.$wrapper.empty();
    $(`<div class="row component-div"></div>`).appendTo(component_wrapper);
    let selected_component;
    this.components.map((f) => {
      let items = $(`<div class="col-md-6" style="float:left;">
                <div class="comp-title">${f.name}</div>
            </div>
            <style>
                .component-div .comp-title{
                    text-align: center;
                    padding: 10px 15px;
                    background: #ddd;
                    border: 1px solid #ddd;
                    margin-bottom: 10px;
                }
                .component-div .active{
                    background: #63c463;
                }
            </style>`);
      items.find(".comp-title").click(() => {
        selected_component = f;
        component_wrapper.find(".active").removeClass("active");
        items.find(".comp-title").addClass("active");
      });
      component_wrapper.find(".row").append(items);
    });

    this.components_dialog.set_primary_action(__("Add"), function () {
      if (selected_component) {
        let cls_list = class_name.split(" ");
        let new_cls_name = "";
        $(cls_list).each(function (k, v) {
          new_cls_name += "." + v;
        });
        me.update_component(
          selected_component,
          row_count,
          column_count,
          new_cls_name
        );
        me.save_template();
        me.make_row();
        me.components_dialog.hide();
      } else {
        frappe.msgprint(__("Please select any one component"));
      }
    });

    this.components_dialog.show();
  },
  create_style_elements: function (styles_list) {
    let me = this;
    $(styles_list).each(function (k, v) {
      if (v && v.trim() != "") {
        me.style_template.appendChild(
          document.createTextNode("#{{section}}" + v)
        );
      }
    });
  },
  copy_element: function (
    wrapper,
    type,
    selector,
    row_count,
    column_count,
    component_class
  ) {
    let me = this;
    let cls = selector.split("#{{section}} ")[1];
    if (type == "Component") {
      let component_name = this.section_template
        .find(cls)
        .find("." + component_class)
        .attr("data-component");
      let component = this.components.find((obj) => obj.name == component_name);
      if (component) {
        me.update_component(component, row_count, column_count, cls);
        me.save_template();
        me.make_row();
      }
    } else if (type == "Row") {
      let row_html = this.section_template.find(cls);
      let row_length = $(this.section_template).children().length + 1;
      let new_row = $(
        `<div class="row section-row sec-row${row_length}"></div>`
      );
      let child_nodes = $(this.section_template).children();
      let node = $(row_html)[0];
      if ($(node)[0].children.length > 0) {
        for (var j = 0; j < $(node)[0].children.length; j++) {
          let col_html = "";
          let cls = "";
          let col_node = $(node)[0].children[j];
          $($(node)[0].children[j].classList).each(function (a, b) {
            if (b.startsWith("sec-row")) {
              cls += "sec-row" + row_length + "-col" + (j + 1);
            } else {
              cls += b + " ";
            }
          });
          col_html = $(`<div class="${cls}"></div>`);
          if ($(col_node)[0].children.length > 0) {
            for (var k = 0; k < $(col_node)[0].children.length; k++) {
              let component_name = $($(col_node)[0].children[k]).attr(
                "data-component"
              );
              let component = me.components.find(
                (obj) => obj.name == component_name
              );
              let html = me.update_component(
                component,
                row_length,
                j + 1,
                `.sec-row${row_length}-col${j + 1}`,
                true
              );
              col_html.append(html);
            }
          }
          new_row.append(col_html);
        }
      }
      $(this.section_template).append(new_row);
      this.save_template();
      this.make_row();
    }
  },
  delete_element: function (
    wrapper,
    type,
    selector,
    row_count,
    column_count,
    component_class
  ) {
    let me = this;
    let cls = selector.split("#{{section}} ")[1];
    if (type == "Component") {
      me.delete_component(cls, component_class);
      me.save_template();
      me.make_row();
    } else if ("Row") {
      let row_html = this.section_template.find(".sec-row" + row_count);
      $(row_html)
        .find(".section-comp")
        .each(function () {
          let parent_cls = $(this).parent()[0].classList;
          let p_cls = null;
          for (var i = 0; i < parent_cls.length; i++) {
            if (parent_cls[i].startsWith("sec-row")) {
              p_cls = parent_cls[i];
            }
          }
          if (p_cls) {
            let comp_cls = $(this)[0].classList;
            let c_cls = null;
            for (var j = 0; j < comp_cls.length; j++) {
              if (comp_cls[j].startsWith("sr")) {
                c_cls = comp_cls[j];
              }
            }
            if (c_cls) {
              me.delete_component(p_cls, c_cls);
            }
          }
        });
    }
  },
  update_component: function (
    component,
    row_count,
    column_count,
    cls,
    return_html = false
  ) {
    let me = this;
    let html = component.html;
    let component_length =
      $(me.section_template).find(cls).find(".section-comp").length + 1;
    if (component.content.length > 0) {
      if (this.from_form) {
        $(component.content).each(function (k, v) {
          let child_row = frappe.model.add_child(
            me.frm.doc,
            "Section Content",
            "content",
            me.frm.doc.content.length + 1
          );
          child_row.content_type = v.content_type;
          child_row.field_type = v.field_type;
          child_row.fields_json = v.fields_json;
          child_row.field_label = v.field_label;
          let field_key = `row${row_count}_col${column_count}_c${component_length}_${v.field_key}`;
          child_row.field_key = field_key;
          html =
            html.split(`{{${v.field_key}}}`)[0] +
            `{{${child_row.field_key}}}` +
            html.split(`{{${v.field_key}}}`)[1];
        });
        me.frm.refresh_field("content");
      }
    }
    let comp_cls = `sr${row_count}c${column_count}-com${component_length}`;
    let component_html = $(
      `<div class="section-comp ${comp_cls}" data-component="${component.name}">${html}</div>`
    );
    if (return_html == true) return component_html;
    $(me.section_template).find(cls).append(component_html);
  },
  delete_component: function (cls, component_class) {
    let component_name = this.section_template
      .find(cls)
      .find("." + component_class)
      .attr("data-component");
    let component = this.components.find((obj) => obj.name == component_name);
    if (!cls.startsWith(".")) cls = "." + cls;
    let html = this.section_template
      .find(cls)
      .find("." + component_class)
      .html();
    let lsplit = html.split("{{");
    let names = [];
    $(lsplit).each(function (k, v) {
      if (v.indexOf("}}") != -1) {
        let key = v.split("}}")[0];
        let check_content = me.frm.doc.content.find(
          (obj) => obj.field_key == key
        );
        if (check_content) {
          names.push(check_content.name);
        }
      }
    });
    if (names.length > 0) {
      let new_list = [];
      $(this.frm.doc.content).each(function (k, v) {
        if (!has_common(names, [v.name])) {
          v.idx = new_list.length + 1;
          new_list.push(v);
        }
      });
      this.frm.doc.content = new_list;
      this.frm.refresh_field("content");
    }
    this.section_template
      .find(cls)
      .find("." + component_class)
      .remove();
  },
});
