from odoo import api, fields, models

class Township(models.Model):
    _name = "township"
    name = fields.Char('Name')
    city_id =fields.Many2one('city',string="City")