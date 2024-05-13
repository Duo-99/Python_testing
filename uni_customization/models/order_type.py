from odoo import fields,models

class OrderType(models.Model):
    _name = "order.type"
    name = fields.Char(string="Name")


