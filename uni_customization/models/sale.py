from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    quo_date = fields.Datetime("Quo Date", compute="compute_quo_date", store=True)
    sale_order_lines = fields.One2many('sale.order.line', 'order_id', string='Sale Orders Lines')
    inv_date_list = fields.Char('Invoice Dates', compute='cpt_inv_date_list')
    # stock_deli = fields.Float("Stock(%)", compute="compute_stock_deli")
    total_qty_delivered = fields.Float()
    total_product_uom_qty = fields.Float()
    # need_to_inv = fields.Float("NeedToINV%", compute="compute_need_to_inv")
    amount_invoiced = fields.Monetary()
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")
    state = fields.Selection(selection_add=[
        ('request_approve', 'Request Approve'),
        ('approve', 'Approve'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('sale_return', 'Sales Return')
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    permit_edit_approve = fields.Boolean('Permit Sale Order Edit', compute='edit_button_permission')
    edit_hide = fields.Html(string='CSS', sanitize=False, compute='_compute_edit_hide', store=False)
    team_members = fields.Many2many('res.partner', string="Team Members")

    def edit_button_permission(self):
        self.permit_edit_approve = False
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        for order in self:
            if user.so_edit_approve == True:
                order.permit_edit_approve = True
            else:
                order.permit_edit_approve = False

    def button_sale_return(self):
        if self.state == 'sale':
            self.write({'state': 'sale_return'})

    def button_set_saleorder(self):
        for order in self:
            order.write({'state': 'sale'})

    def button_request_approve(self):
        if self.state == 'sale':
            self.write({'state': 'request_approve'})

    def button_confirm_approve(self):
        if self.state == 'request_approve':
            self.write({'state': 'approve'})

    @api.depends('state')
    def _compute_edit_hide(self):
        for record in self:
            if record.state in ['sale', 'request_approve']:
                record.edit_hide = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.edit_hide = False

    # @api.depends('order_line.invoice_lines.price_subtotal', 'amount_total')
    # def compute_need_to_inv(self):
    #     for order in self:
    #         order.amount_invoiced = 0.00
    #         for line in order.order_line.invoice_lines:
    #             order.amount_invoiced += line.price_subtotal
    #         if order.state not in ['sale_return']:
    #             if order.amount_total > 0:
    #                 order.need_to_inv = (1 - (order.amount_invoiced or 0.0) / order.amount_total) * 100
    #             else:
    #                 order.need_to_inv = 100.0
    #         else:
    #             order.need_to_inv = 0.0

    # @api.depends('order_line.qty_delivered', 'order_line.product_uom_qty', 'order_line')
    # def compute_stock_deli(self):
    #     for order in self:
    #         order.total_qty_delivered = 0.00
    #         order.total_product_uom_qty = 0.00

    #         for line in order.order_line:
    #             order.total_qty_delivered += line.qty_delivered
    #             order.total_product_uom_qty += line.product_uom_qty
    #         if order.state not in ['sale_return']:
    #             if order.total_product_uom_qty > 0:
    #                 order.stock_deli = (1 - (order.total_qty_delivered or 0.0) / order.total_product_uom_qty) * 100
    #             else:
    #                 order.stock_deli = 100.0
    #         else:
    #             order.stock_deli = 0.0

    delivery_status = fields.Selection([
        ('no', 'Nothing to Delivery'),
        ('to deli', 'Waiting Delivery'),
        ('done', 'Fully Delivery'),
    ], string='Delivery Status', store=True, compute='cpt_deli_status', )

    @api.depends('state', 'picking_ids.state')
    def cpt_deli_status(self):
        for line in self:
            if line.state == 'draft':
                line.delivery_status = 'no'
            elif line.state == 'sent':
                line.delivery_status = 'no'
            elif line.state == 'sale':
                line.delivery_status = 'no'
                for pk_line in line.picking_ids:
                    if pk_line.state not in ['done', 'cancel']:
                        line.delivery_status = 'to deli'
                        break
                    elif pk_line.state == 'done':
                        line.delivery_status = 'done'
            else:
                line.delivery_status = 'done'

    def cpt_inv_date_list(self):
        for line in self:
            if line.invoice_status == 'invoiced':
                bb = ''
                for i in line.invoice_ids:
                    if i.state == 'posted':
                        yy = datetime.strptime(str(i.invoice_date), '%Y-%m-%d').strftime('%Y')
                        mm = datetime.strptime(str(i.invoice_date), '%Y-%m-%d').strftime('%m')
                        dd = datetime.strptime(str(i.invoice_date), '%Y-%m-%d').strftime('%d')
                        cc = mm + '/' + dd + '/' + yy + ','
                        bb = bb + cc
                line.inv_date_list = bb
            else:
                line.inv_date_list = ''

    @api.depends('date_order', 'state')
    def compute_quo_date(self):
        for line in self:
            if line.state == 'draft':
                line.quo_date = line.date_order



    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder,self)._prepare_invoice()
        invoice_vals['pricelist_id'] = self.pricelist_id
        invoice_vals.update({'team_members':self.team_members})
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    remark = fields.Text(string="Remark")
    disc_note = fields.Char(string="Disc Note")
    spec_note = fields.Text(string="Specification Features")
    serial_no = fields.Char(string="No", compute="compute_line_count")
    product_brand = fields.Many2one("product.brand", related="product_id.product_brand")

    def compute_line_count(self):
        for line in self:
            no = 0
            line.serial_no = no
            for l in line.order_id.order_line:
                no += 1
                l.serial_no = no
        # line_num = 1
        # if self.order_id:
        #     current_rec = self.order_id.browse(self.order_id.ids[0])
        #     for line in current_rec.order_line:
        #         line.serial_no = line_num
        #         line_num += 1
        # else:
        #     self.serial_no = '-'

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({'remark': self.remark})
        res.update({'disc_note': self.disc_note})

        return res

    # 
