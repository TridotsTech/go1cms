// Copyright (c) 2018, info@valiantsystems.com and contributors
// For license information, please see license.txt
frappe.require("assets/go1_cms/js/uppy.min.css");
frappe.require("assets/go1_cms/js/uppy.min.js");
frappe.require("assets/go1_cms/js/jquery-sortable.js");
frappe.ui.form.on('Business', {
    refresh: function(frm) {
        $('div[data-fieldname="geolocation_60"] div.map-wrapper.border').find('div .leaflet-control-container div.leaflet-bottom').hide();
        $('div[data-fieldname="geolocation_62"] div.map-wrapper.border').find('div .leaflet-control-container div.leaflet-bottom').hide();
        frappe.call({
            method: "go1_cms.go1_cms.doctype.business.business.get_timeZone",
            callback: function(data) {
                frappe.all_timezones = data.message.timezones;
                frm.set_df_property("time_zone", "options", frappe.all_timezones);
            }
        });
        frappe.call({
            method: "go1_cms.go1_cms.doctype.business.business.get_print_formats",
            callback: function(data) {
                frappe.order_print_formats = data.message;
                frm.set_df_property("print_format", "options", frappe.order_print_formats);
            }
        });
        $('button[data-fieldname="add_image"]').css("height", "27px");
        $('button[data-fieldname="add_image"]').addClass('btn-primary');
        $('button[data-fieldname="add_menu"]').css("height", "27px");
        $('button[data-fieldname="add_menu"]').addClass('btn-primary');
        frm.trigger('multi_upload')
        // $(cur_frm.$wrapper).find('input').on('change',function(){
        // })
        if(frm.doc.__islocal){
            frm.set_value('parent_business', '');
            frm.set_value('old_parent', '');
        } 
    },
    after_save: function(frm) {
        cur_frm.reload_doc();
    },
    add_image: function(frm) {
        if (frm.doc.__islocal)            frappe.throw('Please save the document and then try uploading images')
        localStorage.setItem('randomuppy', ' ');
        frm.events.generate_image_html(frm, 'business_images')
        frm.product_image_list = frm.doc.business_images;
        frm.events.image_upload(frm, frm.doctype, frm.doc.name, 'business_images')
    },
    add_menu: function(frm) {
        if (frm.doc.__islocal)
            frappe.throw('Please save the document and then try uploading images')
        localStorage.setItem('randomuppy', ' ');
        frm.events.generate_image_html(frm, 'menu_images')
        frm.events.image_upload(frm, frm.doctype, frm.doc.name, 'menu_images')
    },
    image_upload: function(frm, link_doctype, link_name, parentfield) {
        let selected_image_list = [];
        let random = Math.random() * 100;
        localStorage.setItem("upload_tab", "Product Image");
        localStorage.setItem('randomuppy', ' ');
        let imgDialog;
        $('body').find('.modal').each(function() {
            $(this).remove()
        })
        frm.trigger('generate_image_html')
        let randomuppy = Math.random() * 100
        localStorage.setItem('randomuppy', parseInt(randomuppy))
        let template = '<div id="drag-drop-area' + parseInt(randomuppy) + '"><div class="loader">Loading.....</div></div>';
        imgDialog = new frappe.ui.Dialog({
            title: __('Attachments'),
            fields: [
                { fieldtype: 'HTML', fieldname: 'files_list', options: frm.files_html },
                { fieldtype: 'Column Break', fieldname: 'clb' },
                { fieldtype: 'HTML', fieldname: 'uploader', options: template }
            ],
            primary_action_label: __('Close')
        });
        imgDialog.$wrapper.find('.modal-dialog').css("width", "1030px");
        $('.modal-dialog').css("width", "1070px !important");
        imgDialog.show();
        frappe.require("assets/go1_cms/js/fileupload.js", function() {
            setTimeout(function() {
                $(imgDialog.$wrapper).find('.loader').remove();
                // upload_files(parseInt(randomuppy),parentfield) 
                upload_files(parseInt(randomuppy), link_doctype, link_name, parentfield, 'Business Images')
            }, 600)
        });
        imgDialog.get_close_btn().on('click', () => {
            this.on_close && this.on_close(this.item);
        });
        $(imgDialog.$wrapper).find('.img-close').on('click', function() {
            let me = this;
            cur_frm.imgid = $(me).attr("data-id");
            frappe.confirm(__("Do you want to delete the image?"), () => {
                frappe.call({
                    method: 'go1_cms.go1_cms.api.delete_current_img',
                    args: {
                        childname: cur_frm.imgid,
                        doctype: cur_frm.doctype
                    },
                    async: false,
                    callback: function(data) {
                        $(imgDialog.$wrapper).find('li[data-id="' + cur_frm.imgid + '"]').remove()
                        $(".menu-btn-group .dropdown-menu li a").each(function() {
                            if ($(this).text() == "Reload") {
                                $(this).click();
                                frappe.show_alert(__("Image deleted !"));
                            }
                        });
                        frm.reload_doc();
                    }
                })
            });
        })
        $(imgDialog.$wrapper).find('#saveImages').click(function() {
            let length = $(imgDialog.$wrapper).find('div[data-fieldname="files_list"] ul li').length;
            if (length > 0) {
                let count = 0;
                $(imgDialog.$wrapper).find('div[data-fieldname="files_list"] ul li').each(function() {
                    let childname = $(this).attr('data-id');
                    count = count + 1;
                    let image_name = $(this).find('input[name="image_name"]').val();
                    let primary = $(this).find('input[name="is_primary"]:checked').val()
                    let is_primary = 0;
                    if (primary == 'on')
                        is_primary = 1;
                    frappe.model.set_value('Business Images', childname, 'idx', count)
                    frappe.model.set_value('Business Images', childname, 'image_name', image_name)
                    frappe.model.set_value('Business Images', childname, 'is_primary', is_primary)
                })
                cur_frm.save();
                imgDialog.hide();
            } else {
                frappe.throw('Please add images to edit them')
            }
        })
        $(imgDialog.$wrapper).find('.img-edit').click(function() {
            let me = this;
            let imgid = $(me).attr("data-id");
            let check_data = frm.doc.business_images.find(obj => obj.name == imgid);
            $(imgDialog.$wrapper).find('#sortable li[data-id="' + imgid + '"]').find('.imageName').hide();
            $(imgDialog.$wrapper).find('#sortable li[data-id="' + imgid + '"]').find('.editImage').show();
        })
        $(imgDialog.$wrapper).find('div[data-fieldname="files_list"] ul').sortable({
            items: '.image-element',
            opacity: 0.7,
            distance: 30
        });
        $(imgDialog.$wrapper).find('input[name="is_primary"]').on('change', function() {
            let id = $(this).attr('data-id');
            $(imgDialog.$wrapper).find('input[name="is_primary"]').each(function() {
                if ($(this).attr('data-id') != id) {
                    $(this).removeAttr('checked')
                }
            })
        })
    },
    multi_upload: function(frm) {
        $(frm.fields_dict['image_html'].wrapper).html("");
        if (frm.doc.business_images) {
            var img_html = '<div class="row" id="img-gallery">';
            $(frm.doc.business_images).each(function(i, v) {
                let checked = "";
                img_html += '<div id="div' + v.idx + '" title="' + v.name + '" class="sortable-div div_' + v.name + '"><div class="col-md-2" \
                id="drag' + v.idx + '"><div style="padding: 15px; class="">\
                <img class="img-name" src="' + v.thumbnail + '" title="' + v.image_name + '" id="' + v.name1 + '" \
                style="height:100px;"></div></div></div>';
            })
            img_html += '</div>';
            $(frm.fields_dict['image_html'].wrapper).html(img_html);
        }
    },
    generate_image_html: function(frm, field) {
        let html = '<div class="uploadFiles"><div class="title">Uploaded Files<button id="saveImages" class="btn btn-primary" style="float:right;margin-top: -4px;">Save</button></div><ul id="sortable">'
        $(frm.doc[field]).each(function(i, j) {
            let checked = "";
            if (j.is_primary == 1)
                checked = 'checked="checked"'
            html += '<li data-id="' + j.name + '"><div class="row"><div class="col-md-4 image-element"><img src="' + j.thumbnail + '" />\
            </div><div class="col-md-6 img-name"><div class="imageName">' + j.image_name + '</div><div class="editImage" style="display:none;"><div>\
            <input type="text" name="image_name" placeholder="Image Alternate Text" value="' + j.image_name + '" /></div><div><label style="font-weight:400;font-size:12px;"><input type="checkbox" data-id="' + j.name + '" name="is_primary" ' + checked + '/> <span>Mark as Primary?</span></label></div></div></div><div class="col-md-2 img-name"><a class="img-edit" data-id="' + j.name + '">\
            <span class="fa fa-edit"></span></a><a class="img-close" data-id="' + j.name + '">\
            <span class="fa fa-trash"></span></a></div></div></li>'
        })
        html += '</ul></div>';
        frm.files_html = html;
    },
    business_address: function (frm) {
        frm.trigger('change_lat_lng');
    },
    city: function (frm) {
        frm.trigger('change_lat_lng');
    },
    country: function (frm) {
        frm.trigger('change_lat_lng');
    },
    state: function (frm) {
        frm.trigger('change_lat_lng');
    },
    zip_code: function (frm) {
        frm.trigger('change_lat_lng');
    },
    change_lat_lng: function (frm) {
        frm.set_value({ 'latitude': '', 'longitude': '' });
    }
});

