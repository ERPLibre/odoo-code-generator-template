from odoo import _, api, models, fields


class Test(models.Model):
    _name = "test"
    _description = "test"

    name = fields.Char()
