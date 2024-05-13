from odoo import api,fields,models
from odoo.tools import float_is_zero, float_compare, float_round

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    remark = fields.Text(string="Remark")

    imp_code = fields.Char(string='IMP Code')


    @api.onchange('product_id')
    def set_code(self):
        self.imp_code = self.product_id.imp_code


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    stock_received = fields.Float("Stock(%)", compute="compute_stock_received")
    total_qty_received = fields.Float()
    total_product_qty = fields.Float()
    need_to_bill = fields.Float("NeedToBILL%", compute="compute_need_to_bill")
    amount_billed = fields.Monetary()



    @api.depends('order_line.invoice_lines.price_subtotal', 'amount_total')
    def compute_need_to_bill(self):
        for order in self:
            order.amount_billed = 0.00
            for line in order.order_line.invoice_lines:
                order.amount_billed += line.price_subtotal
            if order.amount_total > 0:
                order.need_to_bill = (1 - (order.amount_billed) / order.amount_total) * 100
            else:
                order.need_to_bill = 100.00

    @api.depends('order_line.qty_received', 'order_line.product_qty', 'order_line')
    def compute_stock_received(self):
        for order in self:
            order.total_qty_received = 0.00
            order.total_product_qty = 0.00

            for line in order.order_line:
                order.total_qty_received += line.qty_received
                order.total_product_qty += line.product_qty

            if order.total_product_qty > 0.00:
                order.stock_received = (1 - (order.total_qty_received or 0.0) / order.total_product_qty) * 100
            else:
                order.stock_received = 100.0

    delivery_status = fields.Selection([
        ('no', 'Nothing to Delivery'),
        ('to deli', 'Waiting Delivery'),
        ('done', 'Fully Delivery'),
    ], string='Delivery Status', store=True, compute='cpt_deli_status',)

    @api.depends('state','picking_ids.state')
    def cpt_deli_status(self):
        for line in self:
            if line.state == 'draft':
                line.delivery_status = 'no'
            elif line.state == 'sent':
                line.delivery_status = 'no'
            elif line.state == 'purchase':
                line.delivery_status = 'no'
                for pk_line in line.picking_ids:
                    if pk_line.state not in ['done', 'cancel']:
                        line.delivery_status = 'to deli'
                        break
                    elif pk_line.state == 'done':
                        line.delivery_status = 'done'
            else:
                line.delivery_status = 'done'




