"""Mock courier: a fake delivery company that works offline.

Use it for demos and tests. It never calls the internet.
- create_shipment() returns "MOCK-<order name>"
- get_status() returns "in_transit" until you decide otherwise with
  set_mock_status(), for example from the console:

    from dz_cod.couriers.mock import set_mock_status
    set_mock_status("MOCK-SAL-ORD-2026-00012", "delivered")

The simulated statuses are kept in the Redis cache, so they are shared between
the web server and the background workers, and lost when the cache is cleared.
"""

import frappe
from frappe.utils import now_datetime

from dz_cod.couriers.base import IN_TRANSIT, CourierAdapter

CACHE_KEY = "dz_cod_mock_courier_status"


class MockAdapter(CourierAdapter):
	label = "Mock"

	def create_shipment(self, order):
		return f"MOCK-{order.name}"

	def get_status(self, tracking_number):
		return frappe.cache.hget(CACHE_KEY, tracking_number) or IN_TRANSIT

	def get_tracking(self, tracking_number):
		return [
			{
				"date": str(now_datetime()),
				"status": self.get_status(tracking_number),
				"location": "Centre de tri (simulation)",
			}
		]


def set_mock_status(tracking_number, status):
	"""Simulate the courier updating a parcel (for tests and demos)."""
	frappe.cache.hset(CACHE_KEY, tracking_number, status)
