// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Color Palette', {
	refresh: function(frm) {
		frm.ra___id = Math.floor(Math.random() * 1000)
		frm.trigger("render_image_preview")
		frm.trigger("hide_and_set_color_values")
		if (frm.doc.__islocal) {
            if (has_common(frappe.user_roles, ['Vendor']) && frappe.session.user != 'Administrator') {
                frm.set_value('business', frappe.boot.sysdefaults.business)
            } else {
                frm.set_value('business', '')
            }
        }
         if (has_common(frappe.user_roles, ['Vendor']) && frappe.session.user != 'Administrator'){
            frm.set_df_property('business', 'hidden', 1)

         }
	},
	image(frm){
		frm.trigger("render_image_preview")
	},
	render_image_preview(frm){
		frm.image_pre_wrapper = frm.get_field("image_preview_html").$wrapper
		$(frm.image_pre_wrapper).empty()
		if(frm.doc.image){
			let html = `<div class="img-previw-tag id="${frm.ra___id}">
							<div class="img-subcontainer">
								<div class="preview-img"></div>
							</div>
						<style>
						.preview-img{
									width: 50%;
									height: 120px;
									background-image: url('${frm.doc.image.replace(" ",'%20')}');
									border-radius: 6%;
									background-size: cover;
									background-repeat: no-repeat;
									padding: 5px;
									background-position: top;
									border: 1px solid #e5e5e5;
									}
						</style>
						</div>`
			frm.image_pre_wrapper.html(html)
			refresh_field("image_preview_html")
		}
	},
	hide_and_set_color_values(frm){
		if((cur_frm.doc.typo_default_color && cur_frm.doc.typo_default_color.length == 0) || !cur_frm.doc.typo_default_color){
			let heading_data = [{"type":"h1"},{"type":"h2"},{"type":"h3"},{"type":"h4"},{"type":"h5"},{"type":"h6"},{"type":"p - Paragraph"},{"type":"a - Anchor"},{"type":"blockquote - Quote"},{"type":"pre - Formatted"},{"type":"primary - btn"},{"type":"secondary - btn"},{"type":"tertiary - btn"}]
			heading_data.map(each_data =>{
				frm.add_child('typo_default_color', each_data);	
			})
			frm.refresh_field('typo_default_color');
		}
		if(cur_frm.doc.typo_default_color && cur_frm.doc.typo_default_color.length >= 13){
			$(`[data-route="Form/Color Palette/${cur_frm.doc.name}"]`).find('[data-fieldname="typo_default_color"]').find('.btn.btn-xs.btn-secondary.grid-add-row').css({"display":"none"})
			$(`[data-route="Form/Color Palette/${cur_frm.doc.name}"]`).find('[data-fieldname="typo_default_color"]').find('[data-action="delete_rows"]').css({"display":"none"})
		}
	}
});