frappe.ui.form.on("Business", "restaurant_location1", function(frm, cdt, cdn) {
    // cur_frm.clear_table(restaurant_location1);
});

frappe.ui.form.on("Business", "restaurant_name", function(frm, cdt, cdn) {
    if (frm.doc.restaurant_name) {
        if (frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.single_vendor)) {
            frappe.call({
                method: "go1_cms.go1_cms.doctype.business.business.get_all_weekdays",
                args: {

                },
                callback: function(r) {
                    var opening = frm.doc.opening_hour
                    if (opening && opening.length <= 0) {
                        $.each(r.message, function(i, d) {

                            var row = frappe.model.add_child(frm.doc, "Opening Hour", "opening_hour");
                            row.day = d.name;
                        });
                    }
                    refresh_field("opening_hour");
                    $('div[data-fieldname="opening_hour"] .form-grid .grid-body .grid-footer').find('.grid-add-row').hide();
                    $('.grid-add-row').hide();
                }
            });
        }

    }


});

frappe.ui.form.on("Business", "is_percentage", function(frm) {
    if (frm.doc.is_percentage == 1) {
        frm.set_value("commission_amount", "");
    }
});

frappe.ui.form.on('Business', {
    refresh: function(frm) {
        frm.set_query("state", function() {
            return {
                "filters": {
                    "country": frm.doc.country
                }
            }
        });
        frm.set_query("country", function() {
            return {
                "filters": {
                    "enabled": 1
                }
            }
        });
        frm.set_query("category", "business_category", function(doc, cdt, cdn) {
            return {
                'filters': {
                    "parent_product_category": ''
                }
            };
        });
        frm.set_query('business_area', function(){
            return {
                "filters": {
                    "location": frm.doc.business_location
                }
            }
        })
    }
})

