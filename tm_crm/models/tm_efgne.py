# -*- coding: utf-8 -*-

from odoo import fields, models


class TMEfgne(models.Model):
    _inherit = 'tm.datos'
    _name = 'tm.efgne'
    _description = 'Empresa o forma de gestión no estatal.'

    partner_ids = fields.One2many('res.partner', 'efgne_id', string='Clientes', help='Seleccione el cliente')
