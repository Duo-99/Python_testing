
from odoo import api,fields,models

class City(models.Model):
    _name = "city"
    name = fields.Char(string="Name")
    state_id =fields.Many2one('state',string="State")

