"""Frappe reads this file to know how the dz_cod app plugs into ERPNext.

Only the hooks we actually use are listed. For all possible hooks see
https://docs.frappe.io/framework/user/en/python-api/hooks
"""

app_name = "dz_cod"
app_title = "DZ COD"
app_publisher = "Adem"
app_description = "COD e-commerce starter kit for Algerian online sellers on ERPNext"
app_email = "adembenlecheb1@gmail.com"
app_license = "mit"

required_apps = ["erpnext"]

# Create custom fields, workflow, wilayas and webhooks
after_install = "dz_cod.setup.install.after_install"
after_migrate = "dz_cod.setup.install.after_migrate"

# Extra buttons on the Sales Order form (Expédier dialog, return inspection)
doctype_js = {"Sales Order": "public/js/sales_order.js"}

# The COD order life cycle: see dz_cod/cod/order.py
doc_events = {
	"Sales Order": {
		"before_validate": "dz_cod.cod.order.before_validate",
		"validate": "dz_cod.cod.order.validate",
		"before_submit": "dz_cod.cod.order.before_submit",
		"before_update_after_submit": "dz_cod.cod.order.before_update_after_submit",
		"on_update_after_submit": "dz_cod.cod.order.on_update_after_submit",
	},
}

# Ask the couriers for parcel statuses every hour (only if enabled in COD Settings)
scheduler_events = {
	"hourly": ["dz_cod.couriers.sync.sync_shipped_orders"],
}
