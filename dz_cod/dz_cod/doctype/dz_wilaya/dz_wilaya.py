"""DZ Wilaya: one record per wilaya, holding the shipping rate table.

Each row answers two questions for an order going to this wilaya:
- how much do we charge the customer for delivery? (home_rate / stopdesk_rate)
- how much will the courier keep for itself? (home_courier_cost / stopdesk_courier_cost)
"""

import frappe
from frappe import _
from frappe.model.document import Document

HOME = "Domicile"
STOP_DESK = "Stop desk"


class DZWilaya(Document):
	def validate(self):
		# Always store the code with two digits: "1" becomes "01"
		self.code = str(self.code).strip().zfill(2)

	def get_rates(self, delivery_type):
		"""Return (customer_rate, courier_cost) for a delivery type."""
		if not self.enabled:
			frappe.throw(_("La wilaya {0} n'est pas livrable.").format(self.name))

		if delivery_type == STOP_DESK:
			if not self.stopdesk_available:
				frappe.throw(_("Pas de stop desk disponible dans la wilaya {0}.").format(self.name))
			return self.stopdesk_rate, self.stopdesk_courier_cost

		return self.home_rate, self.home_courier_cost
