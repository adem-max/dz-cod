"""Hourly job: ask each courier where our shipped parcels are.

If the courier says "delivered" the order moves to Livrée, if it says
"returned" it moves to Retournée. Uses the normal workflow actions, so the
same checks, stock movements and webhooks run as when a person clicks.

Disabled unless "Synchroniser les statuts automatiquement" is ticked in
COD Settings.
"""

import frappe
from frappe.model.workflow import apply_workflow

from dz_cod.cod import states as S
from dz_cod.couriers import get_adapter
from dz_cod.couriers.base import DELIVERED, RETURNED

# Courier status -> workflow button to press
ACTIONS = {DELIVERED: S.ACTION_DELIVER, RETURNED: S.ACTION_RETURN}


def sync_shipped_orders():
	if not frappe.db.get_single_value("COD Settings", "auto_sync_courier_status"):
		return

	orders = frappe.get_all(
		"Sales Order",
		filters={"docstatus": 1, "workflow_state": S.SHIPPED},
		fields=["name", "dz_courier", "dz_tracking_number"],
	)
	for order in orders:
		sync_order(order)


def sync_order(order):
	"""Check one order. An error on one order must not stop the others."""
	try:
		status = get_adapter(order.dz_courier).get_status(order.dz_tracking_number)
		action = ACTIONS.get(status)
		if action:
			apply_workflow(frappe.get_doc("Sales Order", order.name), action)
			frappe.db.commit()
	except Exception:
		frappe.db.rollback()
		frappe.log_error(title=f"Synchronisation transporteur : {order.name}")
