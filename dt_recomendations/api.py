# dt_recommendations/api.py

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
def log_search_click(item_code: str, query:str|None=None):
    user = frappe.session.user

    if user == "Guest":
        return

    log_interaction(
        user=user,
        product=item_code,
        interaction_type="search_click",
        source="search"
    )

@frappe.whitelist(allow_guest=True)
def get_dynamic_sections(config: str|dict):
    config = json.loads(config) if isinstance(config, str) else config

    output = {}

    for section in config.get("sections", []):
        section_id = section.get("section_id")

        item_codes = resolve_section(section)

        website_items = map_to_website_items(item_codes)
        # 4. Render item_card HTML
        html = render_template(
            "dt_recomendations/templates/includes/dynamic_item_cards.html",
            {
                "items": website_items,  # full list
                "is_featured": 0,
                "is_full_width": True,
                "align": "Center"
            }
        )

        output[section_id] = html

    return output

