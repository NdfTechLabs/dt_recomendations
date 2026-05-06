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

		interaction_type: DF.Literal["view", "wishlist", "purchase_intent", "purchase", "search_click"]
		name: DF.Int | None
		product: DF.Link
		session_id: DF.Data | None
		source: DF.Data | None
		timestamp: DF.Datetime | None
		user: DF.Link
		weight: DF.Float
	# end: auto-generated types

	pass
