from docutils.nodes import title

from odoo import http


class Offers(http.Controller):

    @http.route('/offers/', auth="public", type="json",website='true')
    def get_offers_json(self):
        offers = http.request.env['test_module.offers'].search_read([])
        for i in range(len(offers)):
            offer_data = http.request.env['test_module.offer_benefits'].browse(offers[i].get('benefits')).read()
            offers[i]['benefits'] = [data.get('benefit_title') for data in offer_data]
        return offers

