from odoo import _, api, fields, models


class Enjeux(models.Model):
    _name = "enjeux"
    _description = "Enjeux"

    name = fields.Char()

    id_electeur = fields.Integer(
        string="Id electeur",
    )

    nom = fields.Char()
