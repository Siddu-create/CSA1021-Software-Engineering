
"""
Assignment 2 - Omnichannel Order Fulfilment Platform
Synthetic in-memory validation model.

Run:
    python fulfiliq_test_model.py

This validates business rules only. It is not a production application,
database concurrency test, or live payment/courier integration.
"""

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Order:
    order_id: str
    customer_id: str
    quantity: int
    status: str = "Placed"
    paid: bool = False
    picked: bool = False
    shipment_created: bool = False
    version: int = 1


@dataclass
class Refund:
    refund_id: str
    order_id: str
    amount: float
    status: str = "Requested"
    approved_by: str = ""
    attempts: int = 0


class FulfilmentModel:
    def __init__(self):
        self.stock = {"LAPTOP": 1}
        self.orders = {}
        self.payment_events = {}
        self.refunds = {}
        self.scanner_events = set()
        self.audit_log = []
        self.regional_policies = {}
        self.lock = Lock()

    def audit(self, action, reference):
        self.audit_log.append({
            "action": action,
            "reference": reference
        })

    # T1: Reserve the last unit safely
    def place_order(self, order_id, customer_id, sku, quantity):
        with self.lock:
            available = self.stock.get(sku, 0)

            if quantity <= 0 or available < quantity:
                return False, "Insufficient stock"

            if order_id in self.orders:
                return False, "Duplicate order"

            self.stock[sku] -= quantity

            self.orders[order_id] = Order(
                order_id=order_id,
                customer_id=customer_id,
                quantity=quantity
            )

            self.audit("ORDER_PLACED", order_id)
            return True, "Order placed"

    # T2: Repeated gateway events must not create duplicate payments
    def payment_callback(self, order_id, gateway, event_id, verified):
        if not verified:
            return False, "Unverified callback rejected"

        event_key = (gateway, event_id)

        with self.lock:
            if event_key in self.payment_events:
                return True, "Duplicate callback ignored"

            order = self.orders.get(order_id)
            if not order:
                return False, "Order not found"

            if order.status != "Placed":
                return False, "Order cannot be paid in current state"

            self.payment_events[event_key] = order_id
            order.paid = True
            order.status = "Paid"
            order.version += 1

            self.audit("PAYMENT_CONFIRMED", order_id)
            return True, "Payment confirmed"

    # Warehouse picker confirmation
    def confirm_pick(self, order_id, role):
        if role != "picker":
            return False, "Picker permission required"

        order = self.orders.get(order_id)
        if not order or order.status != "Paid":
            return False, "Only paid orders can be picked"

        order.picked = True
        order.status = "Packed"
        order.version += 1
        self.audit("ORDER_PICKED", order_id)
        return True, "Pick confirmed"

    # T4: Dispatch requires payment and pick confirmation
    def dispatch(self, order_id):
        order = self.orders.get(order_id)

        if not order:
            return False, "Order not found"

        if not order.paid or not order.picked:
            return False, "Dispatch rejected: payment or pick missing"

        if order.status != "Packed":
            return False, "Invalid order state"

        order.status = "Dispatched"
        order.version += 1
        order.shipment_created = True
        self.audit("ORDER_DISPATCHED", order_id)
        return True, "Order dispatched"

    # Refund approval and execution are separate operations
    def approve_refund(self, refund_id, role, reviewer_id):
        if role != "finance_reviewer":
            return False, "Finance reviewer permission required"

        refund = self.refunds.get(refund_id)
        if not refund:
            return False, "Refund not found"

        if refund.status != "Requested":
            return False, "Refund is not awaiting approval"

        refund.status = "Approved"
        refund.approved_by = reviewer_id
        self.audit("REFUND_APPROVED", refund_id)
        return True, "Refund approved"

    def execute_refund(self, refund_id, gateway_success):
        refund = self.refunds.get(refund_id)

        if not refund:
            return False, "Refund not found"

        if refund.status not in ("Approved", "Failed"):
            return False, "Refund approval required"

        if not refund.approved_by:
            return False, "Missing approval record"

        refund.attempts += 1

        if gateway_success:
            refund.status = "Executed"
            self.audit("REFUND_EXECUTED", refund_id)
            return True, "Refund executed"

        refund.status = "Failed"
        self.audit("REFUND_FAILED", refund_id)
        return False, "Gateway failed; controlled retry allowed"

    # T5: Courier failure must preserve a retryable shipment intent
    def sync_courier(self, order_id, courier_success):
        order = self.orders.get(order_id)

        if not order or order.status != "Dispatched":
            return False, "No dispatched order to synchronize"

        if courier_success:
            self.audit("COURIER_SYNCED", order_id)
            return True, "Courier synchronized"

        self.audit("COURIER_SYNC_PENDING", order_id)
        return False, "Sync failed; retry is pending"

    # T6: Customers and support agents cannot approve refunds
    def view_order(self, order_id, user_id, role):
        order = self.orders.get(order_id)

        if not order:
            return False, "Order not found"

        if role == "administrator":
            return True, order

        if role == "customer" and order.customer_id == user_id:
            return True, order

        if role == "support_agent":
            return True, {
                "order_id": order.order_id,
                "status": order.status,
                "payment_details": "Not exposed"
            }

        return False, "Access denied"

    # T7: Late or duplicate scanner events are handled safely
    def receive_scanner_event(self, source_id, event_id, sku, quantity):
        event_key = (source_id, event_id)

        with self.lock:
            if event_key in self.scanner_events:
                return True, "Duplicate scanner event ignored"

            if quantity <= 0:
                return False, "Invalid stock quantity"

            self.scanner_events.add(event_key)
            self.stock[sku] = self.stock.get(sku, 0) + quantity
            self.audit("SCANNER_EVENT_ACCEPTED", event_id)
            return True, "Scanner event accepted"

    # T8: Regional rules are stored with explicit versions
    def set_regional_policy(self, region, version, tax_rate, shipping_fee,
                            refund_limit):
        self.regional_policies[region] = {
            "version": version,
            "tax_rate": tax_rate,
            "shipping_fee": shipping_fee,
            "refund_limit": refund_limit
        }

    # T9: Locally queued approval is not globally approved
    def validate_queued_approval(self, refund_id, local_decision, server_role):
        if local_decision != "APPROVE":
            return False, "No approval submitted"

        if server_role != "finance_reviewer":
            return False, "Server rejected unauthorized approval"

        return self.approve_refund(
            refund_id, server_role, "FINANCE-01"
        )


