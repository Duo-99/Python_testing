from odoo import api,fields,models
class ResPartner(models.Model):
    _inherit = "res.partner"
    city_id = fields.Many2one("city",string="City")
    state = fields.Many2one("state", string="State")
    township = fields.Many2one("township", string="Township")
    code =fields.Char(string="Code")
    short = fields.Char(string="Short")

    # so_edit_approve = fields.Boolean("SO Edit Approve")

 
