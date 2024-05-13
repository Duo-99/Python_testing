# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    alert_date = fields.Datetime(related='lot_id.alert_date', store=True, readonly=False)
    expiration_date = fields.Datetime(related='lot_id.expiration_date', store=True, readonly=False)
    adjustment_remark = fields.Char(string="Remark", store=True)

    parent_warehouse_path = fields.Char('Parent Warehouse Path', compute='_compute_parent_warehouse_path', store=True)

    @api.depends('location_id')
    def _compute_parent_warehouse_path(self):
        for quant in self:
            location = quant.location_id
            parent_path = []
            while location:
                if location.usage == 'internal':
                    warehouse = location.warehouse_id
                    if warehouse:
                        parent_path.append(warehouse.name)
                location = location.location_id
            quant.parent_warehouse_path = '/'.join(reversed(parent_path))

    @api.model
    def _get_inventory_fields_write(self):
        fields = super(StockQuant, self)._get_inventory_fields_write()
        return fields + ['adjustment_remark',]
