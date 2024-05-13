from odoo import models, fields, api

class Location(models.Model):
    _inherit = 'stock.location'

    is_reorder_location = fields.Boolean('Is Reorder Location')

