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

    name = fields.Char('Version Name',compute='_compute_version_name', store=True)
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
    publish_at = fields.Datetime('Publish At')
    change = fields.Selection([
        ('major_change', 'Major Changes'),
        ('minor_change', 'Minor Changes'),
        ('patch_change', 'Patch Changes'),
    ], string="Change", default='major_change')
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
        string="Metadata"
    )

    header_link_ids = fields.One2many(
        'automated_seo.page_header_link',
        'view_version_id',
        string="Links",
        ondelete='cascade'  # This ensures child records are deleted when the parent is deleted
    )
    # prev_version = fields.Many2one('website.page.version', string='Previous Version')
    base_version = fields.Many2one(
        'website.page.version',
        domain="[('view_id', '=', context.get('default_view_id'))]",
        string='Base Version')

    # @api.depends('major_version', 'minor_version', 'patch_version')
    # def _compute_version_number(self):
    #     for record in self:
    #         record.name = f"v{record.major_version}.{record.minor_version}.{record.patch_version}"

    @api.depends('name')
    def _compute_version_name(self):

        self.ensure_one()
        # if self.base_version:
        #     self.name = self.base_version.name

        if self.change:
            if self.change == 'major_change' :
                max_major_version = self.env['website.page.version'].search([('view_id', '=', self.view_id.id)],order='major_version desc', limit=1)
                self.major_version = max_major_version.major_version + 1
            elif self.change == 'minor_change':
                self.major_version = self.base_version.major_version
                self.minor_version = self.base_version.minor_version + 1
            elif self.change == 'patch_change':
                self.major_version = self.base_version.major_version
                self.minor_version = self.base_version.minor_version
                self.patch_version = self.base_version.patch_version + 1
            self.name = f"v{self.major_version}.{self.minor_version}.{self.patch_version}"

    @api.onchange('base_version')
    def _onchange_base_version(self):
        self.ensure_one()
        self._compute_version_name()

    @api.onchange('change')
    def _onchange_change(self):
        self.ensure_one()
        self._compute_version_name()


    def action_version(self):

        id =self.env.context.get('id', 'Unknown')
        view_id = self.env.context.get('view_id')
        current_version = self.env['website.page.version'].search(
            ['&', ('status', '=', True), ('view_id', '=', view_id)], limit=1)
        view = self.env['automated_seo.view'].search([('id','=',current_version.view_id.id)])

        if view.has_edit_permission:
            if current_version:
                current_version.status = False
                current_version.stage = view.stage
                current_version.header_title = view.header_title
                current_version.header_description = view.header_description

            active_version  = self.env['website.page.version'].search([('id','=',id)],limit=1)

            if active_version:
                active_version.status = True
                view.write({
                    'active_version' : active_version.id,
                    'parse_html' : active_version.parse_html if active_version.parse_html else None,
                    'parse_html_filename' : active_version.parse_html_filename   if active_version.parse_html_filename else None,
                    'parse_html_binary' : active_version.parse_html_binary if active_version.parse_html_binary else None,
                    'publish' : active_version.publish if active_version.publish else False,
                    'header_title' : active_version.header_title,
                    'header_description' : active_version.header_description,
                    'stage' : active_version.stage
                })

                view.page_id.arch_db = active_version.view_arch if active_version.view_arch else None

                if current_version.header_metadata_ids:
                    current_version.header_metadata_ids.write({'is_active': False})

                if active_version.header_metadata_ids:
                    active_version.header_metadata_ids.write({'is_active': True})

                if current_version.header_link_ids:
                    current_version.header_link_ids.write({'is_active': False})

                if active_version.header_link_ids:
                    active_version.header_link_ids.write({'is_active': True})

                self.view_id.message_post(body=f"Version '{self.name}' activated", message_type="comment")

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
        initial_version = self.env.context.get('initial_version')
        current_version = self.env['website.page.version'].search(
            ['&', ('status', '=', True), ('view_id', '=', seo_view.id)])
        view_arch = vals.get('view_arch') if vals.get('view_arch') else seo_view.website_page_id.arch_db if seo_view.website_page_id else False

        if current_version and seo_view:
            current_version.stage = seo_view.stage
            current_version.header_title = seo_view.header_title
            current_version.header_description = seo_view.header_description
            current_version.view_arch = seo_view.page_id.arch_db  if seo_view.page_id.arch_db else None
            current_version.status = False
            current_version.header_metadata_ids.write({'is_active': False})
            current_version.header_link_ids.write({'is_active': False})
        if initial_version and seo_view:
            seo_view.page_id.arch_db = view_arch if view_arch else None
            seo_view.stage = 'in_progress'
            seo_view.parse_html_filename = None
            seo_view.parse_html_binary = None
            seo_view.parse_html = None

            vals.update({
                'name' : 'v1.0.0',
                'page_id': seo_view.website_page_id.id,
                'view_arch': view_arch,
                'user_id': self.env.user.id,
                'header_title': seo_view.header_title,
                'header_description': seo_view.header_description,
                'stage': seo_view.stage
            })
        else:
            base_version = self.browse(int(self.env.context.get('base_version')))
            if not base_version:
                raise UserError('Base version is required')

            base_version_vals = base_version.read([
                'view_id',
                'page_id',
                'view_arch',
                'parse_html',
                'parse_html_binary',
                'parse_html_filename',
                'header_title',
                'header_description',
                'selected_filename',
                'header_metadata_ids',
                'header_link_ids'
            ])[0]

            base_version_vals['view_id'] = base_version_vals['view_id'][0] if base_version_vals['view_id'] else False
            base_version_vals['page_id'] = base_version_vals['page_id'][0] if base_version_vals['page_id'] else False

            vals.update(base_version_vals)

            for o2m_field in ['header_metadata_ids', 'header_link_ids']:
                if o2m_field in base_version_vals:
                    vals[o2m_field] = [(6, 0, base_version[o2m_field].ids)]

            change = self.env.context.get('change')

            if not change:
                raise UserError('Change is required')

            description = self.env.context.get('description')

            vals.update({
                'base_version':base_version.id,
                'change': change,
                'description' : description,
                'status' : True,
                'user_id' : self.env.user.id,
                'stage' : 'in_progress',
                'publish' : False
            })

            base_version.header_metadata_ids.write({'is_active': False})
            base_version.header_link_ids.write({'is_active': False})


        record = super(WebsitePageVersion, self).create(vals)


        if not initial_version:
            record._compute_version_name()

        seo_view.write({
            'parse_html': record.parse_html,
            'parse_html_filename': record.parse_html_filename,
            'parse_html_binary': record.parse_html_binary,
            'publish': False,
        })

        if seo_view.website_page_id and record.view_arch:
            seo_view.website_page_id.arch_db = record.view_arch

        record.view_id.message_post(body=f"Version '{record.name}' created and activated", message_type="comment")

        seo_view.active_version = record.id
        if initial_version and not record.selected_filename:
            record.create_default_version_metadata(record)

        return record


    def create_default_version_metadata(self, record):
        if not record.view_id.header_metadata_ids:

            self.env['automated_seo.page_header_metadata'].create([
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
            ])

            self.env['automated_seo.page_header_link'].create({
                'view_id' : record.view_id.id,
                'css_link' : "//cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.css",
                'view_version_id': record.id
            })


    def action_call_create_version(self):

        self.with_context(self.env.context).create({})

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
