// Copyright (c) 2019, Tridots Tech and contributors
// For license information, please see license.txt
frappe.require("assets/go1_cms/js/jquery.ui.min.js");
frappe.require("assets/go1_cms/js/uppy.min.css");
frappe.require("assets/go1_cms/js/uppy.min.js");
frappe.require("assets/go1_cms/css/jodit.min.css");
frappe.require("assets/go1_cms/js/jodit.min.js");
frappe.require("assets/go1_cms/js/jquery.slimscroll.min.js");
frappe.require("/assets/go1_cms/js/proposal.js");
var is_row_updated = 0;
frappe.ui.form.on('Proposal', {
    refresh: function(frm) {
        if(frm.doc.document){
           frm.set_query("data_fetch_from", function() {
            return {
                "query":"go1_cms.go1_cms.doctype.proposal.proposal.get_linked_docs",
                "filters": {
                     "document": frm.doc.document
                }
            };
            });
           frappe.call({
                method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_side_menu_fields',
                args: {
                    dt: frm.doc.data_fetch_from,
                },
                freeze: true,
                callback: function(r) {
                    var opts = []
                    for (var i = 0; i < r.message.length; i++) {
                        opts.push(r.message[i].fieldname);
                    }
                     frm.set_df_property('side_menu_display_field', 'options', opts);
                     frm.refresh_field('side_menu_display_field');
                }
          });
        }
        if (frm.doc.__islocal) {
            frappe.db.get_list('Page Template', {
                }).then(res => {
                if(res.length>0 && (frm.doc.page_type=="Responsive"  || frm.doc.page_type=="Adaptive")){
                    frm.add_custom_button(__('Pick From Template'), function () {
                        new add_page_template({
                            frm: frm,
                        });

                        
                    });
                    
                    $('button[data-label="Pick%20From%20Template"]').attr("class","btn btn-xs btn-default");
                   $('button[data-label="Pick%20From%20Template"]').html("<i class='fa fa-check' style='margin-right:5px'></i> Pick From Template");
                }
            });
        }
        if (!frm.__islocal) {

            frm.trigger('web_section_html');
            if (frm.doc.page_type == 'Adaptive') {
                frm.trigger('mobile_section_html');
            }
            if(is_row_updated==1)
            {
            $('[data-label="Reload"]').parent().click();
            is_row_updated=0;
            }
            if(frm.doc.page_type == "List" && frm.doc.list_style_image!=undefined){
                 $("#list_style_image").remove();
                 var img_html = '<img src="'+frm.doc.list_style_image+'" style="margin-top: 10px;"/>';
                 $('button[data-fieldname="choose_list_style"]').parent().append(img_html);
            }
        }
        if (!frm.__islocal && frm.doc.published==1) {

            // frm.add_custom_button(__('Preview'), function () {
            //     window.open(
            //       'https://go1-cms.web.app/p/'+frm.doc.route,
            //       '_blank' // <- This is what makes it open in a new window.
            //     );

            // });
            // $('button[data-label="Preview"]').attr("class","btn btn-xs btn-default");
            // $('button[data-label="Preview"]').html("<i class='fa fa-eye' style='margin-right:5px'></i> Preview");
            frm.add_custom_button(__('Preview'), function () {
                     window.open(
                  window.location.origin +"/"+frm.doc.route,
                  '_blank' 
                );
            })
            // by gopi on 20/10/22
            frm.add_custom_button(__('Send Document'), function () {

                if (frm.doc.preview_pdf_url && frm.doc.quotation) {
                    let attachments;
                    let recipients;

                    frappe.call({
                        method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_attachement_email_id',
                        args: {
                            file_url: frm.doc.preview_pdf_url,
                            quotation_id: frm.doc.quotation
                        },
                        freeze: true,
                        callback: function (r) {
                            var msg = "Dear {{customer}}<br><br>Please find our attached proposal.<br><br>This proposal is valid until: {{valid_till}}<br>"
                             msg += 'You can view the proposal on the following link: <a href="{{route}}"></a><br><br>Please '
                             msg += "don't hesitate to comment online if you have any questions.<br><br>We look forward to your communication.<br><br>Kind Regards,<br>{{company}}<br>";
                            frappe.call({
                                method: 'frappe.client.get_value',
                                args: {
                                    'doctype': 'Quotation',
                                    'filters': { 'name': frm.doc.quotation },
                                    'fieldname': ['party_name', 'valid_till','company']
                                },
                                async: false,
                                callback: function(data) {
                                    if (data.message) {
                                       
                                        msg = frappe.render_template(msg, { "customer": data.message.customer,"valid_till": data.message.valid_till, "company": data.message.company,"route":frm.doc.route})
                                        console.log(msg)
                                    }
                                }
                            })
                            console.log("----------------------")
                           
                            // console.log(r,"data")
                            if(r.attachement){
                                attachments = r.attachement
                            }
                            if (r.email){
                                recipients = r.email+','
                            }
                            if (!r.email){
                                show_alert('There is no email id found , Please select or type <b>To</b> email from the dialog', 5);
                            }
                            console.log(msg)
                            class email extends frappe.views.CommunicationComposer { }
                            new email({
                                frm: frm,
                                attachments: attachments,
                                recipients: recipients,
                                subject:frm.doc.name,
                                message: msg
                            })
                        }
                    })
                }
                else {
                    if(!frm.doc.preview_pdf_url){
                        frappe.msgprint("There is no proposal pdf file to share..!")
                    }
                    if(!frm.doc.quotation){
                        frappe.msgprint("There is no quotation is selected to share..!")
                    }
                }

            });
            // end

        frm.add_custom_button(__('Preview PDF'), function () {
                    window.open(
                        window.location.origin + '/api/method/go1_cms.go1_cms.doctype.proposal.proposal.generate_pdf?page='+frm.doc.name+'&&name='+frm.doc.quotation,
                        '_blank' // <- This is what makes it open in a new window.
                        );
                        
                    });

        }
        if (frm.doc.__islocal) {
            if (has_common(frappe.user_roles, ['Vendor']) && frappe.session.user != 'Administrator') {
                frm.set_value('business', frappe.boot.user.defaults.business)
            } else {
                frm.set_value('business', '')
            }
        }
        //  if (frappe.session.user != 'Administrator') {
             

        //     frm.set_df_property('header_template', 'hidden', 1)
        //     frm.set_df_property('footer_template', 'hidden', 1)
        //     frm.set_df_property('document', 'hidden', 1)
        //     // frm.set_df_property('route', 'hidden', 1)
        //     frm.set_df_property('theme', 'hidden', 1)


        //  }
         if (has_common(frappe.user_roles, ['Vendor'])){
            frm.set_df_property('business', 'hidden', 1)

         }
        let editor = Jodit.instances.jeditor_webform;
        if (editor) {
            editor.value = frm.doc.content || "";
        }
        frm.trigger("load_custom_editor");
                 let args = {
                    'dt': 'Catalog Settings',
                    'business': frm.doc.business
                };
       if(!frm.doc.__islocal && frm.doc.is_converted_to_template == 0){
           frm.add_custom_button(__('Save As Template'), function () {
               var title_dialog =   new frappe.ui.Dialog({
                            title: "Enter Your Title",
                            fields: [{ "label": __("Enter Section Title"), "fieldname": "title_name", "fieldtype": "Data" }]
                            // fields: title_fileds

                      });
                     
                     title_dialog.set_primary_action(__('Save As Template'), function() {
                         let val = title_dialog.get_values();
                          frappe.call({
                                method: 'go1_cms.go1_cms.doctype.proposal.proposal.save_as_template',
                                args: {
                                    page_id: frm.doc.name,
                                    title:val.title_name,
                                },
                                freeze: true,
                                callback: function(r) {
                                    title_dialog.hide();
                                    $(".modal-backdrop").remove();
                                    frappe.msgprint(__('Page has been saved as Template successfully'));
                                    $('button[data-label="Save%20As%20Template"]').hide();
                                    cur_frm.reload_doc();

                                }
                            });
                      });
                 title_dialog.show();
           })
           $('button[data-label="Save%20As%20Template"]').attr("class","btn btn-xs btn-default");
           $('button[data-label="Save%20As%20Template"]').html("<i class='fa fa-save' style='margin-right:5px'></i> Save As Template");
           
       }
      
               
    },

     load_custom_editor: function(frm) {
                    if (!Jodit.instances.jeditor_webpage) {
                        $(frm.get_field('jodit_editor').wrapper).empty();
                        $('<div class="clearfix"><label class="control-label" style="padding-right: 0px;">Content</label></div><textarea id="jeditor_webpage"></textarea>').appendTo(frm.fields_dict.jodit_editor.wrapper);
                        var ele = document.getElementById('jeditor_webpage');
                        //var editor = new Jodit(ele);
                       
                        var editor = new Jodit(ele, {
                            colorPickerDefaultTab: 'color',
                             colors: ['#ff0000', '#00ff00', '#0000ff'],
                             filebrowser: {
                                 isSuccess: function (resp) {
                                    //   console.log(resp)
                                        return resp.length !== 0;
                                    },
                                    getMsg: function (resp) {
                                        // console.log(resp)
                                        return resp;
                                    },
                                    ajax: {
                                        url: 'ajax.php',
                                        method: 'GET',
                                        dataType: 'text',
                                        headers: {
                                            'X-CSRF-Token': frappe.csrf_token
                                        },
                                        data: {
                                            someparameter: 1
                                        },
                                        prepareData: function (data) {
                                            data.someparameter++;
                                            //  console.log(data)
                                            return data;
                                        },
                                        process: function (resp) {
                                            // console.log(resp)
                                            return resp.split('|'); // return items list
                                        },
                                    }
                             },
                            uploader: {
                                url: window.location.origin + '/api/method/uploadfile',
                                format: 'json',
                                pathVariableName: 'path',
                                filesVariableName: 'images',
                                prepareData: function (data) {
                                    // console.log(data)
                                    return data;
                                },
                                isSuccess: function (resp) {
                                    // console.log(resp)
                                    return !resp.error;
                                },
                                getMsg: function (resp) {
                                    // console.log(resp)
                                    return resp.msg.join !== undefined ? resp.msg.join(' ') : resp.msg;
                                },
                                process: function (resp) {
                                    // console.log(resp)
                                    // console.log(this.options.uploader.filesVariableName)
                                    // console.log(resp[this.options.uploader.filesVariableName])
                                    return {
                                        files: resp[this.options.uploader.filesVariableName] || [],
                                        path: resp.path,
                                        baseurl: resp.baseurl,
                                        error: resp.error,
                                        msg: resp.msg
                                    };

                                },
                                error: function (e) {
                                    // console.log(e)
                                    this.events.fire('errorPopap', [e.getMessage(), 'error', 4000]);
                                },
                                defaultHandlerSuccess: function (data, resp) {
                                    //  console.log(resp)
                                    //   console.log(data)
                                    var i, field = this.options.uploader.filesVariableName;
                                    if (data[field] && data[field].length) {
                                        for (i = 0; i < data[field].length; i += 1) {
                                            this.selection.insertImage(data.baseurl + data[field][i]);
                                        }
                                    }
                                },
                                defaultHandlerError: function (resp) {
                                    //  console.log(resp)
                                    this.events.fire('errorPopap', [this.options.uploader.getMsg(resp)]);
                                }
                            },
                            filebrowser: {
                                ajax: {
                                    url: window.location.origin + '/api/method/uploadfile'
                                }
                            }
                        });
                        editor.setEditorValue('<p>start</p>')

                        editor.value = frm.doc.content || " ";
                        // editor.value = check_doc.field || " ";
                        ele.addEventListener('change', function() {
                             
                            frm.set_value("content", this.value);
                        });
                        $('.jodit_toolbar_btn-fullsize').hide();
                    }
                },
    choose_list_style:function(frm){
        new add_list_template({
            frm: frm,
        });
    },
    map_the_columns:function(frm){
       new columns_mapping({
            frm: frm,
        });
    },
    data_fetch_from:function(frm){
          frappe.call({
                method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_side_menu_fields',
                args: {
                    dt: frm.doc.data_fetch_from,
                },
                freeze: true,
                callback: function(r) {
                    var opts = []
                    for (var i = 0; i < r.message.length; i++) {
                        opts.push(r.message[i].fieldname);
                    }
                     frm.set_df_property('side_menu_display_field', 'options', opts);
                     frm.refresh_field('side_menu_display_field');
                }
          });
    },
    page_type:function(frm){
       frappe.db.get_list('Page Template', {
                }).then(res => {
                if(res.length>0 && (frm.doc.page_type=="Responsive"  || frm.doc.page_type=="Adaptive")){
                    frm.add_custom_button(__('Pick From Template'), function () {
                        new add_page_template({
                            frm: frm,
                        });
                    });
                    
                    $('button[data-label="Pick%20From%20Template"]').attr("class","btn btn-xs btn-default");
                   $('button[data-label="Pick%20From%20Template"]').html("<i class='fa fa-check' style='margin-right:5px'></i> Pick From Template");
                }
                else{
                    $('button[data-label="Pick%20From%20Template"]').remove();
                }
            });
    },
    web_section_html: function(frm) {
        frm.events.section_html(frm, 'web_section', 'web_section_html', 'Web');
    },
    mobile_section_html: function(frm) {
        frm.events.section_html(frm, 'mobile_section', 'mobile_section_html', 'Mobile');
    },
    section_html: function(frm, field, html, device_type) {
        let wrapper = $(frm.get_field(html).wrapper).empty();
        let table = $(`<table class="table table-bordered">
            <thead>
                <tr>
                    <th>${__("Section")}</th>
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
            frm.doc[field].map(f => {
                let section_data = '';
                if (has_common(frappe.user_roles, ['System Manager'])) {
                    section_data = `<a href="/desk#Form/Page Section/${f.section}">${f.section}</a>`;
                    if (f.section != f.section_title) {

                        if (f.custom_title!=undefined) {
                                section_data += `<br><span style="float: left;margin-left: 43px;">${f.custom_title}</span>`;

                        }
                        else{
                            if (f.section_name) {
                                section_data += `<br><span style="float: left;margin-left: 43px;">${f.section_name}</span>`;
                            } else {
                                section_data += `<br><span style="float: left;margin-left: 43px;">${f.section_title}</span>`;
                            }
                       }
                    }
                } else {
                    // section_data = `${f.section_title}`;
                     if (f.custom_title!=undefined) {
                                section_data += `<br><span style="float: left;margin-left: 43px;">${f.custom_title}</span>`;

                        }
                        else{
                        if (f.section_name) {
                            section_data += `<br><span style="float: left;margin-left: 43px;">${f.section_name}</span>`;
                        } else {
                            section_data += `<br><span style="float: left;margin-left: 43px;">${f.section_title}</span>`;
                        }
                    }
                }
                let route = '';
                if (!has_common([f.section_type], ['Slider', 'Static Section'])) {
                    route = f.route ? f.route : '';
                }
                let row = $(`<tr data-id="${f.name}">
                    <td style="width: 50%;"><img src="/assets/go1_cms/images/section-icon.svg" style="height:30px;cursor: all-scroll;position: relative;top: 8px;margin-right: 10px;"> ${section_data}</td>
                
                    <td class="btns" style="width:50%;"></td></tr>`).appendTo(table);
                // <span class="copied">Copied!</span>
                row.find('td:eq(1)').click(function(e) {
                    // let txt = $(this).attr('data-route');
                    // var $temp = $("<input>");
                    // $("body").append($temp);
                    // $temp.val(txt).select();
                    // document.execCommand('copy');
                    // $temp.remove();
                    // $(this).find('.copied').show();
                    // setTimeout(function(){
                    //     row.find('.copied').hide();
                    // }, 5000);
                });
                let allow = false;
                if (f.section_type != 'Slider')
                    allow = true;
                else {
                    let slider_link = $(`<button class="btn btn-primary btn-xs" style="margin-right: 10px;"><span class="fa fa-edit" style="margin-right:5px"></span>Edit Data</button>`);
                    $(row).find('.btns').append(slider_link);
                    slider_link.click(function() {
                        frappe.set_route('List', 'Slider')
                    })
                }
                if (allow) {
                    let modify_data = $(`<button class="btn btn-primary btn-xs" style="margin-right: 10px;"><span class="fa fa-edit" style="margin-right:5px"></span>Edit Data</button>`);
                    $(row).find('.btns').append(modify_data);
                    modify_data.click(() => {
                        new modify_section_data({
                            section: f.section,
                            content_type: 'Data'
                        })
                    });
                }
                if (device_type == 'Mobile') {
                    // let modify_design = $(`<button class="btn btn-info btn-xs" style="margin-right: 10px;"><span class="fa fa-code" style="margin-right:5px"></span>Edit Data</button>`);
                    // $(row).find('.btns').append(modify_design);
                    // modify_design.click(() => {
                    //     new modify_section_data({
                   //         section: f.section,
                    //         content_type: 'Design'
                    //     })
                    // });
                }
                if(f.allow_update_to_style==1){
                    let style_section = $(`<button class="btn btn-warning btn-xs" style="margin-right: 10px;"><span class="fa fa-code" style="margin-right:5px"></span>Edit Styles</button>`);
                    $(row).find('.btns').append(style_section);
                    style_section.click(() => {
                        frm.events.edit_styles_sections(frm, f.name, f.parentfield)
                    });
                }
                let delete_section = $(`<button class="btn btn-danger btn-xs"><span class="fa fa-trash" style="margin-right:5px"></span>Delete</button>`);

                $(row).find('.btns').append(delete_section);
                delete_section.click(() => {
                    frm.events.delete_sections(frm, f.name, f.parentfield)
                });
                
            });
        } else {
            $(table).find('tbody').append(`<tr><td colspan="2">No Records Found!</td></tr>`);
        }
        // let add_section = $(`<button class="btn btn-primary">Add Existing Section</button>`).appendTo(wrapper);
        let create_section = $(`<button class="btn btn-sm btn-primary" style="margin-bottom: 10px;">Add New Section</button>`).appendTo(wrapper);
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
                doctype: 'Mobile Page Section',
                section_type: 'new',
                frm: frm,
                device_type: device_type
            });
        });
        setTimeout(function() {
            $(cur_frm.$wrapper).find('div[data-fieldname="' + html + '"] table tbody').sortable({
                items: 'tr',
                opacity: 0.7,
                distance: 20,
                update: function(e, ui) {
                    $(cur_frm.$wrapper).find('div[data-fieldname="' + html + '"] table tbody tr').each(function(k, v) {
                        frappe.model.set_value('Mobile Page Section', $(this).attr('data-id'), 'idx', (k + 1))
                        // cur_frm.set_value("route","");
                        cur_frm.set_value("published",cur_frm.doc.published);
                        refresh_field("mobile_section");
                        refresh_field("web_section");
                        is_row_updated=1;

                    })
                }
            })
        }, 1000);
    },
    delete_sections: function(frm, name, parentfield) {
        frappe.confirm(
            'Are you sure to want to remove this section?',
            function(){
              frappe.call({
                    method: 'go1_cms.go1_cms.doctype.proposal.proposal.delete_section',
                    args: {
                        name: name,
                        parentfield: parentfield
                    },
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
            }
            
        )


        
    },
    edit_styles_sections: function(frm, name, parentfield) {
        var id=name;
        frappe.call({
                method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_section_properties',
                args: {"section_name":name},
                async: false,
                callback: function(r) {
                    if(r.message.styles){
                        var data = r.message.styles
                        var json_data = {}
                        var fonts_data = []
                        if(r.message.fonts_list){
                            for (var i = 0; i < r.message.fonts_list.length; i++) {
                                fonts_data.push(r.message.fonts_list[i].name)

                            }
                        }
                        if(r.message.css_json!=null && r.message.css_json!=undefined && r.message.css_json!=""){
                            json_data = (r.message.css_json)
                        }
                        var filelist= data
                        var fields=[];
                        var child_sections = [];
                        var units_sections = [];
                        for (var i = 0; i < filelist.length; i++) {
                            if(filelist[i].child_properties){
                                var child_properties = filelist[i].child_properties;
                                var is_collapse = 0;
                                if (filelist[i].collapse){
                                     if (filelist[i].collapse==1){
                                         is_collapse = 1
                                     }
                                }
                                fields.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb_childs', 'label': filelist[i].label, 'collapsible': is_collapse })
                                for (var k = 0; k < child_properties.length; k++) {
                                    if(k==0){
                                        child_sections.push(child_properties[k].fieldname)
                                    }
                                     for (const [key, value] of Object.entries(json_data)) {
                                        if (key==child_properties[k].fieldname){
                                            child_properties[k].default=value
                                        }
                                    }
                                     if(child_properties[k].fieldname!='font-family'){
                                         fields.push(child_properties[k])

                                    }
                                    else{
                                        fields.push({ 'fieldtype': "Select", 'fieldname': child_properties[k].fieldname, 'label':  child_properties[k].label,'default':  child_properties[k].default,'options':fonts_data})

                                    }
                                     if(k!=child_properties.length-1){
                                     // fields.push({ 'fieldtype': 'Column Break', 'fieldname': 'cb_childs'+k, 'label': '', 'collapsible': 0 })
                                     }
                                     else{
                                        fields.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb_childs_next', 'collapsible': 0 })

                                     }
                                    if(child_properties[k].allow_units){
                                        if(child_properties[k].allow_units==1){
                                            units_sections.push(child_properties[k].fieldname);
                                        }
                                    }
                                }


                            }
                            else{
                                 for (const [key, value] of Object.entries(json_data)) {
                                    if (key==filelist[i].fieldname){
                                        filelist[i].default=value
                                    }
                                }
                                 if(filelist[i].fieldname!='font-family'){
                                         fields.push(filelist[i]);

                                }
                                else{
                                    fields.push({ 'fieldtype': "Select", 'fieldname': filelist[i].fieldname, 'label':  filelist[i].label,'default':  filelist[i].default,'options':fonts_data})

                                }
                                if(filelist[i].allow_units){
                                    if(filelist[i].allow_units==1){
                                        units_sections.push(filelist[i].fieldname);
                                    }
                                }
                             }
                        }
                        var is_full_width = 0;
                         for (const [key, value] of Object.entries(json_data)) {
                                    if (key=="is_full_width"){
                                        is_full_width=value
                                    }
                         }
                       fields.push({ 'fieldtype': "Check", 'fieldname': "is_full_width", 'label':  'Is Full Width Section?','default':  is_full_width})
                       var styledialog = new frappe.ui.Dialog({
                            title: "Edit Section Style",
                            fields: fields
                        });
                       styledialog.show();
                       styledialog.$wrapper.find(".modal-dialog").attr("id",id);
                       styledialog.set_primary_action(__('Save'), function() {
                           let values = styledialog.get_values();
                           let style_json = {}
                           let is_full_width = 0
                           let css_design = "."+r.message.class_name+"{"
                           for (let k in values) {

                                if(values[k]!="" && values[k]!="0px" && values[k]!="0"){

                                    style_json[k]=values[k]
                                    if(k=="background-image"){
                                        css_design += k+":url('"+values[k]+"') !important;";
                                    }
                                     else if(k=="font-family"){
                                        let font_famil_name = r.message.fonts_list.find(o => o.name === values[k]);
                                        if(font_famil_name){
                                            css_design += k+":"+font_famil_name.font_family+" !important;";
                                        }
                                    }
                                    else if(k=="is_full_width"){
                                        is_full_width = values[k];
                                    }
                                    else{
                                        var is_allow_units = 0;
                                        if(styledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").attr("allow-units")){
                                             if(styledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").attr("allow-units")=="1"){
                                                 is_allow_units = 1;
                                             }
                                        }
                                        var units = '';
                                        if(is_allow_units==1){
                                            units = styledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").parent().find('select.unit').val();
                                        }
                                        css_design += k+":"+values[k]+units+" !important;";
                                    }
                                }
                            }
                            css_design +="}";
                            $('[data-fieldname="'+id+'"]').attr("css_design",css_design)
                            $('[data-fieldname="'+id+'"]').attr("style_json",JSON.stringify(style_json))
                             frappe.call({
                                method: 'go1_cms.go1_cms.doctype.proposal.proposal.update_section_properties',
                                args: {"is_full_width":is_full_width,"section_name":name,"css_design":css_design,"style_json":style_json},
                                async: false,
                                callback: function(r) {
                                    cur_frm.set_value("published",cur_frm.doc.published);
                                    // cur_frm.set_value("route","");
                                    cur_frm.save();
                                    styledialog.hide();
                                    setTimeout(function(){
                                    $(".modal-dialog[id='"+id+"']").parent().remove();
                                    },1000);
                                }
                            });
                        });
                       styledialog.$wrapper.find('.modal-body').attr("style","max-height:calc(100vh - 100px);min-height:calc(100vh - 100px);overflow-y: auto;overflow-x: hidden;");
                       styledialog.$wrapper.find('.modal-dialog').css("max-width","700px");
                       for (var i = 0; i < child_sections.length; i++) {
                           // if(i!=child_sections.length-1){
                           styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().attr("style","margin-bottom:10px;border-top:none !important;margin-top: -20px;width: calc(100% + 40px);margin-left: -20px;padding-left: 20px;padding-right: 20px;margin-bottom: 0;position: relative;    min-height: 62px;");//modfied by boopathy
                           // styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom:0px");
                           styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom: 20px;margin-top: 0;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;    min-height: 43px;");
                           styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-body").attr("style","margin-top:60px");

                           // }
                           // styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find("h6.form-section-heading.uppercase").attr("style","font-weight: 400;color: #222 !important;text-transform: capitalize;font-size: 14px;");
                           // styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom:0px");
                           // if(i==0){
                           //     styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom:0px;margin-top:15px;");
                           // }
                          if(i==0){
                              styledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom: 20px;margin-top: 4px;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;    min-height: 43px;");
                          }
                           
                       }
                       for (var i = 0; i < units_sections.length; i++) {
                            styledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").attr("style"," box-shadow: none;flex: 0 0 60%;  border-top-right-radius: 0; border-bottom-right-radius: 0; border-right: 1px solid #ddd;");
                            styledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").attr("type","number");
                            styledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").attr("allow-units","1");
                            styledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").parent().attr("style","display: flex;position: relative;max-width: 140px;");
                            var select_html = '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
                            select_html+='<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 12px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
                            styledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").parent().append(select_html);
                       }
                   }
                }
            })

    }
});
var custom_title='';
var add_new_section = Class.extend({
    init: function(opts) {
        this.parentfield = opts.parentfield;
        this.doctype = opts.doctype;
        this.section_type = opts.section_type;
        this.frm = opts.frm;
        this.device_type = opts.device_type;

        this.make();
    },
    make: function() {
        let me = this;
        frappe.run_serially([
            () => {
                if (me.section_type == 'existing')
                    me.get_all_sections();
                else if (me.section_type == 'new')
                    me.get_section_templates()
            },
            () => {
                if ((me.section_type == 'existing' && me.sections) || (me.section_type == 'new' && me.templates))
                    me.make_dialog();
                else {
                    frappe.msgprint('No sections are available. Please create a new section.')
                }
            }
        ])
    },
    get_all_sections: function() {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_sections',
            args: {
                device_type: me.device_type
            },
            async: false,
            callback: function(r) {
                me.sections = r.message;
            }
        })
    },
    get_section_templates: function() {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_section_templates',
            args: {
                device_type: me.device_type
            },
            async: false,
            callback: function(r) {
                me.groups = r.message.template_groups;
                me.templates = r.message.templates;
            }
        })
    },
    make_dialog: function() {
        let me = this;
        let title = 'Pick a section';
        if (this.section_type == 'new')
            title = 'Choose Section Template'
        this.dialog = new frappe.ui.Dialog({
            title: __(title),
            // fields: [{ "label": __("Enter Section Title"), "fieldname": "title_name", "fieldtype": "Data" }, { "fieldname": "section_html", "fieldtype": "HTML" }]
            fields: [{"fieldname": "section_html", "fieldtype": "HTML" }]

        });
        this.selected_section = [];
        // this.dialog.set_primary_action(__('Save'), function() {
        //     if (me.section_type == 'existing') {
        //         if (me.selected_section.length > 0) {
        //             $(me.selected_section).each(function(k, v) {
        //                 let row = frappe.model.add_child(me.frm.doc, me.doctype, me.parentfield);
        //                 row.section = v.section;
        //                 row.section_type = v.section_type;
        //                 row.content_type = v.content_type;
        //             });
        //             me.frm.save();
        //             me.dialog.hide();
        //         } else {
        //             frappe.throw('Please pick any section');
        //         }
        //     } else {
        //         if (me.selected_section.length > 0) {
                   
        //             let titles = ''
        //             let val = me.dialog.get_values();
        //             if (val) {
        //                 titles = val.title_name
        //             }
        //             frappe.call({
        //                 method: 'go1_cms.go1_cms.doctype.proposal.proposal.convert_template_to_section',
        //                 args: {
        //                     'template': me.selected_section[0].template,
        //                     'business': cur_frm.doc.business,
        //                     'section_name':  custom_title
        //                 },
        //                 callback: function(r) {
        //                     if (r.message) {
        //                         let row = frappe.model.add_child(me.frm.doc, me.doctype, me.parentfield);
        //                         row.section = r.message.name;
        //                         row.section_type = r.message.section_type;
        //                         row.content_type = r.message.content_type;
        //                         row.section_name = r.message.section_name;
        //                         row.custom_title = r.message.custom_title;
        //                         row.allow_update_to_style = r.message.allow_update_to_style;
        //                         me.frm.save();
        //                         me.dialog.hide();
        //                     }
        //                 }
        //             });

        //         } else {
        //             frappe.throw('Please pick any section');
        //         }
        //     }
        // });
        this.dialog.show();
        this.section_html();
        this.dialog.$wrapper.find('.form-column.col-sm-12').css("padding","0");
        this.dialog.$wrapper.find('.form-section').attr("style","width: calc(100%);margin-left: 0px;padding-top: 0;margin-top: 0px;border-radius: 0;");
        this.dialog.$wrapper.find('[data-fieldname="section_html"]').attr("style","margin-bottom: 0;");
        this.dialog.$wrapper.find('.modal-dialog').css("width", "90%");
        this.dialog.$wrapper.find('.modal-dialog').css("max-width", "1400px");
        this.dialog.$wrapper.find('.modal-content').css("height", "600px");

    },

    section_html: function() {
        let me = this;
        let wrapper = this.dialog.fields_dict.section_html.$wrapper.empty();
        let html = $(`<div class="row" id="SectionList"></div>
            <style>
                div[data-fieldname="section_html"] #SectionList .section-title{
                    padding: 37% 2%; text-align: center; height: 225px;
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
                        min-height: 227px;
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
        if(me.groups.length>0){
           section_groups = me.groups;
           }
        let data = me.sections ? me.sections : me.templates;
        if(me.groups.length>0){
            // by gopi hide for groups 17/10/22
            //  wrapper.find('#SectionList').append("<div class='col-md-3' id='sec-left-content' style='background-color: #fff;    height: 478px;margin-left: -20px;position: absolute;left: 0;border-right: 1px solid #ddd;overflow-y: auto;overflow-x: hidden;margin-top: -15px;width: 25%;'></div>");
            //  wrapper.find('#SectionList').append("<div class='col-md-9' id='sec-right-content' style='padding-top:20px;margin-left:25%;max-height: 500px;overflow-y: scroll;'></div>");

            wrapper.find('#SectionList').append("<div class='col-md-3' id='sec-left-content' style='display:none;background-color: #fff;    height: 478px;margin-left: -20px;position: absolute;left: 0;border-right: 1px solid #ddd;overflow-y: auto;overflow-x: hidden;margin-top: -15px;width: 25%;'></div>");
            wrapper.find('#SectionList').append("<div class='col-md-12' id='sec-right-content' style='padding-top:20px;max-height: 500px;overflow-y: scroll;'></div>");
            
            // end

             var group_html = "<span style='background: #f3f3f3;float: left;width: calc(100% + 32px);margin-left: -18px;padding: 10px 15px;font-size: 15px;font-weight: bold;border-bottom: 1px solid #ddd;'>Filter By Section Group</span>";
             group_html+="<ul style='float: left;width: 100%;padding: 0;margin: 0;'><li style='list-style:none;float: left;width: calc(100% + 33px);border-bottom: 1px solid #ddd;margin-left: -18px;' class='active'><a class='group-link' id='dtgroupAll' style='float: left;width: 100%;text-decoration: none;padding: 10px 15px;' onclick=filter_section('All')>All</a></li>";
            //  by gopi for adding layout sections 10/9/22
                // group_html+='<li style="list-style:none;float: left;width: calc(100% + 33px);border-bottom: 1px solid #ddd;margin-left: -18px;"><a class="group-link" style="float: left;width: 100%;text-decoration: none;padding: 10px 15px;"';
                // group_html+='data-group="layout-section" id="dtgroup-layout" onclick=filter_layout_section($(this))>Layouts<i class="fa fa-chevron-right" style="float: right;padding-top: 2px;font-size: 13px;color: #9e9e9e;font-weight: normal;"></i></a></li>';
            // end 10/9/22
             for (var i = 0; i < me.groups.length; i++) {
                 group_html+='<li style="list-style:none;float: left;width: calc(100% + 33px);border-bottom: 1px solid #ddd;margin-left: -18px;"><a class="group-link" style="float: left;width: 100%;text-decoration: none;padding: 10px 15px;"';
                 group_html+='data-group="'+me.groups[i].group_name+'" id="dtgroup'+i+'" onclick=filter_section('+i+')>'+me.groups[i].group_name+' <i class="fa fa-chevron-right" style="float: right;padding-top: 2px;font-size: 13px;color: #9e9e9e;font-weight: normal;"></i></a></li>';
             }
             group_html+="</ul>";
             wrapper.find('#SectionList').find("#sec-left-content").append(group_html);
        }

        else{
            wrapper.find('#SectionList').append("<div class='col-md-12' id='sec-right-content' style='padding-top:20px;max-height: 500px;overflow-y: scroll;'></div>");
        }


        //  by gopi for adding layout sections 10/9/22
            // bind_layout_data(wrapper)
         // end 10/9/22


        data.map(f => {
            var bg_color = "style='background: #f3f3f3;'";
            let template = `<div class="section-title" data-group='${f.section_group}'>${f.name}</div>`;
            if (f.image) {
                template = `<div class="section-img" ><img src="${f.image}" /></div><p>${f.name}</p>`
                bg_color = "";
            }
            let item = $(`<div class="col-md-3 col-sm-6 col-xs-6" style="float:left" data-group='${f.section_group}'>
                    <div class="section-item" ${bg_color}>${template}</div>
                </div>`);
            wrapper.find('#SectionList').find("#sec-right-content").append(item)
            item.click(function() {
                if (me.section_type == 'existing') {
                    let check = me.selected_section.find(obj => obj.section == f.name);
                    if (check) {
                        me.selected_section = me.selected_section.filter(obj => obj.section != f.name);
                        $(item).find('.section-item').removeClass('active');
                    } else {
                        me.selected_section.push({ 'section': f.name, 'section_type': f.section_type, 'content_type': f.content_type });
                        $(item).find('.section-item').addClass('active');
                    }
                } else {
                    me.selected_section = [{ 'template': f.name }]
                    $(html).find('.section-item').removeClass('active');
                    $(item).find('.section-item').addClass('active');
                    var title_fileds = [];
                    title_fileds.push({"fieldname": "custom_title", "fieldtype": "Data","label": __("Enter Section Title"),"default":f.name })
                    var image_html="";
                    if(f.image){
                         image_html = "<label class='control-label' style='padding-right: 0px;'>Section Preview</label><img src='"+f.image+"' style='border: 1px solid #ddd;padding: 5px;border-radius: 5px;' />";
                        title_fileds.push({"fieldname": "section_image", "fieldtype": "HTML","label": __("Section Privew") })
                    }
                    var title_dialog =   new frappe.ui.Dialog({
                            title: "Enter Custom Title",
                            // fields: [{ "label": __("Enter Section Title"), "fieldname": "title_name", "fieldtype": "Data" }, { "fieldname": "section_html", "fieldtype": "HTML" }]
                            fields: title_fileds

                      });
                     
                     title_dialog.set_primary_action(__('Add Section'), function() {
                          let val = title_dialog.get_values();
                            if (val) {
                                custom_title = val.custom_title
                            }
                             if (me.selected_section.length > 0) {
                   
                    let titles = ''
                    let val = me.dialog.get_values();
                    if (val) {
                        titles = val.title_name
                    }

                    frappe.call({
                        method: 'go1_cms.go1_cms.doctype.proposal.proposal.convert_template_to_section',
                        args: {
                            'template': me.selected_section[0].template,
                            'business': cur_frm.doc.business,
                            'section_name':  custom_title
                        },
                        callback: function(r) {
                            if (r.message) {
                                let row = frappe.model.add_child(me.frm.doc, me.doctype, me.parentfield);
                                row.section = r.message.name;
                                row.section_type = r.message.section_type;
                                row.content_type = r.message.content_type;
                                row.section_name = r.message.section_name;
                                row.custom_title = r.message.custom_title;
                                row.allow_update_to_style = r.message.allow_update_to_style;
                                me.frm.save();
                                // me.dialog.hide();
                                title_dialog.hide();  
                            }
                        }
                    });

                } else {
                    frappe.throw('Please pick any section');
                }
                          
                     });
                    title_dialog.show();
                    title_dialog.$wrapper.find('.modal-dialog').css("max-width", "650px");
                    if(image_html){
                    title_dialog.fields_dict.section_image.$wrapper.html(image_html);

                    }
                }
            })
        })
         
        // wrapper.find('#SectionList').slimScroll({
        //     height: 540
        // })
    }
});
// by gopi 10/9/22
function bind_layout_data(wrapper){
    frappe.call({
        method: "go1_cms.go1_cms.doctype.section_template_layout.section_template_layout.get_layout_data",
        args: {},
        freeze: true,
        callback: function (r) {
            // console.log(">> layout api response <<",r)
            if(r && r.message && r.message.length > 0){
                bind_layout_data(r.message)
            }
        },
    });
    let seleted_layout_id = ""
    let r___id =Math.floor(Math.random() * 1000)
    function bind_layout_data(layout_data){
			layout_data.map(each_p =>{
			    let	p_add_html = `<div class="each-palette-div" style="position:relative;">
			<label style="cursor:pointer;width:100%;" value="${each_p.unique_id}">
				<div style="height:228px;margin:auto;
					background-image: url(${each_p.preview_image ? "'" + each_p.preview_image.replace(" ",'%20') + "'" : '/files/no-img.jpg'});
					border-radius: 3%;
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
				<input type="radio"  value="${each_p.unique_id}" name="theme_radio" style="position:absolute;top:6px;right:0px;z-index:99;" ${each_p.unique_id == seleted_layout_id}?"checked":"">
			</label></div>`
			
            let p_html =`<div class="palette-main-div" id=${r___id}>
							<div class="palatte-sub-div" style="">
								${p_add_html}
							</div>
						</div>`
        
                let item = $(`<div class="col-md-4 col-sm-6 col-xs-6" style="float:left" data-group='layout-section'>
                            ${p_html}
                    </div>`);
                wrapper.find('#SectionList').find("#sec-right-content").append(item)
                item.click(() =>{
                    // console.log(">> layout click working <<")
                })
			})
    }
}
// end 10/9/22
let reference_name_val;
let no_of_records_val;
let is_dynamic_data_val;
var modify_section_data = Class.extend({
    init: function(opts) {
        this.section = opts.section;
        this.content_type = opts.content_type;
        this.list_section_data = this.random_lists = this.predefined_lists = this.collection_lists = this.patterns = [];

        this.make();
    },
    make: function() {
        let me = this;
        frappe.run_serially([
            () => {
                if (me.content_type == 'Data') {
                    me.get_data_fields();
                } else {
                    me.patterns = me.get_patterns();
                }
            },
            () => {
                me.make_dialog();
            }
        ])
    },
    get_data_fields: function() {
        let me = this;
         // console.log(me,"me----")
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_section_content',
            args: {
                section: me.section,
                content_type: me.content_type
            },
            async: false,
            callback: function(r) {
                if (r.message) {
                    me.fields = r.message;
                    var fonts_data = []
                    if(me.fields.fonts_list){
                        for (var i = 0; i < me.fields.fonts_list.length; i++) {
                            fonts_data.push(me.fields.fonts_list[i].name)

                        }
                    }
                    me.fields.fonts_data = fonts_data;
                }
            }
        })
    },
    get_patterns: function() {
        let patterns = []
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_patterns_list',
            args: {},
            async: false,
            callback: function(r) {
                if (r.message) {
                    patterns = r.message;
                }
            }
        });
        return patterns;
    },
    make_dialog: function() {
        let me = this;
        let title = 'Section Data';
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                'doctype': "Page Section",
                'filters': {
                    'name': me.section
                },
                'fieldname': ['section_name', 'section_title']
            },
            async: false,
            callback: function(r) {
                if (r.message) {
                    let value;
                    if (r.message.section_name)
                        title = r.message.section_name
                    else if (r.message.section_title)
                        title = r.message.section_title
                }
            }
        })
        let fields = [];
        // console.log(this.content_type)
        if (this.content_type == 'Data')
            fields = this.get_fields_list();
        else
            fields = [{ "fieldname": "pattern_html", "fieldtype": "HTML" }];
        if (this.content_type == 'Data' && fields.length == 0)
            frappe.throw('There is no editable part available for this section.')
        this.dialog = new frappe.ui.Dialog({
            title: __(title),
            fields: fields
        });

        this.dialog.set_primary_action(__('Save'), function() {
            if (me.content_type == 'Data')

                me.save_data();
            else
                me.update_design();
        });
        // let css_html = this.dialog.fields_dict.css_setting_html.$wrapper.empty();
        // $(`<p>hi</p>`).appendTo(css_html)

        this.dialog.show();
        // this.dialog.$wrapper.find('input[data-fieldtype="Data"],input[data-fieldtype="Link"],input[data-fieldtype="Select"],input[data-fieldtype="Int"]').css("max-width", "330px");
        this.dialog.$wrapper.find('.modal-dialog').css("width", "1000px");
        this.dialog.$wrapper.find('.modal-dialog').css("max-width", "750px");
        this.dialog.$wrapper.find('.ace-tomorrow').css("max-height", "200px");

        this.dialog.$wrapper.find('.modal-body').attr("style","max-height:calc(100vh - 100px);overflow-y: auto;overflow-x: hidden;");
      
       
        for (var value of this.fields.content) {
            if(value['allow_update_to_style']==1){
                
                // console.log(this.dialog.$wrapper.find('[data-fieldname="'+value.name+'"]').find(".control-label").text())
                // if(value['css_properties_list'].length>0){
                   var label = value.field_label;
                   if(value.image_dimension!="" && value.image_dimension!=undefined && value.image_dimension!=null){
                       label = value.field_label+" ("+value.image_dimension+")";
                   }
                    this.dialog.$wrapper.find('[data-fieldname="'+value.name+'"]').find(".control-label").html(label+"<a style='margin-left: 10px;background: #fff;padding: 2px 7px;text-transform: capitalize;color: #308fdb;font-size: 12px;border: 1px solid #308fdb;border-radius: 3px;font-weight: 600;' onclick=show_element_style('"+value.name+"')><i class='fa fa-cog' style='margin-right:5px'></i>Edit Styles</a>")
                  if(value.field_type=="Border"){
                      
                      // this.dialog.$wrapper.find('.frappe-control[data-fieldname="'+value.name+'"]').attr("style","margin-bottom:-15px");
                      this.dialog.$wrapper.find('[data-fieldname="'+value.name+'"]').find(".control-input").attr("style","display:none");
                    // this.dialog.$wrapper.find('[data-fieldname="'+value.name+'"]').find(".control-label").attr("style"," padding-right: 0px;font-weight: bold;color: #666666 !important;text-transform: uppercase;");


                  }
     
            }
        }

        if (this.content_type != 'Design'){
            this.check_image_field();
            this.check_fieldtype_lists();
            this.check_fieldtype_button();
        }
        if (this.fields && this.fields.section_type == 'Custom Section') {
            // console.log(this.fields)
            if(this.fields.reference_document !="Blog Category"){
                if (this.fields.fetch_product == 1) {
                    this.dialog.fields_dict.reference_name.$wrapper.removeClass('hide-control');
                } else {
                    this.dialog.fields_dict.reference_name.$wrapper.addClass('hide-control');
                }
                this.dialog.fields_dict.fetch_product.input.onchange = function() {
                    if (me.dialog.fields_dict.fetch_product.input.checked) {
                        me.dialog.fields_dict.reference_name.$wrapper.removeClass('hide-control');
                    } else {
                        me.dialog.fields_dict.reference_name.$wrapper.addClass('hide-control');
                    }
                }
            }else{
                me.dialog.fields_dict.reference_name.$wrapper.removeClass('hide-control');
            }
            if(this.fields.reference_document=="Product Category"){

                this.get_category_products("data");
            }
            if(this.fields.reference_document=="Blog Category"){

                this.get_blog_category("data");
            }
        }
        if (this.fields && this.fields.section_type == 'Tabs' && this.fields.reference_document != 'Custom Query') {
            this.list_fields()
            this.dialog.fields_dict.item1.onchange = function() {
                let field_name = '';
                if (me.fields.reference_document == 'Product Category') {
                    field_name = 'category_name'
                } else if (me.fields.reference_document == 'Blog Category') {
                    field_name = 'title'
                } else if (me.fields.reference_document == 'Product Brand') {
                    field_name = 'brand_name'
                } else if (me.fields.reference_document == 'Product') {
                    field_name = 'item'
                }
                frappe.call({
                    method: 'frappe.client.get_value',
                    args: {
                        'doctype': me.fields.reference_document,
                        'filters': {
                            'name': me.dialog.fields_dict.item1.value
                        },
                        'fieldname': [field_name]
                    },
                    callback: function(r) {
                        if (r.message) {
                            let value;
                            if (r.message.category_name)
                                value = r.message.category_name
                            else if (r.message.brand_name)
                                value = r.message.brand_name
                            else if (r.message.item)
                                value = r.message.item
                            if (value)
                                me.dialog.fields_dict.item_title1.set_value(value);
                        }
                    }
                })
            }

        }
        if (this.fields && this.fields.section_type == 'Predefined Section' && this.fields.predefined_section != '') {
            this.list_fields()
            this.dialog.fields_dict.preitem.onchange = function() {
                let field_name = 'name';
                if (me.fields.reference_document == 'Product') {
                    field_name = 'item'
                }
                frappe.call({
                    method: 'frappe.client.get_value',
                    args: {
                        'doctype': me.fields.reference_document,
                        'filters': {
                            'name': me.dialog.fields_dict.preitem.value,
                            'display_home_page': 0
                        },
                        'fieldname': [field_name]
                    },
                    callback: function(r) {
                        if (r.message) {
                            let value;
                            if (r.message.item)
                                value = r.message.item
                            if (value)
                                me.dialog.fields_dict.pre_title.set_value(value);
                        }
                    }
                })
            }

        }
        if (this.fields && this.fields.section_type == 'Collections') {
            this.list_fields()
            // this.dialog.fields_dict.collections.onchange = function() {
            //     this.list_fields()
            // }
        }
        
        if (this.fields && this.fields.section_type == 'Tabs' && this.fields.reference_document == 'Custom Query') {
            this.list_fields()
            this.dialog.fields_dict.tab_item.onchange = function() {
                let field_name = '';
                if (me.fields.reference_document == 'Custom Query') {
                    field_name = 'name'
                }
                frappe.call({
                    method: 'frappe.client.get_value',
                    args: {
                        'doctype': me.fields.reference_document,
                        'filters': {
                            'name': me.dialog.fields_dict.tab_item.value
                        },
                        'fieldname': [field_name]
                    },
                    callback: function(r) {
                        if (r.message) {
                            let value;
                            if (r.message.name)
                                value = r.message.name
                            if (value)
                                me.dialog.fields_dict.tab_title.set_value(value);
                        }
                    }
                })
            }

        }
        if (this.fields && this.fields.section_type == 'Lists') {
            this.list_fields()
            this.dialog.fields_dict.item.onchange = function() {
                let field_name = '';
                if (me.fields.reference_document == 'Product Category') {
                    field_name = 'category_name'
                } else if (me.fields.reference_document == 'Blog Category') {
                    field_name = 'title'
                }  else if (me.fields.reference_document == 'Product Brand') {
                    field_name = 'brand_name'
                } else if (me.fields.reference_document == 'Product') {
                    field_name = 'item'
                }
                frappe.call({
                    method: 'frappe.client.get_value',
                    args: {
                        'doctype': me.fields.reference_document,
                        'filters': {
                            'name': me.dialog.fields_dict.item.value
                        },
                        'fieldname': [field_name]
                    },
                    callback: function(r) {
                        if (r.message) {
                            let value;
                            if (r.message.category_name)
                                value = r.message.category_name
                            else if (r.message.brand_name)
                                value = r.message.brand_name
                            else if (r.message.item)
                                value = r.message.item
                            if (value)
                                me.dialog.fields_dict.item_title.set_value(value);
                        }
                    }
                })
            }
        }
        if (this.content_type == 'Design') {
            this.pattern_html();
        }
    },
    get_blog_category:function(type){
          let me = this; 
          if(type=='shuffle'){
              if(is_dynamic_data_val==0 && reference_name_val!=""){
                frappe.call({
                    method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_shuffled_blog_category',
                    args: {
                        category: reference_name_val,
                        no_of_records:no_of_records_val
                    },
                    async: false,
                    callback: function(r) {
                        // console.log(r)
                        me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').html('');
                        if(r.message){
                               let p_html = me.dialog.fields_dict.blog_category_html.$wrapper.empty();
                                
                                let btns = $(`<div>
                                         <button class="btn btn-primary">${__("Shuffle Data")}</button>
                                    </div>`).appendTo(p_html);
                                btns.find('.btn-primary').click(function() {
                                    me.get_blog_category('shuffle')
                                });
                               
                               var t_html = $(`<table class="table table-bordered"><thead><tr><th style="width:65px"></th><th style="width:200px">ID</th><th>Category Name</th></tr></thead><tbody></tbody></table>`);
                               for (var i = 0; i < r.message.length; i++) {
                                   var row='';
                                   var image_html = "";
                                   if(r.message[i].thumbnail_image!=null && r.message[i].thumbnail_image!=undefined){
                                       image_html = "<img src='"+r.message[i].thumbnail_image+"' style='height: 50px;margin-right: 10px;'/>";
                                   }
                                   row ="<tr><td><img src='/assets/go1_cms/images/section-icon.svg' style='height:30px;cursor: all-scroll;position: relative;top: 0;margin-right: 10px;text-align: center;left: 10px;'></td><td style='width:200px'>"+r.message[i].name+"</td><td>"+image_html+r.message[i].title+"</td></tr>";
                                   t_html.append(row)
                               }
                               t_html.appendTo(p_html);
                            //    console.log(me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').parent().parent().parent().parent())
                               me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').parent().parent().parent().parent().show();
                               // me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').html(p_html);
                               me.categoryblogs = r.message;
                        }
                    }
                });

            }
            else{
                 me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').html('');
                 me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').parent().parent().parent().parent().hide();
                 me.category_products = ""
            }
        }
        else{
             setTimeout(function(){
            let p_html = me.dialog.fields_dict.blog_category_html.$wrapper.empty();
            let btns = $(`<div>
                     <button class="btn btn-primary">${__("Shuffle Data")}</button>
                </div>`).appendTo(p_html);
            btns.find('.btn-primary').click(function() {
                me.get_blog_category('shuffle')
            });
           
           var t_html = $(`<table class="table table-bordered"><thead><tr><th style="width:65px"></th><th style="width:200px">ID</th><th>Category Name</th></tr></thead><tbody></tbody></table>`);
           var json_data = JSON.parse(me.fields.custom_section_data)
           for (var i = 0; i < json_data.length; i++) {
               var row='';
               var image_html = "";
               if(json_data[i].thumbnail_image!=null && json_data[i].thumbnail_image!=undefined){
                   image_html = "<img src='"+json_data[i].thumbnail_image+"' style='height: 50px;margin-right: 10px;'/>";
               }
                row ="<tr><td><img src='/assets/go1_cms/images/section-icon.svg' style='height:30px;cursor: all-scroll;position: relative;top: 0;margin-right: 10px;text-align: center;left: 10px;'></td><td style='width:200px'>"+json_data[i].name+"</td><td>"+image_html+json_data[i].title+"</td></tr>";
               t_html.append(row)
           }
           t_html.appendTo(p_html);
           me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').parent().parent().parent().parent().show();
           // me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').html(p_html);
           me.category_products = json_data;
           },1000)
        }
         setTimeout(function() {
            me.dialog.$wrapper.find('[data-fieldname="blog_category_html"]').find("tbody").sortable({
                items: 'tr',
                opacity: 0.7,
                distance: 20,
                update: function(e, ui) {
                   
                }
            })
        }, 1000);
    },
    get_category_products:function(type){

          let me = this; 
          if(type=='shuffle'){
              if(is_dynamic_data_val==0 && reference_name_val!=""){
                frappe.call({
                    method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_shuffled_category_products',
                    args: {
                        category: reference_name_val,
                        no_of_records:no_of_records_val
                    },
                    async: false,
                    callback: function(r) {
                        me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').html('');
                        if(r.message){
                               let p_html = me.dialog.fields_dict.category_products_html.$wrapper.empty();
                                
                                let btns = $(`<div>
                                         <button class="btn btn-primary">${__("Shuffle Data")}</button>
                                    </div>`).appendTo(p_html);
                                btns.find('.btn-primary').click(function() {
                                    me.get_category_products('shuffle')
                                });
                               
                               var t_html = $(`<table class="table table-bordered"><thead><tr><th style="width:65px"></th><th style="width:200px">ID</th><th>Item Name</th></tr></thead><tbody></tbody></table>`);
                               for (var i = 0; i < r.message.length; i++) {
                                   var row='';
                                   var image_html = "";
                                   if(r.message[i].product_image!=null && r.message[i].product_image!=undefined){
                                       image_html = "<img src='"+r.message[i].product_image+"' style='height: 50px;margin-right: 10px;'/>";
                                   }
                                   row ="<tr><td><img src='/assets/go1_cms/images/section-icon.svg' style='height:30px;cursor: all-scroll;position: relative;top: 0;margin-right: 10px;text-align: center;left: 10px;'></td><td style='width:200px'>"+r.message[i].name+"</td><td>"+image_html+r.message[i].item+"</td></tr>";
                                   t_html.append(row)
                               }
                               t_html.appendTo(p_html);
                               me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').parent().parent().parent().parent().show();
                               // me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').html(p_html);
                               me.category_products = r.message;
                        }
                    }
                });

            }
            else{
                 me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').html('');
                 me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').parent().parent().parent().parent().hide();
                 me.category_products = ""
            }
        }
        else{
             setTimeout(function(){
            let p_html = me.dialog.fields_dict.category_products_html.$wrapper.empty();
            let btns = $(`<div>
                     <button class="btn btn-primary">${__("Shuffle Data")}</button>
                </div>`).appendTo(p_html);
            btns.find('.btn-primary').click(function() {
                me.get_category_products('shuffle')
            });
           
           var t_html = $(`<table class="table table-bordered"><thead><tr><th style="width:65px"></th><th style="width:200px">ID</th><th>Item Name</th></tr></thead><tbody></tbody></table>`);
           var json_data = JSON.parse(me.fields.custom_section_data)
           for (var i = 0; i < json_data.length; i++) {
               var row='';
               var image_html = "";
               if(json_data[i].product_image!=null && json_data[i].product_image!=undefined){
                   image_html = "<img src='"+json_data[i].product_image+"' style='height: 50px;margin-right: 10px;'/>";
               }
                row ="<tr><td><img src='/assets/go1_cms/images/section-icon.svg' style='height:30px;cursor: all-scroll;position: relative;top: 0;margin-right: 10px;text-align: center;left: 10px;'></td><td style='width:200px'>"+json_data[i].name+"</td><td>"+image_html+json_data[i].item+"</td></tr>";
               t_html.append(row)
           }
           t_html.appendTo(p_html);
           me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').parent().parent().parent().parent().show();
           // me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').html(p_html);
           me.category_products = json_data;
           },1000)
        }
         setTimeout(function() {
            me.dialog.$wrapper.find('[data-fieldname="category_products_html"]').find("tbody").sortable({
                items: 'tr',
                opacity: 0.7,
                distance: 20,
                update: function(e, ui) {
                   
                }
            })
        }, 1000);
    },
    get_fields_list: function() {
        let me = this;
        let field_list = [];
        if (this.content_type == 'Design') {
            field_list.push({})
        }
        // if(this.fields.allow_update_to_style==1){
           
        //     if(this.fields.styles.length>1){
        //         var styles=this.fields.styles;
        //         this.child_sections=[];
        //         field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb_design', 'label': 'Section Styles', 'collapsible': 0 })
        //         for (var i = 0; i < styles.length; i++) {
        //             // console.log(me.fields.css_json,"me.fields.css_json")
        //              if(styles[i].child_properties){
        //                         var child_properties = styles[i].child_properties;
        //                          this.child_sections.push(styles[i])
        //                         field_list.push({ 'fieldtype': 'HTML', 'fieldname': styles[i].fieldname, 'label': styles[i].label, 'collapsible': 0 })
        //                         for (var k = 0; k < child_properties.length; k++) {
                                   
        //                             if(me.fields.css_json){
        //                                      for (const [key, value] of Object.entries(me.fields.css_json)) {
        //                                         if (key==child_properties[k].fieldname){
        //                                             child_properties[k].default=value
        //                                         }
        //                                     }
        //                                 }
                                   
        //                         }

        //                     }
        //             else{
        //                 if(me.fields.css_json){
        //                     for (const [key, value] of Object.entries(me.fields.css_json)) {
        //                         // console.log(key, value);
        //                         if (key==styles[i].fieldname){
        //                             styles[i].default=value
        //                         }
        //                     }
        //                 }
        //                 if(styles[i].fieldname!='font-family'){
        //                     field_list.push({ 'fieldtype': styles[i].fieldtype, 'fieldname': styles[i].fieldname, 'label':  styles[i].label,'default':  styles[i].default})
        //                 }
        //                 else{
        //                     field_list.push({ 'fieldtype': "Select", 'fieldname': styles[i].fieldname, 'label':  styles[i].label,'default':  styles[i].default,'options':this.fields.fonts_data})

        //                 }
        //             }
        //         }
        //        field_list.push({ 'fieldtype': "Check", 'fieldname': "is_full_width", 'label':  'Is Full Width Section?','default':  this.fields.is_full_width})

        //     }
        //         // field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb_design1'})

        // }
                if(this.fields.section_type == 'Predefined Section')
                    field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb_design1', 'label': 'Design', 'collapsible': 0 })
                // me.dialog.fields_dict.section_type.set_value("Static Links")
           
          if (this.fields.section_type == 'Custom Section' && this.fields.reference_document=="Blog Category") {
             reference_name_val = this.fields.reference_name ;
             no_of_records_val = this.fields.no_of_records;
             is_dynamic_data_val = this.fields.dynamic_data;

            field_list.push({
                "fieldname": "reference_name",
                "fieldtype": "Link",
                "label": __(this.fields.reference_document),
                "options": this.fields.reference_document,
                "reqd": 1,
                "default": (this.fields.reference_name || ""),
                onchange:function(){
                    reference_name_val = this.get_value();
                    if(reference_name_val){
                        me.get_blog_category('shuffle');
                    }
                }
            });
            field_list.push({
                "fieldname": "dynamic_data",
                "fieldtype": "Check",
                "label": __("Fecth Data Dynamically"),
                "default": (this.fields.dynamic_data || 0),
                "depends_on": "eval: doc.fetch_product == 1",
                onchange:function(){
                    let val = this.get_value();
                    is_dynamic_data_val = val;
                    me.get_category_products('shuffle');
                  
                }
            });
            field_list.push({
                "fieldname": "display_randomly",
                "fieldtype": "Check",
                "label": __("Display Data Randomly"),
                "default": (this.fields.display_randomly || 0),
                "depends_on": "eval: doc.dynamic_data == 1",
            });
            field_list.push({
                "fieldname": "fetch_product",
                "fieldtype": "Check",
                "default": 1,
                "label": __("Get Data From Blogs"),
               
            })
            field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'col_br' })
            field_list.push({
                "fieldname": "no_of_records",
                "fieldtype": "Int",
                "label": __("No. Of Records"),
                "options": this.fields.no_of_records,
                "reqd": 1,
                "default": (this.fields.no_of_records || "")
            });
           
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sec_category_blogs',"depends_on": "eval: doc.reference_name!='' " })
            field_list.push({
                "fieldname": "blog_category_html",
                "fieldtype": "HTML",
               // "depends_on": "eval: {{doc.dynamic_data == 0}}",
                
            });
            if (this.fields.content.length > 0) {
                field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sec_b0' })
            }
            
        }

        if (this.fields.section_type == 'Custom Section' && this.fields.reference_document!="Blog Category") {
             reference_name_val = this.fields.reference_name ;
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
                "fieldname": "no_of_records",
                "fieldtype": "Int",
                "label": __("No. Of Records"),
                "options": this.fields.no_of_records,
                "reqd": 1,
                "default": (this.fields.no_of_records || "")
            });
            field_list.push({
                "fieldname": "dynamic_data",
                "fieldtype": "Check",
                "label": __("Fecth Data Dynamically"),
                "default": (this.fields.dynamic_data || 0),
               
                onchange:function(){
                    let val = this.get_value();
                    is_dynamic_data_val = val;
                    me.get_category_products('shuffle');
                  
                }
            });
            // field_list.push({
            //     "fieldname": "display_randomly",
            //     "fieldtype": "Check",
            //     "label": __("Display Data Randomly"),
            //     "default": (this.fields.display_randomly || 0),
            //     "depends_on": "eval: doc.dynamic_data == 1",
            // });
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sec_category_products',"depends_on": "eval: doc.fetch_product == 1" })
            field_list.push({
                "fieldname": "category_products_html",
                "fieldtype": "HTML",
               // "depends_on": "eval: {{doc.dynamic_data == 0}}",
                
            });
            if (this.fields.content.length > 0) {
                field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sec_br' })
            }
            
        }
        let distinct_groups = [...new Set(this.fields.content.map(obj => obj.group_name))]
        $(distinct_groups).each(function(key, value) {
            let fields = me.fields.content.filter(obj => obj.group_name == value);
            if (distinct_groups.length > 1) {
                field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb' + key, 'label': value, 'collapsible': 1 })
                // field_list.push({ 'fieldtype': 'HTML', 'fieldname': 'css_setting_html','label': 'CSS Setting HTML'})
                
            }

        
            $(fields).each(function(k, v) {
                let field = {};
                field.fieldname = v.name;
                field.fieldtype = v.field_type;
                if (v.field_type == 'Attach') {
                    field.fieldtype = 'Attach Image';
                } else if (v.field_type == 'Text') {
                    field.fieldtype = 'Data';
                } else if (v.fieldtype == 'Small Text') {
                    field.fieldtype = 'Small Text';
                } else if(v.fieldtype == 'List') {
                    field.fieldtype = 'Code';
                    field.options = v.fields_json;
                } else if(v.field_type == 'Attach Video') {
                    field.fieldtype = 'Attach';
                } 
                else if(v.field_type == 'Button') {
                    field.fieldtype = 'Button';
                } 
                else if(v.field_type == 'Border') {
                   field.fieldtype = 'Data';
                    field.label = __(v.field_label);
                     field.default = 1;
                }
                else if(v.field_type == 'Text Editor') {
                   field.fieldtype = 'Text Editor';
                    field.label = __(v.field_label);
                }
                else if (v.field_type == 'Select') {
                    field.fieldtype = 'Select';
                    var str = v.options;
                    console.log(str)
                    var result1 = str.split(/\n/);
                    console.log(result1)
                    field.options = result1;
                } 
                else if (v.field_type == 'Check') {
                    field.fieldtype = 'Check';
                } 
                else {
                    field.fieldtype = 'HTML Editor';
                }

                if (v.content && v.content != '')
                    field.default = v.content;
                
                if(v.image_dimension!="" && v.image_dimension!=undefined){
                    field.label = __(v.field_label)+"("+v.image_dimension+")";
                }

                else{
                    field.label = __(v.field_label);
                }
                
                field_list.push(field);
                //  console.log(v,"kv")
                if(v.field_type == 'List' || v.field_type == 'Text Editor'){
                    field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb'})
                }
               //   if(v.field_type == 'Button') {
               //      field_list.push({ 'fieldtype': 'Data', 'fieldname': 'btn_text','label':"Button Text" })
               //      field_list.push({ 'fieldtype': 'Data', 'fieldname': 'btn_redirect_url','label':"Button Link" })
               //      field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'btn_clbr1' })
               //      field_list.push({ 'fieldtype': 'Data', 'fieldname': 'btn_bg_color','label':"Button Background Color" })
               //      field_list.push({ 'fieldtype': 'Data', 'fieldname': 'btn_color','label':"Button Text Color" })
               // }
                if (distinct_groups.length == 1) {
                    if (me.fields.content.length > 5) {
                        if (((k + 1) % 2) != 0) {
                            field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'cb' + k })
                        } else {
                            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb' + k })
                        }
                    }
                } else {
                    if (fields.length > 5 && ((k + 1) % 3) != 0) {
                        field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'cb' + k })
                    } else if (fields.length <= 5 && fields.length > 1 && ((k) % 2) != 0 && (k + 1) != fields.length) {
                        field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'cb' + k })
                    }
                }

              
            })
        });
        if (this.fields.section_type == 'Tabs' && this.fields.reference_document != 'Custom Query') {
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sec_br_11' });
            field_list.push({
                "fieldname": "table_html1",
                "fieldtype": "HTML"
            });
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sec_br_22' });
            field_list.push({
                "fieldtype": "Link",
                "fieldname": "item1",
                "label": __(this.fields.reference_document),
                "options": this.fields.reference_document,
                "onchange": function() {
                    let val = this.get_value();
                }
            });
            field_list.push({
                "fieldtype": "Data",
                "fieldname": "item_title1",
                "label": __("Title")
            });
            field_list.push({
                "fieldname": "no_of_records",
                "fieldtype": "Int",
                "label": __("No. Of Records"),
                "options": this.fields.no_of_records,
                "default": (this.fields.no_of_records || "")
            });
            field_list.push({ "fieldtype": "HTML", "fieldname": "save_records" });
            field_list.push({
                "fieldtype": "Data",
                "fieldname": "is_edit1",
                "hidden": 1,
                "default": "0"
            });
        }
        if (this.fields.section_type == 'Tabs' && this.fields.reference_document == 'Custom Query') {

            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'tab_sec_br_1' });
            field_list.push({
                "fieldname": "tab_table_html",
                "fieldtype": "HTML"
            });
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'tab_sec_br_2' });
            field_list.push({
                "fieldtype": "Link",
                "fieldname": "tab_item",
                "label": __(this.fields.reference_document),
                "options": this.fields.reference_document,
                "onchange": function() {
                    let val = this.get_value();
                }
            });
            field_list.push({
                "fieldtype": "Data",
                "fieldname": "tab_title",
                "label": __("Title")
            });
            field_list.push({
                "fieldname": "no_of_records",
                "fieldtype": "Int",
                "label": __("No. Of Records"),
                "options": this.fields.no_of_records,
                "default": (this.fields.no_of_records || "")
            });
            field_list.push({ "fieldtype": "HTML", "fieldname": "tab_save_record" });
            field_list.push({
                "fieldtype": "Data",
                "fieldname": "is_edit_tab",
                "hidden": 1,
                "default": "0"
            });
        }
        if (this.fields.section_type == 'Predefined Section' && !this.fields.dynamic_data && !this.fields.is_login_required) {
            // field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'predefined_sec_br_11' });
            // let data = ''
            field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'predefined_col_br_1' });
            // frappe.call({
            //     method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_featured_products',
            //     args: {},
            //     async: false,
            //     callback: function(r) {
            //         data = r.message
            //     }
            // })
            let label_name = this.fields.reference_document
            field_list.push({ "label": __("Add "+label_name), 'fieldtype': 'Section Break', 'fieldname': 'predefined_sec_br_1' });
           
            field_list.push({
                "fieldtype": "Link",
                "fieldname": "preitem",
                "label": __("Select "+label_name),
                "options": this.fields.reference_document,
                "get_query": function() { 
                    let  filtercond= 'published';
                    if (me.fields.reference_document == 'Product Category') {
                        filtercond = 'is_active'
                        return {
                        filters: {
                            is_active: 1
                        }
                    };
                    } else if (me.fields.reference_document == 'Product Brand') {
                        filtercond = 'published'
                        return {
                        filters: {
                            published: 1
                        }
                    };
                    } else if (me.fields.reference_document == 'Product') {
                        filtercond = 'is_active'
                        return {
                        filters: {
                            is_active: 1
                        }
                    };
                    }
                    
                },
                "onchange": function() {
                    let val = this.get_value();
                    let fieldname = 'name';
                    if (me.fields.reference_document == 'Product Category') {
                        fieldname = 'category_name'
                    } else if (me.fields.reference_document == 'Product Brand') {
                        fieldname = 'brand_name'
                    } else if (me.fields.reference_document == 'Product') {
                        fieldname = 'item'
                    }
                    if (val) {
                        frappe.call({
                            method: 'frappe.client.get_value',
                            args: {
                                'doctype': me.fields.reference_document,
                                'filters': {
                                    'name': val
                                },
                                'fieldname': fieldname
                            },
                            async: false,
                            callback: function(r) {
                                if (r.message) {
                                    let value;
                                    if (r.message.item)
                                        value = r.message.item
                                    if (value)
                                        me.dialog.fields_dict.pre_title.set_value(value);
                                }
                            }
                        })
                    } else {
                        me.dialog.fields_dict.pre_title.set_value("");
                    }
                }
            });
            field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'predefined_col_br_1' });
            field_list.push({
                "fieldtype": "Data",
                "fieldname": "pre_title",
                "label": __("Name"),
                "read_only": 1
            });
            field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'predefined_col_br_1' });
            field_list.push({ "fieldtype": "HTML", "fieldname": "save_prerecords" });
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'predefined_sec_br_22' });
            field_list.push({
                "fieldname": "predefined_table_html",
                "fieldtype": "HTML"
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
        if (this.fields.section_type == 'Lists') {
            field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'col_br_1' });
            field_list.push({
                "fieldname": "no_of_records",
                "fieldtype": "Int",
                "label": __("No. Of Records"),
                "options": this.fields.no_of_records,
                "reqd": 1,
                "default": (this.fields.no_of_records || "")
            });
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sec_br_1' });
            field_list.push({
                "fieldname": "table_html",
                "fieldtype": "HTML"
            });
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'sec_br_2' });
            field_list.push({
                "fieldtype": "Link",
                "fieldname": "item",
                "label": __(this.fields.reference_document),
                "options": this.fields.reference_document,
                "onchange": function() {
                    let val = this.get_value();
                }
            });
            field_list.push({
                "fieldtype": "Data",
                "fieldname": "item_title",
                "label": __("Title / Subtitle"),
                "description": "Enter title, subtitle with a pipe symbol as seperator. Eg. Top Offer | Explore Now!"
            });
            let ecommerce = frappe.get_module('Ecommerce Business Store');
            let default_val = '';
            let options = ["Upload image", "Image attached to document", "Random image from linked document", "Pick image from linked document"];
            if(!ecommerce)
                default_val = 'Image attached to document';
            let dt_options = [];
            if(this.fields.image_link_documents){
                let opts = JSON.parse(this.fields.image_link_documents);
                $(opts).each(function(a, b){
                    dt_options.push(b.document_name);
                })
            }

            field_list.push({
                "fieldtype": "Select",
                "fieldname": "image_type",
                "label": __("Image Type"),
                "options": options,
                // "options": "\nRandom images from associated products\nPick / Upload specified image",
                "default": default_val
            });
            field_list.push({
                "fieldname": "image_ref_doc",
                "fieldtype": "Select",
                "options": dt_options,
                "label": __("Reference Document"),
                "depends_on": "eval: {{doc.image_type == 'Random image from linked document' || doc.image_type =='Pick image from linked document'}}"
            });
            field_list.push({ "fieldtype": "HTML", "fieldname": "img" });
            field_list.push({ "fieldtype": "HTML", "fieldname": "save_record" });
            field_list.push({
                "fieldtype": "Data",
                "fieldname": "is_edit",
                "hidden": 1,
                "default": "0"
            });
            field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'col_br_2' });
            field_list.push({ "fieldtype": "HTML", "fieldname": "suggestions" })
        }
        if (this.fields.section_type == 'Collections') {
            field_list.push({
                "fieldtype": "Link",
                "fieldname": "collections",
                "label": __("Select Collection List"),
                "options": "Collections",
                "default": (this.fields.collections || ""),
                "onchange": function() {
                    let val = this.get_value();
                    if(val){
                        me.list_fields()
                    }
                }
            });
            field_list.push({ 'fieldtype': 'Column Break', 'fieldname': 'coll_col_br' });
            field_list.push({ 'fieldtype': 'Section Break', 'fieldname': 'coll_sec_br' });
            field_list.push({
                "fieldname": "collections_table_html",
                "fieldtype": "HTML"
            });
        }
        // console.log(field_list)
        return field_list;
    },
    pattern_html: function() {
        let me = this;
        let html = this.dialog.fields_dict.pattern_html.$wrapper.empty();
        $(`<div class="patterns row"></div><style>
            div[data-fieldname="pattern_html"] .patterns .img-list{min-height: 50px;margin-bottom: 10px;padding: 10px;border: 2px solid transparent;}
            div[data-fieldname="pattern_html"] .patterns .img-list.active{border-color: #0bc50b;}
            </style>`).appendTo(html);

        me.patterns.map(f => {
            let row = $(`<div class="col-md-3 img-list"><img src="${f.background_image}" /></div>`);
            html.find('.patterns').append(row);
            row.click(function() {
                html.find('.patterns .img-list').removeClass('active');
                row.addClass('active');
                me.selected_pattern = f;
            })
        })
    },

    save_data: function() {
        let me = this;
        let values = me.dialog.get_values();
        let style_json = {}
        let css_design='';
        // if(me.fields.allow_update_to_style==1){
        // //updated by boopathy
        //     // let style_json = {}
        //     let class_name = me.fields.class_name
        //     css_design = "."+class_name+"{"
        //     for (let k in values) {
        //         let obj = me.fields.styles.find(o => o.fieldname === k);
        //         if (obj){
        //             style_json[k]=values[k]
        //             if(values[k]!="" && values[k]!=undefined && values[k] != 0 && values[k]!="0" && values[k]!="0px")
        //             {
        //                 if(k=="background-image"){
        //                     css_design += k+":url('"+values[k]+"') !important;";

        //                 }
        //                 else if(k=="font-family"){
        //                     let font_famil_name = me.fields.fonts_list.find(o => o.name === values[k]);
        //                     if(font_famil_name){
        //                         css_design += k+":"+font_famil_name.font_family+" !important;";
        //                     }
        //                 }
        //                 else{
        //                     css_design += k+":"+values[k]+" !important;";
        //                 }
        //             }
                    
        //         }
        //     }
        //     if(this.child_sections){
        //        for (var i = 0; i < this.child_sections.length; i++) {
        //            for (var j = 0; j < this.child_sections[i].child_properties.length; j++) {
        //                var child_value=this.dialog.$wrapper.find('[data-fieldname="'+this.child_sections[i].child_properties[j].fieldname+'"]').val();
        //                var k =this.child_sections[i].child_properties[j].fieldname;
        //                style_json[k]=child_value
        //                if(child_value!="" && child_value!=undefined && child_value != 0 && child_value!="0" && child_value!="0px")
        //                 {
        //                     if(k=="background-image"){
        //                         css_design += k+":url('"+child_value+"');";

        //                     }
        //                     else{
        //                     css_design += k+":"+child_value+";";
        //                     }
        //                 }

        //            }
        //        }
        //     }
        //     // console.log(css_design)
        //     css_design +="}"
            // if(css_design && style_json){
            //     frappe.call({
            //         method: 'go1_cms.go1_cms.doctype.proposal.proposal.generate_css_file',
            //         args: {
            //             section_name:me.fields.name,
            //             content:css_design,
            //             style_json:style_json
            //         },
            //         async: false,
            //         callback: function(r) {
            //             if (r.message) {
            //                 console.log(r.message,"r.message")
            //             }
            //         }
            //     })
            // }
        // }

        //end by boopathy

        var dialog_fields = [];
        let results = [];
        $.each(values, function(k, v) {
            dialog_fields.push( k );
            if (me.fields.section_type != 'Lists' && me.fields.section_type != 'Tabs')
                results.push({ 'name': k, 'content': v, 'doctype': 'Section Content', 'parent': me.section });
            else if (me.fields.section_type == "Lists" && !has_common([k], ['item', 'item_title', 'is_edit', 'image_type', 'image_ref_doc']))
                results.push({ 'name': k, 'content': v, 'doctype': 'Section Content', 'parent': me.section });
            else if (me.fields.section_type == 'Tabs' && !has_common([k], ['tab_item', 'tab_title', 'is_edit_tab', 'no_of_records', 'item1', 'item_title1', 'is_edit1'])) {
                results.push({ 'name': k, 'content': v, 'doctype': 'Section Content', 'parent': me.section });
            } else if (me.fields.section_type == 'Predefined Section' && !has_common([k], ['preitem', 'pre_title'])) {
                results.push({ 'name': k, 'content': v, 'doctype': 'Section Content', 'parent': me.section });
            } else if (me.fields.section_type == 'Collections'){
                results.push({ 'name': k, 'content': v, 'doctype': 'Section Content', 'parent': me.section });
            }
            
        });
        $.each(me.dialog.fields, function(k, v) {
            if(v.fieldtype == "Button"){
                var section_obj={};
                var code_json = {};
              $('[data-key="'+v.fieldname+'"]').each(function(){
                    code_json[$(this).attr("data-fieldname")]=$(this).val();
              })
               section_obj = { 'name': v.fieldname, 'content': JSON.stringify(code_json), 'doctype': 'Section Content', 'parent': me.section };
                 if($('[data-fieldname="'+v.fieldname+'"]').attr("css_design")!=undefined && $('[data-fieldname="'+v.fieldname+'"]').attr("css_design")!="")
                {
                    section_obj = { 'name': v.fieldname, 'doctype': 'Section Content', 'parent': me.section };
                    section_obj['css_text'] = $('[data-fieldname="'+v.fieldname+'"]').attr("css_design");
                }
                 if($('[data-fieldname="'+v.fieldname+'"]').attr("style_json")!=undefined && $('[data-fieldname="'+v.fieldname+'"]').attr("style_json")!="")
                {
                    section_obj['css_json'] = $('[data-fieldname="'+v.fieldname+'"]').attr("style_json");
                }
               results.push(section_obj)
            }
           else if(v.fieldtype != "Section Break"){
                var section_obj={};
                if(jQuery.inArray(v.fieldname, dialog_fields) === -1) {
                    if (me.fields.section_type != 'Lists' && me.fields.section_type != 'Tabs')
                        section_obj = { 'name': v.fieldname, 'content': '', 'doctype': 'Section Content', 'parent': me.section };
                    else if (me.fields.section_type == "Lists" && !has_common([k], ['item', 'item_title', 'is_edit', 'image_type', 'image_ref_doc']))
                        section_obj = { 'name': v.fieldname, 'content': '', 'doctype': 'Section Content', 'parent': me.section };
                    else if (me.fields.section_type == 'Tabs' && !has_common([k], ['tab_item', 'tab_title', 'is_edit_tab', 'no_of_records', 'item1', 'item_title1', 'is_edit1'])) {
                        section_obj = { 'name': v.fieldname, 'content': '', 'doctype': 'Section Content', 'parent': me.section };
                    } else if (me.fields.section_type == 'Predefined Section' && !has_common([k], ['preitem', 'pre_title'])) {
                        section_obj = { 'name': v.fieldname, 'content': '', 'doctype': 'Section Content', 'parent': me.section };
                    } else if (me.fields.section_type == 'Collections'){
                        section_obj = { 'name': v.fieldname, 'content': '', 'doctype': 'Section Content', 'parent': me.section };
                    }
                   
                }
                 if($('[data-fieldname="'+v.fieldname+'"]').attr("css_design")!=undefined && $('[data-fieldname="'+v.fieldname+'"]').attr("css_design")!="")
                {
                    section_obj = { 'name': v.fieldname, 'doctype': 'Section Content', 'parent': me.section };
                    section_obj['css_text'] = $('[data-fieldname="'+v.fieldname+'"]').attr("css_design");
                }
                 if($('[data-fieldname="'+v.fieldname+'"]').attr("style_json")!=undefined && $('[data-fieldname="'+v.fieldname+'"]').attr("style_json")!="")
                {
                    section_obj['css_json'] = $('[data-fieldname="'+v.fieldname+'"]').attr("style_json");
                }
                if(v.fieldname=="category_products_html"){
                     var c_products = []
                     var table_html = $(me.dialog.fields_dict["category_products_html"].$wrapper.find("table tbody"));
                     table_html.find("tr").each(function(){
                         c_products.push({"name":$(this).find("td:eq(1)").text()});
                     })
                     section_obj = { 'name': v.fieldname, 'content': JSON.stringify(c_products), 'doctype': 'Section Content', 'parent': me.section };

                }
                if(v.fieldname=="blog_category_html"){
                    var c_products = []
                    var table_html = $(me.dialog.fields_dict["blog_category_html"].$wrapper.find("table tbody"));
                    table_html.find("tr").each(function(){
                        c_products.push({"name":$(this).find("td:eq(1)").text()});
                    })
                    section_obj = { 'name': v.fieldname, 'content': JSON.stringify(c_products), 'doctype': 'Section Content', 'parent': me.section };

               }
                results.push(section_obj)
            }
          
        })
        if(css_design!=""){
            results.push({ 'name': "section_css_json", 'content': style_json});
            results.push({ 'name': "section_css_text", 'content': css_design});
        }
        if (results.length > 0 || me.list_section_data.length > 0) {
            // console.log(results)
            frappe.call({
                method: 'go1_cms.go1_cms.doctype.proposal.proposal.update_section_content',
                args: {
                    docs: results,
                    lists_data: JSON.stringify(me.list_section_data),
                    section: me.section,
                    business: cur_frm.doc.business
                },
                freeze: true,
                callback: function(r) {
                    if (r.message.status == 'Success') {
                        show_alert('Section updated!', 5);
                       cur_frm.set_value("published",cur_frm.doc.published);
                         // cur_frm.set_value('route', '')
                        // me.dialog.hide();
                        cur_frm.save();
                    }
                }
            })
        } else {
            frappe.throw('Please fill any field')
        }
    },
    update_design: function() {
        let me = this;
        if (this.selected_pattern) {
            this.selected_pattern.section = me.section;
            frappe.call({
                method: 'go1_cms.go1_cms.doctype.proposal.proposal.update_patterns',
                args: me.selected_pattern,
                callback: function(r) {
                    if (r.message.status == 'Success') {
                        show_alert('Section updated!', 5);
                        me.dialog.hide();
                        cur_frm.save();
                    }
                }
            })
        }
    },
    check_image_field: function() {
        let me = this;
        let image_fields = this.fields.content.filter(obj => obj.field_type == 'Attach');
        $(image_fields).each(function(k, v) {
            if (v.content != '' && v.content != null && v.content != undefined) {
                me.dialog.fields_dict[v.name].$wrapper.find('.img-container').css('display', 'block');
                me.dialog.fields_dict[v.name].$wrapper.find('.img-container img').attr('src', v.content);
                me.dialog.fields_dict[v.name].$wrapper.find('.missing-image').css('display', 'none');
                me.dialog.set_value(v.name, v.content);
            }
        })
    },
    check_fieldtype_lists: function() {
        let me = this;
        let list_fields = this.fields.content.filter(obj => obj.field_type == 'List');
        let names_list = [];
        this.fields.content.map(c => {
            names_list.push(c.name);
        })
        $(list_fields).each(function(k, v) {
            if(v.fields_json) {
                let index = names_list.indexOf(v.name);
                let fields = (JSON.parse(v.fields_json) || []);
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
                if(v.content) {
                    values = (JSON.parse(v.content) || []);
                    me.dialog.set_value(v.name, v.content);
                }
                var display_fileds_count = 1;
                if(fields.length>0){
                        list_html.find('thead').append("<tr id='head-cols'></tr>")

                for (var i = 0; i < fields.length; i++) {
                    // if(fields[i].field_type!="Attach"){
                       list_html.find('thead #head-cols').append(`<th style='border-bottom-width: 1px;border-color: #ddd;'>`+fields[i].field_label+`</th>`);
                        display_fileds_count+=1;
                    // }
                        }
                   list_html.find('thead #head-cols').append(`<th style='border-color: #ddd;border-bottom: 0;'>Actions</th>`);
                }
                

               
                
                if(values.length > 0) {
                    values.map(f => {
                        var row_html = '<tr>';
                         for (var i = 0; i < fields.length; i++) {
                            if(fields[i].field_type!="Attach"){
                               row_html+='<td style="border-color: #ddd;">'+f[fields[i].field_key]+'</td>';
                             }
                             else{
                               row_html+='<td style="border-color: #ddd;"><img src="'+f[fields[i].field_key]+'" style="height:50px"/></td>';

                             }
                         }
                         row_html+=' <td style="width: 25%;border-color: #ddd;">';
                         row_html+=' <button class="btn btn-sm btn-primary"><span class="fa fa-edit"></span></button>';
                         row_html+=' <button class="btn btn-sm btn-danger"><span class="fa fa-trash"></span></button>';
                         row_html+=' </td>'
                         row_html += '</tr>';
                        
                        // let row = $(`<tr>
                        //         <td>Row ${f["title"]}</td>
                        //         <td style="width: 25%;">
                        //             <button class="btn btn-primary"><span class="fa fa-edit"></span></button>
                        //             <button class="btn btn-danger"><span class="fa fa-trash"></span></button>
                        //         </td>
                        //     </tr>`);
                        let row = $(row_html)
                        row.find('.btn-primary').click(function() {
                            me.show_list_modal(index, v, 'edit', f);
                        });
                        row.find('.btn-danger').click(function() {
                            let content = values.filter(obj => obj.idx != f.idx);
                            $(content).each(function(i, j) {
                                j.idx = (i + 1);
                            });
                            me.fields.content[index].content = JSON.stringify(content);
                            me.check_fieldtype_lists();
                        })
                        list_html.find('tbody').append(row);
                    });
                } else {
                    list_html.find('tbody').html(`<tr><td style='border-color: #ddd;' colspan="`+display_fileds_count+`">No records found!</td></tr>`);
                }
                list_html.find('.add-list-item').click(function() {
                    me.show_list_modal(index, v, 'add');
                })
            }
        })
    },
     check_fieldtype_button: function() {
        let me = this;
        let list_fields = this.fields.content.filter(obj => obj.field_type == 'Button');
        
        $(list_fields).each(function(k, v) {
            let list_html = me.dialog.fields_dict[v.name].$wrapper.empty();
            var btn_url = '';
            var btn_txt = '';
            var edit_style = '';
            if(v.allow_update_to_style==1){
                edit_style = '<a style="margin-left: 10px;background: #fff;padding: 2px 7px;color: #308fdb;font-size: 12px;border: 1px solid #308fdb;border-radius: 3px;font-weight: 600;" onclick=show_element_style("'+v.name+'")><i class="fa fa-cog" style="margin-right:5px"></i>Edit Styles</a>'
            }
            if(v.content){
            var json_data = JSON.parse(v.content); 
            for (const [key, value] of Object.entries(json_data)) {
                    if (key=="btn_text"){
                        btn_txt=value
                    }
                    if (key=="btn_redirect_url"){
                        btn_url=value
                    }
                }
            }
            let appendHtml = '<div class="row"> <div class="section-head" style="margin: 0 15px 15px"><a class="h6 uppercase">Button'+edit_style+'</a></div>';
            appendHtml+='<div class="col-md-6"><div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="'+v.name+'" title="c1abe1bcce"><div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Button Text</label>                    </div>                    <div class="control-input-wrapper">                        <div class="control-input" style="display: block;"><input type="text" value="'+btn_txt+'" autocomplete="off" class="input-with-feedback form-control" maxlength="140" data-fieldtype="Data" data-fieldname="btn_text" data-key="'+v.name+'" placeholder=""></div><div class="control-value like-disabled-input" style="display: none;">#</div><p class="help-box small text-muted hidden-xs"></p></div></div></div></div>'
            appendHtml+='<div class="col-md-6"><div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="'+v.name+'" title="c1abe1bcce"><div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Button Redirect Url</label></div><div class="control-input-wrapper"><div class="control-input" style="display: block;"><input type="text" value="'+btn_url+'" autocomplete="off" class="input-with-feedback form-control" maxlength="140" data-fieldtype="Data" data-fieldname="btn_redirect_url" data-key="'+v.name+'" placeholder=""></div><div class="control-value like-disabled-input" style="display: none;">#</div><p class="help-box small text-muted hidden-xs"></p></div></div></div></div>'
            // appendHtml+='<div class="col-md-6"><div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="'+v.name+'" title="c1abe1bcce"><div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Button Background Color</label>                    </div>                    <div class="control-input-wrapper"><div class="control-input" style="display: block;"><input type="text" autocomplete="off" class="input-with-feedback form-control" maxlength="140" data-fieldtype="Data" data-fieldname="btn_bg_color" data-key="'+v.name+'" placeholder=""></div><div class="control-value like-disabled-input" style="display: none;">#</div><p class="help-box small text-muted hidden-xs"></p></div></div></div></div>'
            // appendHtml+='<div class="col-md-6"><div class="frappe-control input-max-width" data-fieldtype="Data" data-fieldname="'+v.name+'" title="c1abe1bcce"><div class="form-group"><div class="clearfix"><label class="control-label" style="padding-right: 0px;">Button Text Color</label>                    </div>                    <div class="control-input-wrapper"><div class="control-input" style="display: block;"><input type="text" autocomplete="off" class="input-with-feedback form-control" maxlength="140" data-fieldtype="Data" data-fieldname="btn_text_color" data-key="'+v.name+'" placeholder=""></div><div class="control-value like-disabled-input" style="display: none;">#</div><p class="help-box small text-muted hidden-xs"></p></div></div></div></div>'
            list_html.append(appendHtml)
        });
        //     if(v.fields_json) {
        //         let index = names_list.indexOf(v.name);
        //         let fields = (JSON.parse(v.fields_json) || []);
        //         let list_html = me.dialog.fields_dict[v.name].$wrapper.empty();
        //         $(`<div>
        //             <button class="btn btn-primary add-list-item">Add Item</button>
        //             <table class="table table-bordered">
        //                 <thead>
        //                     <tr></tr>
        //                 </thead>
        //                 <tbody></tbody>
        //             </table></div>`).appendTo(list_html);
        //         list_html.find('thead tr').append(`<th>Records</th>`);
        //         list_html.find('thead tr').append(`<th></th>`);
        //         let values = [];
        //         if(v.content) {
        //             values = (JSON.parse(v.content) || []);
        //             me.dialog.set_value(v.name, v.content);
        //         }
        //         if(values.length > 0) {
        //             values.map(f => {
        //                 let row = $(`<tr>
        // <td>Row ${f.idx}</td>
        //                         <td style="width: 25%;">
        //                             <button class="btn btn-primary"><span class="fa fa-edit"></span></button>
        //                             <button class="btn btn-danger"><span class="fa fa-trash"></span></button>
        //                         </td>
        //                     </tr>`);
        //                 row.find('.btn-primary').click(function() {
        //                     me.show_list_modal(index, v, 'edit', f);
        //                 });
        //                 row.find('.btn-danger').click(function() {
        //                     let content = values.filter(obj => obj.idx != f.idx);
        //                     $(content).each(function(i, j) {
        //                         j.idx = (i + 1);
        //                     });
        //                     me.fields.content[index].content = JSON.stringify(content);
                           
        //                 })
        //                 list_html.find('tbody').append(row);
        //             });
        //         } else {
        //             list_html.find('tbody').html(`<tr><td colspan="2">No records found!</td></tr>`);
        //         }
        //         list_html.find('.add-list-item').click(function() {
        //             me.show_list_modal(index, v, 'add');
        //         })
        //     }
        // })
    },
    show_list_modal: function(index, data, type, edit_data) {
        let me = this;
        let title = (type == 'add') ? 'Add New Item' : 'Edit Item';
        let fields = [];
        let fields_list = JSON.parse(data.fields_json) || [];
       $(fields_list).each(function(k, v) {
            let obj = {};
            obj.fieldname = v.field_key;
            obj.label = v.field_label;
            if(v.field_type == 'Attach')
                obj.fieldtype = 'Attach';
            else if(v.field_type == 'Text')
                obj.fieldtype = 'Data';
            else if(v.field_type == 'Small Text')
                obj.fieldtype = 'Text';
             else if(v.field_type == 'Text Editor')
                obj.fieldtype = 'Text Editor';
            else if(v.field_type == 'Attach Video')
                obj.fieldtype = 'Attach';
            else
                obj.fieldtype = 'HTML Editor';
            fields.push(obj);
        });
        let list_dialog = new frappe.ui.Dialog({
            title: title,
            fields: fields,
            primary_action_label: __('Save'),
            primary_action(values) {
                let content = JSON.parse(data.content || '[]');
                if(type == 'add') {
                    values.idx = content.length + 1;
                    content.push(values);
                } else {
                    let keys = Object.keys(values);
                    $(content).each(function(key, val) {
                        console.log(val.idx)
                        console.log(edit_data.idx)
                        
                        if(val.idx == edit_data.idx) {
                            $(keys).each(function(i, j) {
                                val[j] = values[j];
                            })
                        }
                    })
                }
                me.fields.content[index].content = JSON.stringify(content);
                list_dialog.hide();
                me.check_fieldtype_lists();
            }
        });
        list_dialog.show();
        if(type == 'edit') {
            let keys = Object.keys(edit_data);
            $(keys).each(function(k, v) {
                list_dialog.set_value(v, edit_data[v]);
            })
        }
    },
    list_fields: function() {
        let me = this;
        if (this.fields.section_type == 'Lists') {
            this.table_html(this.fields.custom_section_data);
            this.suggestion_html();
            this.save_btns();
            this.dialog.fields_dict.sec_br_2.wrapper.hide();
        } else if (this.fields.section_type == 'Tabs' && this.fields.reference_document != 'Custom Query') {
            this.table_html1(this.fields.custom_section_data);
            this.save_btns1();
            this.dialog.fields_dict.sec_br_22.wrapper.hide();
        } else if (this.fields.section_type == 'Tabs' && this.fields.reference_document == 'Custom Query') {
            this.tab_table_html(this.fields.custom_section_data);
            this.tab_save_btns();
            this.dialog.fields_dict.tab_sec_br_2.wrapper.hide();
        } else if (this.fields.section_type == 'Predefined Section' && this.fields.predefined_section != '') {
            me.predefined_items()
            // this.predefined_table_html(this.fields.custom_section_data);
            this.predefined_save_btns();
            // this.dialog.fields_dict.predefined_sec_br_22.wrapper.hide();
        }
        else if (this.fields.section_type == 'Collections') {
            me.collection_items()
            // this.collections_save_btns();
        }
    },
    table_html1: function(section_data) {
        let me = this;
        let html = this.dialog.fields_dict.table_html1.$wrapper.empty();
        let btns = $(`<div>
                <button class="btn btn-primary">${__("Add Record")}</button>
            </div>`).appendTo(html);

        btns.find('.btn-primary').click(function() {
            me.dialog.fields_dict.sec_br_22.wrapper.show();
            me.dialog.fields_dict.sec_br_11.wrapper.hide();
            me.dialog.fields_dict.is_edit1.set_value('0');
            me.dialog.fields_dict.item1.set_value("");
            me.dialog.fields_dict.item_title1.set_value("");
            me.dialog.fields_dict.no_of_records.set_value("");
        })
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
            height: 350
        })
        let no_record = false;
        if (!section_data || section_data == '')
            no_record = true;
        else {
            let data = JSON.parse(section_data);
            if (data && data.length > 0) {
                me.list_section_data = data;
                data.map(f => {

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
                    table.find('tbody').append(row);
                    row.find('.btn-primary').click(function() {
                        me.dialog.fields_dict.is_edit1.set_value(f.idx1);
                        me.dialog.fields_dict.item1.set_value(f.item1);
                        me.dialog.fields_dict.item_title1.set_value(f.item_title1);
                        me.dialog.fields_dict.no_of_records.set_value(f.no_of_records);
                        me.dialog.fields_dict.sec_br_22.wrapper.show();
                        me.dialog.fields_dict.sec_br_11.wrapper.hide();

                    });
                    row.find('.btn-danger').click(function() {
                        let obj = me.list_section_data.filter(o => o.idx1 != f.idx1);
                        $(obj).each(function(k, v) {
                            v.idx1 = (k + 1);
                        })
                        me.list_section_data = obj;
                    });

                })
            } else {
                no_record = true;
            }
        }
        if (no_record) {
            table.find('tbody').append(`<tr><td colspan="3">No Records Found!</td></tr>`);
        }
    },
    tab_table_html: function(section_data) {
        let me = this;
        let html = this.dialog.fields_dict.tab_table_html.$wrapper.empty();
        let btns = $(`<div>
                <button class="btn btn-primary">${__("Add Record")}</button>
            </div>`).appendTo(html);

        btns.find('.btn-primary').click(function() {
            me.dialog.fields_dict.tab_sec_br_2.wrapper.show();
            me.dialog.fields_dict.tab_sec_br_1.wrapper.hide();
            me.dialog.fields_dict.is_edit_tab.set_value('0');
            me.dialog.fields_dict.tab_item.set_value("");
            me.dialog.fields_dict.tab_title.set_value("");
            me.dialog.fields_dict.no_of_records.set_value("");
        })
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
            height: 350
        })
        let no_record = false;
        if (!section_data || section_data == '')
            no_record = true;
        else {
            let data = JSON.parse(section_data);
            if (data && data.length > 0) {
                me.list_section_data = data;
                data.map(f => {

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
                    table.find('tbody').append(row);
                    row.find('.btn-primary').click(function() {
                        me.dialog.fields_dict.is_edit_tab.set_value(f.idx);
                        me.dialog.fields_dict.tab_item.set_value(f.tab_item);
                        me.dialog.fields_dict.tab_title.set_value(f.tab_title);
                        me.dialog.fields_dict.no_of_records.set_value(f.no_of_records);
                        me.dialog.fields_dict.tab_sec_br_2.wrapper.show();
                        me.dialog.fields_dict.tab_sec_br_1.wrapper.hide();

                    });
                    row.find('.btn-danger').click(function() {
                        let obj = me.list_section_data.filter(o => o.idx != f.idx);
                        $(obj).each(function(k, v) {
                            v.idx = (k + 1);
                        })
                        me.list_section_data = obj;
                    });

                })
            } else {
                no_record = true;
            }
        }
        if (no_record) {
            table.find('tbody').append(`<tr><td colspan="3">No Records Found!</td></tr>`);
        }
    },
    predefined_table_html: function(section_data) {
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
                        <td>${__(doclabel+" Name")}</td>
                        <td>${__(doclabel+" Image")}</td>
                        <td>${__("Price")}</td>
                        <td></td>
                    </tr>
                </thead>
                <tbody></tbody>
            </table></div>`).appendTo(html);
        table.slimScroll({
            height: 350
        })
        let no_record = false;
        if (!section_data || section_data == '')
            no_record = true;
        else {
            let data = JSON.parse(section_data);
            if (data && data.length > 0) {
                me.list_section_data = data;
                data.map(f => {
                    let hide = "";
                    let image = ''
                    if (f.product_image) {
                        image = f.product_image
                    }
                    let fieldname = 'name';
                    if (me.fields.reference_document == 'Product Category') {
                        fieldname = 'category_name'
                    } else if (me.fields.reference_document == 'Product Brand') {
                        fieldname = 'brand_name'
                    } else if (me.fields.reference_document == 'Product') {
                        fieldname = 'item'
                    }
                    let item = ""
                    let price = ""
                   
                    if(f[fieldname]){
                        item = f[fieldname]
                    }
                    if(f.price){
                        price = f.price
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
            table.find('tbody').append(row);
                    // row.find('.btn-primary').click(function() {
                    //     me.dialog.fields_dict.is_edit_pre.set_value(f.idx);
                    //     me.dialog.fields_dict.pre_item.set_value(f.pre_item);
                    //     me.dialog.fields_dict.pre_title.set_value(f.pre_title);
                    //     me.dialog.fields_dict.no_of_records.set_value(f.no_of_records);
                    //     me.dialog.fields_dict.predefined_sec_br_2.wrapper.show();
                    //     me.dialog.fields_dict.predefine_sec_br_1.wrapper.hide();

                    // });
                    row.find('.btn-danger').click(function() {
                        var name = $(this).parent().attr('data-id')
                        let obj = me.list_section_data.filter(o => o.idx != f.idx);

                        let cond = 'display_home_page';
                        if (me.fields.reference_document == 'Product Category') {
                            cond = 'display_on_home_page'
                        } else if (me.fields.reference_document == 'Product Brand') {
                            cond = 'is_active'
                        } else if (me.fields.reference_document == 'Product') {
                            cond = 'display_home_page'
                        }
                        frappe.call({
                            method: 'go1_cms.go1_cms.doctype.proposal.proposal.update_featured_item',
                            args: {
                                doctype: me.fields.reference_document,
                                name: val.preitem,
                                checked: 1,
                                conditionfield: cond
                            },
                            async: false,
                            callback: function(r) {
                                
                            }
                        })
                        me.predefined_items()
                    });

                })
            } else {
                no_record = true;
            }
        }
        if (no_record) {
            table.find('tbody').append(`<tr><td colspan="3">No Records Found!</td></tr>`);
        }
    },
    collections_table_html: function(section_data) {
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
            height: 350
        })
        let no_record = false;
        if (!section_data || section_data == '')
            no_record = true;
        else {
            let data = JSON.parse(section_data);
            if (data && data.length > 0) {
                me.list_section_data = data;
                data.map(f => {
                    let hide = "";
                    let image = ''
                    if (f.product_image) {
                        image = f.product_image
                    }
                    let row = $(`<tr>
                            <td>${f.name}</td>
                             <td>${f.item}</td>
                        </tr>`);
                    table.find('tbody').append(row);
                    // row.find('.btn-danger').click(function() {
                    //     var name = $(this).parent().attr('data-id')
                    //     let obj = me.list_section_data.filter(o => o.idx != f.idx);
                    //     frappe.call({
                    //         method: 'go1_cms.go1_cms.doctype.proposal.proposal.update_featured_item',
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

                })
            } else {
                no_record = true;
            }
        }
        if (no_record) {
            table.find('tbody').append(`<tr><td colspan="3">No Records Found!</td></tr>`);
        }
    },
    table_html: function(section_data) {
        let me = this;
        let html = this.dialog.fields_dict.table_html.$wrapper.empty();
        let btns = $(`<div>
                <button class="btn btn-warning">${__("Auto Generate Records")}</button>
                <button class="btn btn-primary">${__("Add Record Manually")}</button>
            </div>`).appendTo(html);
        btns.find('.btn-warning').click(function() {
            me.random_items()
        });
        btns.find('.btn-primary').click(function() {
            me.dialog.fields_dict.sec_br_2.wrapper.show();
            me.dialog.fields_dict.sec_br_1.wrapper.hide();
            me.dialog.fields_dict.is_edit.set_value('0');
            me.dialog.fields_dict.item.set_value("");
            me.dialog.fields_dict.item_title.set_value("");
            me.dialog.fields_dict.image_type.set_value("");
            let img_html = me.dialog.fields_dict.img.$wrapper.empty();
        })
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
            height: 350
        })
        let no_record = false;
        if (!section_data || section_data == '')
            no_record = true;
        else {
            let data = JSON.parse(section_data);
            if (data && data.length > 0) {
                me.list_section_data = data;
                data.map(f => {
                    let titles = f.item_title.split(' | ')
                    let t = titles[0];
                    if (titles[1])
                        t += '<br>' + titles[1]
                    if (titles[2])
                        t += '<br>' + titles[2];
                    let hide = "";
                    if (f.image_type && f.image_type != 'Pick / Upload specified image' && f.image_type != 'Upload image')
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
                    table.find('tbody').append(row);
                    row.find('.btn-primary').click(function() {
                        me.dialog.fields_dict.is_edit.set_value(f.idx);
                        me.dialog.fields_dict.item.set_value(f.item);
                        me.dialog.fields_dict.item_title.set_value(f.item_title);
                        me.dialog.fields_dict.image_type.set_value(f.image_type);
                        me.dialog.fields_dict.sec_br_2.wrapper.show();
                        me.dialog.fields_dict.sec_br_1.wrapper.hide();
                        let img_html = me.dialog.fields_dict.img.$wrapper.empty();
                        if (f.image) {
                            img_html.append(`<div><img src="${f.image}" style="height: 75px;" /></div>`);
                        }
                    });
                    row.find('.btn-danger').click(function() {
                        let obj = me.list_section_data.filter(o => o.idx != f.idx);
                        $(obj).each(function(k, v) {
                            v.idx = (k + 1);
                        })
                        me.list_section_data = obj;
                        row.remove();
                    });
                    row.find('.btn-info').click(function() {
                        me.image_dialog(f)
                    })
                })
            } else {
                no_record = true;
            }
        }
        if (no_record) {
            table.find('tbody').append(`<tr><td colspan="3">No Records Found!</td></tr>`);
        }
    },
    suggestion_html: function() {
        let html = this.dialog.fields_dict.suggestions.$wrapper.empty();
        $(`<div style="background: #ddd;border: 1px solid #ccc;padding: 10px;">
                <h4 style="margin-top: 0;">${__("Suggestions for Title / Subtitle")}</h4>
                <ul></ul>
            </div>`).appendTo(html);
        let suggestions = ["Best Selling", "Mega Sale! Limited Stock!", "Discover Now!", "Shop Now!",
            "Grab Now!", "Great Savings!", "Explore Now!", "Hurry!", "Buy Now!", "Top Picks", "Bestsellers",
            "Hot Picks", "Most Popular!"
        ];
        suggestions.map(f => {
            html.find('ul').append(`<li>${f}</li>`)
        });
    },
    save_btns1: function() {
        let me = this;
        let html = this.dialog.fields_dict.save_records.$wrapper.empty();
        $(`<div>
                <button class="btn btn-sm btn-primary">${__("Save")}</button>
                <button class="btn btn-sm btn-danger">${__("Cancel")}</button>
                </div>`).appendTo(html);
        html.find('.btn-primary').click(function() {
            let val = me.dialog.get_values();
            // console.log(val,"-----save_btns1-----")
            if (!val.item1 || !val.item_title1)
                frappe.throw("Please fill all columns");
            if (val.is_edit1 == 0) {
                me.list_section_data.push({
                    "item1": val.item1,
                    "no_of_records": val.no_of_records,
                    "item_title1": val.item_title1,
                    "idx1": (me.list_section_data.length + 1)
                });
            } else {
                $(me.list_section_data).each(function(k, v) {
                    if ((k + 1) == parseInt(val.is_edit1)) {
                        v.item1 = val.item1;
                        v.item_title1 = val.item_title1;
                        v.no_of_records = val.no_of_records;
                    }
                })
            }
            me.table_html1(JSON.stringify(me.list_section_data));
            me.dialog.fields_dict.sec_br_22.wrapper.hide();
            me.dialog.fields_dict.sec_br_11.wrapper.show();
        });
        html.find('.btn-danger').click(function() {
            me.dialog.fields_dict.sec_br_22.wrapper.hide();
            me.dialog.fields_dict.sec_br_11.wrapper.show();
        })
    },
    predefined_save_btns: function() {
        let me = this;
        let html = this.dialog.fields_dict.save_prerecords.$wrapper.empty();
        $(`<div>
                <button class="btn btn-sm btn-primary" style="margin-top:25px;padding: 8px 23px !important;">${__("Add")}</button>
                </div>`).appendTo(html);
        html.find('.btn-primary').click(function() {
            let val = me.dialog.get_values();
            // console.log(val,"-----predefined_save_btns-----")
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
            
            let cond = 'display_home_page';
            if (me.fields.reference_document == 'Product Category') {
                cond = 'display_on_home_page'
            } else if (me.fields.reference_document == 'Product Brand') {
                cond = 'is_active'
            } else if (me.fields.reference_document == 'Product') {
                cond = 'display_home_page'
            }
            frappe.call({
                method: 'go1_cms.go1_cms.doctype.proposal.proposal.update_featured_item',
                args: {
                    doctype: me.fields.reference_document,
                    name: val.preitem,
                    checked: 1,
                    conditionfield: cond
                },
                async: false,
                callback: function(r) {
                    
                }
            })
            me.dialog.fields_dict.preitem.set_value("");
            me.dialog.fields_dict.pre_title.set_value("");
            me.predefined_items()
            
            // me.predefined_table_html(JSON.stringify(me.predefined_lists))
            // me.dialog.fields_dict.predefined_sec_br_22.wrapper.hide();
            // me.dialog.fields_dict.predefined_sec_br_11.wrapper.show();
        });
        // html.find('.btn-danger').click(function() {
        //     me.dialog.fields_dict.predefined_sec_br_22.wrapper.hide();
        //     me.dialog.fields_dict.predefined_sec_br_11.wrapper.show();
        // })
    },
    tab_save_btns: function() {
        let me = this;
        let html = this.dialog.fields_dict.tab_save_record.$wrapper.empty();
        $(`<div>
                <button class="btn btn-sm btn-primary">${__("Save")}</button>
                <button class="btn btn-sm btn-danger">${__("Cancel")}</button>
                </div>`).appendTo(html);
        html.find('.btn-primary').click(function() {
            let val = me.dialog.get_values();
            if (!val.tab_item || !val.tab_title)
                frappe.throw("Please fill all columns");
            if (val.is_edit_tab == 0) {
                me.list_section_data.push({
                    "tab_item": val.tab_item,
                    "tab_title": val.tab_title,
                    "no_of_records": val.no_of_records,
                    "idx": (me.list_section_data.length + 1)
                });
            } else {
                $(me.list_section_data).each(function(k, v) {
                    if ((k + 1) == parseInt(val.is_edit_tab)) {
                        v.tab_item = val.tab_item;
                        v.tab_title = val.tab_title;
                        v.no_of_records = val.no_of_records;
                    }
                })
            }
            me.tab_table_html(JSON.stringify(me.list_section_data));
            me.dialog.fields_dict.tab_sec_br_2.wrapper.hide();
            me.dialog.fields_dict.tab_sec_br_1.wrapper.show();
        });
        html.find('.btn-danger').click(function() {
            me.dialog.fields_dict.tab_sec_br_2.wrapper.hide();
            me.dialog.fields_dict.tab_sec_br_1.wrapper.show();
        })
    },
    save_btns: function() {
        let me = this;
        let html = this.dialog.fields_dict.save_record.$wrapper.empty();
        $(`<div>
                <button class="btn btn-sm btn-primary">${__("Save")}</button>
                <button class="btn btn-sm btn-danger">${__("Cancel")}</button>
                </div>`).appendTo(html);
        html.find('.btn-primary').click(function() {
            let val = me.dialog.get_values();
            // console.log(val,"-----save_btns-----")
            if (!val.item || !val.item_title)
                frappe.throw("Please fill all columns");
            if (val.is_edit == 0) {
                me.list_section_data.push({
                    "item": val.item,
                    "item_title": val.item_title,
                    "idx": (me.list_section_data.length + 1),
                    "image": null,
                    "image_type": val.image_type
                });
            } else {
                $(me.list_section_data).each(function(k, v) {
                    if ((k + 1) == parseInt(val.is_edit)) {
                        v.item = val.item;
                        v.item_title = val.item_title;
                        v.image_type = val.image_type;
                    }
                })
            }
            me.table_html(JSON.stringify(me.list_section_data));
            me.dialog.fields_dict.sec_br_2.wrapper.hide();
            me.dialog.fields_dict.sec_br_1.wrapper.show();
        });
        html.find('.btn-danger').click(function() {
            me.dialog.fields_dict.sec_br_2.wrapper.hide();
            me.dialog.fields_dict.sec_br_1.wrapper.show();
        })
    },
    random_items: function() {
        let me = this;
        frappe.run_serially([
            () => { me.get_random_records(me.fields.reference_document, me.dialog.get_value('no_of_records')) },
            () => {
                me.table_html(JSON.stringify(me.random_lists))
            }
        ])
    },
    predefined_items: function() {
        let me = this;
        frappe.run_serially([
            () => { me.get_predefined_records(me.fields.name, me.fields.reference_document, me.fields.no_of_records, me.fields.business) },
            () => {
                me.predefined_table_html(JSON.stringify(me.predefined_lists))
            }
        ])
    },
    collection_items: function() {
        let me = this;
        frappe.run_serially([
            () => { me.get_collections_records(me.dialog.get_value('collections')) },
            () => {
                me.collections_table_html(JSON.stringify(me.collection_lists))
            }
        ])
    },
    get_random_records: function(dt, records) {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_random_records',
            args: {
                dt: dt,
                records: records,
                business: cur_frm.doc.business
            },
            async: false,
            callback: function(r) {
                if (r.message) {
                    me.random_lists = r.message;
                }
            }
        })
    },
    get_predefined_records: function(name, dt, no_of_records, business) {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_predefined_records',
            args: {
                dt: dt,
                records: no_of_records,
                business: cur_frm.doc.business,
                name: name
            },
            async: false,
            callback: function(r) {
                if (r.message) {
                    me.predefined_lists = r.message;
                }
            }
        })
    },
    get_collections_records: function(collections) {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_collection_records',
            args: {
                collections: collections
            },
            async: false,
            callback: function(r) {
                if (r.message) {
                    me.collection_lists = r.message;
                }
            }
        })
    },
    image_dialog: function(rec) {
        let me = this;
        frappe.run_serially([
            () => { me.get_image_album(me.fields.reference_document, rec.item) },
            () => { me.show_img_dialog(rec) }
        ])
    },
    show_img_dialog: function(rec) {
        let me = this;
        this.imagedialog = new frappe.ui.Dialog({
            title: __("Pick Image"),
            fields: [
                { "fieldname": "tab_html", "fieldtype": "HTML" },
                { "fieldname": "sec_1", "fieldtype": "Section Break" },
                { "fieldname": "upload_img", "fieldtype": "HTML" },
                { "fieldname": "sec_2", "fieldtype": "Section Break" },
                { "fieldname": "image_gallery", "fieldtype": "HTML" }
            ]
        });
        this.imagedialog.set_primary_action(__('Save'), function() {
            let active_tab = me.imagedialog.fields_dict.tab_html.$wrapper.find('li.active').attr('data-id');
            let image = "";
            if (active_tab == '2') {
                image = me.picked_image;
            } else if (active_tab == '1') {
                image = me.uploaded_image;
            }
            $(me.list_section_data).each(function(k, v) {
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
        this.imagedialog.$wrapper.find('.modal-dialog').css("width", "800px");
        this.imagedialog.$wrapper.find('.form-section').css("border-bottom", "0");
    },
    get_image_album: function(dt, dn) {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_image_album',
            args: {
                dt: dt,
                dn: dn,
                business: cur_frm.doc.business
            },
            async: false,
            callback: function(r) {
                if (r.message) {
                    me.gallery = r.message;
                } else {
                    me.gallery = [];
                }
            }
        })
    },
    gallery_tab_html: function() {
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
        tab_html.find('li').click(function() {
            tab_html.find('li').removeClass('active');
            if ($(this).attr('data-id') == '1') {
                me.imagedialog.fields_dict.sec_2.wrapper.hide();
                me.imagedialog.fields_dict.sec_1.wrapper.show();
                tab_html.find('li[data-id="1"]').addClass('active');
            } else {
                me.imagedialog.fields_dict.sec_1.wrapper.hide();
                me.imagedialog.fields_dict.sec_2.wrapper.show();
                tab_html.find('li[data-id="2"]').addClass('active');
            }
        });
    },
    gallery_html: function() {
        let me = this;
        let gallery_html = this.imagedialog.fields_dict.image_gallery.$wrapper.empty();
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
            this.gallery.map(f => {
                let row = $(`<div class="col-md-3 gal-items" style="margin-bottom: 10px; height: 100px;"><img src="${f.thumbnail}" /></div>`);
                gallery_html.find('.gallery').append(row);
                row.click(function() {
                    gallery_html.find('.gal-items').removeClass('active');
                    row.addClass('active');
                    me.picked_image = f.list_image;
                });
            });
            gallery_html.find('.gallery').slimScroll({
                height: 300
            })
        } else {
            gallery_html.append(`<div style="text-align: center;background: #ddd;padding: 10%;font-size: 20px;border: 1px solid #ccc;border-radius: 4px;">No images found!</div>`)
        }
    },
    uploader_component: function() {
        let me = this;
        let uploader = this.imagedialog.fields_dict.upload_img.$wrapper.empty();
        let random = parseInt(Math.random() * 10000);
        uploader.append(`<div id="uploader${random}"></div><div id="progress${random}"></div>`);
        setTimeout(function() {
            me.upload_component(`#uploader${random}`, `#progress${random}`);
        }, 500);

    },
    upload_component: function(target, progress) {
        let me = this;
        var uppy = Uppy.Core({
                restrictions: {
                    maxFileSize: 250000,
                    maxNumberOfFiles: 1,
                    allowedFileTypes: ['image/*', '.jpg', '.png', '.jpeg', '.gif']
                },
                meta: {
                    doctype: 'Page Section',
                    docname: me.section
                }
            })
            .use(Uppy.DragDrop, {
                target: target,
                inline: true,
                note: 'Image only up to 250 KB'
            })
            .use(Uppy.XHRUpload, {
                endpoint: window.location.origin + '/api/method/go1_cms.go1_cms.doctype.proposal.proposal.upload_img',
                method: 'post',
                formData: true,
                fieldname: 'file',
                headers: {
                    'X-Frappe-CSRF-Token': frappe.csrf_token
                }
            })
            .use(Uppy.StatusBar, {
                target: progress,
                hideUploadButton: false,
                hideAfterFinish: false
            })
            .on('upload-success', function(file, response) {
                if (response.status == 200) {
                    me.uploaded_image = response.body.message.file_url;
                    me.imagedialog.$wrapper.find('.modal-header .btn-primary').trigger('click');
                }
            });
    }
});

