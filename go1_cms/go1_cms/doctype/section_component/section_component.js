// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt
{% include 'go1_cms/go1_cms/doctype/section_template/section_content.js' %}

frappe.ui.form.on('Section Component', {
	refresh:function(frm){
		$('[data-fieldname="css_field_list"] .control-value.like-disabled-input.for-description').attr("style","max-height:45px;overflow-y:scroll")
		
	},
	choose_style_properties:function(frm){
		frappe.call({
			method:"go1_cms.go1_cms.doctype.section_component.section_component.get_css_fields",
			args:{},
			callback:function(r){
				console.log(">> api response json <<",r.message)
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
					frm.set_value('css_field_list', JSON.stringify(selected_fields));
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
					if (frm.doc.css_field_list) {
						existing_fields = JSON.parse(frm.doc.css_field_list);
					}
				r.message.map((f,index) => {
					if (!has_common([f.fieldtype], ['Column Break', 'Section Break'])) {
					let checked = "";
					let obj = existing_fields.find(o => o.fieldname ===f.fieldname);
					if (obj)
						checked = 'checked="checked"';
						let css_html = $(`<div class="col-md-6" style='float:left;'>
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

	}

});
