# -*- coding: utf-8 -*-
{
    'name': "TM CRM",

    'summary': """Módulo CRM adecuado para TM""",

    'description': """
        Módulo que hereda las funcionalidades del modulo CRM de Odoo y adaptado a las necesidades de la empresa 
        Tecnomática Cuba.
    """,

    'author': "Yanett",
    'website': 'https://www.odoo.com/page/crm',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'contacts'],

    # always loaded
    'data': [
        'views/ir_actions_act_window.xml',
        'views/menu.xml',
        'views/res_partner_views.xml',
        'views/res_bank_views.xml',
        'views/tm_proveedor_views.xml',
        'views/tm_datos_views.xml',
        'security/ir_model_access.xml'  # puede ir en cualquier lugar
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
