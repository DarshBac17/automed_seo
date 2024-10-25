from docutils.nodes import status
from jinja2.nodes import Tuple
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.dataset import DataSet

from automated_seo.odoo.tools import TEXT_URL_REGEX


class CustomWebsiteVersionController(DataSet):
    @http.route('/web/dataset/call_kw/website.page.version/read', type='json', auth='user', methods=['POST'])
    def version_read(self, model, method, args, kwargs):
        print("model===============",model)
        print("calling the read url=============================",method)
        print("calling the read url=============================",args[0])
        # First, ensure user has necessary permissions
        # if not request.env.user.has_group('base.group_user'):
        #     return {'error': 'Access Denied'}
        #
        id = args[0]
        # try:
        #     # You can modify the read behavior here
        #     # For example, add additional fields or filtering
        if method == 'read' and len(id)==1:
            print("insid=======e")
            print(request.env['website.page.version'].search([('status', '=', True)], limit=1))
            request.env['website.page.version'].search([('status', '=', True)], limit=1).write({
                'status':False
            })
            # if page:
            #     print("inside")
            #     page.status = False
            age = request.env['website.page.version'].search([('status', '=', True)])
            print("page is called",age)
            print(id)
            request.env['website.page.version'].search([('id', '=', id)]).write({
                'status':True
            })


    #         # Get the original records
        #         records = request.env[model].browse(args[0])
        #
        #         # You can modify kwargs to add more fields or conditions
        #         kwargs['fields'] = kwargs.get('fields', []) + ['your_custom_field']
        #
        #         # Perform the read operation with your modifications
        #         result = records.read(**kwargs)
        #
        #         # Add any additional processing here
        #         for record in result:
        #             record['custom_computed_field'] = 'Custom Value'
        #
        #         return result
        #
        # except Exception as e:
        #     return {'error': str(e)}

        # Fall back to original behavior if needed
        return super(CustomWebsiteVersionController, self).call_kw(model, method, args, kwargs)