// Copyright (c) 2019, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Settings', {
	onload: function(frm) {
		frappe.realtime.on('Go1-CMS:reload-page', () => {
			frm.reload_doc();
		});
	},
	refresh: function(frm) {
		//by sivaranjani
		frappe.call({
			method: 'go1_cms.go1_cms.doctype.site_settings.site_settings.get_domainconfig_settings',
			args: {},
			async: false,
			callback: function(data) {
				if (data.message) {
					cur_frm.config_settings = data.message
					// cur_frm.set_df_property('name1',"hidden",1);
					//frm.set_df_property("restaurant", "read_only", frm.doc.__islocal ? 0 : 1);
				}
			}
		})
		frm.add_custom_button(__('Execute Commands'), function() {
			var dialog = new frappe.ui.Dialog({
				title: 'Bench Execute',
				fields: [
					{ fieldname: 'command', fieldtype: 'Data', label: "Command", reqd: true }
				]
			});
			dialog.set_primary_action(__("Execute"), () => {
				var val = dialog.get_values();
				frappe.call({
					method: 'go1_cms.go1_cms.doctype.site_settings.site_settings.execute_bench_command',
					args: {
						method: val.command,
					}
				});
				dialog.hide();
			});
			dialog.show();
		});
		if (cur_frm.config_settings) {
			//frm.set_df_property("disable_www", "hidden", cur_frm.config_settings.installed_wildcard_ssl ? 1 : 0);
			frm.set_df_property("enable_custom_ssl", "hidden", cur_frm.config_settings.installed_wildcard_ssl ? 0 : 1);
			if (cur_frm.config_settings.enable_www == 1) {
				//frm.set_value("disable_www", cur_frm.config_settings.installed_wildcard_ssl ? 0 : 1);
			} else {
				frm.set_df_property("disable_www", "hidden", cur_frm.config_settings.enable_www ? 0 : 1);
			}
		}
		frm.trigger('additional_information');
		if(!frm.doc.__islocal)
			frm.trigger('check_domain');
	},
	additional_information: function(frm) {
		if(frm.doc.additional_information) {
			let data = JSON.parse(frm.doc.additional_information);
			if(data && data.length > 0) {
				let wrapper = $(frm.get_field('additional_information').wrapper).empty();
				let table = $(`<table class="table table-bordered" style="background: #f5f7fa;">
					<tbody></tbody>
				</table>`).appendTo(wrapper);
				data.map(f => {
					let row = $(`<tr><td>${__(f.label)}</td><td>${__(f.value)}</td></tr>`);
					table.find('tbody').append(row);
				})
			} else{
				frm.toggle_display(['additional_information'], false);
			}
		} else {
			frm.toggle_display(['additional_information'], false);
		}
	},
	check_domain: function (frm) {
		if(!frm.doc.domain && frappe.boot.sysdefaults.domain_configuration.enable) {
			frm.add_custom_button(__('Add Domain'), ()=>{
				frm.trigger('show_dialog');
			})
		}
		if(frm.doc.domain && frappe.boot.sysdefaults.domain_configuration.enable) {
			if(!frm.doc.enable_alias_active) {
				frm.add_custom_button(__('Make alias domain as default'), () => {
					frm.trigger('enable_alias');
				});
			} else {
				frm.add_custom_button(__('Make actual domain as default'), () => {
					frm.trigger('disable_alias');
				});
			}
		}
	},
	show_dialog: function(frm) {
		let dialog = new frappe.ui.Dialog({
			title: frm.doc.domain ? __('Edit Domain') : __('Add Domain'),
			fields: [{
				'fieldtype': 'Data',
				'fieldname': 'domain',
				'label': __('Domain'),
				'reqd': 1,
				'default': frm.doc.domain
			}],
			primary_action_label: __("Save"),
			primary_action(values) {
				if(values.domain) {
					frappe.call({
						method: 'go1_cms.go1_cms.doctype.site_settings.site_settings.update_domain',
						args: {
							name: frm.doc.name,
							domain: values.domain
						},
						callback: function(r) {
							dialog.hide();
							if(r.message.status == 'failed') {
								frappe.msgprint('Something went wrong. Unable to add domain.');
							}
							frm.refresh();
						}
					})
				}
			}
		});
		dialog.show();
	},
	enable_alias: function(frm) {
		let confirm = frappe.confirm('Are you sure to make alias domain as default?', 
			() => {
				frappe.call({
					method: 'go1_cms.go1_cms.doctype.site_settings.site_settings.make_alias_active',
					args: {
						name: frm.doc.name
					},
					callback: function(r) {
						frm.refresh();
						if(r.message && r.message.status == 'failed'){
							frappe.msgprint('Alias domain is made as default');
						}
					}
				})
			},
			() => {

			});
	},
	disable_alias: function(frm) {
		let confirm = frappe.confirm('Are you sure to make current domain as default?', 
			() => {
				frappe.call({
					method: 'go1_cms.go1_cms.doctype.site_settings.site_settings.update_domain',
					args: {
						name: frm.doc.name,
						domain: frm.doc.domain
					},
					callback: function(r) {
						frm.refresh();
						if(r.message && r.message.status == 'failed'){
							frappe.msgprint('Alias domain is made as default');
						}
					}
				})
			},
			() => {

			});
	}
});