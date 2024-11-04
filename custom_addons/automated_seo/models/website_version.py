from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import UserError
import json


class WebsitePageVersion(models.Model):
    _name = 'website.page.version'
    _description = 'Website Page Version'
    _order = 'create_date desc'

    name = fields.Char('Version Name', required=True)
    description = fields.Text('Description')
    view_id =  fields.Many2one('automated_seo.view', string='View', required=True)
    page_id = fields.Many2one('website.page', string='Website Page', required=True)
    view_arch = fields.Text('Saved View Architecture', required=True)
    parse_html = fields.Text(string="Parse HTML")
    parse_html_binary = fields.Binary(string="Parsed HTML File", attachment=True)
    parse_html_filename = fields.Char(string="Parsed HTML Filename")
    user_id = fields.Many2one('res.users', string='Created by')
    status = fields.Boolean('Status',default=False)

    def action_version(self):

        id =self.env.context.get('id', 'Unknown')
        current_version  = self.env['website.page.version'].search([('status','=',True)],limit=1)
        if current_version:
            current_version.status = False
        active_version  = self.env['website.page.version'].search([('id','=',id)],limit=1)
        if active_version:
            active_version.status = True
            view = self.env['automated_seo.view'].search([('id','=',active_version.view_id.id)])


            view.parse_html = active_version.parse_html if active_version.parse_html else None

            view.page_id.arch_db = active_version.view_arch if active_version.view_arch else None

            view.parse_html_filename = active_version.parse_html_filename   if active_version.parse_html_filename else None

            view.parse_html_binary = active_version.parse_html_binary if active_version.parse_html_binary else None

    def action_download_html(self):
        """Download the parsed HTML file"""
        self.ensure_one()
        if not self.parse_html_binary:
            raise UserError('No HTML file available for download')

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=website.page.version&id=%s&field=parse_html_binary&filename_field=parse_html_filename&download=true' % (
                self.id),
            'target': 'self',
        }

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """Override to prevent form view from loading"""
        result = super(WebsitePageVersion, self).get_view(view_id, view_type, **options)
        if view_type == 'form':
            raise UserError('Form view is not available for you')
        return result

    def write(self,vals):
        return super(WebsitePageVersion, self).write(vals)
