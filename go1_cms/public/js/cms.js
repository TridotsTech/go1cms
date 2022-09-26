var section_groups; 

function filter_section(id){
    $(".group-link").parent().removeClass("active");
    if(id!='All'){
        $("#sec-right-content .col-md-4.col-sm-6.col-xs-6").hide();
        $(".col-md-4.col-sm-6.col-xs-6[data-group='"+section_groups[id]["group_name"]+"']").show();
    }
    else{
         $("#sec-right-content .col-md-4.col-sm-6.col-xs-6").show();
      }
     $("#dtgroup"+id).parent().addClass("active");
    }

// by gopi on 10/9/22 for layout sections
function filter_layout_section(e){
    // console.log(">> Layout working <<",e)
    $(".group-link").parent().removeClass("active");
    $("#sec-right-content .col-md-4.col-sm-6.col-xs-6").hide();
    $(".col-md-4.col-sm-6.col-xs-6[data-group='layout-section']").show();
    $("#dtgroup-layout").parent().addClass("active");
}
// end 10/9/22
function show_element_style(id){
   frappe.call({
                method: 'go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_element_properties',
                args: {"id":id},
                async: false,
                callback: function(r) {
                    if(r.message.css_properties_list){
                        data = r.message.css_properties_list
                        json_data = {}
                        var fonts_data = []
                        if(r.message.fonts_list){
                            for (var i = 0; i < r.message.fonts_list.length; i++) {
                                fonts_data.push(r.message.fonts_list[i].name)

                            }
                        }
                        if(r.message.css_json!=null && r.message.css_json!=undefined){
                            json_data = JSON.parse(r.message.css_json)
                        }
                        var filelist=JSON.parse(data)
                        var fields=[];
                        var child_sections = [];
                        var units_sections = [];
                        var units_sections_field_with_units = [];
                        var fonts_media_query_data={}
                        var enable_font_media_query=false
                        // gradient and mask and pattern value store variable and divider
		                var gra_patt_mask = {}
                        // end
                        for (var i = 0; i < filelist.length; i++) {
                            if(filelist[i].child_properties){
                                 var is_collapse = 0;
                                if (filelist[i].collapse){
                                     if (filelist[i].collapse==1){
                                         is_collapse = 1
                                     }
                                }
                                var child_properties = filelist[i].child_properties;
                                fields.push({ 'fieldtype': 'Section Break', 'fieldname': 'sb_childs', 'label': filelist[i].label, 'collapsible':is_collapse })
                                for (var k = 0; k < child_properties.length; k++) {
                                    if(k==0){
                                        child_sections.push(child_properties[k].fieldname)
                                    }
                                     for (const [key, value] of Object.entries(json_data)) {
                                        if (key==child_properties[k].fieldname){
                                             // Modify by gopi on 17/9/22
                                             if (!child_properties[k].allow_media_query && key != "font-size" && value && (value.toString().endsWith("-px") || value.toString().endsWith("-%") || value.toString().endsWith("-em") || value.toString().endsWith("-rem"))) {
                                                child_properties[k].default = value.split("-")[0]
                
                                                if (child_properties[k].allow_units) {
                                                    if (child_properties[k].allow_units == 1) {
                                                        units_sections_field_with_units.push({ "field_name": child_properties[k].fieldname, "unit": value.split("-")[1] })
                                                    }
                                                }
                
                                            }

                                            else if((key == child_properties[k].fieldname && key == "bg-gradient-color") || (key == child_properties[k].fieldname && key == "bg-pattern-color") || (key == child_properties[k].fieldname && key == "bg-mask-color") || (key == child_properties[k].fieldname && key == "divider-color") || (key == child_properties[k].fieldname && key == "bg-divider-img")){
                                                if(child_properties[k].fieldname == "bg-gradient-color"){
                                                    // console.log(">> gradiant value <<",value)
                                                    gra_patt_mask["bg-gradient-color"] = value
                                                }
                                                else if(child_properties[k].fieldname == "bg-pattern-color"){
                                                    gra_patt_mask["bg-pattern-color"] = value
                                                }
                                                else if(child_properties[k].fieldname == "bg-mask-color"){
                                                    gra_patt_mask["bg-mask-color"] = value
                                                }
                                                else if(child_properties[k].fieldname == "divider-color"){
                                                    gra_patt_mask["divider-color"] = value
                                                    child_properties[k].default=value
                                                }
                                                else if(child_properties[k].fieldname == "bg-divider-img"){
                                                    gra_patt_mask["bg-divider-img"] = value
                                                    child_properties[k].default=value
                                                }
                                            }

                                            else if(value && key == "font-size" && child_properties[k].allow_media_query){
                                                enable_font_media_query = true
                                                if(typeof(value) === 'object'){
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
                                                else{
                                                    if((value.toString().endsWith("-px") || value.toString().endsWith("-%") || value.toString().endsWith("-em") || value.toString().endsWith("-rem"))){
                                                        fonts_media_query_data['pc-font-size'] = value
                                                        child_properties[k].default = value.split("-")[0]
                                                        if (child_properties[k].allow_units) {
                                                            if (child_properties[k].allow_units == 1) {
                                                                units_sections_field_with_units.push({ "field_name": child_properties[k].fieldname, "unit": value.split("-")[1] })
                                                            }
                                                        }
                                                    }
                                                    else{
                                                        child_properties[k].default = value
                                                        fonts_media_query_data['pc-font-size'] = value+'-px'
                                                    }		   
                                            }
                                            }


                                            else{
                                                child_properties[k].default=value
                                            }

                                            // end
                                        }
                                    }
                                     if(child_properties[k].fieldname!='font-family'){
                                         fields.push(child_properties[k])
                                         if(child_properties[k].fieldname == "font-size" && child_properties[k].allow_media_query){
                                            enable_font_media_query = true
                                        }

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
                                         // Modify by gopi on 17/9/22

                                         if(!filelist[i].allow_media_query && key != "font-size" && value && (value.toString().endsWith("-px") || value.toString().endsWith("-%") || value.toString().endsWith("-em") || value.toString().endsWith("-rem"))){
                                            filelist[i].default = value.split("-")[0]
                
                                            if (filelist[i].allow_units) {
                                                if (filelist[i].allow_units == 1) {
                                                    units_sections_field_with_units.push({"field_name":filelist[i].fieldname,"unit":value.split("-")[1]})
                                                }
                                            }
                
                                        }

                                         else if((key == filelist[i].fieldname && key == "bg-gradient-color") || (key == filelist[i].fieldname && key == "bg-pattern-color") || (key == filelist[i].fieldname && key == "bg-mask-color") || (key == filelist[i].fieldname && key == "divider-color") || (key == filelist[i].fieldname && key == "bg-divider-img")){
                                            if(filelist[i].fieldname == "bg-gradient-color"){
                                                // console.log(">> gradiant value <<",value)
                                                gra_patt_mask["bg-gradient-color"] = value
                                            }
                                            else if(filelist[i].fieldname == "bg-pattern-color"){
                                                gra_patt_mask["bg-pattern-color"] = value
                                            }
                                            else if(filelist[i].fieldname == "bg-mask-color"){
                                                gra_patt_mask["bg-mask-color"] = value
                                            }
                                            else if(filelist[i].fieldname == "bg-divider-img"){
                                                gra_patt_mask["bg-divider-img"] = value
                                            }
                                            else if(filelist[i].fieldname == "divider-color"){
                                                gra_patt_mask["divider-color"] = value
                                                filelist[i].default=value
                                            }
                                        }

                                        else if(value && key == "font-size" && filelist[i].allow_media_query){
                                            enable_font_media_query = true
                                            if(typeof(value) === 'object'){
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
                                                if((value.toString().endsWith("-px") || value.toString().endsWith("-%") || value.toString().endsWith("-em") || value.toString().endsWith("-rem"))){
                                                    filelist[i].default = value.split("-")[0]
                                                    fonts_media_query_data['pc-font-size'] = value
                                                    if (filelist[i].allow_units) {
                                                        if (filelist[i].allow_units == 1) {
                                                            units_sections_field_with_units.push({"field_name":filelist[i].fieldname,"unit":value.split("-")[1]})
                                                        }
                                                    }
                                                }
                                                else{
                                                    filelist[i].default=value
                                                    fonts_media_query_data['pc-font-size'] = value+'-px'
                                                }

                                            }
                                        }

                                        else{
                                            filelist[i].default=value
                                        }

                                        // end
                                    }
                                }
                                 if(filelist[i].fieldname!='font-family'){
                                         fields.push(filelist[i]);
                                         if(filelist[i].fieldname == "font-size" && filelist[i].allow_media_query){
                                            enable_font_media_query = true
                                        }

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
                       var elementstyledialog = new frappe.ui.Dialog({
                            title: "Edit Style",
                            fields: fields
                        });
                       elementstyledialog.show();

                        // Modify by gopi on 17/9/22 for background properties like mask and pattern and gradiend

                        var popup_variable_color_codes ={}
                        var dividers_values = []
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

                       let divider_html = `<div class="divider_modify_sec">
                                               <div class="btn-title-divider">
                                                   Divider Style
                                               </div>
                                               <div class="btn-previw-section" style="width:50%;">
                                                   <div class="divider-color" style="${gra_patt_mask['bg-divider-img']?"-webkit-mask:url('"+gra_patt_mask["bg-divider-img"]+"')no-repeat center / contain;":''}${gra_patt_mask["divider-color"]?'background:'+gra_patt_mask["divider-color"]+';':'#7a5b5b;'}float:left;margin-right: 10px;width:80px;height:28px;border-radius:7px;margin-top:10px;"></div>
                                               </div>         
                                               </div>`
                       $(divider_html).insertBefore(elementstyledialog.$wrapper.find('[data-fieldname="bg-divider-img"] button'))

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
                       
                       elementstyledialog.$wrapper.find('[data-fieldname="bg-divider-img"] button').on("click",(e) =>{
                           // console.log(">> mask color working <<")
                           poup_bg_dialog('Divider')
                       })

                       // end gopi 17/9/22


                       elementstyledialog.$wrapper.find(".modal-dialog").attr("id",id);
                       elementstyledialog.set_primary_action(__('Save'), function() {
                           let values = elementstyledialog.get_values();
                           let style_json = {}
                           let css_design = "."+r.message.class_name+" ."+r.message.field_key+"{"
                           let font_size_css_design=""

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

                                if(k=="background_options"){
                                    style_json[k]=values[k]
                                }

                                if(values[k]!="" && values[k]!="0px" && k!="background_options" && k!="bg-divider-img"){

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


                                    if(k=="background-image"){
                                        css_design += k+":url('"+values[k]+"') !important;";
                                    }

                                     // modify by gopi for dividers 19/9/22

                                     else if(k=="background"){
                                        css_design += k+":url('"+values[k]+"') !important;";
                                    }
                                    else if(k=="divider-position"){
                                        if(values[k] == 'Top'){
                                            divider_css_design +='position:absolute;'
                                            divider_css_design +='top:0px !important;'
                                        }
                                        else if(values[k] == 'Bottom'){
                                            divider_css_design +='position:absolute;'
                                            divider_css_design +='bottom:0px !important;'
                                            divider_css_design +='transform: rotate(180deg) !important;'
                                        }
                                    }
                                    else if(k=="divider-color"){
                                        divider_css_design += "background:"+values[k]+" !important;";
                                    }

                                    else if(k=="divider-width"){

                                        var is_allow_units = 0;
                                        if(elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").attr("allow-units")){
                                             if(elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").attr("allow-units")=="1"){
                                                 is_allow_units = 1;
                                             }
                                        }
                                        var units = '';
                                        if(is_allow_units==1){
                                            units = elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").parent().find('select.unit').val();
                                        }
                                        divider_css_design += "width:"+values[k]+units+" !important;";
                                    }

                                    else if(k=="divider-height"){

                                        var is_allow_units = 0;
                                        if(elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").attr("allow-units")){
                                             if(elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").attr("allow-units")=="1"){
                                                 is_allow_units = 1;
                                             }
                                        }
                                        var units = '';
                                        if(is_allow_units==1){
                                            units = elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").parent().find('select.unit').val();
                                        }
                                        divider_css_design += "height:"+values[k]+units+" !important;";
                                    }

                                    else if(k=="divider-flip"){
                                        if(values[k]){
                                            if(values[k] == "Yes"){
                                                divider_css_design += "transform: rotateY(180deg) !important;";
                                            }
                                        }
                                    }

                                    // end by goppi 19/9/22

                                     else if(k=="font-family"){
                                        let font_famil_name = r.message.fonts_list.find(o => o.name === values[k]);
                                        if(font_famil_name){
                                            css_design += k+":"+font_famil_name.font_family+" !important;";
                                        }
                                    }
                                    else{
                                        if(k != "font-size"){
                                            var is_allow_units = 0;
                                            if(elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").attr("allow-units")){
                                                if(elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").attr("allow-units")=="1"){
                                                    is_allow_units = 1;
                                                }
                                            }
                                            var units = '';
                                            if(is_allow_units==1){
                                                units = elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+k+"']").parent().find('select.unit').val();
                                            }
                                            css_design += k+":"+values[k]+units+" !important;";
                                        }
                                    }
                                }

                                if (k == "font-size" && enable_font_media_query) {
                                    Object.keys(fonts_media_query_data).map(e_res => {
                                        if (e_res == "pc-font-size") {
                                            font_size_css_design += `@media (min-width: 992px){.${r.message.class_name} .${r.message.field_key}{font-size:${fonts_media_query_data[e_res].split('-').join('')+" !important;"}}}`
                                        }
                                        else if (e_res == "mbl-font-size") {
                                            font_size_css_design += `@media (max-width: 767px){.${r.message.class_name} .${r.message.field_key}{font-size:${fonts_media_query_data[e_res].split('-').join('')+" !important;"}}}`
                                        }
                                        else if (e_res == "tab-font-size") {
                                            font_size_css_design += `@media (max-width: 992px){.${r.message.class_name} .${r.message.field_key}{font-size:${fonts_media_query_data[e_res].split('-').join('')+" !important;"}}}`
                                        }
                                    })
                                }
                            }

                            // Modify by gopi on 17/9/22 for background properties like mask and pattern and gradiend and dividers

                            if(popup_variable_color_codes.hasOwnProperty('bg-gradient-color')){
                                popup_variable_color_codes['bg-gradient-color']?(style_json['bg-gradient-color']=popup_variable_color_codes['bg-gradient-color']):""
                                popup_variable_color_codes['bg-gradient-color']?css_design +='background:'+popup_variable_color_codes["bg-gradient-color"].split(";")[0]+' !important;':''
                            }
                            else if(gra_patt_mask.hasOwnProperty('bg-gradient-color')){
                                gra_patt_mask['bg-gradient-color']?(style_json['bg-gradient-color']=gra_patt_mask['bg-gradient-color']):""
                                gra_patt_mask['bg-gradient-color']?css_design +='background:'+gra_patt_mask["bg-gradient-color"].split(";")[0]+' !important;':''
                            }
                
                            if(popup_variable_color_codes.hasOwnProperty('bg-pattern-color')){
                                popup_variable_color_codes['bg-pattern-color']?(style_json['bg-pattern-color']=popup_variable_color_codes['bg-pattern-color']):""
                                popup_variable_color_codes['bg-pattern-color']?css_design +='background-image:url("'+popup_variable_color_codes["bg-pattern-color"]+'") !important;':''
                            }
                            else if(gra_patt_mask.hasOwnProperty('bg-pattern-color')){
                                gra_patt_mask['bg-pattern-color']?(style_json['bg-pattern-color']=gra_patt_mask['bg-pattern-color']):""
                                gra_patt_mask['bg-pattern-color']?css_design +='background-image:url("'+gra_patt_mask["bg-pattern-color"]+'") !important;':''
                            }
                
                            if(popup_variable_color_codes.hasOwnProperty('bg-mask-color')){
                                popup_variable_color_codes['bg-mask-color']?(style_json['bg-mask-color']=popup_variable_color_codes['bg-mask-color']):""
                                popup_variable_color_codes['bg-mask-color']?css_design +='background-image:url("'+popup_variable_color_codes["bg-mask-color"]+'") !important;':''
                            }
                            else if(gra_patt_mask.hasOwnProperty('bg-mask-color')){
                                gra_patt_mask['bg-mask-color']?(style_json['bg-mask-color']=gra_patt_mask['bg-mask-color']):""
                                gra_patt_mask['bg-mask-color']?css_design +='background-image:url("'+gra_patt_mask["bg-mask-color"]+'") !important;':''
                            }

                            if(popup_variable_color_codes.hasOwnProperty('bg-divider-img')){
                                popup_variable_color_codes['bg-divider-img']?(style_json['bg-divider-img']=popup_variable_color_codes['bg-divider-img']):""
                                popup_variable_color_codes['bg-divider-img']?divider_css_design +='-webkit-mask:url("'+popup_variable_color_codes["bg-divider-img"]+'")no-repeat center / contain;':''
                            }
                            else if(gra_patt_mask.hasOwnProperty('bg-divider-img')){
                                gra_patt_mask['bg-divider-img']?(style_json['bg-divider-img']=gra_patt_mask['bg-divider-img']):""
                                gra_patt_mask['bg-divider-img']?divider_css_design +='-webkit-mask:url("'+gra_patt_mask["bg-divider-img"]+'")no-repeat center / contain;':''
                            }

                             // end gopi 17/9/22

                            css_design +="}";
                            if(font_size_css_design){
                                css_design += font_size_css_design
                             }
                            $('[data-fieldname="'+id+'"]').attr("css_design",css_design)
                            $('[data-fieldname="'+id+'"]').attr("style_json",JSON.stringify(style_json))
                            elementstyledialog.hide();
                            setTimeout(function(){ $(".modal-dialog[id='"+id+"']").parent().remove()},1000);
                        });
                        for (var i = 0; i < child_sections.length; i++) {
                           // if(i!=child_sections.length-1){
                           elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().attr("style","margin-bottom:10px;border-top:none !important;margin-top: -20px;width: calc(100% + 40px);margin-left: -20px;padding-left: 20px;padding-right: 20px;margin-bottom: 0;position: relative;m");//modfied by boopathy
                           // elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom:0px");
                           elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom: 20px;margin-top: 0;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;");
                           elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-body").attr("style","margin-top:60px");

                           // }
                           // elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find("h6.form-section-heading.uppercase").attr("style","font-weight: 400;color: #222 !important;text-transform: capitalize;font-size: 14px;");
                           // elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom:0px");
                           // if(i==0){
                           //     elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom:0px;margin-top:15px;");
                           // }
                          if(i==0){
                              elementstyledialog.$wrapper.find(".frappe-control[data-fieldname='"+child_sections[i]+"']").parent().parent().parent().parent().find(".section-head").attr("style","font-weight: 600;margin-bottom: 20px;margin-top: 4px;margin-left: -20px;width: 100%;max-width: calc(100% + 40px);position: absolute;padding-left: 20px;padding-top: 10px;border-bottom: 1px solid var(--border-color);border-top: 1px solid var(--border-color);font-size:14px;");
                          }
                           
                       }
                        for (var i = 0; i < units_sections.length; i++) {
                            elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").attr("style"," box-shadow: none;flex: 0 0 60%;  border-top-right-radius: 0; border-bottom-right-radius: 0; border-right: 1px solid #ddd;");
                            elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").attr("type","number");
                            elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").attr("allow-units","1");
                            elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").parent().attr("style","display: flex;position: relative;max-width: 140px;");
                            var select_html = '<select class="form-control unit" name="unit" style="flex:0 0 40%;box-shadow: none;border-top-left-radius: 0;border-bottom-left-radius: 0;"> <option value="px">px</option><option value="em">em</option><option value="%">%</option>    <option value="rem">rem</option> </select>';
                            select_html+='<div class="select-icon " style="padding-left: inherit;padding-right: inherit;position: absolute;pointer-events: none;top: 7px;right: 6px;"><svg class="icon  icon-sm" style=""><use class="" href="#icon-select"></use></svg></div>';
                            elementstyledialog.$wrapper.find(".form-control[data-fieldname='"+units_sections[i]+"']").parent().append(select_html);
                            elementstyledialog.$wrapper.find(".form-control[data-fieldname='" + units_sections[i] + "']").parent().find("select").val((units_sections_field_with_units[i] && units_sections_field_with_units[i].unit)? units_sections_field_with_units[i].unit:"px")
                       }
                       elementstyledialog.$wrapper.find('.modal-dialog').css("max-width","700px");
                       


                       if(enable_font_media_query){
                        elementstyledialog.$wrapper.find('[data-fieldname="font-size"] label').parent().css({ "display": "flex", "gap": "10px", "align-items": "center" })
                        elementstyledialog.$wrapper.find('[data-fieldname="font-size"] label').parent().css({ "display": "flex", "gap": "10px", "align-items": "center" })
                        elementstyledialog.$wrapper.find('[data-fieldname="font-size"] label').parent().append(`<i id="mbl-font-icon" style="font-size:20px;cursor:pointer;padding-bottom:3px;" class="fa fa-mobile" aria-hidden="true"></i>
                     <i id="tab-font-icon" style="font-size:15px;cursor:pointer;" class="fa fa-tablet" aria-hidden="true"></i>
                     <i id="pc-font-icon" style="font-size:15px;cursor:pointer;font-weight: 700;color: #0101ff;" class="fa fa-desktop" aria-hidden="true"></i>`)
                        elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').attr("input_value", "Web")
                        elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #mbl-font-icon').on("click", () => {
                            // console.log(">>mbl working<<")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').attr("input_value", "Mobile")
                            if (fonts_media_query_data['mbl-font-size']) {
                                elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val(fonts_media_query_data['mbl-font-size'].split('-')[0])
                                elementstyledialog.$wrapper.find(".form-control[data-fieldname='font-size']").parent().find("select").val(fonts_media_query_data['mbl-font-size'].split('-')[1] ? fonts_media_query_data['mbl-font-size'].split('-')[1] : "px")
                            }
                            else {
                                elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val('')
                            }
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #mbl-font-icon').attr("style", "font-size:22px;cursor:pointer;font-weight: 700;color: #0101ff;")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #pc-font-icon').attr("style", "font-size:15px;cursor:pointer;")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #tab-font-icon').attr("style", "font-size:15px;cursor:pointer;")
                        })
                        elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #tab-font-icon').on("click", () => {
                            // console.log(">>tab working<<")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').attr("input_value", "Tab")
                            if (fonts_media_query_data['tab-font-size']) {
                                elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val(fonts_media_query_data['tab-font-size'].split('-')[0])
                                elementstyledialog.$wrapper.find(".form-control[data-fieldname='font-size']").parent().find("select").val(fonts_media_query_data['tab-font-size'].split('-')[1] ? fonts_media_query_data['tab-font-size'].split('-')[1] : "px")
                            }
                            else {
                                elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val('')
                            }
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #tab-font-icon').attr("style", "font-size:17px;cursor:pointer;font-weight: 700;color: #0101ff;")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #pc-font-icon').attr("style", "font-size:15px;cursor:pointer;")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #mbl-font-icon').attr("style", "font-size:20px;cursor:pointer;")
                        })
                        elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #pc-font-icon').on("click", () => {
                            // console.log(">>pc working<<")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').attr("input_value", "Web")
                            if (fonts_media_query_data['pc-font-size']) {
                                elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val(fonts_media_query_data['pc-font-size'].split('-')[0])
                                elementstyledialog.$wrapper.find(".form-control[data-fieldname='font-size']").parent().find("select").val(fonts_media_query_data['pc-font-size'].split('-')[1] ? fonts_media_query_data['pc-font-size'].split('-')[1] : "px")
                            }
                            else {
                                elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input').val('')
                            }
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #pc-font-icon').attr("style", "font-size:17px;cursor:pointer;font-weight: 700;color: #0101ff;")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #mbl-font-icon').attr("style", "font-size:20px;cursor:pointer;")
                            elementstyledialog.$wrapper.find('[data-fieldname="font-size"] #tab-font-icon').attr("style", "font-size:15px;cursor:pointer;")
                        })
                        $(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input')).on("keyup", (e) => {
                            let entered_value = $(e.target).val()
                            let unit = $(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] select')).val()
                            let input_value = $(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input')).attr("input_value")
                            // console.log(`>>${input_value} Entered value<<`,entered_value+unit)
                            if (input_value == "Web") {
                                fonts_media_query_data['pc-font-size'] = entered_value + '-' + unit;
                            }
                            else if (input_value == "Tab") {
                                fonts_media_query_data['tab-font-size'] = entered_value + '-' + unit;
                            }
                            else if (input_value == "Mobile") {
                                fonts_media_query_data['mbl-font-size'] = entered_value + '-' + unit;
                            }
                            // console.log(">> all fonts value<<",fonts_media_query_data)
                        })
                        $(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] select')).on("change", (e) => {
                            // console.log(">> selectd value<<",$(e.target).val())
                            let unit = $(e.target).val()
                            let input_value = $(elementstyledialog.$wrapper.find('[data-fieldname="font-size"] input')).attr("input_value")
                            if (input_value == "Web") {
                                if (fonts_media_query_data['pc-font-size']) {
                                    let each_val = fonts_media_query_data['pc-font-size'].split('-')
                                    fonts_media_query_data['pc-font-size'] = each_val[0] + '-' + unit
                                }
                            }
                            else if (input_value == "Tab") {
                                if (fonts_media_query_data['tab-font-size']) {
                                    let each_val = fonts_media_query_data['tab-font-size'].split('-')
                                    fonts_media_query_data['tab-font-size'] = each_val[0] + '-' + unit
                                }
                            }
                            else if (input_value == "Mobile") {
                                if (fonts_media_query_data['mbl-font-size']) {
                                    let each_val = fonts_media_query_data['mbl-font-size'].split('-')
                                    fonts_media_query_data['mbl-font-size'] = each_val[0] + '-' + unit
                                }
                            }
                        });
                    }



                        // Modify by gopi on 17/9/22 for background properties like mask and pattern and gradiend

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
                                if(each_gradiant.css_properties && !each_gradiant.css_properties.startsWith('data') && !each_gradiant.css_properties.startsWith('<svg') && !each_gradiant.css_properties.startsWith('/files')){
                                temp_html=$(`<div class="each-bg-div" value="${each_gradiant.css_properties}" bg_type="${bg_type}" style="flex: 0 0 calc(20% - 20px);cursor:pointer;">
                                            <div class="bg-gradiant-color" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="background:${each_gradiant.css_properties};height:70px;border-radius:7px;"></div>
                                            <div class="bg-title" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="text-align:center;padding-top:5px;font-weight:600;">${each_gradiant.title}</div>
                                        </div>`)
                                    }
                                else if(each_gradiant.css_properties && each_gradiant.css_properties.startsWith('/files')){
                                    temp_html=$(`<div class="each-bg-div" value="${each_gradiant.css_properties}" bg_type="${bg_type}" style="flex: 0 0 calc(20% - 20px);cursor:pointer;">
                                                <div class="bg-gradiant-color" bg_type="${bg_type}" value="${each_gradiant.css_properties}" src='${each_gradiant.css_properties}' style="${gra_patt_mask['bg-divider-img']?"-webkit-mask:url('"+each_gradiant.css_properties+"')no-repeat center / contain;":''}${gra_patt_mask["divider-color"]?'background:'+gra_patt_mask["divider-color"]+';':"#a14848;"}height:70px;border-radius:7px;"></div>
                                                <div class="bg-title" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="text-align:center;padding-top:5px;font-weight:600;">${each_gradiant.title}</div>
                                            </div>`)
                                        }
                                else if(each_gradiant.css_properties && each_gradiant.css_properties.startsWith('data') && !each_gradiant.css_properties.startsWith('<svg')) {
                                    temp_html=$(`<div class="each-bg-div" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="flex: 0 0 calc(20% - 20px);cursor:pointer;">
                                    <div class="bg-gradiant-color" bg_type="${bg_type}" value="${each_gradiant.css_properties}" style="height:70px;border-radius:7px;">
                                    <img bg_type="${bg_type}" value="${each_gradiant.css_properties}" src=${"'"+each_gradiant.css_properties.replace(' ','%20')+"'"}>
                                    </div>
                                    <div bg_type="${bg_type}" class="bg-title" value="${each_gradiant.css_properties}" style="text-align:center;padding-top:5px;font-weight:600;">${each_gradiant.title}</div>
                                </div>`)
                                }
                                else if(each_gradiant.css_properties){
                                    // console.log(each_gradiant.title+">> converted png file <<",svg_to_png_coverter(each_gradiant.css_properties,0,"white"))
                                    dividers_values.push(each_gradiant.css_properties)
                                    temp_html=$(`<div class="each-bg-div" bg_type="${bg_type}" value="${dividers_values.indexOf(each_gradiant.css_properties)}" style="flex: 0 0 calc(20% - 20px);cursor:pointer;">
                                    <div class="bg-gradiant-color" bg_type="${bg_type}" value="${dividers_values.indexOf(each_gradiant.css_properties)}" style="height:70px;border-radius:7px;text-align:center;">
                                            ${each_gradiant.css_properties}
                                    <div bg_type="${bg_type}" value="${dividers_values.indexOf(each_gradiant.css_properties)}" class="bg-title" style="text-align:center;padding-top:5px;font-weight:600;">${each_gradiant.title}</div>
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
                                        else if($(e.target).attr("bg_type") == 'Divider'){
                                            // console.log(">> svg file<<",dividers_values[parseInt($(e.target).attr("value"))])
                                            // console.log(">> Divider value <<",window.btoa(dividers_values[parseInt($(e.target).attr("value"))]))
                                            let divider_background = gra_patt_mask["divider-color"]?gra_patt_mask["divider-color"]:"Red"
                                            elementstyledialog.$wrapper.find('[data-fieldname="bg-divider-img"] .divider_modify_sec .btn-previw-section .divider-color').css({"-webkit-mask":`url('${$(e.target).attr("value")}')no-repeat center / contain`,"background":`${divider_background}`})
                                            popup_variable_color_codes["bg-divider-img"] = $(e.target).attr("value")
                                            bg_dialog.hide();
                                        }
                                    })
                                    $(bg_wrapper).find(`#${cur_frm.r___id}[bg_type="${bg_type}"].bg-main-div .bg-sub-div`).append(temp_html)
                                }
                            })	
                            $(bg_wrapper).find(`#${cur_frm.r___id}[bg_type="${bg_type}"].bg-main-div .bg-sub-div svg`).css({"max-width":"100%","max-height":"100%"})
                        }

                        // end by gopi 17/9/22

                   }
                }
            })
}

// by gopi for webtheme 6/9/22
function select_unselect_palette(e){
    // console.log("--works--",$(e).is(":checked"))
    // console.log("--value--",$(e).attr("value"))
    cur_frm.selected_palette_id = $(e).attr("value")
}

function select_unselect_layout(e){
    // console.log("--works--",$(e).is(":checked"))
    // console.log("--value--",$(e).attr("value"))
    cur_frm.selected_layout_id = $(e).attr("value")
}
