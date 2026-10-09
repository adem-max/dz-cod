// Versement form: one extra button to pre-fill the lines.
frappe.ui.form.on("Courier Settlement", {
	setup(frm) {
		// Only couriers (suppliers marked "Is Transporter") in the courier field
		frm.set_query("courier", () => ({ filters: { is_transporter: 1 } }));
	},

	onload(frm) {
		// New Versement: take the company from COD Settings
		if (frm.is_new() && !frm.doc.company) {
			frappe.db
				.get_single_value("COD Settings", "company")
				.then((company) => company && frm.set_value("company", company));
		}
	},

	refresh(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.courier) {
			frm.add_custom_button(__("Charger les commandes livrées"), () => {
				frm.call("load_delivered_orders").then(() => frm.dirty());
			});
		}
	},

	// Show the button as soon as a courier is chosen (not only after saving)
	courier(frm) {
		frm.trigger("refresh");
	},
});
