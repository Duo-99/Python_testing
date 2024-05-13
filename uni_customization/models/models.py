# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class uni_customization(models.Model):
#     _name = 'uni_customization.uni_customization'
#     _description = 'uni_customization.uni_customization'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
