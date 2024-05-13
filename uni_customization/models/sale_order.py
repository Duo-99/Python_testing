from odoo import models, fields, api
from odoo.tools import html2plaintext

class SaleInherit(models.Model):
    _inherit = 'sale.order'

    plain_text = fields.Char(compute='_compute_plain_text', string='Terms And Conditions')

    @api.depends('note')
    def _compute_plain_text(self):
        for record in self:
            record.plain_text = html2plaintext(record.note)
