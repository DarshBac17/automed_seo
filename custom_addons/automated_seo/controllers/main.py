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

            def clean_content(content):
                soup = BeautifulSoup(content, 'html.parser')

                # Find the <section> tag and unwrap it (remove the tag but keep its contents)
                section = soup.find('main')
                if section:
                    section.unwrap()
                # Find the wrap div
                wrap_div = soup.find('div', id='wrap')
                if wrap_div:
                    # Clean up the wrap div attributes
                    wrap_div.attrs = {
                        'id': 'wrap',
                        'class': 'oe_structure oe_empty'
                    }

                    # Remove editor-specific attributes and classes from all elements
                    for element in wrap_div.find_all(recursive=True):
                        # Remove data-* attributes
                        # attrs_to_remove = [attr for attr in element.attrs if attr.startswith('data-')]
                        # for attr in attrs_to_remove:
                        #     del element[attr]

                        # Clean up classes
                        if 'class' in element.attrs:
                            classes = element['class']
                            classes = [c for c in classes if c not in ['o_editable', 'o_dirty']]
                            if classes:
                                element['class'] = classes
                            else:
                                del element['class']

                    return str(wrap_div)
                return content

            # Extract and clean the wrap content
            wrap_content = current_arch
            if '<div id="wrap"' in current_arch:
                wrap_content = BeautifulSoup(clean_content(current_arch), 'html.parser').prettify()

            # Format the final arch content
            formatted_arch = f'''<t t-name="{template_name}">
                <t t-call="website.layout">
                    {wrap_content}
                </t>
            </t>'''

            if not all([name, page_id, current_arch]):
                # version = request.env['website.page.version'].search([('status','=',True)]).write({
                #     'view_arch': formatted_arch,
                # })
                return {'error': 'Missing required fields'}
            # else:
            # breakpoint()
            # Create version
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

# class WebsiteVersion(http.Controller):
#     @http.route(['/website/version/save'], type='json', auth="user", website=True)
#     def save_version(self, **kwargs):
#         name = kwargs.get('name')
#         description = kwargs.get('description')
#         page_id = kwargs.get('page_id')
#         current_arch = kwargs.get('current_arch')  # Get the unsaved content
#
#         url = page_id.split('/')[-1]
#         page = request.env['website.page'].search([('url', '=', f'/{url}')], limit=1)
#         view = request.env['automated_seo.view'].search([('website_page_id', '=', page.id)], limit=1)
#
#         if not name or not page_id or not current_arch:
#             return {'error': 'Missing required fields'}
#
#         if not page.exists():
#             return {'error': 'Page not found'}
#
#         version = request.env['website.page.version'].create({
#             'name': name,
#             'description': description,
#             'page_id': page.id,
#             'view_arch': current_arch,  # Use the unsaved content instead of page.view_id.arch
#             'view_id': view.id,
#             'user_id': request.env.user.id
#         })
#
#         return {
#             'success': True,
#             'version_id': version.id
#         }
# class WebsiteVersion(http.Controller):
#     @http.route(['/website/version/save'], type='json', auth="user", website=True)
#     def save_version(self, **kwargs):
#         name = kwargs.get('name')
#         description = kwargs.get('description')
#         page_id = kwargs.get('page_id')
#         url = page_id.split('/')[-1]
#         page = request.env['website.page'].search([('url', '=', f'/{url}')], limit=1)
#         view = request.env['automated_seo.view'].search([('website_page_id', '=', page.id)], limit=1)
#
#
#         # page_id = page.id
#         if not name or not page_id:
#             return {'error': 'Missing required fields'}
#
#         # page = request.env['website.page'].browse(int(page_id))
#         if not page.exists():
#             return {'error': 'Page not found'}
#
#         version = request.env['website.page.version'].create({
#             'name': name,
#             'description': description,
#             'page_id': page.id,
#             'view_arch': page.view_id.arch,
#             'view_id':view.id,
#             'user_id': request.env.user.id
#         })
#
#         return {
#             'success': True,
#             'version_id': version.id
#         }
