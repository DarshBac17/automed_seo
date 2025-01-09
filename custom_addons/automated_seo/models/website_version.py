from email.policy import default
# from multiprocessing.managers import view_type

from odoo import models, fields, api
from odoo.addons.test_convert.tests.test_env import record
from odoo.exceptions import UserError
import json


class WebsitePageVersion(models.Model):
    _name = 'website.page.version'
    _description = 'Website Page Version'
    _order = 'create_date desc'

    name = fields.Char('Version Name',compute='_compute_version_number', store=True)
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
    change = fields.Selection([
        # ('major_change', 'Major Changes'),
        ('minor_change', 'Minor Changes'),
        ('patch_change', 'Patch Changes'),
    ], string="Change")

    stage = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('stage', 'Stage'),
        ('publish', 'Publish'),
    ], string="Stage", default="draft", tracking=True)

    major_version = fields.Integer('Major Version', default=1)
    minor_version = fields.Integer('Minor Version', default=0)
    patch_version = fields.Integer('Patch Version', default=0)
    header_title = fields.Char(string="Title")
    header_description = fields.Text(string="page description")
    # header_description = fields.Text(string="Title")
    selected_filename = fields.Char(string="Selected file name")
    # One-to-Many relationship: A page can have multiple metadata entries
    header_metadata_ids = fields.One2many(
        'automated_seo.page_header_metadata',
        'view_version_id',
        string="Metadata",
        ondelete='cascade'  # This ensures child records are deleted when the parent is deleted
    )

    header_link_ids = fields.One2many(
        'automated_seo.page_header_link',
        'view_version_id',
        string="Links",
        ondelete='cascade'  # This ensures child records are deleted when the parent is deleted
    )
    prev_version = fields.Many2one('website.page.version', string='Previous Version')
    
    @api.depends('major_version', 'minor_version', 'patch_version')
    def _compute_version_number(self):
        for record in self:
            record.name = f"v{record.major_version}.{record.minor_version}.{record.patch_version}"

    def action_version(self):
        id =self.env.context.get('id', 'Unknown')
        view_id = self.env.context.get('view_id')
        current_version = self.env['website.page.version'].search(
            ['&', ('status', '=', True), ('view_id', '=', view_id)], limit=1)
        view = self.env['automated_seo.view'].search([('id','=',current_version.view_id.id)])

        if current_version:
            current_version.status = False
            current_version.stage = view.stage

        active_version  = self.env['website.page.version'].search([('id','=',id)],limit=1)

        if active_version:
            active_version.status = True

            view.parse_html = active_version.parse_html if active_version.parse_html else None

            view.page_id.arch_db = active_version.view_arch if active_version.view_arch else None

            view.parse_html_filename = active_version.parse_html_filename   if active_version.parse_html_filename else None

            view.parse_html_binary = active_version.parse_html_binary if active_version.parse_html_binary else None

            view.publish = active_version.publish if active_version.publish else False

            view.header_title = active_version.header_title

            view.header_description = active_version.header_description

            view.stage = active_version.stage
            # Unlink header_metadata_ids from view without deleting them
            if view.header_metadata_ids :
                view.header_metadata_ids.write({'view_id': False})
            if view.header_link_ids:
                view.header_link_ids.write({'view_id': False})

            # Update header_metadata_ids in active_version to point to the current view
            if active_version.header_metadata_ids:
                active_version.header_metadata_ids.write({'view_id': view.id})

            if view.header_link_ids:
                view.header_link_ids.write({'view_id': view.id})




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
    def create(self, vals):
        if not vals.get('view_id'):
            raise UserError('View ID is required to create a version')
        seo_view = self.env['automated_seo.view'].search([('id','=',vals['view_id'])])
        latest_version = self.env['website.page.version'].search([
            ('view_id', '=', seo_view.id)
        ], order='create_date DESC', limit=1)
        previous_version = self.env['website.page.version'].search(
            ['&', ('status', '=', True), ('view_id', '=', seo_view.id)])
        view_arch = vals.get('view_arch') if vals.get('view_arch') else seo_view.website_page_id.arch_db if seo_view.website_page_id else False

        # Set initial version numbers
        if not latest_version and not vals.get('selected_filename'):
            # First version: v1.0.0
            vals.update({
                'major_version': 1,
                'minor_version': 0,
                'patch_version': 0
            })
        else:
            if vals.get('status'):
                if previous_version:
                    previous_version.write({
                        'status': False,
                        'stage': seo_view.stage
                    })
                seo_view.page_id.arch_db = view_arch if view_arch else None
                seo_view.stage = 'in_progress'
                seo_view.publish = False
                seo_view.parse_html_filename = None
                seo_view.parse_html_binary = None
                seo_view.parse_html = None

            change_type = vals.get('change')
            if not change_type:
                max_major_version = self.env['website.page.version'].search([('view_id','=',seo_view.id)], order='major_version desc', limit=1)
                vals.update({
                    'major_version': max_major_version.major_version + 1,
                    'minor_version': 0,
                    'patch_version': 0
                })

            else:
                if change_type == 'minor_change':
                    vals.update({
                        'major_version': previous_version.major_version,
                        'minor_version': previous_version.minor_version + 1,
                        'patch_version': 0
                    })

                else:
                    # Regular minor change
                    vals.update({
                        'major_version': previous_version.major_version,
                        'minor_version': previous_version.minor_version,
                        'patch_version': previous_version.patch_version + 1
                    })

        vals.update({
            'page_id': seo_view.website_page_id.id,
            'view_arch': view_arch,
            'user_id': self.env.user.id,
            'header_title' : seo_view.header_title,
            'header_description' : seo_view.header_description,
            'stage' : seo_view.stage
        })


        record = super(WebsitePageVersion, self).create(vals)
        if not record.view_id.selected_filename and not record.view_id.header_metadata_ids:
            record.create_default_version_metadata(record)

        previous_version.header_metadata_ids.write({'view_id': False})
        previous_version.header_link_ids.write({'view_id': False})

        return record


    def create_default_version_metadata(self, record):
        if not record.view_id.header_metadata_ids:
            default_metadata = [
                {
                    'property': 'og:title',
                    'content': f'{record.header_title}',
                    'view_id': record.view_id.id,
                    'view_version_id': record.id
                },
                {
                    'property': 'og:description',
                    'content': 'Default page description',
                    'view_id': record.view_id.id,
                    'view_version_id': record.id
                },
                {
                    'property': 'og:image',
                    'content': '<?php echo BASE_URL_IMAGE; ?>main/img/og/DEFAULT_PAGE_IMAGE.jpg',
                    'view_id': record.view_id.id,
                    'view_version_id': record.id
                },
                {
                    'property': 'og:url',
                    'content': f'<?php echo BASE_URL; ?>{record.view_id.name}',
                    'view_id': record.view_id.id,
                    'view_version_id': record.id
                }
            ]

            self.env['automated_seo.page_header_metadata'].create(default_metadata)

            self.env['automated_seo.page_header_link'].create({
                'view_id' : record.view_id.id,
                'css_link' : "//cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.css",
                'view_version_id': record.id
            })




    def action_create_version(self):

        unpublish =self.env.context.get('unpublish')
        self.ensure_one()
        if not self.view_id:
            raise UserError('View ID is required to create a version')

        current_version = self.search([
            ('status', '=', True),
            ('view_id', '=', self.view_id.id)
        ], limit=1)

        if unpublish:
            current_version.status = False
            current_version.publish = True

        self.status = True
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
