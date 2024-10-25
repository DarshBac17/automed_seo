from odoo import http
from odoo.http import request


class WebsiteVersion(http.Controller):
    @http.route(['/website/version/save'], type='json', auth="user", website=True)
    def save_version(self, **kwargs):
        name = kwargs.get('name')
        description = kwargs.get('description')
        page_id = kwargs.get('page_id')
        url = page_id.split('/')[-1]
        page = request.env['website.page'].search([('url', '=', f'/{url}')], limit=1)
        view = request.env['automated_seo.view'].search([('website_page_id', '=', page.id)], limit=1)


        # page_id = page.id
        if not name or not page_id:
            return {'error': 'Missing required fields'}

        # page = request.env['website.page'].browse(int(page_id))
        if not page.exists():
            return {'error': 'Page not found'}

        version = request.env['website.page.version'].create({
            'name': name,
            'description': description,
            'page_id': page.id,
            'view_arch': page.view_id.arch,
            'view_id':view.id,
            'user_id': request.env.user.id
        })

        return {
            'success': True,
            'version_id': version.id
        }