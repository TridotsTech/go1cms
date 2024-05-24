// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Page Section', {
	refresh: function(frm) {
		$('[data-fieldname="css_field_list"] .control-value.like-disabled-input.for-description').attr("style","max-height:45px;overflow-y:scroll")
		// if (!frm.doc.__islocal){
		// 	if(frm.doc.image!=undefined && frm.doc.image!=""){
		// 		// frm.set_df_property('section_layout', 'hidden', 1);
		// 		frm.set_df_property('preview_html', 'hidden',0);
		// 		$("[id='page-Section Template'] .row.form-section.card-section.empty-section:eq(1)").removeClass("empty-section");
		// 		var html = "<div style='max-height: 175px;text-align: center;margin-top: -8px;'><img src='"+frm.doc.image+"' style=' max-height: 175px;'/></div>"
		// 		$("[id='page-Section Template'] .row.form-section.card-section:eq(1)").find('[data-fieldname="preview_html"]').html(html);
		// 	}
		// 	else{
		// 		// frm.set_df_property('section_layout', 'hidden', 0);
		// 		frm.set_df_property('preview_html', 'hidden',1);

		// 	}
		// }
		if(!frm.doc.custom_section_data)
			frm.set_value('custom_section_data', '[]');
		frm.trigger('custom_section_data');
		if (frm.doc.__islocal)
			frm.set_df_property('choose_fields', 'hidden', 1);
		frm.trigger('image_link_documents');
		frm.trigger('web_options');

	},
	content_type: function(frm){
		if(frm.doc.content_type){
			frm.set_value('custom_section_data', '[]');
			frm.trigger('custom_section_data');
		} else{
			$(frm.get_field('custom_section_data').wrapper).empty();
		}
	},
	custom_section_data: function(frm){
		if(frm.doc.content_type){		
			if(frm.doc.content_type == 'Static')
				frm.trigger('static_content');
			// else if(frm.doc.content_type == 'Dynamic' && frm.doc.reference_document)
			// 	frm.trigger('dynamic_content');
		} else{
			$(frm.get_field('custom_section_data').wrapper).empty();
		}		
	},
	static_content: function(frm){
		let wrapper = $(frm.get_field('custom_section_data').wrapper).empty();
		let table = $(`<table class="table table-bordered">
			<thead>
				<tr>
					<th>${__("Title")}</th>
					<th>${__("Sub Title")}</th>
					<th>${__("Image")}</th>
					<th>${__("Redirect Url")}</th>
					<th></th>
				</tr>
			</thead>
			<tbody></tbody>
		</table>`).appendTo(wrapper);
		let no_data = false;
		let check_records = false;
		if(frm.doc.custom_section_data){
			let values = JSON.parse(frm.doc.custom_section_data);
			if(values && values.length > 0){
				if(values.length == frm.doc.no_of_records)
					check_records = true;
				values.map(f=>{
					let row = $(`<tr>
						<td>${f.title}</td>
						<td>${f.sub_title}</td>
						<td>${f.image}</td>
						<td>${f.redirect_to}</td>
						<td><button class="btn btn-primary btn-xs"><span class="fa fa-edit"></span></button><button class="btn btn-danger btn-xs" style="margin-left: 10px;"><span class="fa fa-times"></span></button></td>
						</tr>`);
					table.find('tbody').append(row);
					row.find('.btn-danger').click(function(){
						let obj = values.filter(o => o.idx != f.idx);
						if(obj){
							$(obj).each(function(k, v){
								v.idx = (k + 1)
							});
						} else{
							obj = [];
						}
						cur_frm.set_value('custom_section_data', JSON.stringify(obj));
						cur_frm.save();
					});
					row.find('.btn-primary').click(function(){
						new customData({
							content_type: frm.doc.content_type,
							dialog_type: 'Edit',
							form_data: f,
							doctype: frm.doc.reference_document,
							doc: frm.doc
						})
					})
				})
			} else{
				no_data = true;
			}
		} else{
			no_data = true;
		}
		if(no_data){
			table.find('tbody').append(`<tr><td colspan="5">${__("No Records Found")}</td></tr>`);
		}
		if(!check_records){
			let add_btn = $(`<button class="btn btn-primary">Add New</button>`).appendTo(wrapper);
			add_btn.click(()=>{
				new customData({
					content_type: frm.doc.content_type,
					dialog_type: 'Add',
					doctype: frm.doc.reference_document,
					doc: frm.doc
				})
			})
		}
	},
	choose_fields: function (frm) {
		console.log("ji")
		let dt = frm.doc.reference_document;
		if (has_common([frm.doc.section_type], ['Slider', 'Slider With Banner'])) {
			dt = 'Slider';
		}
		if (dt) {
			frappe.model.with_doctype(dt, () => {
				let fields = frappe.get_meta(dt).fields;
				let default_fields = [
					{ 'fieldname': 'name', 'label': 'Name', 'fieldtype': 'Data' },
					{ 'fieldname': 'docstatus', 'label': 'Document Status', 'fieldtype': 'Int' },
					{ 'fieldname': 'owner', 'label': 'Created By', 'fieldtype': 'Data' },
					{ 'fieldname': 'modified_by', 'label': 'Modified By', 'fieldtype': 'Data' },
					{ 'fieldname': 'creation', 'label': "Created On", 'fieldtype': 'Date' },
					{ 'fieldname': 'modified', 'label': "Modified On", 'fieldtype': 'Date' },
				]
				fields = $.merge(default_fields, fields);
				frm.events.fields_dialog(frm, fields);
			});
		}
	},

	//created by boopathy-30/06/2022

	choose_style_properties:function(frm){
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
					console.log(index,"---f----")
					
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

	},

	
	




	//end by boopathy



	fields_dialog: function (frm, fields) {
		let dialog = new frappe.ui.Dialog({
			title: __("Choose Fields"),
			fields: [{ 'fieldname': 'fields_html', 'fieldtype': 'HTML' }]
		});
		dialog.set_primary_action(__("Update"), function () {
			let selected_fields = [];
			$(wrapper).find('.fields-list input[type="checkbox"]:checked').each(function () {
				selected_fields.push($(this).val())
			});
			frm.set_value('field_list', JSON.stringify(selected_fields));
			dialog.hide();
			frm.save()
		});
		let wrapper = dialog.fields_dict.fields_html.$wrapper.empty();
		$(`<div class="row">
			<div class="col-md-12 col-xs-12">
				<label>${__("Select fields to display")}</label>
			</div>
			<div class="fields-list"></div>
			</div>`).appendTo(wrapper);
		let existing_fields = [];
		if (frm.doc.field_list) {
			existing_fields = JSON.parse(frm.doc.field_list);
		}
		fields.map(f => {
			if (!has_common([f.fieldtype], ['Column Break', 'Section Break'])) {
				let checked = "";
				if (existing_fields.indexOf(f.fieldname) != -1)
					checked = 'checked="checked"';
				let row = $(`<div class="col-md-6" style='float:left'>
					<div class="checkbox" style="margin-top: 0px !important;">
						<label>
							<span class="input-area">
								<input type="checkbox" autocomplete="off" class="input-with-feedback" name="ftd" label="Name" value="${f.fieldname}" ${checked} />
							</span>
							<span class="disp-area" style="display:none">
								<i class="octicon octicon-check" style="margin-right: 3px;"></i>
							</span>
							<span class="label-area small">${f.label}</span>
						</label>
						<p class="help-box small text-muted"></p>
					</div>
				</div>`);
				$(wrapper).find('.fields-list').append(row);
			}
		})
		dialog.show();
	},
	choose_link_documents: function (frm, type, edit_doc) {
		if (frm.doc.image_option && frm.doc.reference_document) {
			frappe.run_serially([
				() => {
					if (!frm.linked_documents)
						frm.trigger('get_linked_documents')
				},
				() => {
					if (frm.linked_documents)
						frm.events.image_dialog(frm, type, edit_doc);
					else
						frappe.msgprint(__('No documents linked to your selected document.'))
				}
			])
		} else {
			if (!frm.doc.reference_document)
				frappe.msgprint(__("Please select reference document"));
			else if (!frm.doc.image_option)
				frappe.msgprint(__("Please select image option"));
		}
	},
	get_linked_documents: function (frm) {
		frappe.call({
			method: 'go1_cms.go1_cms.doctype.section_template.section_template.get_linked_documents',
			args: {
				dt: frm.doc.reference_document,
				image_option: frm.doc.image_option
			},
			async: false,
			callback: function (r) {
				if (r.message) {
					frm.linked_documents = r.message;
				}
			}
		})
	},
	image_link_documents: function (frm) {
		let wrapper = $(frm.get_field('image_link_documents').wrapper).empty();
		$(`<div>
			<div><button class="btn btn-warning">${__("Add Row")}</button></div>
			<table class="table table-bordered">
				<thead>
					<tr>
						<td>${__("Document Name")}</td>
						<td>${__("Image Field")}</td>
						<td></td>
					</tr>
				</thead>
				<tbody></tbody>
			</table>
		</div>`).appendTo(wrapper);
		let docs = [];
		if (frm.doc.image_link_documents) {
			docs = JSON.parse(frm.doc.image_link_documents);
		}
		if (docs && docs.length > 0) {
			docs.map(f => {
				let row = $(`<tr>
						<td>${f.document_name}</td>
						<td>${f.field_name}</td>
						<td style="width: 15%">
							<button class="btn btn-xs btn-info"><span class="fa fa-edit"></span></button>
							<button class="btn btn-xs btn-danger"><span class="fa fa-trash"></span></button>
						</td>
					</tr>`);
				$(wrapper).find('tbody').append(row);
				row.find('.btn-info').click(function () {
					frm.events.choose_link_documents(frm, 'Edit', f);
				})
				row.find('.btn-danger').click(function () {
					let new_list = docs.filter(obj => obj.idx != f.idx);
					$(new_list).each(function (k, v) {
						v.idx = k + 1;
					})
					frm.set_value('image_link_documents', JSON.stringify(new_list));
					frm.save();
				})
			})
		} else {
			$(wrapper).find('tbody').append(`<tr><td colspan="3">${__("No records found.")}</td></tr>`);
		}
		wrapper.find('.btn-warning').click(function () {
			frm.events.choose_link_documents(frm, 'Add');
		})
	},
	image_dialog: function (frm, type, edit_doc) {
		let options = [];
		$(frm.linked_documents).each(function (k, v) {
			options.push(v.document);
		})
		let dialog = new frappe.ui.Dialog({
			title: __("Image Option"),
			fields: [
				{
					fieldtype: "Select",
					"fieldname": "document_name",
					"label": "Document Name",
					"options": options,
					"default": (edit_doc && edit_doc.document_name) || ""
				},
				{ "fieldtype": "Select", "fieldname": "field_name", "label": "Image Field" }
			]
		})
		dialog.show();
		dialog.set_primary_action(__("Update"), function () {
			let values = dialog.get_values();
			let option_values = [];
			if (frm.doc.image_link_documents)
				option_values = JSON.parse(frm.doc.image_link_documents);
			if (type == 'Add') {
				values.idx = option_values.length + 1;
				let check_data = option_values.find(obj => (obj.document_name == values.document_name && obj.field_name == values.field_name));
				if (!check_data)
					option_values.push(values);
			} else {
				$(option_values).each(function (k, v) {
					if (v.idx == edit_doc.idx) {
						v.document_name = values.document_name;
						v.field_name = values.field_name;
					}
				})
			}
			frm.set_value('image_link_documents', JSON.stringify(option_values));
			dialog.hide();
			frm.save();
		})
		setTimeout(function () {
			if (type == 'Edit')
				dialog.fields_dict.document_name.$input.trigger('change');
		}, 500);
		dialog.fields_dict.document_name.input.onchange = function () {
			let val = dialog.get_value('document_name');
			if (val) {
				let fields_list = frm.linked_documents.find(obj => obj.document == val);
				let field_options = [];
				$(fields_list.fields).each(function (k, v) {
					field_options.push({ 'label': v.label, 'value': v.fieldname });
				})
				dialog.fields_dict.field_name.df.options = field_options;
				if (edit_doc && edit_doc.field_name)
					dialog.set_value('field_name', edit_doc.field_name);
				dialog.refresh();
			}
		}
	},
	web_options: function (frm) {
		// setTimeout(() => {
		// 	new cms.TextEditorView({ fieldname: 'web_template', frm: frm });
		// }, 500);
		// let wrapper = $(frm.get_field('web_options').wrapper).empty();
		// $(`<div class="btn-list">
		// 	<button class="btn btn-danger"><span class="fa fa-sitemap"></span> ${__("Use Builder")}</button>
		// 	<button class="btn btn-info hide"><span class="fa fa-edit"></span> ${__("Use Editor")}</button>
		// </div>`).appendTo(wrapper);
		// wrapper.find('.btn-danger').click(() => {
		// 	wrapper.find('.btn-info').removeClass('hide');
		// 	wrapper.find('.btn-danger').addClass('hide');
		// 	new cms.SectionBuilder({
		// 		frm: frm,
		// 		fieldname: 'web_template',
		// 		from_form: 1,
		// 		wrapper: $(frm.get_field('web_template').wrapper).empty(),
		// 		title_field: frm.doc.name,
		// 		template: frm.doc.web_template
		// 	});
		// });
		// wrapper.find('.btn-info').click(() => {
		// 	wrapper.find('.btn-info').addClass('hide');
		// 	wrapper.find('.btn-danger').removeClass('hide');
		// 	new cms.TextEditorView({ fieldname: 'web_template', frm: frm });
		// });
	}
});
{% include 'go1_cms/go1_cms/doctype/section_template/section_content.js' %}

