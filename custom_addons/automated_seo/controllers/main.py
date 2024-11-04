from odoo import http
from odoo.http import request
from bs4 import BeautifulSoup

class WebsiteVersion(http.Controller):
    @http.route(['/website/version/save'], type='json', auth="user", website=True)
    def save_version(self, **kwargs):
        try:
            name = kwargs.get('name')
            description = kwargs.get('description')
            page_id = kwargs.get('page_id')
            current_arch = kwargs.get('current_arch')

            url = page_id.split('?')[0]  # Remove query parameters
            url = url.split('#')[0]  # Remove hash
            url = url.split('/')[-1] or ''  # Get the last part of the URL

            # Find the page
            domain = [('url', 'in', ['/' + url, url])]
            if request.env['website.page.version'].search([('name','=',name)]):
                return {'error': f' the page is already prest'}

            page = request.env['website.page'].search(domain, limit=1)
            if not page:
                return {'error': f'Page not found for URL: {url}'}

            # Find the view
            view = request.env['automated_seo.view'].search([
                ('website_page_id', '=', page.id)
            ], limit=1)

            if not view:
                return {'error': 'Associated view not found'}

            template_name = f"website.{url}" if url else "website.page"
            soup = BeautifulSoup(current_arch, 'html.parser')
            section = soup.find('main')
            if section:
                section.unwrap()
            wrap_div = soup.find('div', id='wrap')
            if wrap_div:
                wrap_div.attrs = {
                    'id': 'wrap',
                    'class': 'oe_structure oe_empty'
                }
                for element in wrap_div.find_all(recursive=True):
                    if 'class' in element.attrs:
                        classes = element['class']
                        classes = [c for c in classes if c not in ['o_editable', 'o_dirty']]
                        if classes:
                            element['class'] = classes
                        else:
                            del element['class']
            wrap_content = soup.prettify()
            formatted_arch = f'''<t t-name="{template_name}">
                <t t-call="website.layout">
                    {wrap_content}
                </t>
            </t>'''

            if not all([name, page_id, current_arch]):
                return {'error': 'Missing required fields'}
            version = request.env['website.page.version'].create({
                'name': name,
                'description': description,
                'page_id': page.id,
                'view_arch': formatted_arch,
                'view_id': view.id,
                'user_id': request.env.user.id
            })

            return {
                'success': True,
                'version_id': version.id
            }

        except Exception as e:
            # _logger.exception("Error saving website version")
            return {'error': str(e)}
