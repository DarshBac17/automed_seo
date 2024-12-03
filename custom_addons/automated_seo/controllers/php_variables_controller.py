from odoo import http
from odoo.http import request

class PhpVariableController(http.Controller):
    class PhpVariableController(http.Controller):
        @http.route('/php-variables/', type='json', auth="public", methods=['GET'], website=True)
        def get_variable_names(self, **kwargs):

            try:
                # Retrieve offset and limit from query parameters, default to 0 and 10
                offset = int(kwargs.get('offset', 0))
                limit = int(kwargs.get('limit', 10))
            except ValueError:
                return request.make_response(
                    '{"error": "Invalid offset or limit value"}',
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            # Fetch the variable records with pagination
            variables = request.env['automated_seo.php_variables'].search([], offset=offset, limit=limit)

            # Extract only the names of the variables
            variable_names = variables.mapped('name')

            # Prepare response
            response_data = {
                'variable_names': variable_names,
                'pagination': {
                    'offset': offset,
                    'limit': limit,
                    'total': request.env['automated_seo.php_variables'].search_count([]),
                }
            }

            return request.make_response(
                request.jsonify(response_data),
                headers=[('Content-Type', 'application/json')]
            )