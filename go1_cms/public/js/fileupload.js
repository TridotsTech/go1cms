function upload_files(random, link_doctype, link_name, parentfield, image_doctype, child_docname) {
	console.log("---------upload_files--------")
	$.getScript('https://transloadit.edgly.net/releases/uppy/v1.18.0/uppy.min.js', function () {
		var uppy = Uppy.Core({
				restrictions:{
					maxFileSize: 1500000,
					allowedFileTypes:['.jpg','.png','.jpeg','.gif']
				}
			})
			.use(Uppy.Dashboard, {
				inline: true,
				target: '#drag-drop-area' + random,
				disablePageScrollWhenModalOpen: true,
				disableInformer: false,
				height: 450,
				hideRetryButton: false,
				animateOpenClose: true,
				closeModalOnClickOutside: false,
				replaceTargetContent:false,
				showProgressDetails:true,
				hideProgressAfterFinish:true,
				disableStatusBar:false,
				theme:"light",
				proudlyDisplayPoweredByUppy:false,
				fileManagerSelectionType: 'files',
				note: 'Images only, up to 1 MB',
				locale:{
					strings:{
						dropPaste: 'Drop files here or %{browse}',
						youCanOnlyUploadFileTypes: 'You can only upload: %{types}',
						exceedsSize: '%{file} exceeds maximum allowed size of %{size}',
					}					
				},
				 metaFields: [
	            { id: 'name', name: 'Name', placeholder: 'File Name' }
	          ]				
			})
	   
		uppy.use(Uppy.ImageEditor, {
		  target: Uppy.Dashboard,
		  quality: 0.8,
		  cropperOptions: {
		    viewMode: 1,
		    background: false,
		    autoCropArea: 1,
		    responsive: true,
		    croppedCanvasOptions: {},
		  },
		  actions: {
		    revert: true,
		    rotate: true,
		    granularRotate: true,
		    flip: true,
		    zoomIn: true,
		    zoomOut: true,
		    cropSquare: true,
		    cropWidescreen: true,
		    cropWidescreenVertical: true,
		  },
		})
		
		var filelists = [];
		uppy.on('upload', (data) => {
			$("<h4 class='msg'>Uploading. Please wait.......</h4>").appendTo(".uppy-Informer");
			$('.uppy-Dashboard-progressindicators').find('.uppy-Informer p').css("display", "none");

			let files_count=uppy.getFiles().length;
			let count=0;
			let all_files=uppy.getFiles();
			$.each(all_files, function (i, check_deleted) {
					$('.uppy-Dashboard-progressindicators').find('.uppy-Informer p').css("display", "none");
		
					var reader = new FileReader();
					
					let date = new Date();
					let datetime = date.toLocaleString().replace(/ /g, '');
					let cur_time = datetime.replace(/\//g, '-');
					let filename = check_deleted.name.split('.' + check_deleted.extension)[0] + '-' + cur_time + '.' + check_deleted.extension;
	
					reader.readAsDataURL(check_deleted.data);
					reader.onload = function (e) {
						
						$('.uppy-Dashboard-progressindicators').find('.uppy-Informer p').css("display", "none");
						var upload_doc = localStorage.getItem("upload_tab");
						var upload_name = localStorage.getItem("upload_doc");
						frappe.call({
							method: 'uploadfile',
							args: {
								from_form: 1,
								doctype: link_doctype,
								docname: link_name,
								is_private: 0,
								filename: filename,
								file_url: '',
								
								file_size: check_deleted.size,
								filedata: e.target.result,
								upload_doc: upload_doc
							},
							async: false,
							callback: function (r) {
								console.log("-----------r",r)
								count = count + 1;
								$('.uppy-Dashboard-progressindicators').find('.uppy-Informer p').css("display", "none");
								if(child_docname)
									update_attribute_image(r.message.name, image_doctype, child_docname, count, files_count)
								else
									update_image(r, check_deleted, upload_doc, files_count, count, parentfield, image_doctype)
							}
						})
					};
					uppy.reset();
			});
		})
		uppy.upload().then((result) => {
		  console.info('Successful uploads:', result.successful)
		  if (result.failed.length > 0) {
		    result.failed.forEach((file) => {
		    })
		  }
		})
		uppy.on('file-added', (file) => {			
			$('.uppy-DashboardContent-addMore').css('display','none');
			if(file.extension=="webp" || file.extension=="svg"){
				uppy.removeFile(file.id);
				alert("Allowed Types are jpg,png,jpeg and gif")
			}
			
		})
		uppy.on('restriction-failed', (file, error) => {
			console.log("----------------1")
		});
		uppy.on('upload-error', function (file, error) {
            console.log(error);
            console.log("---------2-------1")
        });
		$(document).ready(function () {
			$('.uppy-DashboardAddFiles-info').find('.uppy-Dashboard-poweredBy').css("display", "none");
			$('.uppy-Dashboard-progressindicators').find('.uppy-StatusBar-actions button').attr("id", "uploadbtn");
			$('.uppy-Dashboard-progressindicators').find('.uppy-Informer p').css("display", "none");
			$('.uppy-DashboardAddFiles').on('drop',function(e){
				$("input[type=file]").prop("files", e.originalEvent.dataTransfer.files);
				$("input[type=file]").trigger('change')
				$('.uppy-DashboardContent-addMore').css('display','none');
			})
			$('.uppy-DashboardContent-addMore').css('display','none');
		});
		$('input[type=file]').change(function () {
			filelists.push($(this))
			var input = $(this);
		});
	})
}
function isFile(input) {
   if ('File' in window && input instanceof File)
      return true;
   else return false;
}

function isBlob(input) {
    if ('Blob' in window && input instanceof Blob)
        return true;
    else return false;
}
function update_image(r, check_deleted, upload_doc, files_count, count, parentfield, image_doctype){
	
	frappe.call({
		method: 'go1_commerce.go1_commerce.v2.product.update_to_file',
		args: {
			file_name: r.message.file_name,
			upload_doc: upload_doc,
			docname: cur_frm.docname,
			file_type: check_deleted.type,
			file_path: r.message.file_url,
			name: r.message.name,
			total_files: files_count,
			current_file: count,
			doctype: cur_frm.doctype,
			parentfield: parentfield,
			image_doctype: image_doctype
		},
		async: false,
		callback: function (f) {
			cur_frm.isloaded = 1;
			$(".menu-btn-group .dropdown-menu li a").each(function () {
				if ($(this).text() == "Reload") {
					$(this).click();
				}
			});										
			frappe.show_alert(__("Image Added!"));
			if(count == files_count){
				cur_dialog.hide();
				cur_frm.reload_doc();
			}
		}
	});
}

function update_attribute_image(filename, doctype, docname, count, files_count){
	frappe.call({
		method: 'go1_commerce.go1_commerce.v2.product.update_attribute_images',
		args:{
			name: filename,
			dt: doctype,
			dn: docname
		},
		async: false,
		callback: function(r){
			if(r.message){
				frappe.model.set_value(doctype,docname, "image_list",JSON.stringify(r.message));
			}
			frappe.show_alert(__("Image Added!"));
			if(count == files_count){
				cur_dialog.hide();
				EditAttributeOption(docname, doctype);
			}			
		}
	})
}
