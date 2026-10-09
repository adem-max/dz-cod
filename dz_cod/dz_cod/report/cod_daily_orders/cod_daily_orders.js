frappe.query_reports["COD Daily Orders"] = {
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
			fieldname: "from_date",
			label: __("Du"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("Au"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "courier",
			label: __("Transporteur"),
			fieldtype: "Link",
			options: "Supplier",
			get_query: () => ({ filters: { is_transporter: 1 } }),
		},
	],
};
