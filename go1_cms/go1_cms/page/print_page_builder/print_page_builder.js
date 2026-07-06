

let fields = [
	{
		fieldname: "Login",
		label: "Login",
		fieldtype: "Login",
		image: "https://www.schooleducationgateway.eu/files/jpg11/registration-ga80a41042_1920_600x400_1_600x400.jpg"
	},
	{
		fieldname: "Header",
		label: "Header",
		fieldtype: "Header",
		image: "https://static.wixstatic.com/media/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg/v1/fill/w_924,h_510,al_c,q_90/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg"
	},
	{
		fieldname: "Footer",
		label: "Footer",
		fieldtype: "Footer",
		image: "https://images04.nicepage.com/feature/552072/website-footer.png",
	},
	{
		fieldname: "Sidemenu",
		label: "Sidemenu",
		fieldtype: "Sidemenu",
		image: "https://1.bp.blogspot.com/-GCD1ZWFM4GI/X8Yy7iyWIYI/AAAAAAAAABY/9s9w64uOXsA9RRoWWS_gJZaF2-FW1IviQCLcBGAsYHQ/s1280/Side%2BBar%2BMenu%2Busing%2BHTML%2B%2526%2BCSS.webp"
	},
	{
		fieldname: "Gallery",
		label: "Gallery",
		fieldtype: "Gallery",
		image: "https://user-images.strikinglycdn.com/res/hrscywv4p/image/upload/blog_service/2019-10-21-add-images-on-gallery-section.jpg"
	},
]
let selected_section = 'Dynamic Sections'
let groups = ''
let data = [
	"New Section"
]
let preview = false
let is_fullscreen = false
let origin = location.origin;

frappe.pages['print-page-builder'].on_page_load = function (wrapper) {
	frappe.print_page_builder = new frappe.PrintPageBuilder(wrapper);
	frappe.breadcrumbs.add("Setup", "Print Format");
}


