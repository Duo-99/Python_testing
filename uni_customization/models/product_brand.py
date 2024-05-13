# -*- coding: utf-8 -*
from odoo import api, fields, models

class ProductBrand(models.Model):
    _name = "product.brand"
    name = fields.Char(string="Name")
