from odoo import http
from odoo.http import request

class BlogSnippetController(http.Controller):

    @http.route('/dynamic_blog_snippet', type='json', auth='public', website=True)
    def get_blogs(self):
        blogs = request.env['blog.snippet'].sudo().search([], limit=5)
        values = {
            'data_blogs': [{
                'title': blog.title,
                'content': blog.content,
                'image': blog.blog_image.decode('utf-8') if blog.blog_image else False,
            } for blog in blogs]
        }
        return request.env['ir.ui.view']._render_template('my_blog_snippet.dynamic_blog_snippet_template', values)