# from docutils.nodes import status, version
# from jinja2.nodes import Tuple
# from odoo import http
# from odoo.http import request
# from odoo.addons.web.controllers.dataset import DataSet
#
# from automated_seo.odoo.tools import TEXT_URL_REGEX
#
#
# class CustomWebsiteVersionController(DataSet):
#     @http.route('/web/dataset/call_kw/website.page.version/read', type='json', auth='user', methods=['POST'])
#     def version_read(self, model, method, args, kwargs):
#         print("model===============",model)
#         print("calling the read url=============================",method)
#         print("calling the read url=============================",args)
#         print(kwargs)
#         # First, ensure user has necessary permissions
#         # if not request.env.user.has_group('base.group_user'):
#         #     return {'error': 'Access Denied'}
#         #
#         id = args[0]
#         # try:
#         #     # You can modify the read behavior here
#         #     # For example, add additional fields or filtering
#         if method == 'read' and len(id)==1:
#             print("insid=======e")
#             print(request.env['website.page.version'].search([('status', '=', True)], limit=1))
#             current_version = request.env['website.page.version'].search([('status', '=', True)], limit=1)
#             # if page:
#             #     print("inside")
#             #     page.status = False
#             age = request.env['website.page.version'].search([('status', '=', True)])
#             print("page is called",age)
#             print(id)
#             current_version= request.env['website.page.version'].search([('id', '=', id)])
#             versions = request.env['website.page.version'].search([]).read([])
#             print(versions)
#             result = {}
#             response = {
#             "jsonrpc": "2.0",
#             "id": 41,
#                 "result":[
#                         {
#                             "id": 2,
#                             "name": "v2",
#                             "description": "version 2",
#                             "user_id": [
#                                 2,
#                                 "Administrator"
#                             ],
#                             "create_date": "2024-10-25 06:27:13",
#                             "write_date": "2024-10-25 06:33:14",
#                             "status": False
#                         },
#                         {
#                             "id": 1,
#                             "name": "v1",
#                             "description": "version1",
#                             "user_id": [
#                                 2,
#                                 "Administrator"
#                             ],
#                             "create_date": "2024-10-25 06:26:55",
#                             "write_date": "2024-10-25 06:26:55",
#                             "status": True
#                         }
#                     ]
#                 }
#         result = [
#             {
#                 "id": 2,
#                 "name": "v2",
#                 "description": "version 2",
#                 "user_id": [
#                     2,
#                     "Administrator"
#                 ],
#                 "create_date": "2024-10-25 06:27:13",
#                 "write_date": "2024-10-25 06:33:14",
#                 "status": False
#             },
#             {
#                 "id": 1,
#                 "name": "v1",
#                 "description": "version1",
#                 "user_id": [
#                     2,
#                     "Administrator"
#                 ],
#                 "create_date": "2024-10-25 06:26:55",
#                 "write_date": "2024-10-25 06:26:55",
#                 "status": True
#             }
#         ]
#         print(result)
#     # "result": [
#     #     {
#     #         "id": 2,
#     #         "name": "v2",
#     #         "description": "version 2",
#     #         "user_id": [
#     #             2,
#     #             "Administrator"
#     #         ],
#     #         "create_date": "2024-10-25 06:27:13",
#     #         "write_date": "2024-10-25 06:33:14",
#     #         "status": false
#     #     },
#     #     {
#     #         "id": 1,
#     #         "name": "v1",
#     #         "description": "version1",
#     #         "user_id": [
#     #             2,
#     #             "Administrator"
#     #         ],
#     #         "create_date": "2024-10-25 06:26:55",
#     #         "write_date": "2024-10-25 06:26:55",
#     #         "status": false
#     #     }
#     # ]
# # }
#
#
#     #         # Get the original records
#         #         records = request.env[model].browse(args[0])
#         #
#         #         # You can modify kwargs to add more fields or conditions
#         #         kwargs['fields'] = kwargs.get('fields', []) + ['your_custom_field']
#         #
#         #         # Perform the read operation with your modifications
#         #         result = records.read(**kwargs)
#         #
#         #         # Add any additional processing here
#         #         for record in result:
#         #             record['custom_computed_field'] = 'Custom Value'
#         #
#         #         return result
#         #
#         # except Exception as e:
#         #     return {'error': str(e)}
#
#         # Fall back to original behavior if needed
#         print('=========================')
#         print(super(CustomWebsiteVersionController, self).call_kw(model, method, args, kwargs))
#         print('=========================')
#
#         return result