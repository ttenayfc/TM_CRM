# -*- coding: utf-8 -*-
# from odoo import http


# class ./addons/custom/tmCrm(http.Controller):
#     @http.route('/./addons/custom/tm_crm/./addons/custom/tm_crm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/./addons/custom/tm_crm/./addons/custom/tm_crm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('./addons/custom/tm_crm.listing', {
#             'root': '/./addons/custom/tm_crm/./addons/custom/tm_crm',
#             'objects': http.request.env['./addons/custom/tm_crm../addons/custom/tm_crm'].search([]),
#         })

#     @http.route('/./addons/custom/tm_crm/./addons/custom/tm_crm/objects/<model("./addons/custom/tm_crm../addons/custom/tm_crm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('./addons/custom/tm_crm.object', {
#             'object': obj
#         })
