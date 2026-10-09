"""Integration tests: courier settlement (Versement) matching.

Run: bench --site <site> run-tests --module dz_cod.tests.test_settlement
"""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from dz_cod.cod import settlement as rules
from dz_cod.cod import states as S
from dz_cod.demo import data as D
from dz_cod.tests import helpers as h


def delivered_order(qty=1):
	order = h.make_order(qty=qty)
	return h.act(order, S.ACTION_CONFIRM, S.ACTION_PREPARE, S.ACTION_SHIP, S.ACTION_DELIVER)


def new_settlement(lines):
	settlement = frappe.new_doc("Courier Settlement")
	settlement.update({"courier": h.MOCK_COURIER, "company": D.COMPANY, "posting_date": today()})
	for line in lines:
		settlement.append("items", line)
	settlement.insert()
	return settlement


class TestSettlement(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		h.setup_fixtures()

	def test_matching_statuses_and_summary(self):
		ok = delivered_order()
		short = delivered_order()
		in_transit = h.act(h.make_order(), S.ACTION_CONFIRM, S.ACTION_PREPARE, S.ACTION_SHIP)
		forgotten = delivered_order()

		settlement = new_settlement(
			[
				# found by tracking number, full amount
				{
					"tracking_number": ok.dz_tracking_number,
					"collected_amount": ok.dz_cod_amount,
					"courier_fee": ok.dz_courier_fee,
				},
				# 500 DA short
				{
					"sales_order": short.name,
					"collected_amount": short.dz_cod_amount - 500,
					"courier_fee": short.dz_courier_fee,
				},
				# not delivered yet according to us
				{
					"sales_order": in_transit.name,
					"collected_amount": in_transit.dz_cod_amount,
					"courier_fee": 0,
				},
				# tracking number we do not know
				{"tracking_number": "NOPE-0001", "collected_amount": 1000, "courier_fee": 0},
			]
		)
		statuses = [line.status for line in settlement.items]
		self.assertEqual(statuses, [rules.OK, rules.GAP, rules.INVALID, rules.UNKNOWN])
		self.assertEqual(settlement.items[0].sales_order, ok.name)
		self.assertEqual(settlement.items[1].difference, -500)

		self.assertEqual(settlement.paid_count, 1)
		self.assertEqual(settlement.disputed_count, 3)
		# "forgotten" was delivered but is not in the statement
		missing = [o.name for o in settlement.get_missing_orders()]
		self.assertIn(forgotten.name, missing)
		self.assertNotIn(ok.name, missing)

		settlement.submit()
		self.assertEqual(frappe.db.get_value("Sales Order", ok.name, "workflow_state"), S.SETTLED)
		self.assertEqual(frappe.db.get_value("Sales Order", ok.name, "dz_settlement"), settlement.name)
		self.assertEqual(frappe.db.get_value("Sales Order", short.name, "workflow_state"), S.DELIVERED)

	def test_accepted_gap_is_paid_and_cancel_reverts(self):
		order = delivered_order()
		settlement = new_settlement(
			[
				{
					"sales_order": order.name,
					"collected_amount": order.dz_cod_amount - 100,
					"courier_fee": order.dz_courier_fee,
					"accept_difference": 1,
				}
			]
		)
		settlement.submit()
		self.assertEqual(frappe.db.get_value("Sales Order", order.name, "workflow_state"), S.SETTLED)

		settlement.cancel()
		values = frappe.db.get_value(
			"Sales Order", order.name, ["workflow_state", "dz_settlement"], as_dict=True
		)
		self.assertEqual(values.workflow_state, S.DELIVERED)
		self.assertIsNone(values.dz_settlement)

	def test_order_paid_twice_is_flagged(self):
		order = delivered_order()
		line = {
			"sales_order": order.name,
			"collected_amount": order.dz_cod_amount,
			"courier_fee": order.dz_courier_fee,
		}
		new_settlement([line]).submit()
		second = new_settlement([line])
		self.assertEqual(second.items[0].status, rules.ALREADY_SETTLED)

	def test_same_order_twice_in_one_settlement_is_refused(self):
		order = delivered_order()
		line = {
			"sales_order": order.name,
			"collected_amount": order.dz_cod_amount,
			"courier_fee": order.dz_courier_fee,
		}
		with self.assertRaises(frappe.ValidationError):
			new_settlement([line, line])

	def test_load_delivered_orders_button(self):
		order = delivered_order()
		settlement = frappe.new_doc("Courier Settlement")
		settlement.update({"courier": h.MOCK_COURIER, "company": D.COMPANY, "posting_date": today()})
		settlement.load_delivered_orders()
		line = next(line for line in settlement.items if line.sales_order == order.name)
		self.assertEqual(line.status, rules.OK)
		self.assertEqual(line.net_amount, order.dz_cod_amount - order.dz_courier_fee)
