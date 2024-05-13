from odoo import models, fields, api


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    is_repair_pricelist = fields.Boolean(string="Repair Pricelist")


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    pricelist_remark = fields.Char(string="Remark", store=True)
