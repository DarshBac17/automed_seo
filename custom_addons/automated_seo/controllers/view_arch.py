from odoo import http
from odoo.http import request, Response
import logging
_logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup


class WebsiteAutoSaveController(http.Controller):
    @http.route('/website/autosave_content', type='json', auth='user', methods=['POST'])
    def autosave_content(self, html_content):
        """
        Handles auto-save requests, parses the HTML content to extract view information,
        and fetches the corresponding `arch` field of the view.
        """
        # Log the received content for debugging
        # print("Received HTML Content:\n", html_content)

        try:
            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Attempt to find an element with a `data-oe-id` attribute
            editable = soup.find(attrs={'data-oe-model':'ir.ui.view'})
            if not editable:
                return {'status': 'error', 'message': 'No view found in the HTML content'}

            # Extract the view ID
            view_id = int(editable['data-oe-id'])


            # Fetch the view record from the database
            view_record = request.env['ir.ui.view'].sudo().browse(view_id)
            if not view_record.exists():
                return {'status': 'error', 'message': f'View with ID {view_id} does not exist'}



            attrs_to_delete = [attr for attr in editable.attrs if attr not in ['class', 'id']]

            # Now safely delete the attributes
            for attr in attrs_to_delete:

                del editable[attr]

            editable['class'].remove('o_editable')

            # Log the `arch` field of the view

            arch_soup = BeautifulSoup(view_record.arch, 'html.parser')

            t_call_layout = arch_soup.find('t', {'t-call': 'website.layout'})
            # Extract the first <div> inside <t>
            div_inside_t = t_call_layout.find('div') if t_call_layout else None

            div_inside_t.replace_with(editable)



            # Convert the updated BeautifulSoup object back to a string
            updated_arch = str(arch_soup.prettify())

            # Update the 'arch' field of the view record
            view_record.write({'arch': updated_arch})

            return {
                'status': 'success',
                'message': 'View information fetched and updated successfully',
                'view_id': view_id,
                'arch': updated_arch,
            }
        except Exception as e:
            print("got error", e)
            # Handle any unexpected errors
            request.env.cr.rollback()
            return {'status': 'error', 'message': str(e)}


class ViewController(http.Controller):
    @http.route('/automated_seo/get_page_view_id', type='json', auth="user", website=True)
    def get_page_view_id(self, path=None, **kwargs):
        try:
            if not path:
                return {'view_id': False, 'error': 'No path provided'}

            domain = [('url', '=', path)]
            page = request.env['website.page'].sudo().search(domain, limit=1)

            if page:
                view_id = page.view_id.page_id.id
                _logger.info(f"Found view_id: {view_id} for path: {path}")
                return {'view_id': view_id}
            else:
                _logger.warning(f"No page found for path: {path}")
                return {'view_id': False, 'error': 'Page not found'}

        except Exception as e:
            _logger.error(f"Error getting page view_id: {str(e)}")
            return {'view_id': False, 'error': str(e)}