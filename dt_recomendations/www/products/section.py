import frappe

from dt_recomendations.recommender.engine import resolve_section, map_to_website_items

def get_context(context):
    section_id = frappe.form_dict.get("section_id")
    value = frappe.form_dict.get("value")  # for category

    # 🔥 map section_id → config
    section = build_section_config(section_id, value)

    item_codes = resolve_section(section)
    items = map_to_website_items(item_codes)

    context.items = items
    titles = {
        "trending_now": "Trending Now",
        "best_sellers": "Best Sellers",
        "for_you": "Recommended For You"
    }

    context.title = titles.get(section_id, value or "Products")

    return context


def build_section_config(section_id, value=None):
    base = {
        "trending_now": {"source": "trending", "limit": 20},
        "best_sellers": {"source": "best_sellers", "limit": 20},
        "for_you": {"source": "recommended", "limit": 20},
    }

    if section_id == "category":
        print(f"Building config for category: {value}")
        return {
            "section_id": "category",
            "source": "category",
            "value": value,
            "limit": 20
        }

    return {
        "section_id": section_id,
        **base.get(section_id, {})
    }