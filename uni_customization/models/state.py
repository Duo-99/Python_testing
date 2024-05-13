from odoo import api,fields,models

class State(models.Model):
    _name = "state"
    name = fields.Char(string="Name")
    country_id=fields.Many2one('res.country',string="Country")

