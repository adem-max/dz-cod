# UNTESTED: no call to the real Yalidine API was ever made from this app.
"""Yalidine connector: DOCUMENTED STUB, NOT IMPLEMENTED YET.

The official Yalidine developer documentation sits behind the merchant
login and could not be opened from the build machine. A verbatim copy of it
(API + webhooks, September 2026) was later found in an open-source project,
so the API is now known well enough to implement this connector:

    base URL   https://api.yalidine.app/v1/
    headers    X-API-ID, X-API-TOKEN (from the client's Developer Dashboard)
    create     POST parcels/        status   GET histories/<tracking>
    prices     GET fees/?from_wilaya_id=..&to_wilaya_id=..

The full plan, field by field, is in docs/COURIER_INTEGRATION.md (steps Y1
to Y9). Check every detail against the docs in the client's own Yalidine
dashboard before going live.
"""

from frappe import _

from dz_cod.couriers.base import CourierAdapter

NOT_IMPLEMENTED = _(
	"Le connecteur Yalidine n'est pas encore implémenté (documentation officielle non vérifiée). "
	"Utilisez le connecteur « Manuel » et saisissez le n° de suivi."
)


class YalidineAdapter(CourierAdapter):
	label = "Yalidine"

	def create_shipment(self, order):
		raise NotImplementedError(NOT_IMPLEMENTED)

	def get_status(self, tracking_number):
		raise NotImplementedError(NOT_IMPLEMENTED)

	def get_tracking(self, tracking_number):
		raise NotImplementedError(NOT_IMPLEMENTED)
