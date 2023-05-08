from odoo import _, api, fields, models


class Electeurs(models.Model):
    _name = "electeurs"
    _description = "Electeurs"

    name = fields.Char()

    a_jour = fields.Integer(
        string="A jour",
    )

    a_vote_2013 = fields.Integer(
        string="A vote 2013",
    )

    a_vote_2017 = fields.Integer(
        string="A vote 2017",
    )

    a_vote_2021 = fields.Integer(
        string="A vote 2021",
    )

    adresse_postal_cp = fields.Char(
        string="Adresse postal cp",
    )

    adresse_postal_ligne_deux = fields.Char(
        string="Adresse postal ligne deux",
    )

    adresse_postal_ligne_un = fields.Char(
        string="Adresse postal ligne un",
    )

    bva_2013 = fields.Integer()

    bva_2017 = fields.Integer()

    bva_2021 = fields.Integer()

    code_maj = fields.Char(
        string="Code maj",
    )

    code_municipale = fields.Char(
        string="Code municipale",
    )

    code_postal = fields.Char(
        string="Code postal",
    )

    courriel_electeur = fields.Char(
        string="Courriel electeur",
    )

    date_naissance = fields.Char(
        string="Date naissance",
    )

    designation = fields.Char()

    direction = fields.Char()

    generique = fields.Char()

    intention_election_2013 = fields.Char(
        string="Intention election 2013",
    )

    intention_election_2017 = fields.Char(
        string="Intention election 2017",
    )

    intention_election_2021 = fields.Char(
        string="Intention election 2021",
    )

    latitude = fields.Char()

    lien = fields.Char()

    longitude = fields.Char()

    no_appartement = fields.Char(
        string="No appartement",
    )

    no_appartement_suf = fields.Char(
        string="No appartement suf",
    )

    no_civique = fields.Char(
        string="No civique",
    )

    no_civique_suf = fields.Char(
        string="No civique suf",
    )

    no_electeur = fields.Char(
        string="No electeur",
    )

    no_lot = fields.Char(
        string="No lot",
    )

    no_quartier = fields.Integer(
        string="No quartier",
    )

    no_section = fields.Char(
        string="No section",
    )

    no_sequentiel = fields.Char(
        string="No sequentiel",
    )

    nom_electeur = fields.Char(
        string="Nom electeur",
    )

    nom_municipalite = fields.Char(
        string="Nom municipalite",
    )

    nom_quartier = fields.Char(
        string="Nom quartier",
    )

    note = fields.Text()

    note_ami = fields.Text(
        string="Note ami",
    )

    pas_contacter = fields.Integer(
        string="Pas contacter",
    )

    pas_contacter2 = fields.Integer(
        string="Pas contacter2",
    )

    prenom_electeur = fields.Char(
        string="Prenom electeur",
    )

    ramq = fields.Char()

    rue = fields.Char()

    scr = fields.Char()

    sexe = fields.Char()

    taxe_eau = fields.Integer(
        string="Taxe eau",
    )

    telephone_electeur = fields.Char(
        string="Telephone electeur",
    )

    telephone_electeur2 = fields.Char(string="Telephone electeur2")

    type = fields.Char()

    type_occupation = fields.Char(
        string="Type occupation",
    )

    vpa = fields.Char()

    year_sub = fields.Date(string="Year sub")
