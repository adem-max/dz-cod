frappe.query_reports["COD Courier Outstanding"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Société"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			description: __("Vide = société des Paramètres COD"),
		},
		{
			fieldname: "courier",
			label: __("Transporteur"),
			fieldtype: "Link",
			options: "Supplier",
			get_query: () => ({ filters: { is_transporter: 1 } }),
		},
		{
			fieldname: "detail",
			label: __("Détail par commande"),
			fieldtype: "Check",
		},
	],
};
