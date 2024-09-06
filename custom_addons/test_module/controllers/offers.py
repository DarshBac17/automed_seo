from crypt import methods

# from docutils.nodes import title
#
# from odoo import http
#
#
# class Offers(http.Controller):
#
#     @http.route('/offers/', auth="public", type="json",website='true')
#     def get_offers_json(self):
#         offers = http.request.env['test_module.offers'].search_read([])
#         for i in range(len(offers)):
#             offer_data = http.request.env['test_module.offer_benefits'].browse(offers[i].get('benefits')).read()
#             offers[i]['benefits'] = [data.get('benefit_title') for data in offer_data]
#         return offers
#
#     @http.route('/offers/save', auth="public", type="json", website='true')
#     def get_offers_save(self):
#         offers = http.request.env['test_module.offers'].search_read([])
#         for i in range(len(offers)):
#             offer_data = http.request.env['test_module.offer_benefits'].browse(offers[i].get('benefits')).read()
#             offers[i]['benefits'] = [data.get('benefit_title') for data in offer_data]
#         return offers
    # @http.route('/offers/save', auth="public", type="json", website='true',methods = ['POST'])
    # def get_offers_save(self):
    #     # here i want to save change in database
    #     return offers
from odoo import http

class Offers(http.Controller):

    @http.route('/offers/', auth="public", type="json", website=True)
    def get_offers_json(self):
        offers = http.request.env['test_module.offers'].search_read([])
        for i in range(len(offers)):
            offer_data = http.request.env['test_module.offer_benefits'].browse(offers[i].get('benefits')).read()
            offers[i]['benefits'] = [data.get('benefit_title') for data in offer_data]
        return offers

    @http.route('/offers/save', auth="public", type="json", website=True, methods=['POST'])
    def save_offer_changes(self, **post):
        offer_id = post.get('id')
        title = post.get('title')
        description = post.get('description')
        benefits = post.get('benefits', [])


        offer = http.request.env['test_module.offers'].browse(int(offer_id))
        if not offer.exists():
            return {'error': 'Offer not found'}

        # Update offer details
        offer.write({
            'title': title,
            'description': description,
        })

            # Update benefits
        existing_benefits = offer.benefits
        for i, benefit_title in enumerate(benefits):
            if i < len(existing_benefits):
                existing_benefits[i].write({'benefit_title': benefit_title})
            else:
                http.request.env['test_module.offer_benefits'].create({
                    'offer_id': offer.id,
                    'benefit_title': benefit_title,
                })

        # Remove extra benefits if any
        if len(benefits) < len(existing_benefits):
            existing_benefits[len(benefits):].unlink()

        return {'success': True, 'message': 'Offer updated successfully'}