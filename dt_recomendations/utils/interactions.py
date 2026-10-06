# dt_recomendations/utils/interactions.py

import frappe
from frappe.utils import now_datetime


WEIGHTS = {
    "view": 1,
    "search": 1,
    "search_click": 2,
    "wishlist": 3,
    "purchase_intent": 4,
    "purchase": 5,
}


def get_visitor_id():
    """Get the persistent visitor ID from the visitor cookie."""
    if not frappe.request:
        return None

    return frappe.request.cookies.get("visitor_id")


def get_session_id():
    """Get the current Frappe session ID."""
    if hasattr(frappe.local, "session") and frappe.local.session:
        return frappe.local.session.sid

    return None


def get_user():
    """Return the authenticated user or None for guests."""
    user = frappe.session.user

    if not user or user == "Guest":
        return None

    return user

def resolve_link_value(doctype, value):
    """
    Resolve a UTM value to an existing document.

    Returns None when no value exists.
    Creates the document when necessary.
    """

    if not value:
        return None

    if frappe.db.exists(doctype, value):
        return value

    doc = frappe.get_doc({
        "doctype": doctype,
        "name": value,
    })

    doc.insert(ignore_permissions=True)

    return doc.name

def get_utm_data():
    """Read and resolve persisted UTM information from cookies."""

    if not frappe.request:
        return {}

    cookies = frappe.request.cookies

    return {
        "utm_source": resolve_link_value(
            "UTM Source",
            cookies.get("utm_source"),
        ),

        "utm_medium": resolve_link_value(
            "UTM Medium",
            cookies.get("utm_medium"),
        ),

        "utm_campaign": resolve_link_value(
            "UTM Campaign",
            cookies.get("utm_campaign"),
        ),

        "utm_content": cookies.get("utm_content"),

        "utm_data": cookies.get("utm_term"),
    }

def get_page_route():
    """Return the current request path where available."""

    if not frappe.request:
        return None

    return frappe.request.path


def log_interaction(
    user=None,
    product=None,
    interaction_type="view",
    source="webshop",
    session_id=None,
    visitor_id=None,
    search_query=None,
    page_route=None,
    filter_data=None,
):
    """
    Log a complete Product Interaction.

    Event handlers only need to provide event-specific data.
    Identity, visitor, session, UTM and request metadata
    are completed here.
    """

    # ----------------------------------------
    # Identity
    # ----------------------------------------

    if user == "Guest":
        user = None

    if user is None:
        user = get_user()

    is_guest = not bool(user)

    # ----------------------------------------
    # Visitor / session
    # ----------------------------------------

    if visitor_id is None:
        visitor_id = get_visitor_id()

    if session_id is None:
        session_id = get_session_id()

    # ----------------------------------------
    # Request metadata
    # ----------------------------------------

    if page_route is None:
        page_route = get_page_route()

    # ----------------------------------------
    # UTM attribution
    # ----------------------------------------

    utm = get_utm_data()

    # ----------------------------------------
    # Build interaction
    # ----------------------------------------

    doc = frappe.get_doc({
        "doctype": "Product Interaction",

        # Identity
        "user": user,
        "visitor_id": visitor_id,
        "session_id": session_id,
        "is_guest": 1 if is_guest else 0,

        # Event
        "product": product,
        "interaction_type": interaction_type,
        "weight": WEIGHTS.get(interaction_type, 1),

        # Metadata
        "timestamp": now_datetime(),
        "source": source,
        "search_query": search_query,
        "page_route": page_route,
        "filter_data": filter_data,
        # Attribution
        "utm_source": utm.get("utm_source"),
        "utm_medium": utm.get("utm_medium"),
        "utm_campaign": utm.get("utm_campaign"),
        "utm_content": utm.get("utm_content"),
        "utm_data": utm.get("utm_data"),
    })

    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return doc