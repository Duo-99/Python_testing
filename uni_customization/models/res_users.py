# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _

class Users(models.Model):
    _inherit = "res.users"

    so_edit_approve = fields.Boolean("SO Edit Approve")



