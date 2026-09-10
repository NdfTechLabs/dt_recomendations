# dt_recommendations/overrides/website_item.py

from webshop.webshop.doctype.website_item.website_item import WebsiteItem
from dt_recomendations.utils.interactions import log_interaction
import frappe
from frappe.utils import now_datetime, add_to_date
from dt_recomendations.recommender.engine import get_similar_website_items


def viewed_recently(user, product):
    return frappe.db.exists("Product Interaction", {
        "user": user,
        "product": product,
        "interaction_type": "view",
        "timestamp": (">", add_to_date(now_datetime(), minutes=-30))
    })


class CustomWebsiteItem(WebsiteItem):

    def get_context(self, context):
        # keep EVERYTHING original
        context = super().get_context(context)

        # -------------------------------
        # 1. VIEW LOGGING (unchanged)
        # -------------------------------
        if frappe.session.user != "Guest":
            if not viewed_recently(frappe.session.user, self.item_code):
                log_interaction(
                    user=frappe.session.user,
                    product=self.item_code,
                    interaction_type="view",
                    source="web",
                    session_id=frappe.local.session.sid if hasattr(frappe.local, "session") else None
                )
        # -------------------------------
        # 2. RECOMMENDATIONS (NEW)
        # -------------------------------
        try:
            settings = context.shopping_cart.cart_settings
            if settings and settings.enable_recommendations:
                recommended = get_similar_website_items(self.item_code, limit=6)

                # attach to context
                context.recommended_items = recommended

        except Exception as e:
            # fail silently (don’t break page)
            frappe.log_error(frappe.get_traceback(), "Recommendation Error")
            context.recommended_items = []
        return context