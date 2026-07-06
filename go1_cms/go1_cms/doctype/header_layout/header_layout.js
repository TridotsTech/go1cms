// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Header Layout', {
	refresh: function(frm) {
		frm.r___id = Math.floor(Math.random() * 100)
		frm.trigger("render_image_preview") 
	},
	render_image_preview(frm){
		frm.image_pre_wrapper = frm.get_field("preview_html").$wrapper
		$(frm.image_pre_wrapper).empty()
		if(frm.doc.preview){
			let html = `<div class="img-previw-tag id="${frm.r___id}">
							<div class="img-subcontainer">
								<div class="preview-img"></div>
							</div>
						<style>
						.preview-img{
									width: 170px;
									height: 54px;
									background-image: url('${frm.doc.preview.replace(" ",'%20')}');
									background-size: contain;
									background-repeat: no-repeat;
									padding: 5px;
									background-position: center;
									}
						</style>
						</div>`
			frm.image_pre_wrapper.html(html)
			refresh_field("preview_html")
		}
	}
});
