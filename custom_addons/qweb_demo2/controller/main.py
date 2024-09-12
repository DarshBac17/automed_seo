from odoo import http
from odoo.http import request
# 
# class QwebDemo(http.Controller):
#     @http.route('/qweb_demo2', type='http', auth='public', website=True)
#     def qweb_demo(self):
#         some_model = request.env['sale.order'].search([])
#         data = {
#             'title': 'QWeb  Demo',
#             # 'message': 'demo!',
#             # 'integer':5,
#             # 'string': 'hetul',
#             # 'model':some_model
#         }
#         return request.render('qweb_demo.demo_template',data)
# 
# class AutomedSEO(http.Controller):
#     @http.route('/automed_seo', type='http', auth='public', website=True)
#     def qweb_demo(self):
#         print("================automed_seo")
#         data = {
#             'title': 'QWeb Demo',
#         }
#         return request.render('automed_seo.offer_template', data)

    # @http.route('/offers/', auth="public", type="http", website=True)
    # def get_offers_json(self):
    #     print("================get_offers_json")
    #     # offers = http.request.env['test_module.offers'].search([])
    #     # for i in range(len(offers)):
    #     #     offer_data = http.request.env['test_module.offer_benefits'].browse(offers[i].get('benefits')).read()
    #     #     offers[i]['benefits'] = [data.get('benefit_title') for data in offer_data]
    #     data = {
    #         'title': 'QWeb Demo'
    #     }
    #     return request.render('test_module.offers_dynamic_snippet',data)