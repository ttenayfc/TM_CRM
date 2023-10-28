# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TMOsde(models.Model):
    _inherit = 'tm.datos'
    _name = 'tm.osde'
    _description = 'Nomenclador de las OSDES'

    name = fields.Char(string='OSDE', help='Nombre del OSDE')
    organismo_id = fields.Many2one('tm.organismo', string='Organismo', help='Selecione el organismo al que pertenece.')

    @api.constrains('name')
    def _check(self):
        for record in self:
            if record.name and not record.name.replace(' ', '').isalpha():
                raise ValidationError("El campo 'OSDE' solo puede contener caracteres.")