// for builder 



// var print_builder = Class.extend({
//     init: function(opts) {
//         this.frm = opts.frm;
//         this.get_sections()
//         this.make();
//     },
//     async get_sections() {
// 		console.log(origin)
// 		await frappe.call({
// 			method: '',
// 			type: "post",
// 			url: "/api/method/go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_section_templates",
// 			args: {
// 				device_type: "Web",
// 			},
// 			freeze: true,
// 			callback: function (r) {
// 				let d = [];
// 				let f = JSON.stringify(r)
// 				d.push(f)
// 				let value = JSON.parse(d[0]);
// 				var fields = (value.message.templates)
// 				var groups = (value.message.template_groups)
// 				console.log(fields, groups)
// 			}
// 		});
// 	},
//     make: function() {
//     	let wrapper = $(this.frm.get_field("builder_html").wrapper).empty();
//     	this.wrapper = $(
// 			'<div id="print_builder_main" class="col-md-12 border print-format-builder-main frappe-card"></div>'
// 		).appendTo(wrapper);
//        	this.setup_section_settings();
// 		this.setup_column_selector();
// 		this.setup_edit_custom_html();
// 		this.add_component()
// 		// this.wrapper.empty();
// 		this.prepare_data();
// 		var lt = $(frappe.render("print_format_builder_layout", {
// 				// data: this.layout_data,
// 				data: [],
// 				me: this,
// 			})
// 		).appendTo(wrapper);
// 		console.log(lt.innerHTML())
// 		// .appendTo(wrapper);
//     },
//     prepare_data() {
// 		this.print_heading_template = null;
// 		if (!this.print_heading_template) {
// 			// default print heading template
// 			this.print_heading_template =
// 				'<div class="print-heading">\
// 				<h2><div>' +
// 				// __(this.print_format.doc_type)
// 				"docTYpe"
// 				+

