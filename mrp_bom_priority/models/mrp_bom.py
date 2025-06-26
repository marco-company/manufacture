# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    # Column Section
    priority = fields.Selection(
        [("0", "Low"), ("1", "Normal"), ("2", "High"), ("3", "Very High")],
        default="0",
        help="Helps prioritize BoM.",
    )

    @api.model
    def _bom_find(self, products, picking_type=None, company_id=False, bom_type=False):
        """Override native function to change order"""
        bom_by_product = defaultdict(lambda: self.env["mrp.bom"])
        products = products.filtered(lambda p: p.type != "service")
        if not products:
            return bom_by_product
        domain = self._bom_find_domain(
            products,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )

        # Change here
        order = "priority DESC, sequence, product_id, id"

        if len(products) == 1:
            bom = self.search(domain, order=order, limit=1)
            if bom:
                bom_by_product[products] = bom
            return bom_by_product

        boms = self.search(domain, order=order)

        products_ids = set(products.ids)
        for bom in boms:
            products_implies = bom.product_id or bom.product_tmpl_id.product_variant_ids
            for product in products_implies:
                if product.id in products_ids and product not in bom_by_product:
                    bom_by_product[product] = bom

        return bom_by_product
