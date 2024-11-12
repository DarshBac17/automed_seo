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
    publish = fields.Boolean('Publish',default=False)

    def action_version(self):

        id =self.env.context.get('id', 'Unknown')
        view_id = self.env.context.get('view_id')
        current_version = self.env['website.page.version'].search(
            ['&', ('status', '=', True), ('view_id', '=', view_id)], limit=1)

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

            view.publish = active_version.publish if active_version.publish else False

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
    def create(self,vals):
        print("======================================")
        if not vals.get('view_id'):
            raise UserError('View ID is required to create a version')
        seo_view = self.env['automated_seo.view'].browse(vals['view_id'])
        if self.env['website.page.version'].search(['&', ('name', '=', vals.get('name')), ('view_id', '=', seo_view.id)]):
            raise UserError("The version name is already present. Change the name of the version")
        previous_version = self.env['website.page.version'].search(['&',('status','=',True),('view_id','=',seo_view.id)])
        previous_version.write({
            'publish':True
        })
        vals.update({
            'page_id': seo_view.website_page_id.id,
            'view_arch': seo_view.website_page_id.arch_db if seo_view.website_page_id else False,
            'user_id': self.env.user.id,
        })

        return super(WebsitePageVersion, self).create(vals)
    def action_create_version(self):
        # self.write({'stage': 'in_progress'})
        self.ensure_one()
        if not self.view_id:
            raise UserError('View ID is required to create a version')

        # Deactivate current active version
        current_version = self.search([
            ('status', '=', True),
            ('view_id', '=', self.view_id.id)
        ], limit=1)

        if current_version:
            current_version.status = False

        # Set this as the active version
        self.status = True

        # Update the view with version data
        if self.view_id:
            self.view_id.write({
                'parse_html': self.parse_html,
                'parse_html_filename': self.parse_html_filename,
                'parse_html_binary': self.parse_html_binary,
                'stage': 'draft' ,
                'publish':False# Reset to draft after unpublishing
            })

            if self.view_id.website_page_id and self.view_arch:
                self.view_id.website_page_id.arch_db = self.view_arch

        self.view_id.message_post(body=f"Version '{self.name}' created and activated", message_type="comment")

        return {
            'type': 'ir.actions.act_window_close'
        }

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """Override to prevent form view from loading"""
        result = super(WebsitePageVersion, self).get_view(view_id, view_type, **options)
        form_view_ref = self.env.context.get('form_view_ref')
        if form_view_ref:
            return  result
        if view_type == 'form':
            raise UserError('Form view is not available for you')
        return result

    def write(self,vals):
        return super(WebsitePageVersion, self).write(vals)
