"""COD Settings: everything that changes from one client to another.

Rule of the project: per-client differences live here (or in custom fields),
never in `if client == ...` branches in the code.
"""

import frappe
from frappe import _
from frappe.model.document import Document


class CODSettings(Document):
	def validate(self):
		# Both warehouses must belong to the selected company
		for fieldname in ("main_warehouse", "returns_warehouse"):
			warehouse = self.get(fieldname)
			if frappe.db.get_value("Warehouse", warehouse, "company") != self.company:
				frappe.throw(
					_("L'entrepôt {0} n'appartient pas à la société {1}.").format(warehouse, self.company)
				)

		if self.main_warehouse == self.returns_warehouse:
			frappe.throw(_("L'entrepôt des retours doit être différent de l'entrepôt principal."))


def get_settings():
	"""Return the COD Settings document (cached, read-only use)."""
	settings = frappe.get_cached_doc("COD Settings")
	if not settings.main_warehouse:
		frappe.throw(_("Veuillez d'abord remplir les Paramètres COD."))
	return settings
