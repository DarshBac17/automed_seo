from odoo import http
from odoo.http import request

class QwebDemo(http.Controller):
    @http.route('/qweb_demo/get_data', type='json', auth='public', website=True)
    def get_data(self):
        # Replace this with your actual data fetching logic
        print("==================get_datacall")
        return [{
            'name': 'Hetul',
            'value': '25',
        } ,{
            'name': 'darsh',
            'value': '21',

        }]