// Extra behaviour on the Sales Order form for COD orders.
// 1. Before "Expédier": ask for the courier and tracking number.
// 2. On a returned order: a button to record the inspection of the parcel.

frappe.ui.form.on("Sales Order", {
	setup(frm) {
		frm.set_query("dz_courier", () => ({ filters: { is_transporter: 1 } }));
	},

	refresh(frm) {
		if (frm.doc.workflow_state === "Retournée" && !frm.doc.dz_return_inspected) {
			frm.add_custom_button(__("Inspecter le retour"), () => inspect_return(frm));
		}
	},

	// Runs when a workflow button is clicked, before the action is applied.
	// Returning a Promise makes Frappe wait for it.
	before_workflow_action(frm) {
		if (frm.selected_workflow_action !== "Expédier") {
			return;
		}
		// Frappe greys out the screen while a workflow action runs. Lift that
		// while our dialog is open, otherwise nobody can click in it.
		frappe.dom.unfreeze();
		return new Promise((resolve, reject) => {
			let shipped = false; // closing the dialog without shipping cancels the action
			const dialog = new frappe.ui.Dialog({
				title: __("Expédier la commande"),
				fields: [
					{
						fieldname: "courier",
						label: __("Transporteur"),
						fieldtype: "Link",
						options: "Supplier",
						reqd: 1,
						default: frm.doc.dz_courier,
						get_query: () => ({ filters: { is_transporter: 1 } }),
					},
					{
						fieldname: "tracking_number",
						label: __("N° de suivi"),
						fieldtype: "Data",
						default: frm.doc.dz_tracking_number,
						description: __(
							"Laissez vide si le transporteur est connecté (le numéro sera demandé automatiquement)."
						),
					},
				],
				primary_action_label: __("Expédier"),
				primary_action(values) {
					frappe
						.call("dz_cod.cod.order.set_shipping_details", {
							sales_order: frm.doc.name,
							courier: values.courier,
							tracking_number: values.tracking_number,
						})
						.then(() => {
							shipped = true;
							dialog.hide();
							frappe.dom.freeze(); // Frappe unfreezes when the action is done
							resolve();
						});
				},
			});
			dialog.onhide = () => {
				if (!shipped) reject();
			};
			dialog.show();
		});
	},
});

function inspect_return(frm) {
	frappe.call("dz_cod.cod.stock.get_returned_items", { sales_order: frm.doc.name }).then((r) => {
		// One row per returned item: by default everything is in good condition
		const rows = (r.message || []).map((row) => ({
			item_code: row.item_code,
			item_name: row.item_name,
			good_qty: row.qty,
			damaged_qty: 0,
		}));

		const dialog = new frappe.ui.Dialog({
			title: __("Inspection du retour"),
			size: "large",
			fields: [
				{
					fieldtype: "HTML",
					options: `<p>${__(
						"Indiquez pour chaque article combien de pièces sont en bon état (remises en stock) et combien sont abîmées (mises au rebut)."
					)}</p>`,
				},
				{
					fieldname: "items",
					fieldtype: "Table",
					cannot_add_rows: true,
					in_place_edit: true,
					data: rows,
					fields: [
						{ fieldname: "item_code", label: __("Code"), fieldtype: "Data", read_only: 1, in_list_view: 1 },
						{ fieldname: "item_name", label: __("Article"), fieldtype: "Data", read_only: 1, in_list_view: 1 },
						{ fieldname: "good_qty", label: __("Bon état"), fieldtype: "Float", in_list_view: 1 },
						{ fieldname: "damaged_qty", label: __("Abîmé"), fieldtype: "Float", in_list_view: 1 },
					],
				},
			],
			primary_action_label: __("Valider l'inspection"),
			primary_action(values) {
				frappe
					.call("dz_cod.cod.stock.inspect_return", {
						sales_order: frm.doc.name,
						items: values.items,
					})
					.then(() => {
						dialog.hide();
						frm.reload_doc();
					});
			},
		});
		dialog.show();
	});
}
