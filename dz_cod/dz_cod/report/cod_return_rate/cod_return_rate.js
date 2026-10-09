frappe.query_reports["COD Return Rate"] = {
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
			label: __("Expédiées du"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -60),
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
			fieldname: "group_by",
			label: __("Grouper par"),
			fieldtype: "Select",
			options: "Produit\nArticle\nWilaya",
			default: "Produit",
			reqd: 1,
		},
	],
};
