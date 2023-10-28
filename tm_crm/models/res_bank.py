# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


# Banco
class Bank(models.Model):
    _inherit = 'res.bank'

    sucursal = fields.Char(string="Sucursal", placeholder="Número de la sucursal")
    provincia_id = fields.Many2one('res.country.state', string="Provincia")
    municipio_id = fields.Many2one('tm.municipio', string="Municipio")

    @api.constrains('sucursal')
    def _check(self):
        for record in self:
            if record.sucursal and not record.sucursal.replace(' ', '').isdigit():
                raise ValidationError("El campo 'Sucursal' debe tener solo números.")


# Cuenta bancaria
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    # no_cuenta es el campo acc_number
    # titular es el campo: partner_id / acc_holder_name: es nombre titular en caso que sea diferente al puesto partner_id
    partner_id = fields.Many2one('res.partner', string='Account Holder', required=False)
    no_transt = fields.Char(string='Número Transt')
    proveedor_id = fields.Many2one('tm.proveedor')