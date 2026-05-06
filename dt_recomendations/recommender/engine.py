import json
import frappe

from frappe.query_builder.functions import Sum

def get_users_for_item(item_code):
    PI = frappe.qb.DocType("Product Interaction")

    query = (
        frappe.qb.from_(PI)
        .select(PI.user)
        .where(
            (PI.product == item_code)
            & (PI.interaction_type.isin(["wishlist", "purchase", "purchase_intent","view","search_click"]))
        )
        .distinct()
    )

    return [r.user for r in query.run(as_dict=True)]

def get_similar_products(item_code, limit=6):
    PI = frappe.qb.DocType("Product Interaction")

    # base item info
    base_item = frappe.get_value(
        "Item",
        item_code,
        ["item_group", "brand"],
        as_dict=True
    )

    # -------------------------------
    # 1. GLOBAL SIGNAL (flattened)
    # -------------------------------
    global_score = Sum(PI.weight).as_("global_score")

    global_query = (
        frappe.qb.from_(PI)
        .select(PI.product, global_score)
        .where(
            (PI.product != item_code)
            & (PI.interaction_type.isin([
                "wishlist", "purchase", "purchase_intent",
                "view", "search_click"
            ]))
        )
        .groupby(PI.product)
        .having(global_score > 5)
        .orderby(global_score, order=frappe.qb.desc)
        .limit(limit * 5)  # fetch extra for re-ranking
    )

    results = global_query.run(as_dict=True)

    if not results:
        return []

    # -------------------------------
    # 2. USER PERSONALIZATION (optional)
    # -------------------------------
    user_score_map = {}

    current_user = frappe.session.user

    if current_user and current_user != "Guest":
        user_results = (
            frappe.qb.from_(PI)
            .select(PI.product, Sum(PI.weight).as_("u_score"))
            .where(
                (PI.user == current_user)
                & (PI.product != item_code)
            )
            .groupby(PI.product)
        ).run(as_dict=True)

        user_score_map = {
            r.product: r.u_score for r in user_results
        }

    # -------------------------------
    # 3. PYTHON BOOSTING
    # -------------------------------
    boosted = []

    for r in results:
        item = frappe.get_value(
            "Item",
            r.product,
            ["item_group", "brand"],
            as_dict=True
        )

        boost = 0

        # content similarity
        if item and item.item_group == base_item.item_group:
            boost += 3

        if item and item.brand == base_item.brand:
            boost += 2

        # user personalization boost
        user_boost = user_score_map.get(r.product, 0) * 1.5

        final_score = r.global_score + boost + user_boost

        boosted.append((r.product, final_score))

    # -------------------------------
    # 4. SORT + LIMIT
    # -------------------------------
    boosted.sort(key=lambda x: x[1], reverse=True)

    return [p for p, _ in boosted[:limit]]


def get_similar_website_items(item_code, limit=6):
    item_codes = get_similar_products(item_code, limit=limit)

    if not item_codes:
        return []

    wi = frappe.qb.DocType("Website Item")

    query = (
        frappe.qb.from_(wi)
        .select(
            wi.item_code,
            wi.route,
            wi.web_item_name.as_("website_item_name"),
            wi.thumbnail.as_("website_item_thumbnail")
        )
        .where(
            (wi.item_code.isin(item_codes)) &
            (wi.published == 1)
        )
    )

    results = query.run(as_dict=True)

    # preserve ranking
    mapping = {r["item_code"]: r for r in results}

    return [mapping[c] for c in item_codes if c in mapping]


def get_homepage_groups(limit_per_group=6):
    return {
        "trending": get_trending_items(limit_per_group),
        "best_sellers": get_best_sellers(limit_per_group),
        "recommended": get_personalized_items(limit_per_group),
        "by_category": get_category_groups(limit_per_group)
    }

def get_trending_items(limit=6):
    PI = frappe.qb.DocType("Product Interaction")

    score = Sum(PI.weight).as_("score")

    query = (
        frappe.qb.from_(PI)
        .select(PI.product, score)
        .where(
            PI.interaction_type.isin([
                "view", "search_click", "wishlist", "purchase"
            ])
        )
        .groupby(PI.product)
        .orderby(score, order=frappe.qb.desc)
        .limit(limit)
    )

    results = query.run(as_dict=True)

    return [r.product for r in results]