// 				'</div><br><small class="sub-heading">{{ doc.name }}</small>\
// 				</h2></div>';
// 		}
// 		this.data = [
// 			{
// 				columns: [
// 					{
// 						fields: [
// 							{
// 								fieldname: "Login",
// 								label: "Login",
// 								fieldtype: "Login",
// 								image: "https://www.schooleducationgateway.eu/files/jpg11/registration-ga80a41042_1920_600x400_1_600x400.jpg"
// 							},
// 							{
// 								fieldname: "Header",
// 								label: "Header",
// 								fieldtype: "Header",
// 								image: "https://static.wixstatic.com/media/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg/v1/fill/w_924,h_510,al_c,q_90/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg"
// 							},
// 						]
// 					}
// 				], no_of_columns: 0, label: ""
// 			}

// 		]

// 		this.layout_data = [{
// 			fieldname: "Login",
// 			label: "Login",
// 			fieldtype: "Login",
// 			image: "https://www.schooleducationgateway.eu/files/jpg11/registration-ga80a41042_1920_600x400_1_600x400.jpg"
// 		},
// 		{
// 			fieldname: "Header",
// 			label: "Header",
// 			fieldtype: "Header",
// 			image: "https://static.wixstatic.com/media/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg/v1/fill/w_924,h_510,al_c,q_90/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg"
// 		},];
// 		this.fields_dict = {};
// 		this.custom_html_dict = {};
// 		var section = null,
// 			column = null,
// 			me = this,
// 			custom_html_count = 0;