def check(name, condition):
    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")
        raise AssertionError(name)


def run_tests():
    app = FulfilmentModel()

    print("\nASSIGNMENT 2 - VALIDATION RESULTS\n")

    # T1: Two customers compete for the last unit
    first = app.place_order("O-101", "C-01", "LAPTOP", 1)
    second = app.place_order("O-102", "C-02", "LAPTOP", 1)

    check("T1 - Only one customer gets the last unit",
          first[0] and not second[0] and app.stock["LAPTOP"] == 0)

    # T2: Duplicate payment callback
    p1 = app.payment_callback("O-101", "TEST-GATEWAY", "EV-001", True)
    p2 = app.payment_callback("O-101", "TEST-GATEWAY", "EV-001", True)

    check("T2 - Duplicate payment callback has one effect",
          p1[0] and p2[0] and len(app.payment_events) == 1)

    # T3: Refund failure and retry
    app.refunds["R-101"] = Refund("R-101", "O-101", 500.00)
    denied = app.approve_refund("R-101", "support_agent", "SUP-01")
    approved = app.approve_refund("R-101", "finance_reviewer", "FIN-01")
    failed = app.execute_refund("R-101", False)
    retried = app.execute_refund("R-101", True)

    check("T3 - Refund requires finance approval and supports retry",
          not denied[0] and approved[0] and not failed[0]
          and retried[0]
          and app.refunds["R-101"].status == "Executed")

    # T4: Dispatch before payment/picking must fail
    app.orders["O-103"] = Order("O-103", "C-03", 1)
    rejected = app.dispatch("O-103")

    check("T4 - Dispatch without payment and picking is rejected",
          not rejected[0])

    # Complete valid pick and dispatch for O-101
    app.confirm_pick("O-101", "picker")
    dispatched = app.dispatch("O-101")

    check("T4B - Paid and picked order can be dispatched",
          dispatched[0])

    # T5: Courier synchronization can be retried
    failed_sync = app.sync_courier("O-101", False)
    retry_sync = app.sync_courier("O-101", True)

    check("T5 - Courier synchronization retry succeeds",
          not failed_sync[0] and retry_sync[0])

    # T6: Cross-customer access is rejected
    allowed = app.view_order("O-101", "C-01", "customer")
    denied_access = app.view_order("O-101", "C-99", "customer")

    check("T6 - Customer cannot access another customer's order",
          allowed[0] and not denied_access[0])

    # T7: Duplicate offline scanner event is applied once
    scan1 = app.receive_scanner_event("SCANNER-1", "SCAN-001", "LAPTOP", 2)
    scan2 = app.receive_scanner_event("SCANNER-1", "SCAN-001", "LAPTOP", 2)

    check("T7 - Replayed scanner event is deduplicated",
          scan1[0] and scan2[0] and app.stock["LAPTOP"] == 2)

    # T8: Twelve regions can have versioned local policies
    for number in range(1, 13):
        app.set_regional_policy(
            f"REGION-{number}", 1, 0.05, 50.0, 1000.0
        )

    check("T8 - Twelve regional policies are stored",
          len(app.regional_policies) == 12)

    # T9: Offline approval must be checked by server role
    app.refunds["R-102"] = Refund("R-102", "O-101", 250.00)
    offline_denied = app.validate_queued_approval(
        "R-102", "APPROVE", "support_agent"
    )
    offline_approved = app.validate_queued_approval(
        "R-102", "APPROVE", "finance_reviewer"
    )

    check("T9 - Queued refund approval is server-validated",
          not offline_denied[0] and offline_approved[0])

    print("\nAll synthetic model checks completed.")
    print("Audit events recorded:", len(app.audit_log))
    print("Payments recorded:", len(app.payment_events))
    print("Regional policies:", len(app.regional_policies))
    print("\nNOTE: These are in-memory rule checks, not production tests.")


if __name__ == "__main__":
    run_tests()
