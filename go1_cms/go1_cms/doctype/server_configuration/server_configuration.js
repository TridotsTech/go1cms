// Copyright (c) 2020, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Server Configuration', {
	setup: function(frm) {
		frm.trigger('setup_help_text');
	},
	refresh: function(frm) {
		
	},
	install_wildcard: function(frm) {
		console.log(frm)
		frm.call("install_wildcard", {
			url: window.location.hostname
		});
	},
	setup_help_text: function(frm) {
		let wrapper = $(frm.get_field('ssl_help').wrapper).empty();
		let html = $(`<table class="table table-bordered" style="background: #f9f9f9;">
	                <tbody>
	                    <tr>
	                        <td>
	                            <h4>${__("Manual Setup")}</h4>
	                            <ol>
	                                <li>${__("Run the command to generate Wildcard SSL")}</li>
	                                <li>${__('Command: ')}<b>${__('sudo bench setup wildcard-ssl domain.xyz --email info@valiantsystems.com')}</b></li>
					<li>${__('or Command: ')}<b>${__('sudo bench setup wildcard-ssl domain.xyz --exclude-base-domain')}</b></li>
	                                <li>${__('Add text record to your DNS.')}</li>
					<li>${__('To check text record propagation.')}${__(' Command: ')}<b>${__("dig -t TXT _acme-challenge.domain.xyz")}</b></li>
	                            </ol>
	                        </td>
	                    </tr>
	                </tbody>
	            </table>`).appendTo(wrapper)
	    },
});
