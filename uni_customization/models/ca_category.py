from odoo import fields,models

class CACategory(models.Model):
    _name = "ca.category"
    name = fields.Char(string="Name")


