from odoo import http
from odoo.http import request, Response
import logging
_logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup
from ..models.ftp_setup import transfer_file_via_scp
import  os
from odoo.exceptions import UserError


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

    @http.route('/website/update_stage_server', type='json', auth='user', methods=['POST'])
    def update_stage_server(self, view_id):
        view = request.env['ir.ui.view'].sudo().search([('id', '=', view_id)], limit=1)
        if not view:
            return {'status': 'error', 'message': 'View not found'}
        seo_view = request.env['automated_seo.view'].sudo().search([('page_id', '=', view.id)], limit=1)        
        if seo_view.validate_header():
            seo_view.action_compile_button()
            selected_file_version = None
            if seo_view.selected_filename:
                base_name, ext = os.path.splitext(seo_view.selected_filename.name)
                selected_file_version = f'{base_name}_{seo_view.active_version.name}.{ext}'

            page_name = f'{selected_file_version}' if selected_file_version else f"{seo_view.name}_{seo_view.active_version.name}.php"

            upload_success = transfer_file_via_scp(
                page_name=page_name,
                file_data=seo_view.parse_html_binary
            )
            if upload_success:
                seo_view.message_post(body=f"{page_name} file successfully uploaded to staging server.")
                seo_view.active_version.write({
                    'stage_url': f"https://automatedseo.bacancy.com/{page_name}"
                })
                seo_view.message_post(body="Record sent for review")

                seo_view.message_post(body="Record moved to the done approved")
            else:
                seo_view.message_post(body=f"{page_name} file upload failed.")
                return False
                # raise UserError(f"{page_name} file upload failed.")
        return True


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