// select multiple cuisines
frappe.ui.form.on('Business', {
    refresh: function(frm) {
        if (frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant) || frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.deals_and_offers)) {
            frm.trigger('get_available_cuisines')
            $('div[data-fieldname="table_37"] .grid-add-multiple-rows').removeClass('hidden')
            $('div[data-fieldname="table_37"] .grid-add-row').addClass('hide')
            $('div[data-fieldname="table_37"] .grid-add-multiple-rows').addClass('addCuisines')
            // $('.addCuisines').click(function() {
                frappe.run_serially([
                    () => { frm.trigger('get_available_cuisines') },
                    () => {
                        if (frm.doc.business_category){
                            // frm.trigger('cuisine_dialog')
                            frm.trigger('cuisine_multiselect');
                        }
                        else{
                            if(frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant)){
                                // frm.trigger('cuisine_dialog')
                                frm.trigger('cuisine_multiselect');
                            }
                            else
                                frappe.throw('Please select category')
                        }
                    }
                ]);
            // })
        }
    },
    get_available_cuisines: function(frm) {
        let category_list = ''
        if (frm.doc.business_category) {
            $(frm.doc.business_category).each(function(k, v) {
                category_list = category_list + '"' + v.category + '",';
            })
        } else{
            category_list = ','
        }
        category_list = category_list.slice(0, -1)
        if (category_list != '' || frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant)) {
            frappe.call({
                method: 'go1_cms.go1_cms.doctype.business.business.get_all_cuisines',
                args: {
                    category_list: category_list
                },
                async: false,
                callback: function(data) {
                    frm.cuisines = data.message;
                    let count = 3;
                    if (frm.cuisines.length > 30)
                        count = 4;
                    let html = '<ul class="cuisineList" style="list-style: none;padding-inline-start: 10px;column-count: ' + count + ';">'
                    $(data.message).each(function(k, v) {
                        let check;
                        let checked = ''
                        if (frm.doc.table_37) {
                            check = frm.doc.table_37.find(obj => obj.cuisine == v.name)
                            if (check)
                                checked = 'checked="checked"'
                        }
                        html += '<li><label style="font-weight: normal;"><input type="checkbox" value="' + v.name + '" name="cuisines" ' + checked + ' /> ' + v.name + '</label></li>';
                    });
                    html += '</ul>'
                    frm.cuisine_html = html;
                }
            })
        }
    },
    cuisine_dialog: function(frm) {
        let title = 'Services';
        if (frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant)) {
            title = 'Cuisines';
        }
        let dialog = new frappe.ui.Dialog({
            title: __(title),
            fields: [{ fieldtype: 'HTML', fieldname: 'cuisines_list', options: frm.cuisine_html }]
        });
        $('.modal[data-types="cuisines"').each(function() {
            $(this).remove();
        })
        dialog.show();
        $(dialog.$wrapper).attr('data-types', 'cuisines')
        if (frm.cuisines.length > 30)
            dialog.$wrapper.find('.modal-dialog').css("min-width", "827px");
        dialog.set_primary_action(__('Save'), function() {
            frm.doc.table_37 = [];
            $('.cuisineList li input[type="checkbox"]:checked').each(function() {
                let row = frappe.model.add_child(frm.doc, "Business Cuisine", "table_37");
                row.cuisine = $(this).val();
            })
            cur_frm.refresh_field('table_37');
            $('div[data-fieldname="table_37"] .grid-add-row').addClass('hide')
            if (!frm.doc.__islocal)
                cur_frm.save()
            dialog.hide();
        })
    },
    cuisine_multiselect: function(frm){
        $(frm.get_field('table_37').wrapper).empty();
        frm.cuisine_list = frappe.ui.form.make_control({
            parent: frm.fields_dict.table_37.$wrapper,
            df: {
                fieldname: "cuisine_list",
                fieldtype: "MultiCheck",
                columns: 4,
                get_data: () => {
                    let active_tags = (frm.doc.table_37);
                    return frm.cuisines.map(val => {
                        return {
                            label: val.name,
                            value: val.name,
                            checked: active_tags.find(obj => obj.cuisine == val.name) ? true : false
                        };
                    });
                }
            },
            render_input: true
        });
        frm.cuisine_list.refresh_input();
    },
    validate: function(frm){
        frm.doc.table_37 = [];
        if(frm.cuisine_list){
            let values = frm.cuisine_list.get_value();
            $(values).each(function(k, v){
                frm.add_child('table_37', {'cuisine': v})
            });
            frm.refresh_field('table_37');
        }
    }
})
// restaurant settings
frappe.ui.form.on('Business', {
    refresh: function(frm) {
        if (frm.doc.__islocal) {
            if (frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant) || frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.deals_and_offers)) {
                if (!frm.doc.opening_hour) {
                    frappe.call({
                        method: 'frappe.client.get_list',
                        args: {
                            'doctype': 'Week Day',
                            'fields': ['name'],
                            'order_by': 'displayorder'
                        },
                        callback: function(data) {
                            if (data.message) {
                                $(data.message).each(function(k, v) {
                                    let row = frappe.model.add_child(cur_frm.doc, 'Opening Hour', 'opening_hour', k + 1)
                                    row.day = v.name;
                                    row.status = 'Open';
                                    row.from_hrs = '';
                                    row.to_hrs = '';
                                });
                                cur_frm.refresh_field('opening_hour')
                            }
                        }
                    })
                }
            }
            if (frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant)) {
                frm.set_value('time_zone', frappe.boot.sysdefaults.time_zone)
                frm.set_value('online_order_to_start_delivery', 15)
                frm.set_value('online_order_to_end_delivery', 15)
                frm.set_value('order_online_time_difference_delivery', 30)                
                frm.set_df_property('time_zone', 'reqd', 1)
                frm.set_value('online_order_to_start_pickup', 15)
                frm.set_value('online_order_to_end_pickup', 15)
                frm.set_value('order_online_time_difference_pickup', 30)                
            }
        }
        if(frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant))
            frm.trigger('check_general_settings')
    },
    delivery: function(frm){
        frm.set_df_property('online_order_to_start_delivery', 'reqd', 1 ? frm.doc.delivery : 0)
        frm.set_df_property('online_order_to_end_delivery', 'reqd', 1 ? frm.doc.delivery : 0)
        frm.set_df_property('order_online_time_difference_delivery', 'reqd', 1 ? frm.doc.delivery : 0)
    },
    pickup: function(frm){
        frm.set_df_property('online_order_to_start_pickup', 'reqd', 1 ? frm.doc.pickup : 0)
        frm.set_df_property('online_order_to_end_pickup', 'reqd', 1 ? frm.doc.pickup : 0)
        frm.set_df_property('order_online_time_difference_pickup', 'reqd', 1 ? frm.doc.pickup : 0)
    },
    check_general_settings: function(frm){
        let business = frm.doc.name;
        if(frm.doc.is_group && frm.doc.parent_business)
            business = frm.doc.parent_business;
        frappe.call({
            method:'go1_cms.go1_cms.api.get_general_settings',
            args:{
                business: business
            },
            callback: function(r){
                if(r.message){                    
                    if(r.message.order_type == 'Delivery' || r.message.order_type == 'Pickup & Delivery'){
                        if(frm.doc.__islocal)
                            frm.set_value('delivery', 1)
                        // frm.set_df_property('delivery','hidden',0)
                    } else{
                        // frm.set_df_property('delivery','hidden',1)
                    }
                    if(r.message.order_type == 'Pickup' || r.message.order_type == 'Pickup & Delivery'){
                        if(frm.doc.__islocal)
                            frm.set_value('pickup', 1)
                        // frm.set_df_property('pickup','hidden',0)
                    } else{
                        // frm.set_df_property('pickup','hidden',1)
                    }
                    if (r.message.enable_tip) {
                        frm.toggle_display(['tips_section'], true);
                        let options = [];
                        $(r.message.tip_percent).each(function (k, v) {
                            options.push({ 'label': v.tip_label, 'value': v.tip_percent })
                        })
                        frm.set_df_property('default_tip_pickup', 'options', options);
                        frm.set_df_property('default_tip_delivery', 'options', options);
                    } else {
                        frm.toggle_display(['tips_section'], false);
                    }               
                }
            }
        })
    },
    manage_payments: function(frm){
        if(frm.doc.__islocal){
            frappe.throw('Please save the document before proceeding.')
        } else{
            if(frm.doc.__unsaved){
                cur_frm.save();
            }
            frappe.set_route('List','Business Payment Gateway Settings',{'business':frm.doc.name})
        }
    }
});
// multi branch
frappe.ui.form.on('Business', {
    refresh: function(frm) {
        if (frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.multi_store)) {
            if (frm.doc.is_group == 1) {
                frm.set_intro(__('This is a template business and transactions cannot be made against this business'))
                frm.add_custom_button(__("Add Branch"), function() {
                    frm.trigger('add_branch')
                });
            }
        }
    },
    add_branch: function(frm) {
        let dialog = new frappe.ui.Dialog({
            title: __("Add Branch"),
            fields: [
                { "fieldname": "business_name", "label": __("Business Name"), "fieldtype": "Data", "reqd": 1, "default": frm.doc.restaurant_name },
                { "fieldname": "business_phone", "label": __("Business Phone"), "fieldtype": "Small Text", "reqd": 1 },
                { "fieldname": "contact_person", "label": __("Contact Person"), "fieldtype": "Data", "reqd": 1 },
                { "fieldname": "contact_number", "label": __("Contact Number"), "fieldtype": "Data", "options": "Phone", "reqd": 1 },
                { "fieldname": "contact_email", "label": __("Contact Email"), "fieldtype": "Data", "options": "Email", "reqd": 1 },
                { "fieldname": "business_address", "label": __("Business Address"), "fieldtype": "Data", "reqd": 1 },
                { "fieldname": "city", "label": __("City"), "fieldtype": "Data", "reqd": 1 }
            ]
        })
        dialog.show();
        dialog.set_primary_action(__("Add"), function() {
            let values = dialog.get_values();
            values.parent_business = frm.doc.name;
            values.is_group = 0;
            frappe.call({
                method: 'go1_cms.go1_cms.doctype.business.business.add_branch',
                args: values,
                callback: function(r) {
                    if (r.message) {
                        dialog.hide();
                        frappe.set_route('Form', 'Business', r.message)
                    }
                }
            })
        })
    }
})
// pos settings
frappe.ui.form.on('Business', {
    refresh: function(frm) {
        frappe.call({
            method: 'go1_cms.go1_cms.api.check_PosSettings',
            args: {},
            async: false,
            callback: function(data) {
                if (data.message.enable_pos == 1) {
                    frm.toggle_display(['pos_settings'],true)
                } else {
                    frm.toggle_display(['pos_settings'],false)                    
                }
            }
        })
    }
});
// create sample data
frappe.ui.form.on('Business', {
    refresh: function(frm) {
        if (frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.saas) || frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.multi_store) || frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.multi_vendor)) {
            if (has_common(frappe.user_roles, ['System Manager'])) {
                if (!frm.doc.sample_data && !frm.doc.__islocal) {
                    frm.add_custom_button(__("Create Default Records"), function() {
                        frm.trigger('create_records')
                    })
                }
                if (!frm.doc.sample_data && !frm.doc.__islocal) {
                    frm.add_custom_button(__("Import From Business"), function() {
                        frm.trigger('choose_business')
                    })
                }
                if (!frm.doc.__islocal) {
                    frm.add_custom_button(__("Import Data from Template"), function() {
                        frm.trigger('create_dummy_data')
                    })
                }
            }
            if(has_common(frappe.user_roles, ['Admin'])) {
                if (!frm.doc.sample_data && !frm.doc.__islocal) {
                    frm.add_custom_button(__("Import From Business"), function() {
                        frm.trigger('choose_business')
                    })
                }
            }
            if (! has_common(frappe.user_roles, ['System Manager']) && has_common(frappe.user_roles, ['Vendor'])) {
                if (frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant)){
                    setTimeout(function() {
                        $('[type="checkbox"]').attr("disabled","disabled")
                        $('[type="text"]').attr("disabled","disabled")
                        $('select').attr("disabled","disabled")
                    },1000);
                }
            }
        }
    },
    create_records: function(frm){
        frm.call('insert_sample_records').then(r=>{
            if(r.message && r.message.status == 'Success'){
                show_alert('Sample Records Created!', 5);
                frm.reload_doc();
            }
        })
    },
     create_dummy_data: function(frm){
        var dialog2 = new frappe.ui.Dialog({
            title: __('Select Vertical'),
            fields: [
                { fieldtype: "Link", label: __("Vertical"), fieldname: "select_business",options: "Verticals" }
            ],
            primary_action_label: __('Close')
        });
       dialog2.set_primary_action(__('Save'), function() {
        var values = dialog2.get_values();
        // var favorite = $("input[name='business']:checked").val();
        // var favorite = [];
        //     $.each($("input[name='business']:checked"), function(){
        //         favorite.push($(this).val());
        //     });
        // let business = frm.doc.name;
        frappe.show_progress("Sample Data Importing...", 90,100,'Please wait');
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.business.business.insert_dummy_data',
            args: {
                "checked_business": values.select_business,
                "business": frm.doc.name,
                "business_name": frm.doc.restaurant_name
            },
            async: false,
            callback: function(r) {
                dialog2.hide();
                if(r.message && r.message.status == 'Success'){
                show_alert('Sample Data Created!');
                }
            }
        })
       })
       dialog2.show();
        // frm.call('insert_dummy_records').then(r=>{
        //     if(r.message && r.message.status == 'Success'){
        //         show_alert('Sample Data Created!');
        //     }
        // })
    },
    choose_business: function(frm){
       var dialog1 = new frappe.ui.Dialog({
            title: __('Select Business'),
            fields: [
                { fieldtype: "Link", label: __("Business"), fieldname: "business", options: "Business",
                onchange: function(e) {
                    if(this.value){
                      frappe.call({
                            method: 'go1_cms.go1_cms.doctype.business.business.get_business_data_summary',
                            args: {
                                "selected_business": this.value,
                                "cur_business": frm.doc.name
                            },
                            async: false,
                            callback: function(data) { 
                                if(data.message){
                                    let html ="<div>";
                                    html +='<div class="col-md-12 col-sm-12 col-xs-12" style="border: #dddddd solid 1px;">\
                                    <h4>Summary</h4> \
                                    <div class="row">\
                                        <div class="col-md-4 col-sm-4 col-xs-12">\
                                            <h5>Total Products:</h5>\
                                        </div>\
                                        <div class="col-md-2 col-sm-2 col-xs-12">\
                                            <h5>:</h5>\
                                        </div>\
                                        <div class="col-md-6 col-sm-6 col-xs-12">\
                                            <div class="detail_content" style="padding: 10px;">'+data.message.product_count+'</div>\
                                        </div>\
                                    </div>\
                                    <div class="row">\
                                        <div class="col-md-4 col-sm-4 col-xs-12">\
                                            <h5>Total Categories:</h5>\
                                        </div>\
                                        <div class="col-md-2 col-sm-2 col-xs-12">\
                                            <h5>:</h5>\
                                        </div>\
                                        <div class="col-md-6 col-sm-6 col-xs-12">\
                                            <div class="detail_content" style="padding: 10px;">'+data.message.product_category+'</div>\
                                        </div>\
                                    </div>\
                                     <div class="row">\
                                        <div class="col-md-4 col-sm-4 col-xs-12">\
                                            <h5>No. of Attachments</h5>\
                                        </div>\
                                        <div class="col-md-2 col-sm-2 col-xs-12">\
                                            <h5>:</h5>\
                                        </div>\
                                        <div class="col-md-6 col-sm-6 col-xs-12">\
                                            <div class="detail_content" style="padding: 10px;">'+data.message.attached_files+'</div>\
                                        </div>\
                                    </div>\
                                    </div>'
                                    html +="</div>";                                   
                                    var wrapper = dialog1.fields_dict.summary_html.$wrapper;
                                    wrapper.empty();
                                    wrapper.html(html);
                                }
                            }
                        })
                      }
                    } 
                },
                { fieldtype: "HTML", label: __("Summary"), fieldname: "summary_html"}
            ],
            primary_action_label: __('Close')
        });
       dialog1.set_primary_action(__('Import'), function() {
        var value = dialog1.get_values();
        // let business = frm.doc.name;
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.business.business.insert_business_products1',
            args: {
                "selected_business": value.business,
                "cur_business": frm.doc.name
            },
            async: false,
            callback: function(data) {
                dialog1.hide();
                //updated by sivaranjnai
                frappe.msgprint({
                    title: __('Import Started'),
                    indicator: 'orange',
                    message: __('Data import is scheduled and it will take some time.')
                });
                // frappe.call({
                //             method: 'go1_cms.go1_cms.doctype.business.business.get_business_data_summary',
                //             args: {
                //                 "selected_business": value.business,
                //                 "cur_business": frm.doc.name
                //             },
                //             async: false,
                //             callback: function(data) { 
                //                 if(data.message){
                //                     // let htmls = '<span>Data imported successfully!<ul><li></li><li></li><li></li></ul></spapn>'
                //                     frappe.msgprint({
                //                         title: __('Success'),
                //                         indicator: 'green',
                //                         message: __('Data imported successfully!')
                //                     });
                //                 }
                //             }
                //         })
            }
        })
       })
       dialog1.show();
    }
});
// enabling payment methods based on order type for restaurants
frappe.ui.form.on('Business',{
    refresh: function(frm){
        let saas = frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.saas);
        let restaurant = frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant);
        if(restaurant){
            if(frm.doc__islocal){
                frm.toggle_display(['payment_options'], false);
            } else{
                frm.trigger('payment_options_html');
            }
        } else {
            frm.toggle_display(['payment_options'], false);
        }
    },
    payment_options_html: function(frm){
        frappe.run_serially([
            ()=>{
                frm.trigger('get_payment_methods');
            },
            ()=>{
                frm.trigger('payment_options');
            }
        ])
    },
    get_payment_methods: function(frm){
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.business.business.get_payment_methods',
            args:{
                business: frm.doc.name,
                custom_payments: frm.doc.custom_payments
            },
            async: false,
            callback: function(r){
                if(r.message){
                    frm.payment_methods = r.message;
                }
            }
        })
    },
    payment_options: function(frm){
        let wrapper = $(frm.get_field('payment_options').wrapper).empty();
        let html = $(`<div>
            <h4>${__("Payment Methods")}</h4>
            <div>${__("Select the payment methods for each order type.")}</div>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>${__("Order Type")}</th>
                        <th>${__("Payment Methods")}</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>`).appendTo(wrapper);
        let payment_options = {};
        if(frm.doc.payment_options)
           payment_options = JSON.parse(frm.doc.payment_options);
        if(frm.doc.pickup || frm.doc.delivery){
            if(frm.doc.pickup){
                let row = $(`<tr><td style="width: 20%;">${__("Pickup")}</td><td class="paymethods pickupmethods"></td></tr>`);
                let opts = [];
                if(payment_options['pickup'])
                    opts = payment_options.pickup.split(',');
                if(frm.payment_methods){
                    let paymethods = '';
                    frm.payment_methods.map(f=>{
                        let check = '';
                        if($.inArray(f.name, opts) > -1)
                            check = 'checked="checked"';
                        paymethods += `<div class="checkbox unit-checkbox col-sm-12">
                        <label>
                            <input type="checkbox" ${check} value="${f.name}">				
                            <span class="label-area small" data-name="${f.name}">${f.payment_method}</span>
                        </label>
                    </div>`;
                    });
                    row.find('.paymethods').append(paymethods);
                    html.find('tbody').append(row);
                }
            }
            if(frm.doc.delivery){
                let row = $(`<tr><td style="width: 30%;">${__("Delivery")}</td><td class="paymethods deliverymethods"></td></tr>`);
                let opts = [];
                if(payment_options['delivery'])
                    opts = payment_options.delivery.split(',');
                if(frm.payment_methods){
                    let paymethods = '';
                    frm.payment_methods.map(f=>{
                        let check = '';
                        if($.inArray(f.name, opts) > -1)
                            check = 'checked="checked"';
                        paymethods += `<div class="checkbox unit-checkbox col-sm-12">
                        <label>
                            <input type="checkbox" ${check} value="${f.name}">				
                            <span class="label-area small" data-name="${f.name}">${f.payment_method}</span>
                        </label>
                    </div>`;
                    });
                    row.find('.paymethods').append(paymethods);
                    html.find('tbody').append(row);
                }
            }
        } else{
            html.find('tbody').append(`<tr><td colspan="2">${__("Please enable either pickup or delivery")}</td></tr>`);
        }
        $(wrapper).find('.pickupmethods').find('input[type=checkbox]').change(function(){
            let list = [];
            $(wrapper).find('.pickupmethods').find('input[type=checkbox]:checked').each(function(){
                list.push(this.value);
            });
            payment_options.pickup = list.join();
            frm.set_value('payment_options', JSON.stringify(payment_options));
        });
        $(wrapper).find('.deliverymethods').find('input[type=checkbox]').change(function(){
            let list = [];
            $(wrapper).find('.deliverymethods').find('input[type=checkbox]:checked').each(function(){
                list.push(this.value);
            });
            payment_options.delivery = list.join();
            frm.set_value('payment_options', JSON.stringify(payment_options));
        });
    }
});
// autocomplete settings for restaurant
frappe.ui.form.on('Business', {
    refresh: function (frm) {
        let saas = frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.saas);
        let restaurant = frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant);
        frm.__has_website = 0;
        if(restaurant && !frm.doc.__islocal){
            if(saas) {
                frappe.call({
                    method: 'go1_cms.go1_cms.doctype.business.business.get_website_details',
                    args: {
                        business: frm.doc.name
                    },
                    callback: function(r) {
                        if(r.message && r.message.has_web == 1)
                            frm.__has_website = 1;
                        frm.trigger('auto_complete_json');
                    }
                })
            } else {
                frm.trigger('auto_complete_json');
            }
        }
    },
    auto_complete_json: function(frm) {
        let wrapper = $(frm.get_field('auto_complete_json').wrapper).empty();
        $(`<table class="table table-bordered">
                <thead>
                    <tr>
                        ${frm.__has_website == 1 ? `<th>${__('Website Type')}</th>` : ''}
                        <th>${__('Shipping Method')}</th>
                        <th>${__('Auto Complete After Status')}</th>
                        <th>${__('Auto Complete After Order Time (In Minutes)')}</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>`).appendTo(wrapper);
        frm.auto_complete_list = [];
        if(frm.doc.auto_complete_json) {
            try {
                frm.auto_complete_list = JSON.parse(frm.doc.auto_complete_json);
            } catch(e) {
                frm.auto_complete_list = [];
            }
        }        
        let website_type = [];
        if(frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.multi_vendor))
            website_type.push('Marketplace');
        if(frm.__has_website)
            website_type.push('Website');
        if(website_type.length == 0 && frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.single_vendor))
            website_type.push('Website');
        $(wrapper).find('tbody').html('');
        let order_type = [{'name': 'delivery', 'label': 'Delivery'}, {'name': 'pickup', 'label': 'Pickup'}]
        website_type.map(web => {
            let items_list = frm.auto_complete_list.filter(obj => obj.website == web);
            order_type.map(ord => {
                if(frm.doc[ord.name]) {
                    let row = $(`<tr>
                            ${website_type.length == 1 ? '' : `<td>${__(web)}</td>`}
                            <td>${ord.label}</td>
                            <td><div class="workflow-status"></div></td>
                            <td><div class="autocomplete-time"></div></td>
                        </tr>`);
                    wrapper.find('tbody').append(row);
                    let status_div = frappe.ui.form.make_control({
                        df: {
                            "fieldtype": "Link",
                            "fieldname": "workflow_status",
                            "placeholder": __("Auto Complete On Status"),
                            "reqd": 1,
                            "options": "Workflow State",
                            "onchange": function() {
                                let val = this.get_value();
                                check_data = frm.auto_complete_list.find(obj => (obj.order_type == ord.name && obj.website == web));
                                if(check_data) {
                                    frm.auto_complete_list[check_data.idx - 1].status = val;
                                } else {
                                    frm.auto_complete_list.push({'idx': frm.auto_complete_list.length + 1, 'order_type': ord.name, 'method': ord.label, 'status': val, 'website': web, 'complete_after': null});
                                }
                                frm.set_value('auto_complete_json', JSON.stringify(frm.auto_complete_list));
                            }
                        },
                        parent: row.find('.workflow-status'),
                        only_input: true,
                    });
                    status_div.make_input();
                    let check_data = items_list.find(obj => obj.order_type == ord.name);
                    if (check_data && check_data.status)
                        status_div.set_value(check_data.status)
                    let time_div = frappe.ui.form.make_control({
                        df: {
                            "fieldtype": "Int",
                            "fieldname": "complete_after",
                            "placeholder": __("Auto Complete After Order Time (In Minutes)"),
                            "reqd": 1,
                            "onchange": function() {
                                let val = this.get_value();
                                check_data = frm.auto_complete_list.find(obj => (obj.order_type == ord.name && obj.website == web));
                                if(check_data) {
                                    frm.auto_complete_list[check_data.idx - 1].complete_after = val;
                                } else {
                                    frm.auto_complete_list.push({'idx': frm.auto_complete_list.length + 1, 'order_type': ord.name, 'method': ord.label, 'status': null, 'website': web, 'complete_after': val});
                                }
                                frm.set_value('auto_complete_json', JSON.stringify(frm.auto_complete_list));
                            }
                        },
                        parent: row.find('.autocomplete-time'),
                        only_input: true,
                    });
                    time_div.make_input();
                    if (check_data && check_data.complete_after)
                        time_div.set_value(check_data.complete_after);                    
                }                    
            })
        })
    }
})