frappe.PrintPageBuilder = class PrintPageBuilder {
	constructor(parent) {
		this.parent = parent;
		this.get_sections()
		setTimeout(() => {
			this.make();
			this.refresh();
		}, 5000)
	}
	async get_sections() {
		console.log(origin)
		await frappe.call({
			method: '',
			type: "post",
			url: "http://45.140.185.144:8004/api/method/ecommerce_business_store.cms.doctype.web_page_builder.web_page_builder.get_section_templates",
			args: {
				device_type: "Web",
			},
			freeze: true,
			callback: function (r) {
				let d = [];
				let f = JSON.stringify(r)
				d.push(f)
				let value = JSON.parse(d[0]);
				fields = (value.message.templates)
				groups = (value.message.template_groups)
				console.log(fields, groups)
			}
		});
	}


	
	get_fullscreen() {
		var me = this;
		var elem = document.getElementById("print_builder_main")
		$("#fullscreen").on('click', function () {
			is_fullscreen = !is_fullscreen
	var d = new frappe.ui.Dialog({
		title: "Edit Section",
		fields: [
			{
				label: __("Select Template"),
				fieldname: "template",
				fieldtype: "HTML",
			},
			{
			label: __("Select Style"),
			fieldname: "component_style",
			fieldtype: "Data",
			description: __("Select component style"),
		},
		{
			label: __("Cancel"),
			fieldname: "remove_section",
			fieldtype: "Button",
			click: function () {
				d.hide();
				section.fadeOut(function () {
					section.remove();    
				});
			},
			input_class: "btn-danger",
			input_css: {
				"margin-top": "20px",
			},
		},
		],
		primary_action_label: 'Submit',
		primary_action(values) {
			console.log(values);
			d.hide();
			console.log(d.fields_dict.template.$wrapper)
			me.addTemplate(values.component);
		}
	});
	var layout_popup = d.fields_dict.template.$wrapper
	d.show();	
	d.$wrapper.addClass("in")


		})

	}
	refresh() {
		$(document.body).on('change', "#sections", function (e) {
			//doStuff
			var optVal = $("#sections option:selected").val();
			console.log(optVal);
		});

		this.custom_html_count = 0;
		this.show_start();
		this.render_layout();
	
	}
	make() {
		this.page = frappe.ui.make_app_page({
			parent: this.parent,
			title: __("Print Page Builder"),
		});

		this.page.main.css({ "border-color": "transparent" });

		this.page.sidebar = $('<div class="print-format-builder-sidebar"></div>').appendTo(
			this.page.sidebar
		);
		this.page.main = $(
			'<div id="print_builder_main" class="col-md-12 border print-format-builder-main frappe-card"></div>'
		).appendTo(this.page.main);

		// future-bindings for buttons on sections / fields
		// bind only once
		this.setup_section_settings();
		this.setup_column_selector();
		this.setup_edit_custom_html();
		this.add_component()
		$(this.page.sidebar).css({ "position": 'fixed' });
		// $(this.page.main).parent().css({"margin-left": '16.67%'});
	}
// ADD Components function

   async get_components(){
	await frappe.call({
		method: 'ecommerce_business_store.cms.doctype.section_template_layout.section_template_layout.get_layout_section_template_data',
		type: "post",
		args: {
		},
		freeze: true,
		callback: function (r) {
			console.log(r)
		}
	});
   }


    add_component() {
		var me = this;
		this.page.main.on("click", ".add_component", function () {
			var section = $(this)
			  me.get_components()
			// console.log(components)
			// var component_fields = []
            // components.map(c=>{
			// 	component_fields.push(c.field_label)
			// })
			// console.log(component_fields)
			// new dialog
			var d = new frappe.ui.Dialog({
				title: "Edit Section",
				fields: [
					{
						label: __("Select Component"),
						fieldname: "component",
						fieldtype: "Select",
						options: ["Header", "Title", "Subtitle", "Card", 'Image'],
					},
					{
						label: __("Select Style"),
						fieldname: "component_style",
						fieldtype: "Data",
						description: __("Select component style"),
					},
					{
						label: __("Cancel"),
						fieldname: "remove_section",
						fieldtype: "Button",
						click: function () {
							d.hide();
							section.fadeOut(function () {
								section.remove();    
							});
						},
						input_class: "btn-danger",
						input_css: {
							"margin-top": "20px",
						},
					},

				],
				primary_action_label: 'Submit',
				primary_action(values) {
					console.log(values);
					me.renderComponent(values.component,section)
					d.hide();
				}
			});
			d.show();
			d.$wrapper.addClass("in")
			d.set_input("component", component + "");
			d.set_input("no_of_columns", no_of_columns + "");
			d.set_input("label", label || "");

			d.set_primary_action(__("Update"), function () {
				// resize number of columns
				me.update_columns_in_section(
					section,
					no_of_columns,
					cint(d.get_value("no_of_columns"))
				);

				section.attr("data-label", d.get_value("label") || "");
				section.find(".section-label").html(d.get_value("label") || "");

				d.hide();
			});


			// return false;
		});
	}
	renderComponent(component_name,col_id){
		console.log(col_id);
		console.log(col_id.parent());
		// for(let i=1;i<6;i++){
			$('#page-print-page-builder .page-content').find(col_id.parent()).append(frappe.render_template("components",{data:component_name,me: this,}));
		// }
	}
// ADD row



	show_preview() {

		this.page.main.find("#preview").on("click", function () {
			preview = !preview
			if (preview) {
				$('#page-print-page-builder .page-content').find(".layout-side-section").addClass("hide_element");
				$('#page-print-page-builder .page-content').find(".print-format-builder-header").addClass("hide_element");
				$('#page-print-page-builder .page-content').find(".print-format-builder-add-section").addClass("hide_element");
				$('#page-print-page-builder .page-content').find(".print-format-builder-section-head").addClass("hide_element");
				$('#page-print-page-builder .page-content').find(".print-format-builder-field").addClass("remove_border");
				$('#page-print-page-builder .page-content').find(".print-format-builder-section").addClass("remove_border");
				$('#page-print-page-builder .page-content').find(".print-format-builder-column").addClass("remove_border");
				$('#page-print-page-builder .page-content').find(".print-format-builder-main").addClass("remove_border");
				$('#page-print-page-builder .page-content').find(".section-column").addClass("remove_border");
				$('#page-print-page-builder .page-content').find(".layout-main-section-wrapper").addClass("col-md-12").removeClass("col-md-10")
			}
			else {
				$('#page-print-page-builder .page-content').find(".layout-side-section").removeClass("hide_element");
				$('#page-print-page-builder .page-content').find(".print-format-builder-header").removeClass("hide_element");
				$('#page-print-page-builder .page-content').find(".print-format-builder-add-section").removeClass("hide_element");
				$('#page-print-page-builder .page-content').find(".print-format-builder-section-head").removeClass("hide_element");
				$('#page-print-page-builder .page-content').find(".print-format-builder-field").removeClass("remove_border");
				$('#page-print-page-builder .page-content').find(".print-format-builder-section").removeClass("remove_border");
				$('#page-print-page-builder .page-content').find(".print-format-builder-main").removeClass("remove_border");
				$('#page-print-page-builder .page-content').find(".print-format-builder-column").removeClass("remove_border");
				$('#page-print-page-builder .page-content').find(".section-column").removeClass("remove_border");
				$('#page-print-page-builder .page-content').find(".layout-main-section-wrapper").addClass("col-md-10").removeClass("col-md-12")
	
			}
		})

	}

	screen_size() {
		$("#mobile").on('click', function () {
			$('.print-format-builder-main').addClass('mobile_size').removeClass("tab_size")
		})
		$("#tab").on('click', function () {
			$('.print-format-builder-main').addClass('tab_size').removeClass('mobile_size')
		})
		$("#desktop").on('click', function () {
			$('.print-format-builder-main').removeClass('tab_size mobile_size')
		})
	}
	show_start() {
		$('#page-print-page-builder .page-content').find('.print-format-builder-sidebar').append(frappe.render_template("print_format_builder_sidebar", {}));
		// this.page.main.html(frappe.render_template("print_format_builder_sidebar", {}));
		this.page.clear_actions();
		// this.page.set_title(__("Print Format Builder"));
		// this.start_edit_print_format();
		// this.start_new_print_format();
	}
	start_edit_print_format() {
		// print format control
		var me = this;
		this.print_format_input = frappe.ui.form.make_control({
			parent: this.page.main.find(".print-format-selector"),
			df: {
				fieldtype: "Link",
				options: "Print Format",
				filters: {
					print_format_builder: 1,
				},
				label: __("Select Print Format to Edit"),
				only_select: true,
			},
			render_input: true,
		});

		// create a new print format.
		this.page.main.find(".btn-edit-print-format").on("click", function () {
			var name = me.print_format_input.get_value();
			if (!name) return;
			frappe.model.with_doc("Print Format", name, function (doc) {
				frappe.set_route("print-format-builder", name);
			});
		});
	}
	start_new_print_format() {
		var me = this;
		this.doctype_input = frappe.ui.form.make_control({
			parent: this.page.main.find(".doctype-selector"),
			df: {
				fieldtype: "Link",
				options: "DocType",
				filters: {
					istable: 0,
					issingle: 0,
				},
				label: __("Select a DocType to make a new format"),
			},
			render_input: true,
		});

		this.name_input = frappe.ui.form.make_control({
			parent: this.page.main.find(".name-selector"),
			df: {
				fieldtype: "Data",
				label: __("Name of the new Print Format"),
			},
			render_input: true,
		});

		this.page.main.find(".btn-new-print-format").on("click", function () {
			var doctype = me.doctype_input.get_value(),
				name = me.name_input.get_value();
			if (!(doctype && name)) {
				frappe.msgprint(__("Both DocType and Name required"));
				return;
			}
			me.setup_new_print_format(doctype, name);
		});
	}
	setup_new_print_format(doctype, name, based_on, beta) {
		frappe.call({
			method: "frappe.printing.page.print_format_builder.print_format_builder.create_custom_format",
			args: {
				doctype: doctype,
				name: name,
				based_on: based_on,
				beta: Boolean(beta),
			},
			callback: (r) => {
				if (r.message) {
					let print_format = r.message;
					if (print_format.print_format_builder_beta) {
						frappe.set_route("print-format-builder-beta", print_format.name);
					} else {
						this.print_format = print_format;
						this.refresh();
					}
				}
			},
		});
	}
	setup_section_settings() {
		var me = this;
		this.page.main.on("click", ".section-settings", function () {
			var section = $(this).parent().parent();
			var no_of_columns = section.find(".section-column").length;
			var label = section.attr("data-label");
			console.log(section, no_of_columns, label);

			// new dialog
			var d = new frappe.ui.Dialog({
				title: "Edit Section",
				fields: [
					{
						label: __("No of Columns"),
						fieldname: "no_of_columns",
						fieldtype: "Select",
						options: ["1", "2", "3", "4", '5'],
					},
					{
						label: __("Section Heading"),
						fieldname: "label",
						fieldtype: "Data",
						description: __("Will only be shown if section headings are enabled"),
					},
					{
						label: __("add"),
						fieldname: "add",
						fieldtype: "Button",
						click: function () {
							d.hide();
							section.fadeOut(function () {
								section.remove();
							});
						},
						input_class: "btn-primary",
						input_css: {
							"margin-top": "20px",
						},
					},
					{
						label: __("Remove Section"),
						fieldname: "remove_section",
						fieldtype: "Button",
						click: function () {
							d.hide();
							section.fadeOut(function () {
								section.remove();
							});
						},
						input_class: "btn-danger",
						input_css: {
							"margin-top": "20px",
						},
					},

				],
			});
			d.show();
			d.$wrapper.addClass("in")
			d.set_input("no_of_columns", no_of_columns + "");
			d.set_input("label", label || "");

			d.set_primary_action(__("Update"), function () {
				// resize number of columns
				me.update_columns_in_section(
					section,
					no_of_columns,
					cint(d.get_value("no_of_columns"))
				);

				section.attr("data-label", d.get_value("label") || "");
				section.find(".section-label").html(d.get_value("label") || "");

				d.hide();
			});


			// return false;
		});
	}
	update_columns_in_section(section, no_of_columns, new_no_of_columns) {
		var col_size = 12 / new_no_of_columns,
			me = this,
			resize = function () {
				section
					.find(".section-column")
					.removeClass()
					.addClass("section-column")
					.addClass("col-md-" + col_size);
			};

		if (new_no_of_columns < no_of_columns) {
			// move contents of last n columns to previous column
			for (var i = no_of_columns; i > new_no_of_columns; i--) {
				var $col = $(section.find(".print-format-builder-column").get(i - 1));
				var prev = section.find(".print-format-builder-column").get(i - 2);

				// append each field to prev
				$col.parent().addClass("to-drop");
				$col.find(".print-format-builder-field").each(function () {
					$(this).appendTo(prev);
				});
			}

			// drop columns
			section.find(".to-drop").remove();

			// resize
			resize();
		} else if (new_no_of_columns > no_of_columns) {
			// add empty column and resize old columns
			for (var i = no_of_columns; i < new_no_of_columns; i++) {
				var col = $(
					'<div class="section-column">\
					<div class="print-format-builder-column"></div></div>'
				).appendTo(section);
				me.setup_sortable_for_column(col.find(".print-format-builder-column").get(0));
			}
			// resize
			resize();
		}
	}

	setup_column_selector() {
		var me = this;
		this.page.main.on("click", ".select-columns", function () {
			var parent = $(this).parents(".print-format-builder-field:first"),
				doctype = parent.attr("data-doctype"),
				label = parent.attr("data-label"),
				columns = parent.attr("data-columns").split(","),
				column_names = $.map(columns, function (v) {
					return v.split("|")[0];
				}),
				widths = {};

			$.each(columns, function (i, v) {
				var parts = v.split("|");
				widths[parts[0]] = parts[1] || "";
			});

			var d = new frappe.ui.Dialog({
				title: __("Select Table Columns for {0}", [label]),
			});

			var $body = $(d.body);

			var doc_fields = frappe.get_meta(doctype).fields;
			var docfields_by_name = {};

			// docfields by fieldname
			$.each(doc_fields, function (j, f) {
				if (f) docfields_by_name[f.fieldname] = f;
			});

			// add field which are in column_names first to preserve order
			var fields = [];
			$.each(column_names, function (i, v) {
				if (in_list(Object.keys(docfields_by_name), v)) {
					fields.push(docfields_by_name[v]);
				}
			});
			// add remaining fields
			$.each(doc_fields, function (j, f) {
				if (
					f &&
					!in_list(column_names, f.fieldname) &&
					!in_list(["Section Break", "Column Break", "Tab Break"], f.fieldtype) &&
					f.label
				) {
					fields.push(f);
				}
			});
			// render checkboxes
			$(
				frappe.render_template("print_format_builder_column_selector", {
					fields: fields,
					column_names: column_names,
					widths: widths,
				})
			).appendTo(d.body);

			Sortable.create($body.find(".column-selector-list").get(0));

			var get_width_input = function (fieldname) {
				return $body.find(".column-width[data-fieldname='" + fieldname + "']");
			};

			// update data-columns property on update
			d.set_primary_action(__("Update"), function () {
				var visible_columns = [];
				$body.find("input:checked").each(function () {
					var fieldname = $(this).attr("data-fieldname"),
						width = get_width_input(fieldname).val() || "";
					visible_columns.push(fieldname + "|" + width);
				});
				parent.attr("data-columns", visible_columns.join(","));
				d.hide();
			});

			let update_column_count_message = () => {
				// show a warning if user selects more than 10 columns for a table
				let columns_count = $body.find("input:checked").length;
				$body.find(".help-message").toggle(columns_count > 10);
			};
			update_column_count_message();

			// enable / disable input based on selection
			$body.on("click", "input[type='checkbox']", function () {
				var disabled = !$(this).prop("checked"),
					input = get_width_input($(this).attr("data-fieldname"));

				input.prop("disabled", disabled);
				if (disabled) input.val("");

				update_column_count_message();
			});

			d.show();

			return false;
		});
	}
	setup_print_format() {
		var me = this;
		console.log(frappe);
		frappe.model.with_doctype(this.print_format.doc_type, function (doctype) {
			me.meta = frappe.get_meta(me.print_format.doc_type);
			me.setup_sidebar();
			me.render_layout();
			me.page.set_primary_action(__("Save"), function () {
				me.save_print_format();
			});
			me.page.clear_menu();
			me.page.add_menu_item(
				__("Start new Format"),
				function () {
					me.print_format = null;
					me.refresh();
				},
				true
			);
			me.page.clear_inner_toolbar();
			me.page.add_inner_button(__("Edit Properties"), function () {
				frappe.set_route("Form", "Print Format", me.print_format.name);
			});
		});
	}
	setup_sidebar() {
		// prepend custom HTML field
		var fields = [this.get_custom_html_field()].concat(this.meta.fields);
		this.page.sidebar.html(
			$(frappe.render_template("print_format_builder_sidebar", { fields: fields }))
		);
		this.setup_field_filter();
	}
	get_custom_html_field() {
		return {
			fieldtype: "Custom HTML",
			fieldname: "_custom_html",
			label: __("Custom HTML"),
		};
	}
	render_layout() {
		this.page.main.empty();
		this.prepare_data();
		$(
			frappe.render_template("print_format_builder_layout", {
				// data: this.layout_data,
				data: [],
				me: this,
			})
		).appendTo(this.page.main);
		this.setup_sortable();
		this.setup_add_section();
		this.setup_edit_heading();
		this.setup_field_settings();
		this.setup_html_data();
		this.show_preview();
		this.get_fullscreen();
		this.screen_size();
	}
	setup_sortable() {
		var me = this;

		// drag from fields library
		// groups.map((g,i)=>{
		// 	console.log(g);
		// })
		data.map(d => {

		})
		Sortable.create(this.page.sidebar.find(".section_0").get(0), {
			group: {
				name: "field",
				put: true,
				pull: "clone",
			},
			sort: false,
			onAdd: function (evt) {
				// on drop, trash!
				$(evt.item).fadeOut();
			},
		});
		Sortable.create(this.page.sidebar.find(".section_1").get(0), {
			group: {
				name: "field",
				put: true,
				pull: "clone",
			},
			sort: false,
			onAdd: function (evt) {
				// on drop, trash!
				$(evt.item).fadeOut();
			},
		});
		Sortable.create(this.page.sidebar.find(".section_2").get(0), {
			group: {
				name: "field",
				put: true,
				pull: "clone",
			},
			sort: false,
			onAdd: function (evt) {
				// on drop, trash!
				$(evt.item).fadeOut();
			},
		});

		// sort, drag and drop between columns
		this.page.main.find(".print-format-builder-column").each(function () {
			me.setup_sortable_for_column(this);
		});

		// section sorting
		Sortable.create(this.page.main.find(".print-format-builder-layout").get(0), {
			handle: ".print-format-builder-section-head",
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
			group: {
				name: "field1",
				put: true,
				pull: true,
			},
			onAdd: function (evt) {
				// on drop, change the HTML

				var $item = $(evt.item);
				console.log("event", evt, $item)
				if (!$item.hasClass("print-format-builder-field")) {
					var fieldname = $item.attr("data-fieldname");
					if (fieldname === "_custom_html") {
						var field = me.get_custom_html_field();
					} else {
						console.log(frappe);
						var field = me.get_field(fieldname)
					}

					var html = frappe.render_template("print_format_builder_field", {
						field: field,
						me: me,
					});

					$item.replaceWith(html);
				}
			},
		});
	}
	get_field(fieldname) {
		let new_field = ''
		fields.map(f => {
			if (f.name == fieldname) {
				new_field = f
			}
		})
		return new_field
	}

	addTemplate(template) {
		console.log("template",template);
		var me = this;
			var me = this;
			var $section = $(
				frappe.render_template("templates", {
					section: template,
					me: me,  
				})
			).appendTo(me.page.main.find(".print-format-builder-layout"));

			me.setup_sortable_for_column($section.find(".print-format-builder-column").get(0));
	}
// add Template
async setup_add_section() {
	var seleted_layout_id= ""
	var me = this;
	this.page.main.find(".print-format-builder-add-section").on("click", function () {
		// boostrap new section info
			// new dialog
			frappe.call({
				method: "ecommerce_business_store.cms.doctype.section_template_layout.section_template_layout.get_layout_data",
				args: {},
				freeze: true,
				callback: function (r) {
					console.log(">> api response <<",r)
					if(r && r.message && r.message.length > 0){
						pop_up_layout_dialog(r.message)
					}
				},
			});

		function pop_up_layout_dialog(layout_data){
			var r___id = Math.floor(Math.random() * 1000)
			let layout_dialog = new frappe.ui.Dialog({
				title:"Edit Section Layout",
				fields:[
				{fieldname:"layout_html",
					fieldtype:"HTML"		
				}
				]
			})
			let layout_dialog_wrapper = layout_dialog.fields_dict.layout_html.$wrapper
			$(layout_dialog.$wrapper).find(".modal-dialog").css({"min-width":"70%"})
			layout_dialog.show()
			layout_dialog.$wrapper.addClass("in")
			layout_dialog.set_primary_action("Save",()=>{
				// console.log(">> values <<",layout_dialog.get_values())
				get_each_layout_data(seleted_layout_id)
			})
			let p_add_html = ""
			layout_data.map(each_p =>{
				p_add_html += `<div class="each-palette-div" style="flex:0 0 calc(33.33% - 20px);position:relative;">
			<label style="cursor:pointer;width:100%;" value="${each_p.unique_id}">
				<div style="width:80%;height:80px;margin:auto;
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
				<input type="radio"  value="${each_p.unique_id}" name="theme_radio" style="position:absolute;top:6px;right:30px;z-index:99;" ${each_p.unique_id == seleted_layout_id}?"checked":"">
			</label></div>`
			
			})
	
			let p_html =`<div class="palette-main-div" id=${r___id}>
							<div class="palatte-sub-div" style="display:flex;flex-wrap:wrap;gap:20px;">
								${p_add_html}
							</div>
						</div>`
			$(layout_dialog_wrapper).html(p_html)
			
			layout_dialog_wrapper.find(`#${r___id}`).find("input").on("click",(e) =>{
				console.log(">> selected layout id <<",$(e.target).val())
				seleted_layout_id = $(e.target).val()
			})

	}

	});

	function get_each_layout_data(layout_id){
		console.log(">> seleted layout id on save <<",layout_id)
		frappe.call({
			method: "ecommerce_business_store.cms.doctype.section_template_layout.section_template_layout.get_each_layout_data",
			args: {layout_id:layout_id},
			freeze: true,
			callback: function (r) {
				console.log(">> api response <<",r)
				if(r && r.message && r.message.length > 0){
					me.addTemplate(r.message[0]);
				}
			},
		});
	}

}

// 


	get_new_section() {
		return { columns: [], no_of_columns: 1, label: "" };
	}
	get_new_column() {
		return { fields: [] };
	}
	setup_edit_heading() {
		var me = this;
		var $heading = this.page.main.find(".print-format-builder-print-heading");

		// set content property
		$heading.data("content", this.print_heading_template);

		this.page.main.find(".edit-heading").on("click", function () {
			var d = me.get_edit_html_dialog(__("Edit Heading"), __("Heading"), $heading);
		});
	}
	get_edit_html_dialog(title, label, $content) {
		var me = this;
		var d = new frappe.ui.Dialog({
			title: title,
			fields: [
				{
					fieldname: "content",
					fieldtype: "Code",
					label: label,
					options: "HTML",
				},
				{
					fieldname: "help",
					fieldtype: "HTML",
					options:
						"<p>" +
						__(
							"You can add dynamic properties from the document by using Jinja templating."
						) +
						__("For example: If you want to include the document ID, use {0}", [
							"<code>{{ doc.name }}</code>",
						]) +
						"</p>",
				},
			],
		});

		// set existing content in input
		var content = $content.data("content") || "";
		if (content.indexOf(me.get_no_content()) !== -1) content = "";
		d.set_input("content", content);

		d.set_primary_action(__("Update"), function () {
			$($content[0]).data("content", d.get_value("content"));
			$content.html(d.get_value("content"));
			d.hide();
		});

		d.show();

		return d;
	}
	get_no_content() {
		return __("Edit to add content");
	}
	setup_edit_custom_html() {
		var me = this;
		this.page.main.on("click", ".edit-html", function () {
			me.get_edit_html_dialog(
				__("Edit Custom HTML"),
				__("Custom HTML"),
				$(this).parents(".print-format-builder-field:first").find(".html-content")
			);
		});
	}
	setup_field_settings() {
		this.page.main.find(".field-settings").on("click", function () {
			console.log("clicked", field)
			const field = $(e.currentTarget).parent();
			console.log("clicked", field)

			// new dialog
			var d = new frappe.ui.Dialog({
				title: __("Set Properties"),
				fields: [
					{
						label: __("Label"),
						fieldname: "label",
						fieldtype: "Data",
					},
					{
						label: __("Align Value"),
						fieldname: "align",
						fieldtype: "Select",
						options: [
							{ label: __("Left", null, "alignment"), value: "left" },
							{ label: __("Right", null, "alignment"), value: "right" },
						],
					},
					{
						label: __("Remove Field"),
						fieldtype: "Button",
						click: function () {
							d.hide();
							field.remove();
						},
						input_class: "btn-danger",
					},
				],
			});

			d.set_value("label", field.attr("data-label"));

			d.set_primary_action(__("Update"), function () {
				field.attr("data-align", d.get_value("align"));
				field.attr("data-label", d.get_value("label"));
				field.find(".field-label").html(d.get_value("label"));
				d.hide();
			});

			// set current value
			if (field.attr("data-align")) {
				d.set_value("align", field.attr("data-align"));
			} else {
				d.set_value("align", "left");
			}

			d.show();

			return false;
		});
	}
	setup_html_data() {
		// set JQuery `data` for Custom HTML fields, since editing the HTML
		// directly causes problem becuase of HTML reformatting
		//
		// this is based on a dummy attribute custom_html_id, since all custom html
		// fields have the same fieldname `_custom_html`
		var me = this;
		this.page.main.find('[data-fieldtype="Custom HTML"]').each(function () {
			var fieldname = $(this).attr("data-fieldname");
			var content = $($(this).find(".html-content")[0]);
			var html = me.custom_html_dict[parseInt(content.attr("data-custom-html-id"))].options;
			content.data("content", html);
		});
	}
	prepare_data() {
		this.print_heading_template = null;
		if (!this.print_heading_template) {
			// default print heading template
			this.print_heading_template =
				'<div class="print-heading">\
				<h2><div>' +
				// __(this.print_format.doc_type)
				"docTYpe"
				+

				'</div><br><small class="sub-heading">{{ doc.name }}</small>\
				</h2></div>';
		}
		this.data = [
			{
				columns: [
					{
						fields: [
							{
								fieldname: "Login",
								label: "Login",
								fieldtype: "Login",
								image: "https://www.schooleducationgateway.eu/files/jpg11/registration-ga80a41042_1920_600x400_1_600x400.jpg"
							},
							{
								fieldname: "Header",
								label: "Header",
								fieldtype: "Header",
								image: "https://static.wixstatic.com/media/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg/v1/fill/w_924,h_510,al_c,q_90/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg"
							},
						]
					}
				], no_of_columns: 0, label: ""
			}

		]

		this.layout_data = [{
			fieldname: "Login",
			label: "Login",
			fieldtype: "Login",
			image: "https://www.schooleducationgateway.eu/files/jpg11/registration-ga80a41042_1920_600x400_1_600x400.jpg"
		},
		{
			fieldname: "Header",
			label: "Header",
			fieldtype: "Header",
			image: "https://static.wixstatic.com/media/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg/v1/fill/w_924,h_510,al_c,q_90/ea6ac8_70d4744c1fb44ca3a2141575be31bfd7~mv2.jpg"
		},];
		this.fields_dict = {};
		this.custom_html_dict = {};
		var section = null,
			column = null,
			me = this,
			custom_html_count = 0;

		// create a new placeholder for column and set
		// it as "column"
		var set_column = function () {
			if (!section) set_section();
			column = me.get_new_column();
			section.columns.push(column);
			section.no_of_columns += 1;
		};
		var set_section = function (label) {
			section = me.get_new_section();
			if (label) section.label = label;
			column = null;
			me.layout_data.push(section);
		};

		// break the layout into sections and columns
		// so that it is easier to render in a template
		$.each(this.data, function (i, f) {
			me.fields_dict[f.fieldname] = f;
			if (!f.name && f.fieldname) {
				// from format_data (designed format)
				// print_hide should always be false
				if (f.fieldname === "_custom_html") {
					f.label = "Custom HTML";
					f.fieldtype = "Custom HTML";

					// set custom html id to map data properties later
					custom_html_count++;
					f.custom_html_id = custom_html_count;
					me.custom_html_dict[f.custom_html_id] = f;
				} else {
					f = $.extend(
						// frappe.meta.get_docfield(me.print_format.doc_type, f.fieldname) || {},
						frappe.meta.get_docfield("doc", f.fieldname) || {},

						f
					);
				}
			}

			if (f.fieldtype === "Section Break") {
				set_section(f.label);
			} else if (f.fieldtype === "Column Break") {
				set_column();
			} else if (
				!in_list(["Section Break", "Column Break", "Tab Break", "Fold"], f.fieldtype) &&
				f.label
			) {
				if (!column) set_column();

				if (f.fieldtype === "Table") {
					me.add_table_properties(f);
				}

				if (!f.print_hide) {
					column.fields.push(f);
					section.has_fields = true;
				}
			}
		});

		// strip out empty sections
		this.layout_data = $.map(this.layout_data, function (s) {
			return s.has_fields ? s : null;
		});
	}
	save_print_format() {
		var data = [],
			me = this;

		// add print heading as the first field
		// this will be removed and set as a doc property
		// before rendering
		data.push({
			fieldname: "print_heading_template",
			fieldtype: "Custom HTML",
			options: this.page.main.find(".print-format-builder-print-heading").data("content"),
		});

		// add pages
		this.page.main.find(".print-format-builder-section").each(function () {
			var section = { fieldtype: "Section Break", label: $(this).attr("data-label") || "" };
			data.push(section);
			$(this)
				.find(".print-format-builder-column")
				.each(function () {
					data.push({ fieldtype: "Column Break" });
					$(this)
						.find(".print-format-builder-field")
						.each(function () {
							var $this = $(this),
								fieldtype = $this.attr("data-fieldtype"),
								align = $this.attr("data-align"),
								label = $this.attr("data-label"),
								df = {
									fieldname: $this.attr("data-fieldname"),
									print_hide: 0,
								};

							if (align) {
								df.align = align;
							}

							if (label) {
								df.label = label;
							}

							if (fieldtype === "Table") {
								// append the user selected columns to visible_columns
								var columns = $this.attr("data-columns").split(",");
								df.visible_columns = [];
								$.each(columns, function (i, c) {
									var parts = c.split("|");
									df.visible_columns.push({
										fieldname: parts[0],
										print_width: parts[1],
										print_hide: 0,
									});
								});
							}
							if (fieldtype === "Custom HTML") {
								// custom html as HTML field
								df.fieldtype = "HTML";
								df.options = $($this.find(".html-content")[0]).data("content");
							}
							data.push(df);
						});
				});
		});

		// save format_data
		frappe.call({
			method: "frappe.client.set_value",
			args: {
				doctype: "Print Format",
				name: this.print_format.name,
				fieldname: "format_data",
				value: JSON.stringify(data),
			},
			freeze: true,
			btn: this.page.btn_primary,
			callback: function (r) {
				me.print_format = r.message;
				locals["Print Format"][me.print_format.name] = r.message;
				frappe.show_alert({ message: __("Saved"), indicator: "green" });
			},
		});
	}
}
