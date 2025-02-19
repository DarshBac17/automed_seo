# from odoo import http
# from odoo.http import request
#
#
# class PhpVariableController(http.Controller):
#     @http.route('/php-variables/', type='json', auth="public", methods=['GET'], website=True)
#     def get_variable_names(self, **kwargs):
#
#         try:
#             # Retrieve offset and limit from query parameters, default to 0 and 10
#             offset = int(kwargs.get('offset', 0))
#             limit = int(kwargs.get('limit', 10))
#             search = kwargs.get('search', '')
#
#             domain = []
#             if search:
#                 domain.append(('name', 'ilike', search))
#
#         except ValueError:
#             return request.make_response(
#                 '{"error": "Invalid offset or limit value"}',
#                 headers=[('Content-Type', 'application/json')],
#                 status=400
#             )
#
#         # Fetch the variable records with pagination
#         # variables = request.env['automated_seo.php_variables'].search([], offset=offset, limit=limit)
#         variables = request.env['automated_seo.php_variables'].search(
#             domain, offset=offset, limit=limit
#         )
#         # Extract only the names of the variables
#         variable_names = variables.mapped('name')
#
#         # Prepare response
#         response_data = {
#             'variable_names': variable_names,
#             'pagination': {
#                 'offset': offset,
#                 'limit': limit,
#                 'total': request.env['automated_seo.php_variables'].search_count([]),
#             }
#         }
#         print("===============")
#         print(response_data)
#         print("===============")
#
#         return request.make_response(
#             request.jsonify(response_data),
#             headers=[('Content-Type', 'application/json')]
#         )

import json
from odoo import http
from odoo.http import request

class PhpVariableController(http.Controller):
    @http.route('/php-variables/', type='http', auth="public", methods=['GET'], website=True)
    def get_variable_names(self, **kwargs):
        try:
            offset = int(kwargs.get('offset', 0))
            limit = int(kwargs.get('limit', 5))
            is_const_var = kwargs.get('isConstVar') == 'true'

            search = kwargs.get('search', '')

            # Build domain
            domain = []

            domain.append(('is_constant','=',is_const_var))
            if search:
                domain.append(('name', 'ilike', search))

            # Fetch variables
            variables = request.env['automated_seo.php_variables'].search(
                domain, offset=offset, limit=limit,
            )

            # Prepare response data
            response_data = {
                'variable_names': variables.mapped('name'),
                'pagination': {
                    'offset': offset,
                    'limit': limit,
                    'total': request.env['automated_seo.php_variables'].search_count(domain),
                }
            }

            # Return HTTP response with JSON
            return request.make_response(
                json.dumps(response_data),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET'),
                ]
            )

        except ValueError as e:
            error_response = {
                'error': 'Invalid parameters',
                'message': str(e)
            }
            return request.make_response(
                json.dumps(error_response),
                headers=[('Content-Type', 'application/json')],
                status=400
            )
        except Exception as e:
            error_response = {
                'error': 'Server error',
                'message': str(e)
            }
            return request.make_response(
                json.dumps(error_response),
                headers=[('Content-Type', 'application/json')],
                status=500
            )