def get_best_sellers(limit=6):
    PI = frappe.qb.DocType("Product Interaction")

    score = Sum(PI.weight).as_("score")

    query = (
        frappe.qb.from_(PI)
        .select(PI.product, score)
        .where(
            PI.interaction_type.isin([
                "purchase", "purchase_intent"
            ])
        )
        .groupby(PI.product)
        .orderby(score, order=frappe.qb.desc)
        .limit(limit)
    )

    return [r.product for r in query.run(as_dict=True)]

def get_personalized_items(limit=6):
    PI = frappe.qb.DocType("Product Interaction")

    current_user = frappe.session.user

    if not current_user or current_user == "Guest":
        return get_trending_items(limit)

    score = Sum(PI.weight).as_("score")

    query = (
        frappe.qb.from_(PI)
        .select(PI.product, score)
        .where(
            (PI.user == current_user)
        )
        .groupby(PI.product)
        .orderby(score, order=frappe.qb.desc)
        .limit(limit * 3)
    )

    results = query.run(as_dict=True)

    return [r.product for r in results[:limit]]

def get_category_groups(limit=4):
    PI = frappe.qb.DocType("Product Interaction")
    Item = frappe.qb.DocType("Item")

    score = Sum(PI.weight).as_("score")

    query = (
        frappe.qb.from_(PI)
        .join(Item)
        .on(PI.product == Item.name)
        .select(Item.item_group, PI.product, score)
        .groupby(Item.item_group, PI.product)
        .orderby(score, order=frappe.qb.desc)
    )

    results = query.run(as_dict=True)

    grouped = {}

    for r in results:
        group = r.item_group

        if group not in grouped:
            grouped[group] = []

        if len(grouped[group]) < limit:
            grouped[group].append(r.product)

    return grouped

def map_to_website_items(item_codes):
    if not item_codes:
        return []

    # 🔥 fetch only fields required by item_card macro
    results = frappe.get_all(
        "Website Item",
        filters={
            "item_code": ["in", item_codes],
            "published": 1
        },
        fields=[
            "item_code",
            "web_item_name",
            "route",
            "website_image",
            "item_group"
        ]
    )

    if not results:
        return []

    # 🔥 preserve ranking
    mapping = {r["item_code"]: r for r in results}

    ordered = [mapping[c] for c in item_codes if c in mapping]

    return ordered

def get_homepage_data():
    groups = get_homepage_groups()

    return {
        "trending": map_to_website_items(groups["trending"]),
        "best_sellers": map_to_website_items(groups["best_sellers"]),
        "recommended": map_to_website_items(groups["recommended"]),
        "by_category": {
            k: map_to_website_items(v)
            for k, v in groups["by_category"].items()
        }
    }

def get_items_for_category(category, limit=6):
    PI = frappe.qb.DocType("Product Interaction")
    Item = frappe.qb.DocType("Item")

    score = Sum(PI.weight).as_("score")

    query = (
        frappe.qb.from_(PI)
        .join(Item)
        .on(PI.product == Item.name)
        .select(PI.product, score)
        .where(Item.item_group == category)
        .groupby(PI.product)
        .orderby(score, order=frappe.qb.desc)
        .limit(limit)
    )

    results = query.run(as_dict=True)

    return [r.product for r in results]

def resolve_section(section, limit_override=None):
    source = section.get("source")
    limit = limit_override or section.get("limit", 6)

    if source == "trending":
        return get_trending_items(limit)

    elif source == "best_sellers":
        return get_best_sellers(limit)

    elif source == "recommended":
        return get_personalized_items(limit)

    elif source == "category":
        category = section.get("value")
        return get_items_for_category(category, limit)

    return []

def build_homepage_from_config(config):
    output = {}

    for section in config.get("sections", []):
        section_id = section.get("section_id")

        item_codes = resolve_section(section)

        output[section_id] = map_to_website_items(item_codes)

    return output