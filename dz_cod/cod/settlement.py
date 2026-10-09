"""Matching rules for courier settlements (Versement).

Pure functions (no database) so they are easy to read and to test.

Planning analogy: this is a three-way match, like matching a supplier invoice
against the purchase order and the goods receipt. Here we match:
  what the courier says it paid  <->  what the order says it should pay.
"""

from dz_cod.cod import states as S

# Line statuses (shown in French to the user)
OK = "OK"
GAP = "Écart"  # amounts differ more than the tolerance
UNKNOWN = "Inconnue"  # no order found for this tracking number
ALREADY_SETTLED = "Déjà réglée"  # this order was paid in an earlier settlement
INVALID = "Invalide"  # order of another courier, or not in state Livrée


def line_status(order_state, order_courier, settlement_courier, net_paid, expected_net, tolerance):
	"""Decide the status of one settlement line.

	order_state is None when no order matches the line.
	"""
	if order_state is None:
		return UNKNOWN
	if order_state == S.SETTLED:
		return ALREADY_SETTLED
	if order_state != S.DELIVERED or order_courier != settlement_courier:
		return INVALID
	if abs(net_paid - expected_net) <= tolerance:
		return OK
	return GAP


def is_paid(status, accept_difference):
	"""Will this line mark its order as Réglée when the settlement is submitted?"""
	return status == OK or (status == GAP and bool(accept_difference))


def disputed_amount(status, net_paid, difference):
	"""How much money is in question for a line that is not paid."""
	if status == GAP:
		return abs(difference)
	return net_paid
