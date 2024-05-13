from odoo import models, fields, api
from collections import defaultdict
from odoo.tools import add, float_compare, frozendict, split_every

class StockLocationOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'
    stock_location_ids = fields.Many2many('stock.location', domain=[("is_reorder_location", "=", True)],
                                          string='Locations')
    qty_multilocation = fields.Float('On Hand', readonly=True, store=True, compute='_compute_qty')
    reorder_state = fields.Selection([
        ('no_order', 'No Order'),
        ('to_order', 'To Order'),
        ('to_promotion', 'To Promotion')], string='Status', copy=False, index=True, store=True, tracking=True,
        compute='_compute_reorder_state')

    @api.depends('qty_multilocation', 'product_min_qty', 'product_max_qty')
    def _compute_reorder_state(self):
        for order in self:
            if order.qty_multilocation < order.product_min_qty:
                order.reorder_state = 'to_order'
            elif order.qty_multilocation > order.product_max_qty:
                order.reorder_state = 'to_promotion'
            else:
                order.reorder_state = 'no_order'

    @api.depends('product_id', 'location_id', 'product_id.stock_move_ids', 'product_id.stock_move_ids.state',
                 'product_id.stock_move_ids.date', 'product_id.stock_move_ids.product_uom_qty', 'stock_location_ids')
    @api.onchange('stock_location_ids')
    def _compute_qty(self):
        for orderpoint in self:
            default_qty = super(StockLocationOrderpoint, orderpoint)._compute_qty()
            orderpoint.qty_multilocation = default_qty
            if orderpoint.stock_location_ids:
                for location in orderpoint.stock_location_ids:
                    location_qty = sum(stock.quantity for stock in self.env['stock.quant'].search([
                        ('location_id', '=', location.id),
                        ('product_id', '=', orderpoint.product_id.id),
                    ]))
                    orderpoint.qty_multilocation += location_qty






