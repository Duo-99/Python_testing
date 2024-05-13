from odoo import api, models, fields

class PeripheralDevice(models.Model):
    _name = "peripheral.device"

    peripheral_id = fields.Many2one("repair.order",string="Peripheral Device")
    model = fields.Char(string="Model")
    s_n = fields.Char(string="S_N")

class CalibrationDue(models.Model):
    _name = "calibration.due"

    calibration_id = fields.Many2one("repair.order")
    date = fields.Datetime(
        required=True
    )

class MsapmSchedule(models.Model):
    _name = "msapm.schedule"

    schedule_id=fields.Many2one(
       "repair.order"

    )
    date = fields.Datetime(required=True)

class ReplacedParts(models.Model):
    _name = "replaced.parts"

    replaced_parts_id = fields.Many2one(
     "repair.order"

    )
    date = fields.Datetime(required=True)
    description = fields.Char(string="Description")

class ClaimedParts(models.Model):
    _name = "claimed.parts"

    claimed_parts_id = fields.Many2one(
        "repair.order"

    )
    date = fields.Datetime(required=True)
    description = fields.Char(string="Description")
    attached_file = fields.Binary(string="File Attach")
