frappe.ui.form.on('Typography Default Color', {
	form_render(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		$(`[data-route="Form/Color Palette/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-danger.btn-sm.pull-right.grid-delete-row").css({"display":"none"})
		$(`[data-route="Form/Color Palette/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row-below.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Color Palette/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Color Palette/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-duplicate-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Color Palette/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-append-row").css({"display":"none"})
		align_edit_style_btn(frm,item)
	},
	edit_styles(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		// console.log(">> type <<",item.type)
		if(item.type){
			frappe.call({
				method:"go1_cms.go1_cms.doctype.web_theme.web_theme.get_json_render_properties",
				args:{field_type:"cp - "+item.type},
				freeze:true,
				callback:(res) =>{
					// console.log(">> api response <<",res)
					if(res && res.message && res.message.length > 0){
						res.message[0].css_json = item.style_json ? item.style_json:null
						res.message[0].field_key = item.type.replace(/[&\/ \\#,+()$~%.'":*?<>{}]/g, '')
						open_edit_styles_popup(item,res.message[0])
					}
					else{
						frappe.msgprint("There is no styles available to edit...!")
					}
				}
			})
				
		}
		else{
			frappe.msgprint("Please select type before edit styles...!")
		}
	},
	before_buttons_table_remove(frm,cdt,cdn){
		let del_item = locals[cdt][cdn];
		let btn_data = ["Primary Button","Secondary Button","Tertiary Button"]
		if(del_item && del_item.name1 && btn_data.includes(del_item.name1)){
			frappe.validated = false;
			frappe.throw(`Row <b>${del_item.idx}</b> with value <b>${del_item.name1}</b> can't be delete..!`)
		}
	}
})


function align_edit_style_btn(frm,item){
	let btn_wrapper = frm.fields_dict[item.parentfield].grid.grid_rows_by_docname[item.name].grid_form.fields_dict['edit_styles'].wrapper
	$(btn_wrapper).find(".btn.btn-xs.btn-default").css({"margin-top":"27px"})
	$(btn_wrapper).find(".btn.btn-xs.btn-default").attr("class","btn btn-xs btn-primary")
}

function open_edit_styles_popup(item, res) {
	console.log(">> Api modified <<", res)
	if (res.css_properties_list.length > 0) {
		let data = res.css_properties_list
		let json_data = {}
		var fonts_data = [" "]
		
		if (res.fonts_list) {
			for (var i = 0; i < res.fonts_list.length; i++) {
				fonts_data.push(res.fonts_list[i].name)
			}
		}
		if (res.css_json != null && res.css_json != undefined) {
			json_data = JSON.parse(res.css_json)
		}
		var filelist = data
		var fields = [];
		var child_sections = [];
		var units_sections = [];
		var units_sections_with_units = [];
		for (var i = 0; i < filelist.length; i++) {
			if (filelist[i].child_properties) {
				var is_collapse = 0;
				if (filelist[i].collapse) {
					if (filelist[i].collapse == 1) {
						is_collapse = 1
					}
				}
				var child_properties = filelist[i].child_properties;
				fields.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb_childs', 'label': filelist[i].label, 'collapsible': is_collapse })
				for (var k = 0; k < child_properties.length; k++) {
					if (k == 0) {
						child_sections.push(child_properties[k].fieldname)
					}

					for (const [key, value] of Object.entries(json_data)) {
						if (key == child_properties[k].fieldname) {
							// child_properties[k].default = value
							// compare the color and set default values and override  
								if(child_properties[k].fieldname == "color" || child_properties[k].fieldname == "background-color" || child_properties[k].fieldname == "border-color"){
									child_properties[k].default = check_color_assign_label_name(value)
								}
							// end
						}
					}

					
					if (child_properties[k].fieldname != 'font-family') {
						fields.push(child_properties[k])

					}
					else {
						fields.push({ 'fieldtype': "Select", 'fieldname': child_properties[k].fieldname, 'label': child_properties[k].label, 'default': child_properties[k].default, 'options': fonts_data })

					}
					if (k != child_properties.length - 1) {
						// fields.push({ 'fieldtype': 'Column Break', 'fieldname': 'cb_childs'+k, 'label': '', 'collapsible': 0 })
					}
					else {
						fields.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb_childs_next', 'collapsible': 0 })

					}
					if (child_properties[k].allow_units) {
						if (child_properties[k].allow_units == 1) {
							units_sections.push(child_properties[k].fieldname);
							// modify for units set i.e px,rem,%
							if(item.doctype  && (item.doctype=="Typography Heading" || item.doctype=="Typography Text" || item.doctype=="Web Theme Button") &&  cur_frm.doc.font_size_with_property && child_properties[k].default && child_properties[k].fieldname == "font-size" && child_properties[k].allow_unit_set){
								units_sections_with_units.push({"field_name":child_properties[k].fieldname,"unit_prop":cur_frm.doc.font_size_with_property.split("-")[1]})
							}
						// end
						}
					}
				}

			}
			else {
				for (const [key, value] of Object.entries(json_data)) {
					if (key == filelist[i].fieldname) {
						// filelist[i].default = value
						// compare the color and set default values and override  
							if(filelist[i].fieldname == "color" || filelist[i].fieldname == "background-color" || filelist[i].fieldname == "border-color"){
								filelist[i].default = check_color_assign_label_name(value)
							}
						// end
					}
				}
			
				if (filelist[i].fieldname != 'font-family') {
					fields.push(filelist[i]);

				}
				else {
					fields.push({ 'fieldtype': "Select", 'fieldname': filelist[i].fieldname, 'label': filelist[i].label, 'default': filelist[i].default, 'options': fonts_data })

				}
				if (filelist[i].allow_units) {
					if (filelist[i].allow_units == 1) {
						units_sections.push(filelist[i].fieldname);
						// modify for units set i.e px,rem,%
						if(item.doctype  && (item.doctype=="Typography Heading" || item.doctype=="Typography Text" || item.doctype=="Web Theme Button") &&  cur_frm.doc.font_size_with_property && filelist[i].default && filelist[i].fieldname == "font-size" && filelist[i].allow_unit_set){
							units_sections_with_units.push({"field_name":filelist[i].fieldname,"unit_prop":cur_frm.doc.font_size_with_property.split("-")[1]})
						}
						// end
					}
				}
			}
		}
		var elementstyledialog = new frappe.ui.Dialog({
			title: "Edit Style",
			fields: fields
		});
		elementstyledialog.show();
		elementstyledialog.$wrapper.find(".modal-dialog").attr("id", item.name);
		elementstyledialog.set_primary_action(__('Save'), function () {
			let values = elementstyledialog.get_values();
			let style_json = {}
			
			
			// let css_design = "." + res.class_name + " ." + res.field_key + "{"
			// let css_design = "." + res.field_key + "{"
			// for (let k in values) {
			// 	if (values[k] != "" && values[k] != "0px") {
			// 		style_json[k] = values[k]
			// 		if (k == "background-image") {
			// 			css_design += k + ":url('" + values[k] + "') !important;";
			// 		}
			// 		else if (k == "font-family") {
			// 			let font_famil_name = res.fonts_list.find(o => o.name === values[k]);
			// 			if (font_famil_name) {
			// 				css_design += k + ":" + font_famil_name.font_family + " !important;";
			// 			}
			// 		}
			// 		else {
			// 			var is_allow_units = 0;
			// 			if (elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").attr("allow-units")) {
			// 				if (elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").attr("allow-units") == "1") {
			// 					is_allow_units = 1;
			// 				}
			// 			}
			// 			var units = '';
			// 			if (is_allow_units == 1) {
			// 				units = elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").parent().find('select.unit').val();
			// 			}
			// 			css_design += k + ":" + values[k] + units + " !important;";
			// 		}
			// 	}
			// }
			// css_design += "}";
			
			// $('[data-name="' + item.name + '"]').attr("css_design", css_design)
			// $('[data-name="' + item.name + '"]').attr("style_json", JSON.stringify(style_json))


			// modified
			let css_design =""
			for (let k in values) {
				if (check_colors_lable_and_assign_fieldname(values[k]) != "" && check_colors_lable_and_assign_fieldname(values[k]) != "0px") {
					style_json[k] = check_colors_lable_and_assign_fieldname(values[k])

					filelist.map(each_list => {
						if(each_list.child_properties && each_list.child_properties.length > 0){
							each_list.child_properties.map(ls =>{
								if(ls.fieldname == k){
									// console.log("each field json",ls)
									// console.log(ls.fieldname,"==",k)
									if(ls.hasOwnProperty('variable_name')){
										// console.log("--values--",values[k])
										if (k == "background-image") {
											css_design += ls.variable_name.replace('$',res.field_key)+":"+"url('" + check_colors_lable_and_assign_fieldname(values[k]) + "');"
										}

										else if (k == "font-family") {
											let font_famil_name = res.fonts_list.find(o => o.name === check_colors_lable_and_assign_fieldname(values[k]));
											if (font_famil_name) {
												css_design += ls.variable_name.replace('$',res.field_key)+":"+font_famil_name.font_family+";"
											}
										}

										else {
											var is_allow_units = 0;
											if (elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").attr("allow-units")) {
												if (elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").attr("allow-units") == "1") {
													is_allow_units = 1;
												}
											}
											var units = '';
											if (is_allow_units == 1) {
												units = elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").parent().find('select.unit').val();
											}
											css_design += ls.variable_name.replace('$',res.field_key)+":"+check_colors_lable_and_assign_fieldname(values[k]) + units +";"
										}

									}
								}
							})
						}
					})
				}
			}
			
			// store selected css in child table
			item.style_json = JSON.stringify(style_json)
			item.css_design = JSON.stringify(css_design)
			cur_frm.doc.__unsaved = 1
			refresh_field("heading")
			refresh_field("text")

			// end

			elementstyledialog.hide();
			setTimeout(function () { $(".modal-dialog[id='" + item.name + "']").parent().remove() }, 1000);
		});
		for (var i = 0; i < child_sections.length; i++) {
			elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='" + child_sections[i] + "']").parent().parent().parent().parent().attr("style", "margin-bottom:10px;border-top:none !important;margin-top: -20px;width: calc(100% + 40px);margin-left: -20px;padding-left: 20px;padding-right: 20px;margin-bottom: 0;position: relative;m");//modfied by boopathy
			elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='" + child_sections[i] + "']").parent().parent().parent().parent().find(".section-head").attr("style", "font-weight: 600;margin-bottom: 20px;margin-top: 0;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;");
			elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='" + child_sections[i] + "']").parent().parent().parent().parent().find(".section-body").attr("style", "margin-top:60px");
			if (i == 0) {
				elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='" + child_sections[i] + "']").parent().parent().parent().parent().find(".section-head").attr("style", "font-weight: 600;margin-bottom: 20px;margin-top: 4px;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;");
			}

		}
		for (var i = 0; i < units_sections.length; i++) {
			elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").attr("style", " box-shadow: none;flex: 0 0 60%;  border-top-right-radius: 0; border-bottom-right-radius: 0; border-right: 1px solid #ddd;");
			elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").attr("type", "number");
			elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").attr("allow-units", "1");
			elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().attr("style", "display: flex;position: relative;max-width: 140px;");
			
			// for default unit select modify
			var select_html=""
			if(units_sections_with_units && units_sections_with_units.length > 0){
				units_sections_with_units.map(ui =>{
					if(ui.field_name == units_sections[i]){
						select_html = `<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> 
											<option value="px" kk ${ui.unit_prop == "px"?"selected":""}>px</option>
											<option value="em" ${ui.unit_prop == "em"?"selected":""}>em</option>
											<option value="%" ${ui.unit_prop == "%"?"selected":""}>%</option>  
											<option value="rem" ${ui.unit_prop == "rem"?"selected":""}>rem</option>
										</select>`;
						select_html += '<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 12px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
						elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().append(select_html);
					}
					else{
						select_html = '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
						select_html += '<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 12px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
						elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().append(select_html);
					}
				})
			}
			else{
				select_html = '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
				select_html += '<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 12px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
				elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().append(select_html);
			}

			// org content

			// var select_html = '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
			// select_html += '<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 12px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
			// elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().append(select_html);
		
			// end
		}
		elementstyledialog.$wrapper.find('.modal-dialog').css("max-width", "700px");
	}
	else {
		frappe.msgprint("There is no styles available to edit...!")
	}

}

