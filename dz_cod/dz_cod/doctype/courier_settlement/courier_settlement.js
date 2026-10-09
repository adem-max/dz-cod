// Versement form: one extra button to pre-fill the lines.
frappe.ui.form.on("Courier Settlement", {
	setup(frm) {
		// Only couriers (suppliers marked "Is Transporter") in the courier field
		frm.set_query("courier", () => ({ filters: { is_transporter: 1 } }));
	},

	refresh(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.courier) {
			frm.add_custom_button(__("Charger les commandes livrées"), () => {
				frm.call("load_delivered_orders").then(() => frm.dirty());
			});
		}
	},
});
