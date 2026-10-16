# dt_recomendations/recommender/ranking.py

import frappe

from frappe.utils import add_days, now_datetime


def calculate_product_rankings(days=90):
    """
    Calculate product rankings from recent Product Interaction records
    and persist the scores to Website Item.ranking.

    Ranking is based on the sum of interaction weights within the
    configured time window.

    Returns a summary of the ranking update.
    """

    cutoff = add_days(now_datetime(), -days)

    # Aggregate interactions for the ranking window.
    results = frappe.db.sql(
        """
        SELECT
            product,
            SUM(weight) AS ranking,
            COUNT(*) AS interaction_count
        FROM `tabProduct Interaction`
        WHERE
            product IS NOT NULL
            AND product != ''
            AND timestamp >= %s
        GROUP BY product
        """,
        (cutoff,),
        as_dict=True,
    )

    # Map each product to its calculated score.
    scores = {
        row.product: float(row.ranking or 0)
        for row in results
    }

    # Retrieve all website items, including those without interactions.
    website_items = frappe.get_all(
        "Website Item",
        filters={"published": 1},
        fields=["name", "item_code", "ranking"],
    )

    updated = 0

    for website_item in website_items:
        score = scores.get(website_item.item_code, 0)

        current_score = float(website_item.ranking or 0)

        if current_score != score:
            frappe.db.set_value(
                "Website Item",
                website_item.name,
                "ranking",
                score,
                update_modified=False,
            )

            updated += 1

    return {
        "products_scored": len(scores),
        "website_items_processed": len(website_items),
        "website_items_updated": updated,
        "period_days": days,
    }