function field_css(name){
    console.log("Success_scscs",name)
}

function generate_css(style_json){
    // console.log(style_json,"style_json111")
    const num = 8;
    const randomNameGenerator = num => {
       let res = '';
       for(let i = 0; i < num; i++){
          const random = Math.floor(Math.random() * 27);
          res += String.fromCharCode(97 + random);
       };
       return res;
    };
    let class_name =randomNameGenerator(num);
    let css_design = "."+class_name+"{"
    for (let k in style_json) {
        css_design += k+":"+style_json[k]+";"
    }
    css_design +="}"
    // console.log(css_design,"css_design")
}

//page templates dialog

var add_page_template = Class.extend({
    init: function(opts) {
        this.frm = opts.frm;
        this.make();
    },
    make: function() {
        let me = this;
        frappe.run_serially([
            () => {
               me.get_page_templates();
               
            },
            () => {
                me.make_dialog();
               
            }
        ])
    },
    get_page_templates: function() {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_page_templates',
            args: {
               
            },
            async: false,
            callback: function(r) {
                me.sections = r.message;
            }
        })
    },
    
    make_dialog: function() {
        let me = this;
        let title = 'Choose Page Template';
        this.dialog = new frappe.ui.Dialog({
            title: __(title),
            // fields: [{ "label": __("Enter Section Title"), "fieldname": "title_name", "fieldtype": "Data" }, { "fieldname": "section_html", "fieldtype": "HTML" }]
            fields: [{"fieldname": "section_html", "fieldtype": "HTML" }]

        });
        this.selected_section = [];
        // this.dialog.set_primary_action(__('Save'), function() {
        //         if (me.selected_section.length > 0) {
        //             let titles = ''
        //             let val = me.dialog.get_values();
        //             if (val) {
        //                 titles = val.title_name
        //             }
        //             frappe.call({
        //                 method: 'go1_cms.go1_cms.doctype.proposal.proposal.convert_template_to_section',
        //                 args: {
        //                     'template': me.selected_section[0].template,
        //                     'business': cur_frm.doc.business,
        //                     'section_name':  custom_title
        //                 },
        //                 callback: function(r) {
        //                     if (r.message) {
        //                         let row = frappe.model.add_child(me.frm.doc, me.doctype, me.parentfield);
        //                         row.section = r.message.name;
        //                         row.section_type = r.message.section_type;
        //                         row.content_type = r.message.content_type;
        //                         row.section_name = r.message.section_name;
        //                         row.custom_title = r.message.custom_title;
        //                         row.allow_update_to_style = r.message.allow_update_to_style;
        //                         me.frm.save();
        //                         me.dialog.hide();
        //                     }
        //                 }
        //             });

        //         } else {
        //             frappe.throw('Please pick any section');
        //         }
            
        // });
        this.dialog.show();
        this.section_html();
        this.dialog.$wrapper.find('.form-column.col-sm-12').css("padding","0");
        this.dialog.$wrapper.find('.form-section').attr("style","width: calc(100%);margin-left: 0px;padding-top: 0;margin-top: 0;");
        this.dialog.$wrapper.find('[data-fieldname="section_html"]').attr("style","margin-bottom: 0;");
        this.dialog.$wrapper.find('.modal-dialog').css("width", "90%");
        this.dialog.$wrapper.find('.modal-dialog').css("max-width", "1400px");
        this.dialog.$wrapper.find('.modal-content').css("height", "600px");

    },

    section_html: function() {
        let me = this;
        let wrapper = this.dialog.fields_dict.section_html.$wrapper.empty();
        let html = $(`<div class="row" id="PageList"></div>
            <style>
                div[data-fieldname="section_html"] #PageList .section-title{
                    padding: 30% 2%; text-align: center; height: 205px;
                }
                div[data-fieldname="section_html"] #PageList .section-item.active{
                    border: 1px solid #0c9e0c; background: #efefef1f; color: #0c9e0c;
                }
                div[data-fieldname="section_html"] #PageList .section-img{
                    position: relative; height: 203px;
                }
                div[data-fieldname="section_html"] #PageList .section-img img{
                    position: absolute; top: 50%; left: 50%; max-height: 190px;
                    transform: translate(-50%, -50%); vertical-align: middle;
                }
                div[data-fieldname="section_html"] #PageList .section-item{
                    margin-bottom: 10px; border: 1px solid #ddd; background: #f3f3f3; cursor:pointer;
                }
                div[data-fieldname="section_html"] #PageList .section-item p{
                    text-align: center;
                }
                li.active{background-color:#f3f3f3;}
               
                </style>`).appendTo(wrapper);
       
        let data = me.sections ? me.sections : me.templates;
        wrapper.find('#PageList').append("<div class='col-md-12' id='sec-right-content' style='padding-top: 15px;height: 510px;overflow-y: auto;'></div>");
        data.map(f => {
            let template = `<div class="section-title">${f.page_title}</div>`;
            if (f.image) {
                template = `<div class="section-img" ><img src="${f.image}" /></div><p>${f.page_title}</p>`
            }
            let item = $(`<div class="col-md-4 col-sm-6 col-xs-6" style="float:left" >
                    <div class="section-item">${template}</div>
                </div>`);
            wrapper.find('#PageList').find("#sec-right-content").append(item)
            item.click(function() {
                if(cur_frm.doc.page_title!="" && cur_frm.doc.page_title!=undefined){
                    me.selected_section = { 'template': f.name }
                    $(html).find('.section-item').removeClass('active');
                    $(item).find('.section-item').addClass('active');
                    frappe.confirm('Are you sure you want to proceed?',
                        () => {
                             frappe.call({
                                    method: 'go1_cms.go1_cms.doctype.proposal.proposal.import_sections_from_template',
                                    args: {
                                        'page_id': me.selected_section.template,
                                    },
                                    freeze: true,
                                    callback: function(r) {

                                        if (r.message) {
                                            var info = r.message.info;
                                            var mobile_sections = r.message.mobile_sections;
                                            var web_sections = r.message.web_sections;
                                            me.frm.doc.published = info.published
                                            me.frm.doc.page_type = info.page_type
                                            me.frm.doc.meta_title = info.meta_title
                                            me.frm.doc.meta_keywords = info.meta_keywords
                                            me.frm.doc.meta_description = info.meta_description
                                            me.frm.doc.use_page_builder = info.use_page_builder
                                            me.frm.doc.is_location_based = info.is_location_based
                                            if (info.content){
                                                me.frm.doc.content = info.content
                                            }
                                             if (info.header_component){
                                                me.frm.doc.header_component = info.header_component
                                            }
                                             if (info.footer_component){
                                                me.frm.doc.footer_component = info.footer_component
                                            }
                                            
                                            for (var i = 0; i < mobile_sections.length; i++) {
                                                var a = frappe.model.add_child(cur_frm.doc, "Mobile Page Section", "mobile_section");
                                                a.allow_update_to_style = mobile_sections[i].allow_update_to_style;
                                                a.content_type = mobile_sections[i].content_type;
                                                a.section = mobile_sections[i].section;
                                                a.section_title = mobile_sections[i].section_title;
                                                a.section_type = mobile_sections[i].section_type;
                                            }
                                             for (var i = 0; i < web_sections.length; i++) {
                                                var a = frappe.model.add_child(cur_frm.doc, "Mobile Page Section", "web_section");
                                                a.allow_update_to_style = web_sections[i].allow_update_to_style;
                                                a.content_type = web_sections[i].content_type;
                                                a.section = web_sections[i].section;
                                                a.section_title = web_sections[i].section_title;
                                                a.section_type = web_sections[i].section_type;
                                            }
                                            // me.frm.doc.mobile_section = r.message.mobile_sections
                                            // me.frm.doc.web_section = r.message.web_sections
                                            // cur_frm.save();
                                            me.frm.save();
                                            me.dialog.hide();
                                        }
                                    }
                                });

                        }, () => {
                            // action to perform if No is selected
                    })
                }
                else{
                    frappe.throw("Please enter the page title")
                }

                
            })
        })
         
        // wrapper.find('#PageList').slimScroll({
        //     height: 540
        // })
    }
});



