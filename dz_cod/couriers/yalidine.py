# UNTESTED: no call to the real Yalidine API was ever made (official docs not reachable).
"""Yalidine connector: DOCUMENTED STUB, NOT IMPLEMENTED.

Why a stub?
-----------
The project rule is: build a real connector only from public, reliable API
documentation, and never invent endpoints. When this app was written
(October 2026) the official Yalidine developer documentation
(https://yalidine.app -> espace développeur) could not be reached from the
build machine, and neither could the docs of ZR Express, Maystro or the
Ecotrack platform. So no real connector was written.

What we know (NOT verified against official docs)
--------------------------------------------------
An unofficial open-source Python client ("yalidine" 0.0.3 on PyPI) uses:
- base URL: https://api.yalidine.app/v1/
- authentication with two HTTP headers: X-API-ID and X-API-TOKEN
  (both found in the Yalidine merchant dashboard)
- resources named parcels/, histories/, wilayas/, communes/, centers/,
  deliveryfees/

Treat this as a lead only. Before implementing, log into the client's Yalidine
account, open the official API documentation, and check every URL, field name
and status word.

How to implement it later
-------------------------
1. Fill the three methods below using `requests` (already installed with Frappe).
2. Read the credentials from the courier (Supplier) record:
       api_id = self.courier.dz_api_id
       api_token = self.courier.get_password("dz_api_token")
3. In get_status(), translate Yalidine's status words into our four words
   (IN_TRANSIT, DELIVERED, RETURNED, UNKNOWN from base.py).
4. Test with the client's real account on a test parcel.
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
