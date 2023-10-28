# -*- coding: utf-8 -*-

from odoo import fields, models


class Currency(models.Model):
    _inherit = 'res.currency'

    # siglas -> name /moneda ->currency_unit_label
    country_ids = fields.Many2many(comodel_name='res.country', relation='tm_currency_country_rel',
                                       column1='currency_id', column2='country_id', string='País')
