# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TMDatos(models.AbstractModel):
    _name = 'tm.datos'
    _description = 'Clase abstracta para llevar datos genericos.'

    name = fields.Char(string='Nombre', help="Escriba el nombre.")
    direccion = fields.Char(string='Dirección', help="Escriba la dirección.")
    telefono = fields.Char(string="Teléfono", size=30)
    celular = fields.Char(string="Celular", size=15)
    correo = fields.Char(string="Correo electrónico")
    provincia_id = fields.Many2one('res.country.state', string="Provincia")
    municipio_id = fields.Many2one('tm.municipio', string="Municipio")

    @api.constrains('telefono', 'celular')
    def _check(self):
        for record in self:
            if record.telefono and not record.telefono.replace(' ', '').replace('+', '').replace('-', '').isdigit():
                raise ValidationError("El campo 'Teléfono' solo puede contener números.")
            if record.celular and not record.celular.replace(' ', '').replace('+', '').replace('-', '').isdigit():
                raise ValidationError("El campo 'Celular' solo puede contener números.")
