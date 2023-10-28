# -*- coding: utf-8 -*-

from odoo import models, fields


class Country(models.Model):
    _inherit = 'res.country'

    code = fields.Char(
        string='Country Code', size=3,
        help='The ISO country code in two chars. \nYou can use this field for quick search.')
    nacionalidad = fields.Char(string='Nacionalidad')
    siglas = fields.Char(string='Siglas')


class CountryState(models.Model):
    _inherit = 'res.country.state'

    municipio_ids = fields.One2many("tm.municipio", 'provincia_id', string="Municipios")


class TMMunicipio(models.Model):
    _name = 'tm.municipio'
    _description = 'Nomenclador de los municipios por provincias de Cuba.'

    name = fields.Char(string='Municipio')
    codigo = fields.Char(string='Código', size=5)
    provincia_id = fields.Many2one('res.country.state', string="Provincia")
