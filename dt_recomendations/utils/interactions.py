# dt_recommendations/utils/interactions.py

import frappe
from frappe.utils import now_datetime

WEIGHTS = {
    "view": 1,
    "search_click": 2,
    "wishlist": 3,
    "purchase_intent": 4,
    "purchase": 5
}

def log_interaction(user, product, interaction_type="wishlist", source="webshop",session_id=None):
    if not user or not product:
        return
    doc = frappe.get_doc({
        "doctype": "Product Interaction",
        "user": user,
        "product": product,
        "interaction_type": interaction_type,
        "weight": WEIGHTS.get(interaction_type, 1),
        "timestamp": now_datetime(),
        "source": source,
        "session_id": session_id
    })

    doc.insert(ignore_permissions=True)

    frappe.db.commit()