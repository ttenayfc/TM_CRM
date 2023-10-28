# -*- coding: utf-8 -*-

from odoo import fields, models


class TMUEBDA(models.Model):
    _name = 'tm.uebda'
    _inherit = 'tm.datos'
    _description = 'Unidad empresarial de base (UEB) o dependencia autorizada.'

    partner_ids = fields.One2many('res.partner', 'uebda_id', string='Clientes', help='Seleccione el cliente')
