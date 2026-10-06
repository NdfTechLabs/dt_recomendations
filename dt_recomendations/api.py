# dt_recommendations/api.py

import hashlib
import json
from typing import Any

import frappe
from frappe.utils.jinja import render_template
from dt_recomendations.utils.interactions import log_interaction

# import original
from webshop.webshop.doctype.wishlist.wishlist import add_to_wishlist as original_add


from .recommender.engine import resolve_section, map_to_website_items

@frappe.whitelist()
def add_to_wishlist(item_code: str):
    # Call original logic first
    result = original_add(item_code)
    # Log interaction AFTER successful insert
    log_interaction(
        user=frappe.session.user,
        product=item_code,
        interaction_type="wishlist",
        source="webshop",
        session_id=frappe.local.session.sid if hasattr(frappe.local, "session") else None
    )

    return result


@frappe.whitelist(allow_guest=True)
@frappe.whitelist(allow_guest=True)
def log_catalog_interaction(
    action,
    query=None,
    filters=None,
):
    if isinstance(filters, str):
        filters = frappe.parse_json(filters)

    filters = filters or {}

    log_interaction(
        interaction_type=action,
        source="catalog",
        search_query=query,
        page_route="/catalog",
        filter_data=filters,
    )


@frappe.whitelist(allow_guest=True)
def log_search_click(item_code: str, query: str | None = None):
    if not item_code:
        return

    log_interaction(
        product=item_code,
        interaction_type="search_click",
        source="search",
        search_query=query,
    )

@frappe.whitelist(allow_guest=True)
def get_dynamic_sections(config: str | dict):
    config = json.loads(config) if isinstance(config, str) else config

    config_json = json.dumps(config, sort_keys=True)
    cache_key = "homepage_dynamic_sections:" + hashlib.md5(
        config_json.encode("utf-8")
    ).hexdigest()[:16]

    cached = frappe.cache().get_value(cache_key)

    if cached:
        return cached

    # Fetch Webshop Settings
    webshop_settings = frappe.get_single("Webshop Settings")

    settings = {
        "enabled": webshop_settings.enabled,
        "enable_wishlist": webshop_settings.enable_wishlist,
        "show_stock_availability": webshop_settings.show_stock_availability,
        "allow_items_not_in_stock": webshop_settings.allow_items_not_in_stock,
        "enable_checkout": webshop_settings.enable_checkout,
    }

    groups = []

    for section in config.get("sections", []):
        item_codes = resolve_section(section)
        website_items = map_to_website_items(item_codes)

        groups.append({
            "section_id": section.get("section_id"),
            "item_group": section.get("value"),
            "title": section.get("title"),
            "limit": section.get("limit", 6),
            "items": website_items,
        })

    response = {
        "settings": settings,
        "groups": groups,
    }
    frappe.cache().set_value(
        cache_key,
        response,
        expires_in_sec=300
    )
    return response

