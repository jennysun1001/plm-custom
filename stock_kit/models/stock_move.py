from odoo import _, models
from odoo.tools.float_utils import float_is_zero, float_round
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _compute_kit_quantities(self, product_id, kit_qty, kit_bom, filters):
        """ Computes the quantity delivered or received when a kit is sold or purchased.
        A ratio 'qty_processed/qty_needed' is computed for each component, and the lowest one is kept
        to define the kit's quantity delivered or received.
        :param product_id: The kit itself a.k.a. the finished product
        :param kit_qty: The quantity from the order line
        :param kit_bom: The kit's BoM
        :param filters: Dict of lambda expression to define the moves to consider and the ones to ignore
        :return: The quantity delivered or received
        """
        qty_ratios = []
        boms, bom_sub_lines = kit_bom.explode(product_id, kit_qty)
        for bom_line, bom_line_data in bom_sub_lines:
            # skip service since we never deliver them
            if bom_line.product_id.type == 'service':
                continue
            if float_is_zero(bom_line_data['qty'], precision_rounding=bom_line.product_uom_id.rounding):
                # As BoMs allow components with 0 qty, a.k.a. optionnal components, we simply skip those
                # to avoid a division by zero.
                continue
            bom_line_moves = self.filtered(lambda m: m.bom_line_id == bom_line)
            if bom_line_moves:
                # We compute the quantities needed of each components to make one kit.
                # Then, we collect every relevant moves related to a specific component
                # to know how many are considered delivered.
                uom_qty_per_kit = bom_line_data['qty'] / bom_line_data['original_qty']
                qty_per_kit = bom_line.product_uom_id._compute_quantity(uom_qty_per_kit, bom_line.product_id.uom_id, round=False)
                if not qty_per_kit:
                    continue
                incoming_moves = bom_line_moves.filtered(filters['incoming_moves'])
                outgoing_moves = bom_line_moves.filtered(filters['outgoing_moves'])
                qty_processed = sum(incoming_moves.mapped('product_qty')) - sum(outgoing_moves.mapped('product_qty'))
                # We compute a ratio to know how many kits we can produce with this quantity of that specific component
                qty_ratios= qty_processed / qty_per_kit            
            else:
                return 0.0
        return qty_ratios