// enabling tip options based on amount range for restaurants
frappe.ui.form.on('Business',{
    refresh: function(frm){
        frm.toggle_display(['pickup_tip_option', 'delivery_tip_options'], false);
        frm.trigger('enable_tip_for_pickup');
        frm.trigger('enable_tip_for_delivery');
    },
    enable_tip_for_pickup: function(frm) {
        let show = false;
        if(frm.doc.enable_tip_for_pickup)
            show = true;
        frm.toggle_display(['select_tip_pickup', 'pickup_tip_option'], show);
        if(show && !frm.doc.__islocal && frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant))
            frm.trigger('pickup_tip_options_html');
    },
    enable_tip_for_delivery: function(frm) {
        let show = false;
        if(frm.doc.enable_tip_for_delivery)
            show = true;
        frm.toggle_display(['select_tip_delivery', 'delivery_tip_options'], show);
        if(show && !frm.doc.__islocal && frappe.boot.active_domains.includes(frappe.boot.sysdefaults.domain_constants.restaurant))
            frm.trigger('delivery_tip_options_html');
    },
    select_tip_pickup: function(frm){
        if(frm.doc.select_tip_pickup){
            frm.set_value('pickup_tip_option', '');
            frm.trigger('pickup_tip_options_html');
        }
    },
    select_tip_delivery: function(frm){
        if(frm.doc.select_tip_delivery){
            frm.set_value('delivery_tip_options', '');
            frm.trigger('delivery_tip_options_html');
        }
    },
    pickup_tip_options_html: function(frm){
        frappe.run_serially([
            ()=>{
                frm.trigger('get_tip_range');
            },
            ()=>{
                frm.trigger('tip_options');
            }
        ])
    },
    delivery_tip_options_html: function(frm){
        frappe.run_serially([
            ()=>{
                frm.trigger('get_tip_range1');
            },
            ()=>{
                frm.trigger('tip_options1');
            }
        ])
    },
    get_tip_range: function(frm){
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.business.business.get_tip_range',
            args:{
                business: frm.doc.name,
                tip_template: frm.doc.select_tip_pickup
            },
            async: false,
            callback: function(r){
                if(r.message){
                    frm.tip_template = r.message;
                }
            }
        })
    },
    get_tip_range1: function(frm){
        frappe.call({
            method: 'go1_cms.go1_cms.doctype.business.business.get_tip_range',
            args:{
                business: frm.doc.name,
                tip_template: frm.doc.select_tip_delivery
            },
            async: false,
            callback: function(r){
                if(r.message){
                    frm.tip_template1 = r.message;
                }
            }
        })
    },
    tip_options: function(frm){
        let wrapper = $(frm.get_field('pickup_tip_option').wrapper).empty();
        let html = $(`<div>
            <div>${__("Select the default tip option for each range.")}</div>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>${__("Range")}</th>
                        <th>${__("Default Tip")}</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>`).appendTo(wrapper);
        let pickup_tip_option = {};
        if(frm.doc.pickup_tip_option)
           pickup_tip_option = JSON.parse(frm.doc.pickup_tip_option);
        if(frm.doc.select_tip_pickup){
                let opts = [];
                if(pickup_tip_option['default']){
                    opts = pickup_tip_option.default.split(',');
                }
                if(frm.tip_template){
                    frm.tip_template.map(f=>{
                        let tip_range = '';
                        let tip_options = '';
                        let row = $(`<tr class="tip_range"></tr>`);
                        tip_range += `<td class="tip_range1">${f.range}</td>`;
                        tip_range += `<td class="tip_range2"><select style="padding: 3px 15px;">`
                        f.tip_lists.map(t=>{
                            let check = '';
                            if(frm.doc.pickup_tip_option == ''){
                                if(t.default==1){
                                    check = 'selected="selected"';
                                }
                            }
                            else{
                                pickup_tip_option.tip_op.map(u=>{
                                    if(f.range==u.range && t.tip_label==u.default_label){
                                        check = 'selected="selected"';
                                    }
                                })
                            }
                            tip_range+=`<option ${check} data-range="${f.range}" value="${t.tip_label}">${t.tip_label}</option>`
                        })
                        tip_range += '</select></td>'
                        row.append(tip_range);
                        html.find('tbody').append(row);
                    });
                    
                    
                }
        } else{
            html.find('tbody').append(`<tr><td colspan="2">${__("No Records Found.")}</td></tr>`);
        }
        $(wrapper).find('.tip_range2').find('select').change(function(){
            let list = [];
            let range_wise = [];
            $(wrapper).find('.tip_range2').find('select option:selected').each(function(){
                list.push(this.value);
                var amt_range = $(this).attr('data-range');
                range_wise.push({'range': amt_range, 'default_label': this.value})
            });
            pickup_tip_option.default = list.join();
            pickup_tip_option.tip_op = range_wise
            frm.set_value('pickup_tip_option', JSON.stringify(pickup_tip_option));
        });
        if(frm.doc.enable_tip_for_pickup==1 && frm.doc.pickup_tip_option == ''){
            $(wrapper).find('.tip_range2').find('select').each(function() {
                let list = [];
                let range_wise = [];
                $(wrapper).find('.tip_range2').find('select option:selected').each(function(){
                    list.push(this.value);
                    var amt_range = $(this).attr('data-range');
                    range_wise.push({'range': amt_range, 'default_label': this.value})
                });
                pickup_tip_option.default = list.join();
                pickup_tip_option.tip_op = range_wise;
                frm.set_value('pickup_tip_option', JSON.stringify(pickup_tip_option));
                cur_frm.refresh_field('pickup_tip_option');
            })
        }
    },
    tip_options1: function(frm){
        let wrapper = $(frm.get_field('delivery_tip_options').wrapper).empty();
        let html = $(`<div>
            <div>${__("Select the default tip option for each range.")}</div>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>${__("Range")}</th>
                        <th>${__("Default Tip")}</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>`).appendTo(wrapper);
        let delivery_tip_options = {};
        if(frm.doc.delivery_tip_options)
           delivery_tip_options = JSON.parse(frm.doc.delivery_tip_options);
        if(frm.doc.select_tip_delivery){
                let opts = [];
                if(delivery_tip_options['default']){
                    opts = delivery_tip_options.default.split(',');
                }
                if(frm.tip_template1){
                    frm.tip_template1.map(f=>{
                        let tip_range = '';
                        let tip_options = '';
                        let row = $(`<tr class="tip_range"></tr>`);
                        tip_range += `<td class="tip_range1">${f.range}</td>`;
                        tip_range += `<td class="tip_range2"><select style="padding: 3px 15px;">`
                        f.tip_lists.map(t=>{
                            let check = '';
                            if(frm.doc.delivery_tip_options == ''){
                                if(t.default==1){
                                    check = 'selected="selected"';
                                }
                            }
                            else{
                                delivery_tip_options.tip_op.map(u=>{
                                    if(f.range==u.range && t.tip_label==u.default_label){
                                        check = 'selected="selected"';
                                    }
                                })
                            }
                            tip_range+=`<option ${check} data-range="${f.range}" value="${t.tip_label}">${t.tip_label}</option>`
                        })
                        tip_range += '</select></td>'
                        row.append(tip_range);
                        html.find('tbody').append(row);
                    });
                }
        } else{
            html.find('tbody').append(`<tr><td colspan="2">${__("No Records Found.")}</td></tr>`);
        }
        $(wrapper).find('.tip_range2').find('select').change(function(){
            let list = [];
            let range_wise = [];
            $(wrapper).find('.tip_range2').find('select option:selected').each(function(){
                list.push(this.value);
                var amt_range = $(this).attr('data-range');
                range_wise.push({'range': amt_range, 'default_label': this.value})
            });
            delivery_tip_options.default = list.join();
            delivery_tip_options.tip_op = range_wise
            frm.set_value('delivery_tip_options', JSON.stringify(delivery_tip_options));
        });
        if(frm.doc.enable_tip_for_delivery==1 && frm.doc.delivery_tip_options == '' || frm.doc.delivery_tip_options == undefined){
            $(wrapper).find('.tip_range2').find('select').each(function() {
                let list = [];
                let range_wise = [];
                $(wrapper).find('.tip_range2').find('select option:selected').each(function(){
                    list.push(this.value);
                    var amt_range = $(this).attr('data-range');
                    range_wise.push({'range': amt_range, 'default_label': this.value})
                });
                delivery_tip_options.default = list.join();
                delivery_tip_options.tip_op = range_wise;
                frm.set_value('delivery_tip_options', JSON.stringify(delivery_tip_options));
                cur_frm.refresh_field('delivery_tip_options');
            })
        }
    }
});