from odoo import models, fields, api
from odoo.tools import html2plaintext

class StockMove(models.Model):
    _inherit = "stock.move"
    remark = fields.Text(string="SO Remark", related="sale_line_id.remark",store=True)
    general_remark = fields.Text(string="Remark")

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()

        partners = self.mapped('partner_id')
        sale_line = self.mapped('sale_line_id')
        partner = len(partners) == 1 and partners.id or False
        res['note'] = sale_line.order_id.note or " "
        # for line in sale_line:
        #     res['remark'] = sale_line.order_id.note or " "
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # lot_id = fields.Many2one(
    #     'stock.production.lot', 'Lot/Serial Number',
    #     domain="[('available_to_choose','>', 0),('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)

    expir_date = fields.Datetime(related="lot_id.expiration_date",store=True)
    demand_qty = fields.Float(related="move_id.product_uom_qty", store=True)
    partner_id = fields.Many2one(related="picking_id.partner_id", string='Partner')

    source_ref = fields.Many2one('stock.picking', string='Source Reference', compute='_computed_source')

    @api.depends('reference')
    def _computed_source(self):
        for move in self:
            if move.reference:
                domain = [('name', '=', move.reference)]
                picking = self.env['stock.picking'].search(domain)
                move.source_ref = picking.id if picking else False


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    available_to_choose = fields.Boolean('Available', store=True, compute='_available')

    @api.depends('quant_ids', 'quant_ids.reserved_quantity', 'quant_ids.quantity', 'product_qty')
    def _available(self):
        for lot in self:
            if lot.product_qty <= 0:
                lot.available_to_choose = False
            elif lot.product_qty > 0:
                quants = lot.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
                for q in quants:
                    if q.quantity - q.reserved_quantity > 0:
                        lot.available_to_choose = True
                    elif q.quantity - q.reserved_quantity < 0:
                        lot.available_to_choose = False

    @api.onchange('product_qty')
    def _onchange_usage(self):
        if self.product_qty > 0:
            self.available_to_choose = True
        else:
            self.available_to_choose = False

class Picking(models.Model):
    _inherit = "stock.picking"
    note = fields.Html(string="Remark")
    plain_text = fields.Char(compute='_compute_plain_text', string='Note')

    @api.depends('note')
    def _compute_plain_text(self):
        for record in self:
            record.plain_text = html2plaintext(record.note)


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'
    
    ref = fields.Many2one('stock.picking',related='stock_move_id.picking_id',string='Reference')
    