// List Page Styles


var add_list_template = Class.extend({
    init: function(opts) {
        this.frm = opts.frm;
        this.make();
    },
    make: function() {
        let me = this;
        frappe.run_serially([
            () => {
               me.get_page_templates();
               
            },
            () => {
                me.make_dialog();
               
            }
        ])
    },
    get_page_templates: function() {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_list_page_templates',
            args: {
            },
            async: false,
            callback: function(r) {
                me.sections = r.message.templates;
            }
        })
    },
    
    make_dialog: function() {
        let me = this;
        let title = 'Choose List Style';
        this.dialog = new frappe.ui.Dialog({
            title: __(title),
            // fields: [{ "label": __("Enter Section Title"), "fieldname": "title_name", "fieldtype": "Data" }, { "fieldname": "section_html", "fieldtype": "HTML" }]
            fields: [{"fieldname": "section_html", "fieldtype": "HTML" }]

        });
        this.selected_section = [];
        this.dialog.show();
        this.section_html();
        this.dialog.$wrapper.find('.form-column.col-sm-12').css("padding","0");
        this.dialog.$wrapper.find('.form-section').attr("style","width: calc(100%);margin-left: 0px;padding-top: 0;margin-top: 0;");
        this.dialog.$wrapper.find('[data-fieldname="section_html"]').attr("style","margin-bottom: 0;");
        this.dialog.$wrapper.find('.modal-dialog').css("width", "90%");
        this.dialog.$wrapper.find('.modal-dialog').css("max-width", "1400px");
        this.dialog.$wrapper.find('.modal-content').css("height", "600px");

    },

    section_html: function() {
        let me = this;
        let wrapper = this.dialog.fields_dict.section_html.$wrapper.empty();
        let html = $(`<div class="row" id="PageList"></div>
            <style>
                div[data-fieldname="section_html"] #PageList .section-title{
                    padding: 30% 2%; text-align: center; height: 205px;
                }
                div[data-fieldname="section_html"] #PageList .section-item.active{
                    border: 1px solid #0c9e0c; background: #efefef1f; color: #0c9e0c;
                }
                div[data-fieldname="section_html"] #PageList .section-img{
                    position: relative; height: 203px;
                }
                div[data-fieldname="section_html"] #PageList .section-img img{
                    position: absolute; top: 50%; left: 50%; max-height: 190px;
                    transform: translate(-50%, -50%); vertical-align: middle;
                }
                div[data-fieldname="section_html"] #PageList .section-item{
                    margin-bottom: 10px; border: 1px solid #ddd; background: #f3f3f3; cursor:pointer;
                }
                div[data-fieldname="section_html"] #PageList .section-item p{
                    text-align: center;
                }
                li.active{background-color:#f3f3f3;}
               
                </style>`).appendTo(wrapper);
       
        let data = me.sections ? me.sections : me.templates;
        wrapper.find('#PageList').append("<div class='col-md-12' id='sec-right-content' style='padding-top: 15px;height: 510px;overflow-y: auto;'></div>");
        data.map(f => {
            let template = `<div class="section-title">${f.name}</div>`;
            if (f.image) {
                template = `<div class="section-img" ><img src="${f.image}" /></div><p>${f.name}</p>`
            }
            let item = $(`<div class="col-md-4 col-sm-6 col-xs-6" style="float:left" >
                    <div class="section-item">${template}</div>
                </div>`);
            wrapper.find('#PageList').find("#sec-right-content").append(item)
            item.click(function() {
                // if(cur_frm.doc.page_title!="" && cur_frm.doc.page_title!=undefined){
                    me.selected_section = { 'template': f.name }
                   
                    new columns_mapping({
                       frm: me.frm,
                       list_style:f.name,
                       list_style_image:f.image
                    });
                    me.dialog.hide();
                
            })
        })
         
        // wrapper.find('#PageList').slimScroll({
        //     height: 540
        // })
    }
});

