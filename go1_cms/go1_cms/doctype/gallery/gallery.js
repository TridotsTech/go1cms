// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gallery', {
	refresh(frm){
		$(`[data-route="Form/Gallery/${cur_frm.doc.name}"]`).find('[data-fieldname="gallery"]').find('.btn.btn-xs.btn-secondary.grid-add-row').css({"display":"none"})
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
	attach_files(frm) {
		let uploader = new frappe.ui.FileUploader({
			as_dataurl: true,
			allow_multiple: true,
			on_success(file) {

				// let data_file_name=""
				// // console.log(file,"file")
				// let image__video = []
				// let is_cover_image = []
				// cur_frm.doc.gallery.map((res,idxx) => {
				// 	image__video.push(res.image__video)
				// 	is_cover_image.push(res.is_cover_image)
				// })
				// if(file.dataurl){
				// 	data_file_name = file.name
				// 	console.log(data_file_name,"data_file_name")
				// 	// console.log("file_names",file_name)
				// 	// console.log("file.name",file.name)
				// 	console.log(file,"file")
				// 	console.log(file.name,"file.name")
				// 	if(image__video.includes(file.name)){
				// 		frappe.show_alert({
				// 			message:__(`The file <b>${file.name}</b> is already exists..!`),
				// 			indicator:'red'
				// 		}, 5);
				// 		// console.log(uploader.dialog.$wrapper)
				// 		// uploader.dialog.$wrapper.hide()
				// 		return
				// 	}
				// }
				// else{
				// 	data_file_name = file.image__video
				// 	if(image__video.includes(file.image__video)){
				// 		frappe.show_alert({
				// 			message:__(`The file <b>${file.file_name}</b> is already exists..!`),
				// 			indicator:'red'
				// 		}, 5);
				// 		return
				// 	}
				// 	// if(api_file_names.includes(file.file_name)){
				// 	// 	frappe.show_alert({
				// 	// 		message:__(`The file <b>${file.file_name}</b> is already exists..!`),
				// 	// 		indicator:'red'
				// 	// 	}, 5);
				// 	// 	return
				// 	// }
				// }

				frappe.show_alert({
					message:__(`Please wait your file <b>${file.file_name ? file.file_name :file.name}</b> being uploaded..!`),
					indicator:'green'
				}, 2);
				// console.log("file",file.file_name)
				let xhr = new XMLHttpRequest();
				xhr.upload.addEventListener('loadstart', (e) => {
					file.uploading = true;
				})
				xhr.upload.addEventListener('progress', (e) => {
					if (e.lengthComputable) {
						file.progress = e.loaded;
						file.total = e.total;
					}
				})
				xhr.upload.addEventListener('load', (e) => {
					file.uploading = false;
					// resolve();
				})
				xhr.addEventListener('error', (e) => {
					file.failed = true;
					// reject();
				})
				xhr.onreadystatechange = () => {
					if (xhr.readyState == XMLHttpRequest.DONE) {
						if (xhr.status === 200) {
							let r = null;
							let file_doc = null;
							try {
								r = JSON.parse(xhr.responseText);
								if (r.message.doctype === 'File') {
									file_doc = r.message;
								}
							} catch (e) {
								r = xhr.responseText;
							}
							console.log(file_doc,"file_doc")
							file.doc = file_doc;

							if (this.on_success) {
								// console.log("file.doc",file.doc)
								// For adding uploaded url to child doctype doctype
								let all_urls = []
									cur_frm.doc.gallery.map((res,idxx) => {
										all_urls.push(res.link)
									})
									if((!all_urls.includes(file_doc.file_url)) && file_doc.file_url){
										console.log(file_doc.file_url,"file_doc.file_url")
										let chid_doc = frappe.model.add_child(frm.doc, "Gallery Files", "gallery");
										chid_doc.image__video = file_doc.file_url
										refresh_field("gallery")
										frappe.show_alert({
											message:__(`The file <b>${file_doc.file_name}</b> upload complete..!`),
											indicator:'green'
										}, 5);
										// end
									}
									else if(all_urls.includes(file_doc.file_url) || (!file_doc.file_url)){
										if(all_urls.includes(file_doc.file_url)){
											frappe.show_alert({
												message:__(`The file <b>${file_doc.file_name}</b> is already exists..!`),
												indicator:'red'
											}, 5);
										}
										else if(!file_doc.file_url){
											frappe.show_alert({
												message: __("Some files url not found, please check and reupload your file...!"),
												indicator: 'red'
											}, 5);
										}
										else{
											frappe.show_alert({
												message: __("Something went wrong, please check your files correctly uploaded...!"),
												indicator: 'red'
											}, 5);
										}
									}
							$(`[data-route="Form/Gallery/${cur_frm.doc.name}"]`).find('[data-fieldname="gallery"]').find('.btn.btn-xs.btn-secondary.grid-add-row').css({"display":"none"})
							}
						} else if (xhr.status === 403) {
							let response = JSON.parse(xhr.responseText);
							frappe.msgprint({
								title: __('Not permitted'),
								indicator: 'red',
								message: response._error_message
							});
						} else {
							file.failed = true;
							let error = null;
							try {
								error = JSON.parse(xhr.responseText);
							} catch (e) {
								// pass
							}
							frappe.request.cleanup({}, error);
						}
					}
				}
				xhr.open('POST', '/api/method/upload_file', true);
				xhr.setRequestHeader('Accept', 'application/json');
				xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);

				let form_data = new FormData();

				if (file.file_obj) {
					form_data.append('file', file.file_obj, file.name);
				}
				form_data.append('is_private', +file.private);
				form_data.append('folder', this.folder);

				if (file.file_url) {
					form_data.append('file_url', file.file_url);
				}

				if (file.file_name) {
					form_data.append('file_name', file.file_name);
				}

				if (cur_frm.doctype && cur_frm.docname) {
					form_data.append('doctype', cur_frm.doctype);
					form_data.append('docname', cur_frm.docname);
				}

				if (cur_frm.fieldname) {
					form_data.append('fieldname', cur_frm.fieldname);
				}

				if (this.method) {
					form_data.append('method', this.method);
				}
				xhr.send(form_data);
			}
		});
	},
});