// 		// create a new placeholder for column and set
// 		// it as "column"
// 		var set_column = function () {
// 			if (!section) set_section();
// 			column = me.get_new_column();
// 			section.columns.push(column);
// 			section.no_of_columns += 1;
// 		};
// 		var set_section = function (label) {
// 			section = me.get_new_section();
// 			if (label) section.label = label;
// 			column = null;
// 			me.layout_data.push(section);
// 		};

// 		// break the layout into sections and columns
// 		// so that it is easier to render in a template
// 		$.each(this.data, function (i, f) {
// 			me.fields_dict[f.fieldname] = f;
// 			if (!f.name && f.fieldname) {
// 				// from format_data (designed format)
// 				// print_hide should always be false
// 				if (f.fieldname === "_custom_html") {
// 					f.label = "Custom HTML";
// 					f.fieldtype = "Custom HTML";

// 					// set custom html id to map data properties later
// 					custom_html_count++;
// 					f.custom_html_id = custom_html_count;
// 					me.custom_html_dict[f.custom_html_id] = f;
// 				} else {
// 					f = $.extend(
// 						// frappe.meta.get_docfield(me.print_format.doc_type, f.fieldname) || {},
// 						frappe.meta.get_docfield("doc", f.fieldname) || {},

// 						f
// 					);
// 				}
// 			}

