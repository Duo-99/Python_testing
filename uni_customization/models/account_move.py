from odoo import api,fields,models,_
from odoo.tools import html2plaintext

class AccountMove(models.Model):
    _inherit = 'account.move'

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist',readonly=True)
    team_members = fields.Many2many('res.partner',readonly=True)

    team_id = fields.Many2one(
        'crm.team', string='Sales Team',
        readonly=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    plain_text = fields.Char(compute='_compute_plain_text', string='Terms And Conditions')

    @api.depends('narration')
    def _compute_plain_text(self):
        for record in self:
            record.plain_text = html2plaintext(record.narration)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    remark = fields.Text(string="Remark")
    disc_note =fields.Char(string="Disc Note")
    serial_no = fields.Char(string="No", compute="compute_line_count",store=True)
    @api.depends('move_id')
    def compute_line_count(self):
        for line in self:
            no = 0
            line.serial_no = no
            if line.move_id.move_type!='entry':
                for l in line.move_id.invoice_line_ids:
                    no += 1
                    l.serial_no = no
            else:
                serial_no='-'

    # @api.depends('move_id.invoice_line_ids')
    # def _get_line_numbers(self):
    #     for line in self:
    #         no = 0
    #         line.sr_no = no
    #         for l in line.move_id.invoice_line_ids:
    #             no += 1
    #             l.sr_no = no

