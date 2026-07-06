// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Web Theme', {
	refresh: function(frm) {
		frm.r___id = Math.floor(Math.random() * 1000)
		frm.trigger("hide_and_set_heading_values")
		frm.trigger("hide_and_set_button_values")
		frm.trigger("hide_and_set_text_values")
		frm.trigger("store_pre_loaded_text")
		frm.trigger("render_image_preview")
		frm.trigger("hide_and_set_global_fonts")
	},
	store_pre_loaded_text(frm){
		frm.pre_stored_text_arr = []
		frm.pre_stored_btn_arr = []
		if(cur_frm.doc.text && cur_frm.doc.text.length != 0){
			cur_frm.doc.text.map(res =>{
				// console.log(res.name1)
				frm.pre_stored_text_arr.push(res.name1)
			})
		}

		if(cur_frm.doc.buttons_table && cur_frm.doc.buttons_table.length != 0){
			cur_frm.doc.buttons_table.map(res =>{
				// console.log(res.name1)
				frm.pre_stored_btn_arr.push(res.name1)
			})
		}
	},
	validate(frm){
		if(cur_frm.doc.text && cur_frm.doc.text.length != 0){
			let tempt_tit_arr = []
			cur_frm.doc.text.map(each_res =>{
				tempt_tit_arr.push(each_res.name1)
			})
			let dub_flage = tempt_tit_arr.filter((item, index) => tempt_tit_arr.indexOf(item) !== index)
			if(dub_flage && dub_flage.length > 0){
				// console.log("dublicate console",dub_flage)
				frappe.validated = false
				frappe.throw("Text names must be unique..!")
			}
		}

		if(cur_frm.doc.buttons_table && cur_frm.doc.buttons_table.length != 0){
			let tempt_tit_arr = []
			cur_frm.doc.buttons_table.map(each_res =>{
				tempt_tit_arr.push(each_res.name1)
			})
			let dub_flage = tempt_tit_arr.filter((item, index) => tempt_tit_arr.indexOf(item) !== index)
			if(dub_flage && dub_flage.length > 0){
				// console.log("dublicate console",dub_flage)
				frappe.validated = false
				frappe.throw("Button names must be unique..!")
			}
		}
	},
	hide_and_set_heading_values(frm){
		if((cur_frm.doc.heading && cur_frm.doc.heading.length == 0) || !cur_frm.doc.heading){
			let heading_data = [{"name1":"Heading 1","type":"h1"},{"name1":"Heading 2","type":"h2"},{"name1":"Heading 3","type":"h3"},{"name1":"Heading 4","type":"h4"},{"name1":"Heading 5","type":"h5"},{"name1":"Heading 6","type":"h6"}]
			heading_data.map(each_data =>{
				frm.add_child('heading', each_data);	
			})
			frm.refresh_field('heading');
		}
		if(cur_frm.doc.heading && cur_frm.doc.heading.length >= 6){
			$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="heading"]').find('.btn.btn-xs.btn-secondary.grid-add-row').css({"display":"none"})
			$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="heading"]').find('[data-action="delete_rows"]').css({"display":"none"})
		}
	},
	hide_and_set_button_values(frm){
		
		if((cur_frm.doc.buttons_table && cur_frm.doc.buttons_table.length == 0) || !cur_frm.doc.buttons_table){
			let heading_data = [{"name1":"Primary Button","type":"primary - btn"},{"name1":"Secondary Button","type":"secondary - btn"},{"name1":"Tertiary Button","type":"tertiary - btn"}]
			heading_data.map(each_data =>{
				frm.add_child('buttons_table', each_data);	
			})
			frm.refresh_field('buttons_table');
		}
		if(cur_frm.doc.buttons_table && cur_frm.doc.buttons_table.length == 3){
			$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="buttons_table"]').find('.btn.btn-xs.btn-secondary.grid-add-row').css({"display":"none"})
			$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="buttons_table"]').find('[data-action="delete_rows"]').css({"display":"none"})
		}
	},
	hide_and_set_text_values(frm){
		if((cur_frm.doc.text && cur_frm.doc.text.length == 0) || !cur_frm.doc.text){
			let heading_data = [{"name1":"Paragraph","type":"p - Paragraph"},{"name1":"Anchor","type":"a - Anchor"},{"name1":"Quote","type":"blockquote - Quote"},{"name1":"Formatted","type":"pre - Formatted"},{"name1":"List","type":"li - List"}]
			heading_data.map(each_data =>{
				frm.add_child('text', each_data);	
			})
			frm.refresh_field('text');
		}
		if(cur_frm.doc.text && cur_frm.doc.text.length == 5){
			$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="text"]').find('.btn.btn-xs.btn-secondary.grid-add-row').css({"display":"none"})
			$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="text"]').find('[data-action="delete_rows"]').css({"display":"none"})
		}
	},
	hide_and_set_global_fonts(frm){
		if((cur_frm.doc.global_fonts && cur_frm.doc.global_fonts.length == 0) || !cur_frm.doc.global_fonts){
			let heading_data = [{"title":"Primary"},{"title":"Secondary"},{"title":"Text"},{"title":"Accent"}]
			heading_data.map(each_data =>{
				frm.add_child('global_fonts', each_data);	
			})
			frm.refresh_field('global_fonts');
		}
		if(cur_frm.doc.global_fonts && cur_frm.doc.global_fonts.length == 4){
			$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="global_fonts"]').find('.btn.btn-xs.btn-secondary.grid-add-row').css({"display":"none"})
			$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="global_fonts"]').find('[data-action="delete_rows"]').css({"display":"none"})
		}
	},
	make_edit_styles_btn_visible(frm){
		$(() =>{
		if(cur_frm.doc.heading && cur_frm.doc.heading.length > 0){
			cur_frm.doc.heading.map(h =>{
				// console.log($(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="heading"]').find('.rows').find(`[data-name="${h.name}"]`).find(`.data-row.row`).addClass("editable-row"))
				$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find('[data-fieldname="heading"]').find('.rows').find(`[data-name="${h.name}"]`).find(`[data-fieldname="edit_styles"] .field-area`).css({"display":"block"})
			})
		}

		if(cur_frm.doc.text && cur_frm.doc.text.length > 0){
			
		}
	})
	},
	pick_color_palette(frm){
		frappe.call({
			method:"go1_cms.go1_cms.doctype.web_theme.web_theme.get_color_palette_datas",
			args:{},
			freeze:true,
			callback:(res) =>{
				// console.log(">> color palatte api response <<",res)
				if(res && res.message && res.message.length > 0){
					frm.events.open_color_palette_popoup(frm,res.message)
					frm.palettes_api_data = res.message
				}
				else{
					frappe.throw("There is no color palette to view..!")
				}
			}
		})
	},
	open_color_palette_popoup(frm,palettes){
		let palatte_dialog = new frappe.ui.Dialog({
			title:"Pick Palette Color",
			fields:[
			{fieldname:"palatte_html",
			 fieldtype:"HTML"		
			}
			],
			secondary_action_label :"New",
			secondary_action(values) {
				let local_docname = frappe.model.make_new_doc_and_get_name('Color Palette')
				frappe.set_route('Form', 'Color Palette', local_docname)
			}
		})
		let palette_wrapper = palatte_dialog.fields_dict.palatte_html.$wrapper
		$(palatte_dialog.$wrapper).find(".modal-dialog").css({"min-width":"70%"})
		palatte_dialog.show()
		// empty seleted palette colour id
		cur_frm.selected_palette_id = ""
		// end
		palatte_dialog.set_primary_action("Save",()=>{
			frm.events.save_update_palette_clr(frm,palatte_dialog)
		})
		let p_add_html = ""
		palettes.map(each_p =>{
			p_add_html += `<div class="each-palette-div" style="flex:0 0 calc(33.33% - 20px);position:relative;">
		<label style="cursor:pointer;width:80%;" value="${each_p.name}">
			<div style="width:100%;height:80px;margin:auto;
				background-image: url(${each_p.image ? "'" + each_p.image.replace(" ",'%20') + "'" : '/files/no-img.jpg'});
				border-radius: 5px;
				background-size:cover;
				background-repeat: no-repeat;
				background-position:top;
				border: 1px solid #e5e5e5;">
			</div>
			<div class="palette" style="width:100%;">
				<p style="margin: 0;font-size: 15px;font-weight: bold;
					margin-top: 10px;color: #222;white-space: nowrap;
					overflow: hidden;text-overflow: ellipsis;text-align:center">${each_p.name1}
				</p>
			</div>
			<input type="radio" value="${each_p.name}" name="theme_radio" onclick="select_unselect_palette($(this))" style="position:absolute;top:2px;right:43px;">
		</label></div>`
		
		})

		let p_html =`<div class="palette-main-div" id=${cur_frm.r___id}>
						<div class="palatte-sub-div" style="display:flex;flex-wrap:wrap;gap:20px;justify-content: center;">
							${p_add_html}
						</div>
					</div>`
		$(palette_wrapper).html(p_html)
	},
	save_update_palette_clr(frm,palatte_dialog){
		if(frm.selected_palette_id){
			// console.log(">>seleted palatte id<<",frm.selected_palette_id)
			frm.palettes_api_data.map(res =>{
				if(frm.selected_palette_id == res.name){
					cur_frm.set_value("palette_image",res.image)
					refresh_field("palette_image")
					frm.trigger("render_image_preview")
					// console.log(">> api selected data<<",res)
					cur_frm.set_value("accent_color",res.accent_color)
					refresh_field("accent_color")
					cur_frm.set_value("body_text_color",res.body_text_color)
					refresh_field("body_text_color")
					cur_frm.set_value("dark_color",res.dark_color)
					refresh_field("dark_color")
					cur_frm.set_value("heading_text_color",res.heading_text_color)
					refresh_field("heading_text_color")
					cur_frm.set_value("light_color",res.light_color)
					refresh_field("light_color")
					cur_frm.set_value("primary_color",res.primary_color)
					refresh_field("primary_color")
					cur_frm.set_value("secondary_color",res.secondary_color)
					refresh_field("secondary_color")
					frm.events.update_default_values(frm,res)
				}
			})
			palatte_dialog.hide();
		}
		else{
			frappe.msgprint("There is no palette colour selected..!")
		}
		// console.log(">> selected palette clr >>",frm.selected_palette_id)
	},
	render_image_preview(frm){
		frm.image_pre_wrapperr = frm.get_field("palette_img_prview").$wrapper
		$(frm.image_pre_wrapperr).empty()
		if(frm.doc.palette_image){
			let html = `<div class="img-previw-tag id="${frm.r___id}">
							<div class="img-subcontainer">
								<div class="preview-img" style="width: 170px;
								height: 54px;
								background-image: url('${frm.doc.palette_image.replace(" ",'%20')}');
								border-radius: 5px;
								background-size: cover;
								background-repeat: no-repeat;
								padding: 5px;
								background-position: top;"></div>
							</div>
						</div>`
			frm.image_pre_wrapperr.html(html)
			refresh_field("palette_img_prview")
		}
	},
	update_default_values(frm,res){
		frappe.call({
			method:"go1_cms.go1_cms.doctype.web_theme.web_theme.get_color_palette_default_datas",
			args:{"palette_id":frm.selected_palette_id},
			freeze:true,
			callback:(res) =>{
				// console.log(">> color palatte  default api response <<",res)
				if(res && res.message && res.message.length > 0){
					frm.palettes_api_default_data = res.message
					frm.events.set_heading_default_color()
					frm.events.set_text_default_color()
					frm.events.set_buttons_default_color()
					cur_frm.doc.__unsaved = 1
					cur_frm.save()
					cur_frm.refresh()
				}
			}
		})
	},
	set_buttons_default_color(){
		if(cur_frm.doc.buttons_table && cur_frm.doc.buttons_table.length > 0){
			// console.log(">> buttons array <<",cur_frm.doc.buttons_table)
			cur_frm.doc.buttons_table.map(btn =>{
				if(btn.css_design && btn.css_design.length > 0){
					cur_frm.palettes_api_default_data.map(api_each_pop =>{
						if(api_each_pop.css_design && api_each_pop.css_design.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update css_design variable data
								let api_css_parse_data = JSON.parse(api_each_pop.css_design).split(";")
								api_css_parse_data.splice(api_css_parse_data.length -1,1)
								let css_parse_data = JSON.parse(btn.css_design).split(";")
								css_parse_data.splice(css_parse_data.length -1,1)

								let css_each_ele_parse_data = []
								let api_css_each_ele_parse_data = []

								api_css_parse_data.map(api_prop =>{
									api_css_each_ele_parse_data.push(api_prop.split(":")[0])
								})

								css_parse_data.map(css_pop =>{
									css_each_ele_parse_data.push(css_pop.split(":")[0])
								})

								api_css_each_ele_parse_data.map(res =>{
									if(css_each_ele_parse_data.includes(res)){
										
										api_css_parse_data.map(each_api_prp =>{
											if(css_parse_data && css_parse_data.length > 0){
												css_parse_data.map((each_pop,idxx) =>{
													let css_key_val = each_pop.split(":")
													if(css_key_val[0] == each_api_prp.split(":")[0]){
														css_parse_data[idxx] = each_api_prp.split(":")[0]+":"+each_api_prp.split(":")[1]
													}
												})
											}
										})
									}
									else{
										api_css_parse_data.map(api_var =>{
											if(api_var.split(":")[0] == res){
												css_parse_data.push(api_var)
											}
										})
									}
								})

								// console.log(">> final table css_design <<",css_parse_data)
								btn.css_design = JSON.stringify(css_parse_data.join(";")+";")
								// console.log(">> btn.css_design <<",btn.css_design)
							}
						}
						if(api_each_pop.style_json && api_each_pop.style_json.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update style_json variable data
								let api_css_parse_data = JSON.parse(api_each_pop.style_json)
								let css_parse_data = JSON.parse(btn.style_json)

								let css_each_ele_parse_data = Object.keys(css_parse_data)
								let api_css_each_ele_parse_data = Object.keys(api_css_parse_data)

								api_css_each_ele_parse_data.map(res =>{
									if(css_each_ele_parse_data.includes(res)){
										Object.keys(api_css_parse_data).map(each_api_prp =>{
											if(css_parse_data && Object.keys(css_parse_data).length > 0){
												Object.keys(css_parse_data).map((each_pop,idxx) =>{
													if(each_pop == each_api_prp && each_pop==res){
														css_parse_data[each_pop] = api_css_parse_data[each_api_prp]
													}
												})
											}
										})
									}
									else{
										Object.keys(api_css_parse_data).map(api_var =>{
											if(api_var == res){
												css_parse_data[res] = api_css_parse_data[api_var]
											}
										})
									}
								})

								// console.log(">> final table style_json  <<",css_parse_data)
								btn.style_json = JSON.stringify(css_parse_data)
								// console.log(">> btn.style_json <<",btn.style_json)
							}
						}
					})
				}
				else{
					cur_frm.palettes_api_default_data.map(api_each_pop =>{
						if(api_each_pop.css_design && api_each_pop.css_design.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update css_design variable data
								btn.css_design = api_each_pop.css_design	
								// console.log(">> btn.css_design <<",btn.css_design)
							}
						}
						if(api_each_pop.style_json && api_each_pop.style_json.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update style_json variable data
								btn.style_json = api_each_pop.style_json
								// console.log(">> btn.style_json <<",btn.style_json)
							}
						}
					})
				}
			})
		}
	},
	set_text_default_color(){
		if(cur_frm.doc.text && cur_frm.doc.text.length > 0){
			// console.log(">> Text array <<",cur_frm.doc.text)
			cur_frm.doc.text.map(btn =>{
				if(btn.css_design && btn.css_design.length > 0){
					cur_frm.palettes_api_default_data.map(api_each_pop =>{
						if(api_each_pop.css_design && api_each_pop.css_design.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update css_design variable data
								let api_css_parse_data = JSON.parse(api_each_pop.css_design).split(";")
								api_css_parse_data.splice(api_css_parse_data.length -1,1)
								let css_parse_data = JSON.parse(btn.css_design).split(";")
								css_parse_data.splice(css_parse_data.length -1,1)

								let css_each_ele_parse_data = []
								let api_css_each_ele_parse_data = []

								api_css_parse_data.map(api_prop =>{
									api_css_each_ele_parse_data.push(api_prop.split(":")[0])
								})

								css_parse_data.map(css_pop =>{
									css_each_ele_parse_data.push(css_pop.split(":")[0])
								})

								api_css_each_ele_parse_data.map(res =>{
									if(css_each_ele_parse_data.includes(res)){
										
										api_css_parse_data.map(each_api_prp =>{
											if(css_parse_data && css_parse_data.length > 0){
												css_parse_data.map((each_pop,idxx) =>{
													let css_key_val = each_pop.split(":")
													if(css_key_val[0] == each_api_prp.split(":")[0]){
														css_parse_data[idxx] = each_api_prp.split(":")[0]+":"+each_api_prp.split(":")[1]
													}
												})
											}
										})
									}
									else{
										api_css_parse_data.map(api_var =>{
											if(api_var.split(":")[0] == res){
												css_parse_data.push(api_var)
											}
										})
									}
								})

								// console.log(">> final table css_design <<",css_parse_data)
								btn.css_design = JSON.stringify(css_parse_data.join(";")+';')
								// console.log(">> text css_design <<",btn.css_design)
							}
						}
						if(api_each_pop.style_json && api_each_pop.style_json.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update style_json variable data
								let api_css_parse_data = JSON.parse(api_each_pop.style_json)
								let css_parse_data = JSON.parse(btn.style_json)

								let css_each_ele_parse_data = Object.keys(css_parse_data)
								let api_css_each_ele_parse_data = Object.keys(api_css_parse_data)

								api_css_each_ele_parse_data.map(res =>{
									if(css_each_ele_parse_data.includes(res)){
										Object.keys(api_css_parse_data).map(each_api_prp =>{
											if(css_parse_data && Object.keys(css_parse_data).length > 0){
												Object.keys(css_parse_data).map((each_pop,idxx) =>{
													if(each_pop == each_api_prp && each_pop==res){
														css_parse_data[each_pop] = api_css_parse_data[each_api_prp]
													}
												})
											}
										})
									}
									else{
										Object.keys(api_css_parse_data).map(api_var =>{
											if(api_var == res){
												css_parse_data[res] = api_css_parse_data[api_var]
											}
										})
									}
								})

								// console.log(">> final table style_json  <<",css_parse_data)
								btn.style_json = JSON.stringify(css_parse_data)
								// console.log(">> text style_json <<",btn.style_json)
							}
						}
					})
				}

				else{
					cur_frm.palettes_api_default_data.map(api_each_pop =>{
						if(api_each_pop.css_design && api_each_pop.css_design.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update css_design variable data
								btn.css_design = api_each_pop.css_design	
								// console.log(">> btn.css_design <<",btn.css_design)
							}
						}
						if(api_each_pop.style_json && api_each_pop.style_json.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update style_json variable data
								btn.style_json = api_each_pop.style_json
								// console.log(">> btn.style_json <<",btn.style_json)
							}
						}
					})
				}
			})
		}
	},
	set_heading_default_color(){
		if(cur_frm.doc.heading && cur_frm.doc.heading.length > 0){
			// console.log(">> heading array <<",cur_frm.doc.heading)
			cur_frm.doc.heading.map(btn =>{
				if(btn.css_design && btn.css_design.length > 0){
					cur_frm.palettes_api_default_data.map(api_each_pop =>{
						if(api_each_pop.css_design && api_each_pop.css_design.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update css_design variable data
								let api_css_parse_data = JSON.parse(api_each_pop.css_design).split(";")
								api_css_parse_data.splice(api_css_parse_data.length -1,1)
								let css_parse_data = JSON.parse(btn.css_design).split(";")
								css_parse_data.splice(css_parse_data.length -1,1)

								let css_each_ele_parse_data = []
								let api_css_each_ele_parse_data = []

								api_css_parse_data.map(api_prop =>{
									api_css_each_ele_parse_data.push(api_prop.split(":")[0])
								})

								css_parse_data.map(css_pop =>{
									css_each_ele_parse_data.push(css_pop.split(":")[0])
								})

								api_css_each_ele_parse_data.map(res =>{
									if(css_each_ele_parse_data.includes(res)){
										api_css_parse_data.map(each_api_prp =>{
											if(css_parse_data && css_parse_data.length > 0){
												css_parse_data.map((each_pop,idxx) =>{
													let css_key_val = each_pop.split(":")
													if(css_key_val[0] == each_api_prp.split(":")[0] && css_key_val[0]==res){
														css_parse_data[idxx] = each_api_prp.split(":")[0]+":"+each_api_prp.split(":")[1]
													}
												})
											}
										})
									}
									else{
										api_css_parse_data.map(api_var =>{
											if(api_var.split(":")[0] == res){
												css_parse_data.push(api_var)
											}
										})
									}
								})

								// console.log(">> final table css_design <<",css_parse_data)
								btn.css_design = JSON.stringify(css_parse_data.join(";")+';')
								// console.log(">> heading css_design <<",btn.css_design)
							}
						}
						if(api_each_pop.style_json && api_each_pop.style_json.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update style_json variable data
								let api_css_parse_data = JSON.parse(api_each_pop.style_json)
								let css_parse_data = JSON.parse(btn.style_json)

								let css_each_ele_parse_data = Object.keys(css_parse_data)
								let api_css_each_ele_parse_data = Object.keys(api_css_parse_data)

								api_css_each_ele_parse_data.map(res =>{
									if(css_each_ele_parse_data.includes(res)){
										Object.keys(api_css_parse_data).map(each_api_prp =>{
											if(css_parse_data && Object.keys(css_parse_data).length > 0){
												Object.keys(css_parse_data).map((each_pop,idxx) =>{
													if(each_pop == each_api_prp && each_pop==res){
														css_parse_data[each_pop] = api_css_parse_data[each_api_prp]
													}
												})
											}
										})
									}
									else{
										Object.keys(api_css_parse_data).map(api_var =>{
											if(api_var == res){
												css_parse_data[res] = api_css_parse_data[api_var]
											}
										})
									}
								})

								// console.log(">> final table style_json  <<",css_parse_data)
								btn.style_json = JSON.stringify(css_parse_data)
								// console.log(">> heading style_json <<",btn.style_json)
							}
						}
					})
				}
				else{
					cur_frm.palettes_api_default_data.map(api_each_pop =>{
						if(api_each_pop.css_design && api_each_pop.css_design.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update css_design variable data
								btn.css_design = api_each_pop.css_design	
								// console.log(">> btn.css_design <<",btn.css_design)
							}
						}
						if(api_each_pop.style_json && api_each_pop.style_json.length > 0){
							if(btn.type == api_each_pop.type){
								// compare and update style_json variable data
								btn.style_json = api_each_pop.style_json
								// console.log(">> btn.style_json <<",btn.style_json)
							}
						}
					})
				}
			})
		}
	}
});


