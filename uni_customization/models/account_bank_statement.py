from odoo import api,fields,models,_

class inherit_bank_statement(models.Model):
    _inherit='account.bank.statement'
    _description='inherit'
    
    label = fields.Char(related='line_ids.payment_ref')