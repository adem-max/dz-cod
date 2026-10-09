"""Courier Settlement ("Versement"): money paid to us by a delivery company.

How it is used:
1. The courier sends a statement: a list of parcels, with the cash collected
   and its fee for each one, and transfers the net total.
2. Create a Versement, choose the courier, then either click
   "Charger les commandes livrées" (pre-fills one line per delivered order)
   or upload the courier's statement as CSV in the table.
3. Save: every line is matched to its order and gets a status
   (OK / Écart / Inconnue / Déjà réglée / Invalide), and the summary shows
   what is paid, what is disputed and what is missing.
4. Submit: every OK line (and every Écart line you ticked "Accepter") moves
   its order to "Réglée". The others stay "Livrée" and keep showing in the
   "Encours transporteurs" report.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
from frappe.utils import flt

from dz_cod.cod import settlement as rules
from dz_cod.cod import states as S

ORDER_FIELDS = [
	"name",
	"workflow_state",
	"dz_courier",
	"dz_cod_amount",
	"dz_courier_fee",
	"dz_tracking_number",
]


class CourierSettlement(Document):
	def validate(self):
		self.match_lines()
		self.compute_summary()

	def on_submit(self):
		paid_lines = [line for line in self.items if rules.is_paid(line.status, line.accept_difference)]
		for line in paid_lines:
			order = frappe.get_doc("Sales Order", line.sales_order)
			order.flags.dz_event_date = self.posting_date
			apply_workflow(order, S.ACTION_SETTLE)
			frappe.db.set_value("Sales Order", order.name, "dz_settlement", self.name)

	def on_cancel(self):
		"""Put the orders paid by this settlement back to "Livrée".

		A Workflow cannot go backwards, so we write the fields directly.
		"""
		for name in frappe.get_all("Sales Order", filters={"dz_settlement": self.name}, pluck="name"):
			frappe.db.set_value(
				"Sales Order",
				name,
				{"workflow_state": S.DELIVERED, "dz_settlement": None, "dz_settled_on": None},
			)
			frappe.get_doc("Sales Order", name).add_comment(
				"Comment", _("Versement {0} annulé : retour à l'état {1}.").format(self.name, S.DELIVERED)
			)

	# ------------------------------------------------------------ matching

	def match_lines(self):
		"""Find the order of each line and decide its status."""
		tolerance = flt(frappe.db.get_single_value("COD Settings", "settlement_tolerance"))
		seen_orders = set()

		for line in self.items:
			order = self.find_order(line)
			if order and order.name in seen_orders:
				frappe.throw(
					_("Ligne {0} : la commande {1} apparaît deux fois.").format(line.idx, order.name)
				)

			line.net_amount = flt(line.collected_amount) - flt(line.courier_fee)
			if order:
				seen_orders.add(order.name)
				line.sales_order = order.name
				line.tracking_number = line.tracking_number or order.dz_tracking_number
				line.expected_amount = flt(order.dz_cod_amount)
				line.expected_fee = flt(order.dz_courier_fee)
				line.difference = line.net_amount - (line.expected_amount - line.expected_fee)
			else:
				line.expected_amount = line.expected_fee = line.difference = 0

			line.status = rules.line_status(
				order_state=order.workflow_state if order else None,
				order_courier=order.dz_courier if order else None,
				settlement_courier=self.courier,
				net_paid=line.net_amount,
				expected_net=line.expected_amount - line.expected_fee,
				tolerance=tolerance,
			)

	def find_order(self, line):
		"""The line's order, by order name or else by tracking number."""
		filters = None
		if line.sales_order:
			filters = {"name": line.sales_order}
		elif line.tracking_number:
			filters = {"dz_tracking_number": line.tracking_number.strip(), "docstatus": 1}
		if not filters:
			return None
		orders = frappe.get_all("Sales Order", filters=filters, fields=ORDER_FIELDS, limit=1)
		return orders[0] if orders else None

	# ------------------------------------------------------------- summary

	def compute_summary(self):
		self.total_collected = sum(flt(line.collected_amount) for line in self.items)
		self.total_fees = sum(flt(line.courier_fee) for line in self.items)
		self.total_net = self.total_collected - self.total_fees
		self.difference_received = flt(self.amount_received) - self.total_net if self.amount_received else 0

		self.paid_count = self.paid_amount = self.disputed_count = self.disputed_amount = 0
		for line in self.items:
			if rules.is_paid(line.status, line.accept_difference):
				self.paid_count += 1
				self.paid_amount += line.net_amount
			else:
				self.disputed_count += 1
				self.disputed_amount += rules.disputed_amount(line.status, line.net_amount, line.difference)

		missing = self.get_missing_orders()
		self.missing_count = len(missing)
		self.missing_amount = sum(flt(o.dz_cod_amount) - flt(o.dz_courier_fee) for o in missing)

	def get_missing_orders(self):
		"""Orders this courier delivered up to the settlement date, not in this
		settlement and not paid yet."""
		in_this_settlement = [line.sales_order for line in self.items if line.sales_order]
		filters = {
			"docstatus": 1,
			"workflow_state": S.DELIVERED,
			"dz_courier": self.courier,
			"dz_delivered_on": ["<=", self.posting_date],
		}
		if in_this_settlement:
			filters["name"] = ["not in", in_this_settlement]
		return frappe.get_all("Sales Order", filters=filters, fields=ORDER_FIELDS)

	@frappe.whitelist()
	def load_delivered_orders(self):
		"""Button "Charger les commandes livrées": one line per missing order,
		pre-filled with the expected amounts (edit only the exceptions)."""
		for order in self.get_missing_orders():
			self.append(
				"items",
				{
					"sales_order": order.name,
					"tracking_number": order.dz_tracking_number,
					"collected_amount": order.dz_cod_amount,
					"courier_fee": order.dz_courier_fee,
				},
			)
		self.validate()