frappe.ui.form.on('Typography Heading', {
	form_render(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-danger.btn-sm.pull-right.grid-delete-row").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row-below.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-duplicate-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-append-row").css({"display":"none"})
		align_edit_style_btn(frm,item)
	},
	edit_styles(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		// console.log(">> type <<",item.type)
		if(item.type){
			frappe.call({
				method:"go1_cms.go1_cms.doctype.web_theme.web_theme.get_json_render_properties",
				args:{field_type:item.type},
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
	}
})


frappe.ui.form.on('Typography Text', {
	form_render(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-danger.btn-sm.pull-right.grid-delete-row").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row-below.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-duplicate-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-append-row").css({"display":"none"})
		align_edit_style_btn(frm,item)
	},
	edit_styles(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		// console.log(">> type <<",item.type)
		if(item.type){
			frappe.call({
				method:"go1_cms.go1_cms.doctype.web_theme.web_theme.get_json_render_properties",
				args:{field_type:item.type},
				freeze:true,
				callback:(res) =>{
					// console.log(">> api response <<",res)
					if(res && res.message && res.message.length > 0){
						res.message[0].css_json = item.style_json ? item.style_json:null
						res.message[0].field_key = item.type.replace(/[&\/ \\#,+()$~%.'":*?<>{}]/g, '').split("-")[0]
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
	name1(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		store_pre_loaded_text(frm,item.name1)
	},
	before_text_remove(frm,cdt,cdn){
		let del_item = locals[cdt][cdn];
		let text_data = ["Paragraph","Anchor","Quote","Formatted","List"]
		if(del_item && del_item.name1 && text_data.includes(del_item.name1)){
			frappe.validated = false;
			frappe.throw(`Row <b>${del_item.idx}</b> with value <b>${del_item.name1}</b> can't be delete..!`)
		}
	}
})

function store_pre_loaded_text(frm,title){
	if(cur_frm.doc.text.length != 0){
		if(frm.pre_stored_text_arr.includes(title)){
			frappe.validated=false
			frappe.throw("Name must be unique..!")
		}
		frm.pre_stored_text_arr = []
		cur_frm.doc.text.map(res =>{
			// console.log(res.name1)
			frm.pre_stored_text_arr.push(res.name1)
		})
	}
}

frappe.ui.form.on('Web Theme Button', {
	form_render(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-danger.btn-sm.pull-right.grid-delete-row").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row-below.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-duplicate-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-append-row").css({"display":"none"})
		align_edit_style_btn(frm,item)
	},
	edit_styles(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		// console.log(">> type <<",item.type)
		if(item.type){
			frappe.call({
				method:"go1_cms.go1_cms.doctype.web_theme.web_theme.get_json_render_properties",
				args:{field_type:item.type},
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
	name1(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		store_pre_loaded_btn(frm,item.name1)
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

function store_pre_loaded_btn(frm,title){
	if(cur_frm.doc.buttons_table.length != 0){
		if(frm.pre_stored_btn_arr.includes(title)){
			frappe.validated=false
			frappe.throw("Name must be unique..!")
		}
		frm.pre_stored_btn_arr = []
		cur_frm.doc.buttons_table.map(res =>{
			// console.log(res.name1)
			frm.pre_stored_btn_arr.push(res.name1)
		})
	}
}

frappe.ui.form.on('Global Fonts', {
	form_render(frm,cdt,cdn){
		let item = locals[cdt][cdn];
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-danger.btn-sm.pull-right.grid-delete-row").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row-below.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-insert-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-duplicate-row.hidden-xs").css({"display":"none"})
		$(`[data-route="Form/Web Theme/${cur_frm.doc.name}"]`).find(`[data-name="${item.name}"]`).find(".btn.btn-secondary.btn-sm.pull-right.grid-append-row").css({"display":"none"})
	},
	font_family(frm,cdt,cdn){
		let item = locals[cdt][cdn];

	},
	font_weight(frm,cdt,cdn){
		let item = locals[cdt][cdn];

	}
})

function align_edit_style_btn(frm,item){
	let btn_wrapper = frm.fields_dict[item.parentfield].grid.grid_rows_by_docname[item.name].grid_form.fields_dict['edit_styles'].wrapper
	$(btn_wrapper).find(".btn.btn-xs.btn-default").css({"margin-top":"27px"})
	$(btn_wrapper).find(".btn.btn-xs.btn-default").attr("class","btn btn-xs btn-primary")
}

function open_edit_styles_popup(item, res) {
	// console.log(">> Api modified <<", res)
	var css_fonts_list = res.fonts_list;
	if (res.css_properties_list.length > 0) {
		let data = res.css_properties_list
		let json_data = {}
		var fonts_data = [" ","Primary(Font Family)","Secondary(Font Family)","Text(Font Family)","Accent(Font Family)"]
		var global_fonts_data = [" ","Primary(Font Family)","Secondary(Font Family)","Text(Font Family)","Accent(Font Family)"]
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
		var units_sections_field_with_units = [];
		var enable_font_media_query=false
		var fonts_media_query_data={}
		// gradient and mask and pattern value store variable
		var gra_patt_mask = {}
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
						// child_properties[k].default = value
						// modified for units set 
						if (key == child_properties[k].fieldname) {
							// console.log(key,">> == <<",value)
							if (!child_properties[k].allow_media_query && key != "font-size" && value && (value.toString().endsWith("-px") || value.toString().endsWith("-%") || value.toString().endsWith("-em") || value.toString().endsWith("-rem"))) {
								child_properties[k].default = value.split("-")[0]

								if (child_properties[k].allow_units) {
									if (child_properties[k].allow_units == 1) {
										units_sections_field_with_units.push({ "field_name": child_properties[k].fieldname, "unit": value.split("-")[1] })
									}
								}

							}
							// console.log(key,">> equal <<",value,">> child properties <<",child_properties[k].fieldname)
							else if ((key == child_properties[k].fieldname && key == "bg-gradient-color") || (key == child_properties[k].fieldname && key == "bg-pattern-color") || (key == child_properties[k].fieldname && key == "bg-mask-color")) {
								if (child_properties[k].fieldname == "bg-gradient-color") {
									// console.log(">> gradiant value <<",value)
									gra_patt_mask["bg-gradient-color"] = value
								}
								else if (child_properties[k].fieldname == "bg-pattern-color") {
									gra_patt_mask["bg-pattern-color"] = value
								}
								else if (child_properties[k].fieldname == "bg-mask-color") {
									gra_patt_mask["bg-mask-color"] = value
								}
							}

							else if(value && key == "font-size" && child_properties[k].allow_media_query){
								enable_font_media_query = true
								
								Object.keys(value).map(each =>{
										if(each == "mbl-font-size"){
											fonts_media_query_data['mbl-font-size'] = value['mbl-font-size']
										}
										else if(each == "tab-font-size"){
											fonts_media_query_data['tab-font-size'] = value['tab-font-size']
										}
										else if(each == "pc-font-size"){
											fonts_media_query_data['pc-font-size'] = value['pc-font-size']
											child_properties[k].default = value['pc-font-size'].split('-')[0]
											if (child_properties[k].allow_units) {
												if (child_properties[k].allow_units == 1) {
													units_sections_field_with_units.push({ "field_name": child_properties[k].fieldname, "unit": value['pc-font-size'].split('-')[1] })
												}
											}
										}
									})			
							}

							else {
								child_properties[k].default = value
							}
							// end
						}
					}

					if (child_properties[k].fieldname != 'font-family') {
						if(child_properties[k].fieldname == "font-weight"){
							let weight_label = ["Primary(Font Weight)","Secondary(Font Weight)","Text(Font Weight)","Accent(Font Weight)"]
							child_properties[k].options.push(...weight_label)
							fields.push(child_properties[k])
						}

						else{
							fields.push(child_properties[k])
							if(child_properties[k].fieldname == "font-size" && child_properties[k].allow_media_query){
								enable_font_media_query = true
							}
						}
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
						}
					}
				}

			}
			else {
				for (const [key, value] of Object.entries(json_data)) {
					if (key == filelist[i].fieldname) {
						// filelist[i].default = value
						// modified for units set 
						if(!filelist[i].allow_media_query && key != "font-size" &&  value && (value.toString().endsWith("-px") || value.toString().endsWith("-%") || value.toString().endsWith("-em") || value.toString().endsWith("-rem"))){
							filelist[i].default = value.split("-")[0]

							if (filelist[i].allow_units) {
								if (filelist[i].allow_units == 1) {
									units_sections_field_with_units.push({"field_name":filelist[i].fieldname,"unit":value.split("-")[1]})
								}
							}

						}

						else if((key == filelist[i].fieldname && key == "bg-gradient-color") || (key == filelist[i].fieldname && key == "bg-pattern-color") || (key == filelist[i].fieldname && key == "bg-mask-color")){
							if(filelist[i].fieldname == "bg-gradient-color"){
								gra_patt_mask["bg-gradient-color"] = value
							}
							else if(filelist[i].fieldname == "bg-pattern-color"){
								gra_patt_mask["bg-pattern-color"] = value
							}
							else if(filelist[i].fieldname == "bg-mask-color"){
								gra_patt_mask["bg-mask-color"] = value
							}
						}
						else if(value && key == "font-size" && filelist[i].allow_media_query){
							enable_font_media_query = true
							Object.keys(value).map(each =>{
								if(each == "mbl-font-size"){
									fonts_media_query_data['mbl-font-size'] = value['mbl-font-size']
								}
								else if(each == "tab-font-size"){
									fonts_media_query_data['tab-font-size'] = value['tab-font-size']
								}
								else if(each == "pc-font-size"){
									fonts_media_query_data['pc-font-size'] = value['pc-font-size']
									filelist[i].default = value['pc-font-size'].split('-')[0]
									if (filelist[i].allow_units) {
										if (filelist[i].allow_units == 1) {
											units_sections_field_with_units.push({"field_name":filelist[i].fieldname,"unit":value['pc-font-size'].split('-')[1]})
										}
									}
								}
							})
						}

						else{
							filelist[i].default = value
						}
						// end
					}
				}
				
				if (filelist[i].fieldname != 'font-family') {
					if(filelist[i].fieldname == "font-weight"){
						let weight_label = ["Primary(Font Weight)","Secondary(Font Weight)","Text(Font Weight)","Accent(Font Weight)"]
						filelist[i].options.push(...weight_label)
						fields.push(filelist[i]);
					}
					else{
						fields.push(filelist[i]);
						if(filelist[i].fieldname == "font-size" && filelist[i].allow_media_query){
							enable_font_media_query = true
						}
					}
				}
				else {
					fields.push({ 'fieldtype': "Select", 'fieldname': filelist[i].fieldname, 'label': filelist[i].label, 'default': filelist[i].default, 'options': fonts_data })

				}
				
				if (filelist[i].allow_units) {
					if (filelist[i].allow_units == 1) {
						units_sections.push(filelist[i].fieldname);
					}
				}
			}
		}
		var elementstyledialog = new frappe.ui.Dialog({
			title: "Edit Style",
			fields: fields
		});
		elementstyledialog.show();
		// console.log(">> already stored values<<",gra_patt_mask)
		elementstyledialog.$wrapper.addClass("in")

		// for background gradient mask and pattern modification
		
		var popup_variable_color_codes ={}
		let gradient_html = `<div class="gradient_modify_sec">
								<div class="btn-title-gradient">
									Background Gradient
								</div>
								<div class="btn-previw-section" style="width:50%;">
									<div class="gradient-color" style="${gra_patt_mask['bg-gradient-color']?'background:'+gra_patt_mask["bg-gradient-color"]+';':''}float:left;margin-right: 10px;width:35px;height:26px;border-radius:7px;margin-top:10px;"></div>
								</div>
								</div>`
		$(gradient_html).insertBefore(elementstyledialog.$wrapper.find('[data-fieldname="bg-gradient-color"] button'))
		
		let mask_html = `<div class="mask_modify_sec">
								<div class="btn-title-mask">
									Background Mask
								</div>
								<div class="btn-previw-section" style="width:50%;">
									<div class="mask-color" style="${gra_patt_mask['bg-mask-color']?'background-image:url("'+gra_patt_mask["bg-mask-color"]+'");':''}float:left;margin-right: 10px;width:35px;height:26px;border-radius:7px;margin-top:10px;"></div>
								</div>
								</div>`
		$(mask_html).insertBefore(elementstyledialog.$wrapper.find('[data-fieldname="bg-mask-color"] button'))

		let pattern_html = `<div class="pattern_modify_sec">
								<div class="btn-title-pattern">
									Background Pattern
								</div>
								<div class="btn-previw-section" style="width:50%;">
									<div class="pattern-color" style="${gra_patt_mask['bg-pattern-color']?'background-image:url("'+gra_patt_mask["bg-pattern-color"]+'");':''}float:left;margin-right: 10px;width:35px;height:26px;border-radius:7px;margin-top:10px;"></div>
								</div>
								</div>`
		$(pattern_html).insertBefore(elementstyledialog.$wrapper.find('[data-fieldname="bg-pattern-color"] button'))

		elementstyledialog.$wrapper.find('[data-fieldname="bg-gradient-color"] button').on("click",(e) =>{
			// console.log(">> gradinat color working<<")
			poup_bg_dialog('Gradient')
		})
		elementstyledialog.$wrapper.find('[data-fieldname="bg-pattern-color"] button').on("click",(e) =>{
			// console.log(">> pattern color working <<")
			poup_bg_dialog('Pattern')
		})
		elementstyledialog.$wrapper.find('[data-fieldname="bg-mask-color"] button').on("click",(e) =>{
			// console.log(">> mask color working <<")
			poup_bg_dialog('Mask')
		})

		// end
		elementstyledialog.$wrapper.find(".modal-dialog").attr("id", item.name);
		elementstyledialog.set_primary_action(__('Save'), function () {
			let values = elementstyledialog.get_values();
			// console.log(">> submitted values<<",values)
			let style_json = {}
			let css_design =""

			filelist.map(each_list => {
				if(each_list.child_properties && each_list.child_properties.length > 0){
					each_list.child_properties.map(ls =>{
						if(ls.hasOwnProperty('variable_name')){
							if(ls.variable_name == "--go1-button-$-gc"){
								// console.log(">> varilable name<<",ls.variable_name)
								if(popup_variable_color_codes.hasOwnProperty('bg-gradient-color')){
									popup_variable_color_codes['bg-gradient-color']?(css_design += ls.variable_name.replace('$',res.field_key)+":"+popup_variable_color_codes['bg-gradient-color']):""
								}
								else if(gra_patt_mask.hasOwnProperty('bg-gradient-color')){
									gra_patt_mask['bg-gradient-color']?(css_design += ls.variable_name.replace('$',res.field_key)+":"+gra_patt_mask['bg-gradient-color']):""
								}
							}
						}
					})
				}
			})

			if (enable_font_media_query) {
				style_json['font-size'] = {}
				Object.keys(fonts_media_query_data).map(e_res => {
					if (e_res == "mbl-font-size") {
						style_json['font-size']['mbl-font-size'] = fonts_media_query_data[e_res]
					}
					else if (e_res == "tab-font-size") {
						style_json['font-size']['tab-font-size'] = fonts_media_query_data[e_res]
					}
					else if (e_res == "pc-font-size") {
						style_json['font-size']['pc-font-size'] = fonts_media_query_data[e_res]
					}
				})

			}


			for (let k in values) {
				if (values[k] != "" && values[k] != "0px") {
					// console.log(`>> values -- ${k} <<`,values[k])
					// modified save with units
					
					var is_allow_units = 0;
					var units = '';
					if (elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").attr("allow-units")) {
						if (elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").attr("allow-units") == "1") {
							is_allow_units = 1;
						}
					}
					if (is_allow_units == 1) {
						units = elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + k + "']").parent().find('select.unit').val();
					}
					if(units && k != "font-size"){
						style_json[k] = values[k] +'-'+units
					}
					else{	
						if(k != "font-size"){
							style_json[k] = values[k]
						}
					}
					
					// end

					filelist.map(each_list => {
						if(each_list.child_properties && each_list.child_properties.length > 0){
							each_list.child_properties.map(ls =>{
								if(ls.fieldname == k){
									// console.log("each field json",ls)
									// console.log(ls.fieldname,"==",k)
									if(ls.hasOwnProperty('variable_name')){
										// console.log("--values--",values[k])
										if (k == "background-image") {
											css_design += ls.variable_name.replace('$',res.field_key)+":"+"url('" + values[k] + "');"
										}

										else if (k == "font-family") {
											// let font_famil_name = res.fonts_list.find(o => o.name === values[k]);
											// if (font_famil_name) {
											// 	css_design += ls.variable_name.replace('$',res.field_key)+":"+font_famil_name.font_family+";"
											// }
											let font_famil_name = fonts_data.find(o => o === values[k]);
											let check_global = global_fonts_data.find(o=>o===values[k]);
											if(check_global==undefined || check_global == ""){
												var css_font_name = css_fonts_list.find(o=> o.name==values[k])
												if(css_font_name!=undefined && css_font_name!=""){
													font_famil_name= css_font_name.font_family;
												}
											}
											// console.log(font_famil_name)
											if (font_famil_name) {
												css_design += ls.variable_name.replace('$',res.field_key)+":"+font_famil_name+";"
											}
										}

										else {
											if(k != "font-size"){
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
												css_design += ls.variable_name.replace('$',res.field_key)+":"+values[k] + units +";"
											}
										}

									}
								}
							})
						}
					})
				}

				filelist.map(each_list => {
					if (each_list.child_properties && each_list.child_properties.length > 0) {
						each_list.child_properties.map(ls => {
							if (ls.fieldname == k) {
								// console.log("each field json",ls)
								// console.log(ls.fieldname,"==",k)
								if (ls.hasOwnProperty('variable_name')) {
									if (k == "font-size" && ls.allow_media_query && enable_font_media_query) {
										Object.keys(fonts_media_query_data).map(e_res => {
											if (e_res == "mbl-font-size") {
												css_design += ls.variable_name.replace('$', res.field_key) + "-mbl:" + fonts_media_query_data[e_res].split('-').join('') + ";"
											}
											else if (e_res == "tab-font-size") {
												css_design += ls.variable_name.replace('$', res.field_key) + "-tab:" + fonts_media_query_data[e_res].split('-').join('') + ";"
											}
											else if (e_res == "pc-font-size") {
												css_design += ls.variable_name.replace('$', res.field_key) + "-pc:" + fonts_media_query_data[e_res].split('-').join('') + ";"
											}
										})
									}
								}
							}
						})
					}
				})
			}
			
			// store selected css in child table
			if(popup_variable_color_codes.hasOwnProperty('bg-gradient-color')){
				popup_variable_color_codes['bg-gradient-color']?(style_json['bg-gradient-color']=popup_variable_color_codes['bg-gradient-color']):""
			}
			else if(gra_patt_mask.hasOwnProperty('bg-gradient-color')){
				gra_patt_mask['bg-gradient-color']?(style_json['bg-gradient-color']=gra_patt_mask['bg-gradient-color']):""
			}

			if(popup_variable_color_codes.hasOwnProperty('bg-pattern-color')){
				popup_variable_color_codes['bg-pattern-color']?(style_json['bg-pattern-color']=popup_variable_color_codes['bg-pattern-color']):""
			}
			else if(gra_patt_mask.hasOwnProperty('bg-pattern-color')){
				gra_patt_mask['bg-pattern-color']?(style_json['bg-pattern-color']=gra_patt_mask['bg-pattern-color']):""
			}

			if(popup_variable_color_codes.hasOwnProperty('bg-mask-color')){
				popup_variable_color_codes['bg-mask-color']?(style_json['bg-mask-color']=popup_variable_color_codes['bg-mask-color']):""
			}
			else if(gra_patt_mask.hasOwnProperty('bg-mask-color')){
				gra_patt_mask['bg-mask-color']?(style_json['bg-mask-color']=gra_patt_mask['bg-mask-color']):""
			}
			

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
			elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='" + child_sections[i] + "']").parent().parent().parent().parent().attr("style", "margin-bottom:10px;border-top:none !important;margin-top: -20px;width: calc(100% + 40px);margin-left: -20px;padding-left: 20px;padding-right: 20px;margin-bottom: 0;position: relative;m");
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
			select_html = '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
			select_html += '<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 6px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
			elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().append(select_html);
			elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().find("select").val((units_sections_field_with_units[i] && units_sections_field_with_units[i].unit)? units_sections_field_with_units[i].unit:"px")
	
			// org content

			// var select_html = '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
			// select_html += '<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 12px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
			// elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().append(select_html);
		
			// end
		}

		if(enable_font_media_query){
			elementstyledialog.$wrapper.find('[data-fieldname="font-size"] label').parent().css({"display":"flex","gap":"10px","align-items":"center"})
			elementstyledialog.$wrapper.find('[data-fieldname="font-size"] label').parent().css({"display":"flex","gap":"10px","align-items":"center"})
			elementstyledialog.$wrapper.find('[data-fieldname="font-size"] label').parent().append(`<i id="mbl-font-icon" style="font-size:20px;cursor:pointer;padding-bottom:3px;" class="fa fa-mobile" aria-hidden="true"></i>
			<i id="tab-font-icon" style="font-size:15px;cursor:pointer;" class="fa fa-tablet" aria-hidden="true"></i>
			<i id="pc-font-icon" style="font-size:15px;cursor:pointer;font-weight: 700;color: #0101ff;" class="fa fa-desktop" aria-hidden="true"></i>`)
			elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').attr("input_value","Web")
			elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #mbl-font-icon').on("click",()=>{
				// console.log(">>mbl working<<")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').attr("input_value","Mobile")
				 if(fonts_media_query_data['mbl-font-size']){
					elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val(fonts_media_query_data['mbl-font-size'].split('-')[0])
					elementstyledialog.$wrapper.find(".form-control[data-fieldname='font-size']").parent().find("select").val(fonts_media_query_data['mbl-font-size'].split('-')[1]? fonts_media_query_data['mbl-font-size'].split('-')[1]:"px")
				}
				else{
					elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val('')
				}
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #mbl-font-icon').attr("style","font-size:22px;cursor:pointer;font-weight: 700;color: #0101ff;")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #pc-font-icon').attr("style","font-size:15px;cursor:pointer;")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #tab-font-icon').attr("style","font-size:15px;cursor:pointer;")
			})
			elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #tab-font-icon').on("click",()=>{
				// console.log(">>tab working<<")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').attr("input_value","Tab")
				if(fonts_media_query_data['tab-font-size']){
					elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val(fonts_media_query_data['tab-font-size'].split('-')[0])
					elementstyledialog.$wrapper.find(".form-control[data-fieldname='font-size']").parent().find("select").val(fonts_media_query_data['tab-font-size'].split('-')[1]? fonts_media_query_data['tab-font-size'].split('-')[1]:"px")
				}
				else{
					elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val('')
				}
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #tab-font-icon').attr("style","font-size:17px;cursor:pointer;font-weight: 700;color: #0101ff;")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #pc-font-icon').attr("style","font-size:15px;cursor:pointer;")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #mbl-font-icon').attr("style","font-size:20px;cursor:pointer;")
			})
			elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #pc-font-icon').on("click",()=>{
				// console.log(">>pc working<<")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').attr("input_value","Web")
				if(fonts_media_query_data['pc-font-size']){
					elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val(fonts_media_query_data['pc-font-size'].split('-')[0])
					elementstyledialog.$wrapper.find(".form-control[data-fieldname='font-size']").parent().find("select").val(fonts_media_query_data['pc-font-size'].split('-')[1]? fonts_media_query_data['pc-font-size'].split('-')[1]:"px")
				}
				else{
					elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val('')
				}
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #pc-font-icon').attr("style","font-size:17px;cursor:pointer;font-weight: 700;color: #0101ff;")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #mbl-font-icon').attr("style","font-size:20px;cursor:pointer;")
				elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #tab-font-icon').attr("style","font-size:15px;cursor:pointer;")
			})
			$(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input')).on("keyup",(e)=>{
				let entered_value = $(e.target).val()
				let unit = $(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] select')).val()
				let input_value = $(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input')).attr("input_value")
				// console.log(`>>${input_value} Entered value<<`,entered_value+unit)
				if(input_value == "Web"){
					fonts_media_query_data['pc-font-size'] = entered_value+'-'+unit;
				}
				else if(input_value == "Tab"){
					fonts_media_query_data['tab-font-size'] = entered_value+'-'+unit;
				}
				else if(input_value == "Mobile"){
					fonts_media_query_data['mbl-font-size'] = entered_value+'-'+unit;
				}
				// console.log(">> all fonts value<<",fonts_media_query_data)
			})
			$(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] select')).on("change",(e)=>{
				// console.log(">> selectd value<<",$(e.target).val())
				let unit = $(e.target).val()
				let input_value = $(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input')).attr("input_value")
				if(input_value == "Web"){
					if(fonts_media_query_data['pc-font-size']){
						let each_val= fonts_media_query_data['pc-font-size'].split('-')
						fonts_media_query_data['pc-font-size'] =each_val[0]+'-'+unit
					}
				}
				else if(input_value == "Tab"){
					if(fonts_media_query_data['tab-font-size']){
						let each_val= fonts_media_query_data['tab-font-size'].split('-')
						fonts_media_query_data['tab-font-size'] =each_val[0]+'-'+unit
					}
				}
				else if(input_value == "Mobile"){
					if(fonts_media_query_data['mbl-font-size']){
						let each_val= fonts_media_query_data['mbl-font-size'].split('-')
						fonts_media_query_data['mbl-font-size'] =each_val[0]+'-'+unit
					}
				}
			});
		}	
		

		elementstyledialog.$wrapper.find('.modal-dialog').css("max-width", "700px");

		function poup_bg_dialog(bg_type){
			frappe.call({
				method:"go1_cms.go1_cms.doctype.web_theme.web_theme.get_color_code_data",
				args:{bg_type:bg_type},
				freeze:true,
				callback:(res) =>{
					// console.log(">> api bg dialog res<<",res)
					if(res && res.message && res.message.length > 0 ){
						generate_colors_html(res.message,bg_type)
					}
					else{
						frappe.msgprint(`There is no <b>${bg_type}</b> records found..!`)
					}
				}
			})
		}

		function generate_colors_html(gradiant_data,bg_type){
			var bg_dialog = new frappe.ui.Dialog({
				title:"Select Background",
				fields:[
				{
					fieldname:"bg_colors_html",
					fieldtype:"HTML"
				}
				]
			})
			bg_dialog.show();
			bg_dialog.$wrapper.addClass("in")
			var bg_wrapper = bg_dialog.fields_dict.bg_colors_html.$wrapper
			$(bg_dialog.$wrapper).find(".modal-dialog").css({"min-width":"70%"})
			let p_html =`<div class="bg-main-div" bg_type="${bg_type}" id="${cur_frm.r___id}">
						<div class="bg-sub-div" style="display:flex;flex-wrap:wrap;gap:20px;">
	
						</div>
					</div>`
			$(bg_wrapper).html(p_html)

			gradiant_data.map(each_gradiant =>{
				// console.log(">> file type <<",typeof(each_gradiant.css_properties))
				// console.log(">> file <<",each_gradiant.css_properties)
				let temp_html;
				if(each_gradiant.css_properties && !each_gradiant.css_properties.startsWith('data')){
				temp_html=$(`<div class="each-bg-div" value="${each_gradiant.css_properties}" bg_type="${bg_type}" style="flex: 0 0 calc(20% - 20px);cursor:pointer;">
							<div class="bg-gradiant-color" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="background:${each_gradiant.css_properties};height:70px;border-radius:7px;"></div>
							<div class="bg-title" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="text-align:center;padding-top:5px;font-weight:600;">${each_gradiant.title}</div>
						</div>`)
					}
				else if(each_gradiant.css_properties && each_gradiant.css_properties.startsWith('data')) {
					temp_html=$(`<div class="each-bg-div" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="flex: 0 0 calc(20% - 20px);cursor:pointer;">
					<div class="bg-gradiant-color" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="height:70px;border-radius:7px;">
					<img bg_type="${bg_type}" value="${each_gradiant.css_properties}" src=${"'"+each_gradiant.css_properties.replace(' ','%20')+"'"}>
					</div>
					<div bg_type="${bg_type}" class="bg-title" value="${each_gradiant.css_properties}" style="text-align:center;padding-top:5px;font-weight:600;">${each_gradiant.title}</div>
				</div>`)
				}
				if(temp_html){
					temp_html.click((e) =>{
						// console.log(`>> ${$(e.target).attr("bg_type")} color value<<`,$(e.target).attr("value"))
						if($(e.target).attr("bg_type") == 'Gradient'){
							popup_variable_color_codes["bg-gradient-color"] = $(e.target).attr("value")
							elementstyledialog.$wrapper.find('[data-fieldname="bg-gradient-color"] .gradient_modify_sec .btn-previw-section .gradient-color').css({"background":`${$(e.target).attr("value").split(";")[0]}`})
							bg_dialog.hide();
						}
						else if($(e.target).attr("bg_type") == 'Pattern'){
							popup_variable_color_codes["bg-pattern-color"] = $(e.target).attr("value")
							elementstyledialog.$wrapper.find('[data-fieldname="bg-pattern-color"] .pattern_modify_sec .btn-previw-section .pattern-color').css({"background":`${$(e.target).attr("value")}`})
							bg_dialog.hide();
						}
						else if($(e.target).attr("bg_type") == 'Mask'){
							popup_variable_color_codes["bg-mask-color"] = $(e.target).attr("value")
							elementstyledialog.$wrapper.find('[data-fieldname="bg-mask-color"] .mask_modify_sec .btn-previw-section .mask-color').css({"background":`${$(e.target).attr("value")}`})
							bg_dialog.hide();
						}
					})
					$(bg_wrapper).find(`#${cur_frm.r___id}[bg_type="${bg_type}"].bg-main-div .bg-sub-div`).append(temp_html)
				}
			})	
		}
	}
	else {
		frappe.msgprint("There is no styles available to edit...!")
	}

}

// end
