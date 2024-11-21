from odoo import http
from odoo.http import request
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
            print(f"Extracted View ID: {view_id}")

            # Fetch the view record from the database
            view_record = request.env['ir.ui.view'].sudo().browse(view_id)
            if not view_record.exists():
                return {'status': 'error', 'message': f'View with ID {view_id} does not exist'}

            print(editable.attrs)

            attrs_to_delete = [attr for attr in editable.attrs if attr not in ['class', 'id']]

            # Now safely delete the attributes
            for attr in attrs_to_delete:
                print("deleting..", attr)
                del editable[attr]

            editable['class'].remove('o_editable')

            # Log the `arch` field of the view
            print(editable)
            arch_soup = BeautifulSoup(view_record.arch, 'html.parser')

            t_call_layout = arch_soup.find('t', {'t-call': 'website.layout'})
            # Extract the first <div> inside <t>
            div_inside_t = t_call_layout.find('div') if t_call_layout else None

            div_inside_t.replace_with(editable)

            print(f"View Arch Field:\n{arch_soup}")

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
