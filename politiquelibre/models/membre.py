from odoo import _, api, fields, models


class Membre(models.Model):
    _name = 'membre'
    _description = 'Membre'

    name = fields.Char()

    email = fields.Char()

    password = fields.Char()

    pseudo = fields.Char()

    status = fields.Integer()
