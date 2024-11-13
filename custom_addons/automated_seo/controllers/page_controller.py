from odoo import http
from odoo.http import request

class PageController(http.Controller):
    @http.route('/website/get_page_id', type='json', auth="public", website=True)
    def get_page_id(self):
        page = request.env['website.page'].search([('url', '=', request.httprequest.path)], limit=1)
        return {
            'page_id': page.id if page else None,
        }
