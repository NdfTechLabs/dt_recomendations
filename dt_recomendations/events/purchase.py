# dt_recomendations/events/purchase.py

import json
import frappe
from dt_recomendations.utils.interactions import log_interaction


def get_user_from_invoice(doc):

    # 0. BEST: Customer → Portal Users
    portal_users = frappe.db.get_all(
        "Portal User",
        filters={"parent": doc.customer, "parenttype": "Customer"},
        fields=["user"]
    )

    for pu in portal_users:
        if frappe.db.exists("User", pu.user):
            return pu.user

    # 1. Direct email on invoice
    if doc.contact_email and frappe.db.exists("User", doc.contact_email):
        return doc.contact_email

    # 2. Customer email
    email = frappe.db.get_value("Customer", doc.customer, "email_id")
    if email and frappe.db.exists("User", email):
        return email

    # 3. Contact emails
    contacts = frappe.db.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": doc.customer,
            "parenttype": "Contact"
        },
        fields=["parent"]
    )

    for c in contacts:
        contact_doc = frappe.get_doc("Contact", c.parent)
        for e in contact_doc.email_ids:
            if frappe.db.exists("User", e.email_id):
                return e.email_id

    # 4. Fallback
    if doc.owner and frappe.db.exists("User", doc.owner):
        return doc.owner

    return None


def on_submit(doc, method):
    user = get_user_from_invoice(doc)
    # Skip if no user mapping
    if not user:
        return

    for item in doc.items:
        log_interaction(
            user=user,
            product=item.item_code,
            interaction_type="purchase",
            source="erp"
        )

def on_invoice_submit(doc, method):
    user = get_user_from_invoice(doc)

    if not user:
        return

    for item in doc.items:
        log_interaction(
            user=user,
            product=item.item_code,
            interaction_type="purchase_intent",
            source="erp"
        )

def on_payment_submit(doc, method):
    # Payment Entry references invoices
    for ref in doc.references:
        if ref.reference_doctype == "Sales Invoice":
            invoice = frappe.get_doc("Sales Invoice", ref.reference_name)
            user = get_user_from_invoice(invoice)
            print(user)
            if not user:
                continue

            for item in invoice.items:
                log_interaction(
                    user=user,
                    product=item.item_code,
                    interaction_type="purchase",
                    source="erp"
                )

def on_pos_invoice(doc, method):
    user = get_user_from_invoice(doc)

    if not user:
        return

    for item in doc.items:
        log_interaction(
            user=user,
            product=item.item_code,
            interaction_type="purchase",
            source="pos"
        )