// 			if (f.fieldtype === "Section Break") {
// 				set_section(f.label);
// 			} else if (f.fieldtype === "Column Break") {
// 				set_column();
// 			} else if (
// 				!in_list(["Section Break", "Column Break", "Tab Break", "Fold"], f.fieldtype) &&
// 				f.label
// 			) {
// 				if (!column) set_column();

// 				if (f.fieldtype === "Table") {
// 					me.add_table_properties(f);
// 				}

// 				if (!f.print_hide) {
// 					column.fields.push(f);
// 					section.has_fields = true;
// 				}
// 			}
// 		});

// 		// strip out empty sections
// 		this.layout_data = $.map(this.layout_data, function (s) {
// 			return s.has_fields ? s : null;
// 		});
// 	},
//     get_fullscreen() {
// 		var me = this;
// 		var elem = document.getElementById("print_builder_main")
// 		$("#fullscreen").on('click', function () {
// 			is_fullscreen = !is_fullscreen
// 	var d = new frappe.ui.Dialog({
// 		title: "Edit Section",
// 		fields: [
// 			{
// 				label: __("Select Template"),
// 				fieldname: "template",
// 				fieldtype: "HTML",
// 			},
// 			{
// 			label: __("Select Style"),
// 			fieldname: "component_style",
// 			fieldtype: "Data",
// 			description: __("Select component style"),
// 		},
// 		{
// 			label: __("Cancel"),
// 			fieldname: "remove_section",
// 			fieldtype: "Button",
// 			click: function () {
// 				d.hide();
// 				section.fadeOut(function () {
// 					section.remove();    
// 				});
// 			},
// 			input_class: "btn-danger",
// 			input_css: {
// 				"margin-top": "20px",
// 			},
// 		},
// 		],
// 		primary_action_label: 'Submit',
// 		primary_action(values) {
// 			console.log(values);
// 			d.hide();
// 			console.log(d.fields_dict.template.$wrapper)
// 			me.addTemplate(values.component);
// 		}
// 	});
// 	var layout_popup = d.fields_dict.template.$wrapper
// 	d.show();	
// 	d.$wrapper.addClass("in")