//mapping columns

var columns_mapping = Class.extend({
    init: function(opts) {
        this.frm = opts.frm;
        this.list_style = opts.list_style;
        this.list_style_image = opts.list_style_image;
        this.make();
    },
    make: function() {
        let me = this;
        frappe.run_serially([
            () => {
               me.get_section_columns();
               
            },
            () => {
                me.make_dialog();
               
            }
        ])
    },
    get_section_columns: function() {
        let me = this;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.proposal.proposal.get_section_columns',
            args: {
                section:me.list_style,
                dt:me.frm.doc.document

            },
            async: false,
            callback: function(r) {
                console.log(r.message)
                me.t_fields = r.message.t_fields;
            }
        })
    },
    
    make_dialog: function() {
        let me = this;
        let title = 'Columns Mapping';
        this.dialog = new frappe.ui.Dialog({
            title: __(title),
            // fields: [{ "label": __("Enter Section Title"), "fieldname": "title_name", "fieldtype": "Data" }, { "fieldname": "section_html", "fieldtype": "HTML" }]
            fields: [{"fieldname": "section_html", "fieldtype": "HTML" }]

        });
        this.selected_section = [];
        this.dialog.show();
        this.section_html();
        this.dialog.$wrapper.find('.form-column.col-sm-12').css("padding","0");
        this.dialog.$wrapper.find('.form-section').attr("style","width: calc(100%);margin-left: 0px;padding-top: 0;margin-top: 0;");
        this.dialog.$wrapper.find('[data-fieldname="section_html"]').attr("style","margin-bottom: 0;");
       

    },

    section_html: function() {
        let me = this;
        let wrapper = this.dialog.fields_dict.section_html.$wrapper.empty();
        let html = $(`<div class="row" id="ColumnList" style="padding: 0 15px;"></div>`).appendTo(wrapper);
        let data = me.t_fields;
        // wrapper.find('#ColumnList').append("<div class='col-md-12' id='sec-right-content' style='padding-top: 15px;height: 510px;overflow-y: auto;'></div>");
        wrapper.find('#ColumnList').append("<table style='margin: 5px 0;' class='table table-bordered' ><thead><tr><th>List Column</th><th>Column Map</th></tr></thead><tbody id='colsdata'></tbody></table>");
        data.map(f => {
            var drp_html = "<select class='form-control'>";
            for (var i = 0; i < f.d_fields.length; i++) {
               drp_html +='<option value="'+f.d_fields[i].fieldname+'">'+f.d_fields[i].label+'</option>';
            }
            drp_html+="</select>"
            let template = `<td dtype='${f.field_key}'>${f.field_label}</td><td>${drp_html}</td>`;
            let item = $(`<tr>
                    ${template}</tr>`);
            wrapper.find('#ColumnList').find("#colsdata").append(item)
           me.dialog.set_primary_action(__('Save'), function() {
                 var check_vals = true;
                 var col_vals = []
                 wrapper.find("#colsdata tr").each(function(){
                     if($(this).find("td:eq(1)").find("select").val()=="" || $(this).find("td:eq(1)").find("select").val()==undefined){
                         check_vals = false;
                     }
                     else{
                       var f_name = $(this).find("td:eq(0)").attr("dtype");
                       var d_obj = {};
                       d_obj[f_name] = $(this).find("td:eq(1)").find("select").val();
                       col_vals.push(d_obj)  
                     }
                 })
                 if(!check_vals){
                     frappe.msgprint("Please fill all columns");
                 }
                 else{
                     me.frm.doc.columns_mapping = JSON.stringify(col_vals)
                     me.frm.doc.list_style = me.list_style;
                     me.frm.doc.list_style_image = me.list_style_image;
                     $("#list_style_image").remove();
                     var img_html = '<img id="list_style_image" src="'+me.list_style_image+'" style="margin-top: 10px;"/>';
                      $('button[data-fieldname="choose_list_style"]').parent().append(img_html);
                     me.dialog.hide();
                 }
             });
        })
         
       
    }
});