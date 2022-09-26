frappe.ui.form.on('Field Types Property', {
    field_type: function (frm, cdt, cdn) {
        let item = locals[cdt][cdn];
        if (item.field_type == 'List') {
            setTimeout(() => {
                let wrapper = frm.fields_dict[item.parentfield].grid.grid_rows_by_docname[cdn].grid_form.fields_dict['fields_json'].wrapper;
                fields_json(item, wrapper);
            }, 500);
        }
    },
         //created by boopathy-30/06/2022

    choose_style_properties:function(frm, cdt, cdn){
        console.log(frm, cdt, cdn,"frm, cdt, cdn")
        frappe.call({
            method:"go1_cms.go1_cms.doctype.section_template.section_template.get_css_fields",
            args:{},
            callback:function(r){
                console.log(r.message,"r.message")
                let dialog = new frappe.ui.Dialog({
                    title: __("Choose Properties"),
                    fields: [{ 'fieldname': 'css_fields_html', 'fieldtype': 'HTML' }]
                });
                dialog.set_primary_action(__("Update"), function () {
                    let selected_fields = [];
                    $(wrapper).find('.fields-list input[type="checkbox"]:checked').each(function () {
                        let obj = r.message.find(o => o.fieldname === $(this).val());
                        selected_fields.push(obj)
                    });
                    console.log(cur_frm.doc.name,"cur_frm.doc.name")
                    console.log(JSON.stringify(selected_fields),"JSON.stringify(selected_fields)")
                    // frm.set_value('css_properties_list', JSON.stringify(selected_fields));
                    frappe.model.set_value(cdt,cdn,'css_properties_list',JSON.stringify(selected_fields))
                    dialog.hide();
                    frm.save()
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
                r.message.map((f,index) => {
                    console.log(index,"---f----")
                    
                    if (!has_common([f.fieldtype], ['Column Break', 'Section Break'])) {
                    let checked = "";
                    let obj = existing_fields.find(o => o.fieldname ===f.fieldname);
                    if (obj)
                        checked = 'checked="checked"';
                        let css_html = $(`<div class="col-md-6" style="float:left">
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
                        $(wrapper).find('.fields-list').append(css_html);
                    }
                })
            dialog.show()
            }

        })

    },

    
    




    //end by boopathy



})