// 		})

// 	},
// 	 async get_components(){
// 	await frappe.call({
// 		method: 'go1_cms.go1_cms.doctype.section_template_layout.section_template_layout.get_layout_section_template_data',
// 		type: "post",
// 		args: {
// 		},
// 		freeze: true,
// 		callback: function (r) {
// 			console.log(r)
// 		}
// 	});
//    },
//     add_component() {
// 		var me = this;
// 		this.wrapper.on("click", ".add_component", function () {
// 			var section = $(this)
// 			  me.get_components()
// 			// console.log(components)
// 			// var component_fields = []
//             // components.map(c=>{
// 			// 	component_fields.push(c.field_label)
// 			// })
// 			// console.log(component_fields)
// 			// new dialog
// 			var d = new frappe.ui.Dialog({
// 				title: "Edit Section",
// 				fields: [
// 					{
// 						label: __("Select Component"),
// 						fieldname: "component",
// 						fieldtype: "Select",
// 						options: ["Header", "Title", "Subtitle", "Card", 'Image'],
// 					},
// 					{
// 						label: __("Select Style"),
// 						fieldname: "component_style",
// 						fieldtype: "Data",
// 						description: __("Select component style"),
// 					},
// 					{
// 						label: __("Cancel"),
// 						fieldname: "remove_section",
// 						fieldtype: "Button",
// 						click: function () {
// 							d.hide();
// 							section.fadeOut(function () {
// 								section.remove();    
// 							});
// 						},
// 						input_class: "btn-danger",
// 						input_css: {
// 							"margin-top": "20px",
// 						},
// 					},

// 				],
// 				primary_action_label: 'Submit',
// 				primary_action(values) {
// 					console.log(values);
// 					me.renderComponent(values.component,section)
// 					d.hide();
// 				}
// 			});
// 			d.show();
// 			d.$wrapper.addClass("in")
// 			d.set_input("component", component + "");
// 			d.set_input("no_of_columns", no_of_columns + "");
// 			d.set_input("label", label || "");

// 			d.set_primary_action(__("Update"), function () {
// 				// resize number of columns
// 				me.update_columns_in_section(
// 					section,
// 					no_of_columns,
// 					cint(d.get_value("no_of_columns"))
// 				);

// 				section.attr("data-label", d.get_value("label") || "");
// 				section.find(".section-label").html(d.get_value("label") || "");

// 				d.hide();
// 			});


// 			// return false;
// 		});
// 	},
// 	setup_section_settings() {
// 		var me = this;
// 		this.wrapper.on("click", ".section-settings", function () {
// 			var section = $(this).parent().parent();
// 			var no_of_columns = section.find(".section-column").length;
// 			var label = section.attr("data-label");
// 			console.log(section, no_of_columns, label);

// 			// new dialog
// 			var d = new frappe.ui.Dialog({
// 				title: "Edit Section",
// 				fields: [
// 					{
// 						label: __("No of Columns"),
// 						fieldname: "no_of_columns",
// 						fieldtype: "Select",
// 						options: ["1", "2", "3", "4", '5'],
// 					},
// 					{
// 						label: __("Section Heading"),
// 						fieldname: "label",
// 						fieldtype: "Data",
// 						description: __("Will only be shown if section headings are enabled"),
// 					},
// 					{
// 						label: __("add"),
// 						fieldname: "add",
// 						fieldtype: "Button",
// 						click: function () {
// 							d.hide();
// 							section.fadeOut(function () {
// 								section.remove();
// 							});
// 						},
// 						input_class: "btn-primary",
// 						input_css: {
// 							"margin-top": "20px",
// 						},
// 					},
// 					{
// 						label: __("Remove Section"),
// 						fieldname: "remove_section",
// 						fieldtype: "Button",
// 						click: function () {
// 							d.hide();
// 							section.fadeOut(function () {
// 								section.remove();
// 							});
// 						},
// 						input_class: "btn-danger",
// 						input_css: {
// 							"margin-top": "20px",
// 						},
// 					},

