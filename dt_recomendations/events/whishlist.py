# dt_recommendations/events/wishlist.py
import json
from dt_recomendations.utils.interactions import log_interaction

def on_add(doc, method):
    log_interaction(
        user=doc.owner,
        product=doc.item_code or doc.product,
        interaction_type="wishlist",
        source="webshop"
    )
