# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TMOrganismo(models.Model):
    _inherit = 'tm.datos'
    _name = 'tm.organismo'
    _description = 'Nomenclador organismos de Cuba.'

    name = fields.Char(string='Descripción', help='Descripción del organismo')
    codigo = fields.Char(string='Código', help='Escriba el código del organismo')
    osde_ids = fields.One2many('tm.osde', 'organismo_id', string='OSDE', help='Selecione el OSDE al que pertenece.')

    @api.constrains('name')
    def _check(self):
        for record in self:
            if record.name and not record.name.replace(' ', '').isalpha():
                raise ValidationError("El campo 'Descripción' solo puede contener caracteres.")