// 				],
// 			});
// 			d.show();
// 			d.$wrapper.addClass("in")
// 			d.set_input("no_of_columns", no_of_columns + "");
// 			d.set_input("label", label || "");

// 			d.set_primary_action(__("Update"), function () {
// 				// resize number of columns
// 				me.update_columns_in_section(
// 					section,
// 					no_of_columns,
// 					cint(d.get_value("no_of_columns"))
// 				);

// 				section.attr("data-label", d.get_value("label") || "");
// 				section.find(".section-label").html(d.get_value("label") || "");

// 				d.hide();
// 			});


// 			// return false;
// 		});
// 	},
// 	setup_edit_custom_html() {
// 		var me = this;
// 		this.wrapper.on("click", ".edit-html", function () {
// 			me.get_edit_html_dialog(
// 				__("Edit Custom HTML"),
// 				__("Custom HTML"),
// 				$(this).parents(".print-format-builder-field:first").find(".html-content")
// 			);
// 		});
// 	},
//     setup_column_selector() {
// 		var me = this;
// 		this.wrapper.on("click", ".select-columns", function () {
// 			var parent = $(this).parents(".print-format-builder-field:first"),
// 				doctype = parent.attr("data-doctype"),
// 				label = parent.attr("data-label"),
// 				columns = parent.attr("data-columns").split(","),
// 				column_names = $.map(columns, function (v) {
// 					return v.split("|")[0];
// 				}),
// 				widths = {};

// 			$.each(columns, function (i, v) {
// 				var parts = v.split("|");
// 				widths[parts[0]] = parts[1] || "";
// 			});

// 			var d = new frappe.ui.Dialog({
// 				title: __("Select Table Columns for {0}", [label]),
// 			});

// 			var $body = $(d.body);

// 			var doc_fields = frappe.get_meta(doctype).fields;
// 			var docfields_by_name = {};

// 			// docfields by fieldname
// 			$.each(doc_fields, function (j, f) {
// 				if (f) docfields_by_name[f.fieldname] = f;
// 			});

// 			// add field which are in column_names first to preserve order
// 			var fields = [];
// 			$.each(column_names, function (i, v) {
// 				if (in_list(Object.keys(docfields_by_name), v)) {
// 					fields.push(docfields_by_name[v]);
// 				}
// 			});
// 			// add remaining fields
// 			$.each(doc_fields, function (j, f) {
// 				if (
// 					f &&
// 					!in_list(column_names, f.fieldname) &&
// 					!in_list(["Section Break", "Column Break", "Tab Break"], f.fieldtype) &&
// 					f.label
// 				) {
// 					fields.push(f);
// 				}
// 			});
// 			// render checkboxes
// 			$(
// 				frappe.render_template("print_format_builder_column_selector", {
// 					fields: fields,
// 					column_names: column_names,
// 					widths: widths,
// 				})
// 			).appendTo(d.body);

// 			Sortable.create($body.find(".column-selector-list").get(0));

// 			var get_width_input = function (fieldname) {
// 				return $body.find(".column-width[data-fieldname='" + fieldname + "']");
// 			};

// 			// update data-columns property on update
// 			d.set_primary_action(__("Update"), function () {
// 				var visible_columns = [];
// 				$body.find("input:checked").each(function () {
// 					var fieldname = $(this).attr("data-fieldname"),
// 						width = get_width_input(fieldname).val() || "";
// 					visible_columns.push(fieldname + "|" + width);
// 				});
// 				parent.attr("data-columns", visible_columns.join(","));
// 				d.hide();
// 			});

// 			let update_column_count_message = () => {
// 				// show a warning if user selects more than 10 columns for a table
// 				let columns_count = $body.find("input:checked").length;
// 				$body.find(".help-message").toggle(columns_count > 10);
// 			};
// 			update_column_count_message();

// 			// enable / disable input based on selection
// 			$body.on("click", "input[type='checkbox']", function () {
// 				var disabled = !$(this).prop("checked"),
// 					input = get_width_input($(this).attr("data-fieldname"));

// 				input.prop("disabled", disabled);
// 				if (disabled) input.val("");

// 				update_column_count_message();
// 			});

// 			d.show();

// 			return false;
// 		});
// 	},
// });
