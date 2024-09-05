from odoo import http


class Offers(http.Controller):

    @http.route('/offers/', auth="public", type="json", methods=['POST'])
    def get_offers(self):
        offers = http.request.env['test_module.offers'].search_read(
            [],
            ['title', 'description', 'benefits.benefit_title', 'benefits.benefit_description']
        )
        return offers