function check_colors_lable_and_assign_fieldname(label_name){

	if(label_name){
		if(label_name == "Primary Color"){
			return cur_frm.doc.primary_color?cur_frm.doc.primary_color:""
		}
		else if(label_name == "Secondary Color"){
			return cur_frm.doc.secondary_color?cur_frm.doc.secondary_color:""
		}
		else if(label_name == "Accent Color"){
			return cur_frm.doc.accent_color?cur_frm.doc.accent_color:""
		}
		else if(label_name == "Light Color"){
			return cur_frm.doc.light_color?cur_frm.doc.light_color:""
		}
		else if(label_name == "Dark Color"){
			return cur_frm.doc.dark_color?cur_frm.doc.dark_color:""
		}
		else if(label_name == "Body Text Color"){
			return cur_frm.doc.body_text_color?cur_frm.doc.body_text_color:""
		}
		else if(label_name == "Heading Text Color"){
			return cur_frm.doc.heading_text_color?cur_frm.doc.heading_text_color:""
		}
	}
	else{
		return ""
	}
}

function check_color_assign_label_name(val){
	if(val && (cur_frm.doc.heading_text_color || cur_frm.doc.body_text_color || cur_frm.doc.dark_color || cur_frm.doc.light_color || cur_frm.doc.accent_color || cur_frm.doc.secondary_color || cur_frm.doc.primary_color)){
		if(cur_frm.doc.heading_text_color && val==cur_frm.doc.heading_text_color ){
			return "Heading Text Color"
		}
		else if(cur_frm.doc.body_text_color && val==cur_frm.doc.body_text_color ){
			return "Body Text Color"
		}
		else if(cur_frm.doc.accent_color && val==cur_frm.doc.accent_color ){
			return "Accent Color"
		}
		else if(cur_frm.doc.dark_color && val==cur_frm.doc.dark_color ){
			return "Dark Color"
		}
		else if(cur_frm.doc.light_color && val==cur_frm.doc.light_color ){
			return "Light Color"
		}
		else if(cur_frm.doc.secondary_color && val==cur_frm.doc.secondary_color ){
			return "Secondary Color"
		}
		else if(cur_frm.doc.primary_color && val==cur_frm.doc.primary_color ){
			return "Primary Color"
		}
	}
	else{
		return ""
	}
}