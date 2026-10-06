# Copyright (c) 2026, NDF Tech Labs and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProductInteraction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		filter_data: DF.JSON | None
		interaction_type: DF.Literal["view", "wishlist", "purchase_intent", "purchase", "search_click", "catalog_view", "catalog_search", "catalog_filter"]
		is_guest: DF.Check
		name: DF.Int | None
		page_route: DF.Data | None
		product: DF.Link | None
		search_query: DF.Data | None
		session_id: DF.Data | None
		source: DF.Data | None
		timestamp: DF.Datetime | None
		user: DF.Link | None
		utm_campaign: DF.Link | None
		utm_content: DF.Data | None
		utm_data: DF.Data | None
		utm_medium: DF.Link | None
		utm_source: DF.Link | None
		visitor_id: DF.Data | None
		weight: DF.Float
	# end: auto-generated types

	pass
