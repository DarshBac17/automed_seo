import json
from odoo import models, fields, api
from bs4 import BeautifulSoup,Comment,NavigableString
import  html
import base64
import boto3
import io
import string
from odoo.exceptions import UserError
from botocore.exceptions import ClientError
import re
import random
from PIL import Image, UnidentifiedImageError
from pathlib import Path
import mimetypes
from html import escape, unescape
import xml.etree.ElementTree as ET
from datetime import datetime
from ftplib import FTP
import os
# from .ftp_setup import push_changes_to_ftp
# from .git_script import push_changes_to_git
from urllib.parse import urlparse
import subprocess
# from dotenv import load_dotenv
AWS_ACCESS_KEY_ID = 'AKIA4XF7TG4AOK3TI2WY'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'bacancy-website-images'

class View(models.Model):
    _name = 'automated_seo.view'
    _description = 'Automated SEO View'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='Page URL', help="Page URL")
    page_id = fields.One2many('ir.ui.view', 'page_id', string="Views")
    unique_page_id = fields.Char(string="Page Id")
    website_page_id = fields.Many2one('website.page', string="Website Page", readonly=True)
    parse_html = fields.Text(string="Parse HTML")
    parse_html_binary = fields.Binary(string="Parsed HTML File", attachment=True)
    parse_html_filename = fields.Char(string="Parsed HTML Filename")
    version = fields.One2many('website.page.version','view_id',string="Version")
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('stage', 'Stage'),
        ('publish', 'Publish'),
    ], string="Stage", default="draft", tracking=True)
    contributor_ids = fields.Many2many(
        'res.users',
        'seo_view_contributor_rel',
        'view_id',
        'user_id',
        string='Contributors',
        tracking=True
    )

    is_owner = fields.Boolean(
        compute='_compute_is_owner',
        string='Is Owner',
        store=False
    )

    publish = fields.Boolean('Publish', default=False)
    upload_file = fields.Binary(string="Upload File", attachment=True)
    is_new_page = fields.Boolean(default=True)
    is_processed = fields.Boolean(default=False)

    header_title = fields.Char(string="Title")

    header_description = fields.Text(string="page description")
    # header_description = fields.Text(string="Title")

    # One-to-Many relationship: A page can have multiple metadata entries
    header_metadata_ids = fields.One2many(
        'automated_seo.page_header_metadata',
        'view_id',
        string="Metadata"
    )

    header_link_ids = fields.One2many(
        'automated_seo.page_header_link',
        'view_id',
        string="Link",
        ondelete='cascade'  # This ensures child records are deleted when the parent is deleted
    )

    active_version_id = fields.Many2one(
        'website.page.version',
        compute='_compute_active_version_id',
        string="Active Version",
        store=False  # Set to True if you want to store the value persistently
    )

    # New computed field for filtered metadata
    filtered_header_metadata_ids = fields.One2many(
        'automated_seo.page_header_metadata',
        compute='_compute_filtered_header_metadata',
        string="Version Specific Metadata",
        store=False
    )

    filtered_header_link_ids = fields.One2many(
        'automated_seo.page_header_link',
        compute='_compute_filtered_header_link',
        string="Version Specific Link",
        store=False
    )

    has_edit_permission = fields.Boolean(
        compute='_check_edit_permission',
        string='Has edit permission',
        store=False,
        default=True
    )

    file_source = fields.Selection([
        ('draft', 'Draft'),
        ('remote', 'Select Remote File')
    ], string="File Source", default='draft')

    selected_filename = fields.Many2one(
        'automated_seo.remote_files',
        string="Remote Files",
        domain=[('is_processed', '=', False)]
    )
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The name must be unique!')
    ]

    @api.model
    def _get_remote_files(self):
        domain = [('is_processed', '=', False)]
        if self._context.get('search_term'):
            domain.append(('name', 'ilike', self._context['search_term']))
        files = self.env['automated_seo.remote_files'].search(domain)
        return [(f.name, f.name) for f in files]


    @api.depends('header_metadata_ids', 'active_version_id')
    def _compute_filtered_header_metadata(self):
        for record in self:
            record.filtered_header_metadata_ids = record.header_metadata_ids.filtered(
                lambda x: x.view_version_id == record.active_version_id
            )

    @api.depends('header_metadata_ids', 'active_version_id')
    def _compute_filtered_header_link(self):
        for record in self:
            record.filtered_header_link_ids = record.header_link_ids.filtered(
                lambda x: x.view_version_id == record.active_version_id
            )

    @api.depends('version.status')
    def _compute_active_version_id(self):
        for record in self:
            active_version = record.version.filtered(lambda v: v.status)
            record.active_version_id = active_version[0].id if active_version else None
            record.filtered_header_link_ids = record.header_link_ids.filtered(
                lambda x: x.view_version_id == record.active_version_id

            )
    @api.onchange('upload_file')
    def _onchange_upload_file(self):
        if self.upload_file:
            if self.env.context.get('upload_filename'):
                self.upload_filename = self.env.context.get('upload_filename')


    # @api.depends('version.publish')
    # def _compute_publish_status(self):
    #     for record in self:
    #         active_version = record.version.filtered(lambda r: r.status == True)[:1]
    #         record.publish = active_version.publish if active_version else False

    @api.depends('create_uid')
    def _compute_is_owner(self):
        """Compute if current user is the owner"""
        current_user = self.env.user
        for record in self:
            record.is_owner = current_user.id == record.create_uid.id

    @api.depends('create_uid', 'contributor_ids')
    def _check_edit_permission(self):
        """Compute if the current user has edit permissions"""
        current_user = self.env.user
        for record in self:
            # Convert Many2many field to list of IDs
            contributor_ids = record.contributor_ids.ids
            record.has_edit_permission = (
                current_user.id == record.create_uid.id or current_user.id in contributor_ids
            )


    def _get_next_page_id(self):
        last_view = self.search([], order='id desc', limit=1)
        if last_view and last_view.unique_page_id:
            last_id_num = int(last_view.unique_page_id[4:])
            return f'PAGE{str(last_id_num + 1).zfill(4)}'
        else:
            return 'PAGE0001'

    @api.model
    def create(self, vals):
        website_page = False
        new_page = None
        if not self.env.context.get('from_ir_view'):
            page_name = vals['name']
            # new_page = self.env['website'].with_context(from_seo_view=True).new_page(page_name)
            new_page = self.env['website'].with_context(
                from_seo_view=True,
                website_id=self.env['website'].get_current_website().id
            ).new_page(
                name=page_name,
                add_menu=True,  # Add to website menu
                template='website.default_page',  # Use default template
                ispage=True
            )
            vals['page_id'] = [(6, 0, new_page.get('view_id'))]
            vals['unique_page_id'] = self._get_next_page_id()
            website_page = self.env['website.page'].search([('view_id', '=', new_page['view_id'])], limit=1)
            if website_page:
                vals['website_page_id'] = website_page.id

            if page_name:
                vals["header_title"] = page_name.strip()
                vals["header_description"] = "Default page description"

        # if vals.get('file_source') == 'remote':
        #     print("file_source=============================")
        #
        #     if not vals.get('selected_filename'):
        #         raise UserError("Please select a file first.")
        #
        #     remote_file = self.env['automated_seo.remote_files'].browse(vals['selected_filename'])
        #     if not remote_file:
        #         raise UserError("Selected file not found")
        #
        #     try:
        #         cat_command = ['ssh', 'bacancy@35.202.140.10',
        #                       f'cat /home/pratik.panchal/temp/html/{remote_file.name}']
        #         result = subprocess.run(cat_command, capture_output=True, text=True)
        #
        #         if result.returncode != 0:
        #             raise UserError("Failed to read remote file")
        #
        #         file_content = result.stdout
        #         name, ext = remote_file.name.rsplit('.', 1)
        #
        #         if ext not in ['php','html']:
        #             raise UserError("Only PHP or HTML files are allowed.")
        #
        #         content = self.convert_php_tags(content=file_content)
        #         template_name = f"website.{new_page.get('url').split('/')[-1]}" if new_page.get('url') else "website.page"
        #
        #         formatted_arch = f'''<t t-name="{template_name}">
        #                             <t t-call="website.layout">
        #                             <div id="wrap" class="oe_structure oe_empty">
        #                                 {content}
        #                             </div>
        #                             </t>
        #                         </t>'''
        #
        #         soup = BeautifulSoup(formatted_arch, 'html.parser')
        #         breakpoint()
        #         self.env['website.page.version'].create({
        #             'description': f'{remote_file.name} File is processed',
        #             'view_id': new_page.get('view_id'),
        #             'page_id': vals.get('website_page_id'),
        #             'view_arch': soup.prettify(),
        #             'user_id': self.env.user.id,
        #             'status': True,
        #         })
        #
        #         self.create_php_header(header=file_content)
        #         self.selected_filename.write({'is_processed': True})
        #         self.message_post(body=f'{self.selected_filename} file processed successfully',
        #                           message_type="comment")
        #     except Exception as e:
        #         raise UserError(f"Error processing file: {str(e)}")
        record  = super(View, self).create(vals)
        record.is_new_page = False

        if not vals.get('selected_filename'):
            self.env['website.page.version'].create({
                'description' : 'First Version',
                'view_id':record.id,
                'page_id':website_page.id,
                'view_arch':website_page.view_id.arch_db,
                'user_id':self.env.user.id,
                'status':True
            })
        print("================================")
        print(record.is_new_page)
        print("================================")

        return record

    def write(self, vals):

        for record in self:
            if 'name' in vals and record.website_page_id:
                new_name = vals['name']
                current_website = self.env['website'].get_current_website()

                # Update website page
                record.website_page_id.write({
                    'name': new_name,
                    'url': '/' + new_name.lower().replace(' ', '-'),
                })

                # Update view
                if record.page_id:
                    record.page_id.write({
                        'name': new_name,
                        'key': 'website.' + new_name.lower().replace(' ', '_'),
                    })
                menu_item = self.env['website.menu'].search([
                    ('page_id', '=', record.website_page_id.id),
                    ('website_id', '=', current_website.id)
                ], limit=1)
                if menu_item:
                    menu_item.write({'name': new_name})

                if not self.env.context.get('from_ir_view'):
                    formatted_name = new_name.replace(' ', '').upper()

            current_version = self.env['website.page.version'].search(
                ['&', ('status', '=', True), ('view_id', '=', record.id)], limit=1)

            if current_version:

                updated_version = {}
                if 'header_title' in vals:
                    updated_version["header_title"] = vals["header_title"].strip()
                if 'header_description' in vals:
                    updated_version["header_description"] = vals["header_description"].strip()

                current_version.write(updated_version)

                # if 'header_metadata_ids' in vals:
                #     # Update existing metadata values
                #     for metadata, new_metadata in zip(
                #             current_version.header_metadata_ids,
                #             record.header_metadata_ids
                #     ):
                #         metadata.write({
                #             'property': new_metadata.property,
                #             'content': new_metadata.content,
                #         })
                #
                #     # Add additional metadata if `record.header_metadata_ids` has more items
                #     if len(record.header_metadata_ids) > len(current_version.header_metadata_ids):
                #         extra_metadata = record.header_metadata_ids[len(current_version.header_metadata_ids):]
                #         for meta in extra_metadata:
                #             self.env['automated_seo.page_header_metadata'].create({
                #                 'property': meta.property,
                #                 'content': meta.content,
                #                 'page_id': meta.page_id.id if meta.page_id else False,
                #                 'page_version_id': current_version.id,
                #             })

        return super(View, self).write(vals)

    # @api.constrains('url')
    # def _check_url_valid(self):
    #     for record in self:
    #         if record.url:
    #             # Basic URL pattern validation
    #             url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    #             if not re.match(url_pattern, record.url):
    #                 raise UserError('Please enter a valid URL starting with http:// or https://')
    #
    #             # Check if URL is reachable (optional)
    #             try:
    #                 result = urlparse(record.url)
    #                 if not all([result.scheme, result.netloc]):
    #                     raise UserError('Invalid URL format')
    #             except Exception:
    #                 raise UserError('Invalid URL format')


    def action_view_website_page(self):
        self.ensure_one()
        if not self.page_id:
            raise UserError("No website page associated with this record.")
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_page_id.url,
            'target': 'self',
        }

    def action_send_for_review(self):
        self.action_compile_button()
        self.write({'stage': 'in_review'})
        self.message_post(body="Record sent for review", message_type="comment")

    def action_set_to_in_preview(self):
        # Set status to 'draft' or 'quotation'
        self.stage = 'in_preview'
        self.message_post(body="Record sent for preview", message_type="comment")
        # Send email to admin here
        template = self.env.ref('automated_seo.email_template_preview')
        template.send_mail(self.id, force_send=True)

    def action_done_button(self):
        if self.validate_header():
            self.write({'stage': 'stage'})
            self.message_post(body="Record moved to the done stage", message_type="comment")

            page_name = self.name
            page_version = self.active_version_id[0].name
            last_updated = self.write_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_id = self.env.user.id

            # Step 3: Call the push_changes_to_ftp function to upload the file to the FTP server
            # upload_success = connect_to_aws_ftp(
            #     page_name=page_name,
            #     page_version=page_version,
            #     last_updated=last_updated,
            #     user_id=user_id,
            #     user_name=self.env.user.name,
            #     file_data= self.parse_html_binary
            # )

            # if upload_success:
            #     print("File successfully uploaded to FTP server.")
            # else:
            #     print("File upload failed.")

            # # Get Git details
            # page_name = self.name
            #
            # last_updated = self.write_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # user_id = self.env.user.id
            # base_branch = "master"
            # feature_branch = "git-commit"
            #
            # # Push changes to Git
            # success = push_changes_to_git(
            #     page_name=page_name,
            #     page_version=self.active_version_id.name,
            #     last_updated=last_updated,
            #     user_id=user_id,
            #     user_name=self.env.user.name,  # Include `user_name`
            #     base_branch=base_branch,
            #     feature_branch=feature_branch,
            #     file_data=self.parse_html_binary
            # )
            # if success:
            #     self.message_post(body="Changes successfully pushed to Git.", message_type="comment")
            # else:
            #     self.message_post(body="Failed to push changes to Git.", message_type="comment")

    def validate_header(self):

        if not self.header_title:
            raise UserError("Set Head Title")
        if not self.header_description:
            raise UserError("Set Head Description")
        if self.header_metadata_ids:
            required_metadata = {"og:description","og:title","og:image","og:url"}
            header_metadata = {
                metadata.property
                for metadata in self.header_metadata_ids
                if metadata.property and metadata.content
            }
            result = required_metadata.issubset(header_metadata)
            if not result:
                raise UserError(f"Head metadata must include all listed properties:\n{required_metadata}")
        else:
            raise UserError("Set Head metadata")
        return True

    def action_publish_button(self):
        self.write({'stage': 'publish'})
        self.message_post(body="Record publish", message_type="comment")
        self.active_version_id.publish_at = datetime.now()

    def action_unpublish_button(self):
        self.write({'stage': 'in_progress'})
        self.message_post(body="Record in progress", message_type="comment")

    def action_reject(self):
        self.write({'stage': 'in_progress'})
        self.message_post(body="Record rejected", message_type="comment")

    def send_email_action(self):
        # Logic to send email using Odoo's email system
        mail_values = {
            'subject': self.subject,
            'body_html': self.body,
            'email_to': self.email_to,
            'email_from': self.env.user.email,
        }
        self.env['mail.mail'].create(mail_values).send()

    def action_approve(self):
        self.write({'stage': 'approved'})
        self.message_post(body="Record approved", message_type="comment")

    def action_edit_website_page(self):
        """Opens the related website page in edit mode."""
        self.ensure_one()

        for record in self:
            if self.env.user.id != record.create_uid.id and self.env.user.id not in record.contributor_ids.ids:
                raise UserError("You do not have permission to edit this page. Only the owner and contributors can edit it.")
        if not self.page_id:
            raise UserError("No website page associated with this record.")
        self.write({'stage': 'in_progress'})
        base_url = self.website_page_id.url
        base_url = base_url.rstrip('/')

        return {
            'type': 'ir.actions.act_url',
            'url': f'{base_url}?enable_editor=1',
            'target': 'self',
        }

    def get_remote_file_content(self, filename):
        try:
            cat_command = ['ssh', 'bacancy@35.202.140.10', f'cat /home/pratik.panchal/temp/html/{filename}']
            result = subprocess.run(cat_command, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            return False
        except Exception:
            return False

    def action_parse_uploaded_file(self):
        self.ensure_one()
        if not self.selected_filename:
            raise UserError("Please select a file first.")

        try:
            file_name = self.selected_filename.name
            # Get remote file content
            cat_command = ['ssh', 'bacancy@35.202.140.10',
                          f'cat /home/pratik.panchal/temp/html/{file_name}']
            result = subprocess.run(cat_command, capture_output=True, text=True)
            if result.returncode != 0:
                raise UserError("Failed to read remote file")

            file_content = result.stdout
            name, ext = file_name.rsplit('.', 1)

            if ext not in ['php','html']:
                raise UserError("Only PHP or HTML files are allowed.")

            content = self.convert_php_tags(content=file_content)
            template_name = f"website.{self.website_page_id.url.split('/')[-1]}" if self.website_page_id.url else "website.page"

            formatted_arch = f'''<t t-name="{template_name}">
                                    <t t-call="website.layout">
                                    <div id="wrap" class="oe_structure oe_empty">
                                        {content}
                                    </div>
                                    </t>
                                </t>'''

            soup = BeautifulSoup(formatted_arch,'html.parser')

            version = self.env['website.page.version'].create({
                'description': f'{file_name} File is processed',
                'view_id': self.id,
                'page_id': self.page_id,
                'view_arch': soup.prettify(),
                'user_id': self.env.user.id,
                'status': True,
                'publish': True,
                'selected_filename':self.selected_filename.name,
            })
            self.with_context(view_name=self.name).action_compile_button()
            version.status = False
            new_version = self.env['website.page.version'].create({
            'description': f'{file_name} File is processed',
            'view_id': self.id,
            'page_id': self.page_id,
            'view_arch': soup.prettify(),
            'user_id': self.env.user.id,
            'prev_version': version.id,
            'publish': False,
            })

            # Call action_create_version on new version
            new_version.with_context(
                prev_version=version.id,
                unpublish=True
            ).action_create_version()

            self.create_php_header(header=file_content)
            self.is_processed = True
            self.selected_filename.write({'is_processed': True})


            self.message_post(body=f'{self.selected_filename} file processed successfully',
                            message_type="comment")



        except Exception as e:
            raise UserError(f"Error processing file: {str(e)}")

    # def action_parse_uploaded_file(self):

    #     self.file_uploaded = bool(self.upload_file)
    #     self.message_post(body=f'{self.upload_filename} File is uploaded', message_type="comment")
    #     name, ext = self.upload_filename.rsplit('.', 1)
    #     if ext not in ['php','html']:
    #         raise UserError("Upload php or html file.")
    #     file_content = base64.b64decode(self.upload_file)
    #     file_text = file_content.decode('utf-8')
    #     content = self.convert_php_tags(content=file_text)
    #     template_name = f"website.{self.website_page_id.url.split('/')[-1]}" if self.website_page_id.url else "website.page"
    #     formatted_arch = f'''<t t-name="{template_name}">
    #                             <t t-call="website.layout">
    #                             <div id="wrap" class="oe_structure oe_empty">
    #                                 {content}
    #                             </div>
    #                             </t>
    #                         </t>'''
    #     soup = BeautifulSoup(formatted_arch,'html.parser')
    #     self.env['website.page.version'].create({
    #         'description': f'{self.upload_filename} File is uploaded',
    #         'view_id': self.id,
    #         'page_id': self.page_id,
    #         'view_arch':soup.prettify(),
    #         'user_id': self.env.user.id,
    #         'status': True,
    #     })
    #     self.create_php_header(header=file_text)

    # def action_open_page_header(self):
    #
    #     return {
    #         'name': 'Page Header',
    #         'view_mode': 'form',
    #         'res_model': 'automated_seo.page_header',
    #         'view_id': self.env.ref('automated_seo.page_header_embedded_form').id,
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',  # This will open in a popup
    #         'context': {
    #             'default_page': self.name,  # If you want to pass any default values
    #         }
    #     }


    def normalize_text(self,text):
        return ' '.join(str(text).split())

    def minify_php_tags(self,content):
        # Regex to match text starting with '<?php' and ending with '?>'
        pattern = r"<\?php.*?\?>"

        # Function to remove spaces within the match
        def remove_spaces(match):
            return re.sub(r"\s+", "", match.group(0))

        # Apply the regex substitution
        return re.sub(pattern, remove_spaces, content, flags=re.DOTALL)

    def replace_php_variables(self,content):
        # Regex pattern to match <?phpecho$variable?>
        # pattern = r"<\?php*\secho\$([a-zA-Z_][a-zA-Z0-9_]*)\?>"
        pattern = r'<\?php\s*echo\s*\$?([a-zA-Z_][a-zA-Z0-9_]*)\s*\?>'

        # Function to generate the replacement text
        def replacer(match):
            variable_name = match.group(1)
            value = self.env['automated_seo.php_variables'].search([('name', '=', variable_name)], limit=1).read(['value'])[0]
            variable_value = value.get('value') if value.get('value') else variable_name
            return (
                f'<span class="o_au_php_var o_text-php-var-info" '
                f'data-php-var="{variable_name}" data-php-const-var="0">{{{variable_value}}}</span>'
            )
        return re.sub(pattern, replacer, content)

    def replace_php_const_variables(self,content):
        # Regex pattern to match <?phpecho$variable?>
        # pattern = r"<\?phpechoconstant\(\s*\"([a-zA-Z_][a-zA-Z0-9_]*)\"\s*\)\?>"
        #  pattern = r'<\?php\s*echo\s*\$?([a-zA-Z_][a-zA-Z0-9_]*)\s*\?>'
        pattern = r'<\?php\s*echo\s*constant\s*\(\s*[\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]?\s*\)\s*\?>'


        # Function to generate the replacement text
        def replacer(match):
            variable_name = match.group(1)
            value = self.env['automated_seo.php_variables'].search([('name', '=', variable_name)], limit=1).read(['value'])[0]
            variable_value = value.get('value') if value.get('value') else variable_name
            return (
                f'<span class="o_au_php_var o_text-php-var-info" '
                f'data-php-var="{variable_name}" data-php-const-var="1">{{{variable_value}}}</span>'
            )

        # Replace all matches in the content
        return re.sub(pattern, replacer, content)

    # def replace_php_constants(self,content):
    #     # Regex pattern to match <?php echo constant("CONSTANT_NAME")?>
    #     pattern = r"<\?phpechoconstant\(\s*\"([a-zA-Z_][a-zA-Z0-9_]*)\"\s*\)\s*\?>"
    #
    #     # Function to generate the replacement text
    #     def replacer(match):
    #         constant_name = match.group(1)
    #         return (
    #             f'<span class="o_au_php_var o_text-php-var-info" '
    #             f'data-php-var="{constant_name}" data-php-const-var="1">{constant_name}</span>'
    #         )
    #
    #     # Replace all matches in the content
    #     return re.sub(pattern, replacer, content)

    def create_php_header(self,header):
        header = BeautifulSoup(header,'html.parser').head
        self.header_title = header.title.text
        meta_tags = header.find_all('meta')
        for meta_tag in meta_tags :
            # try:
            if meta_tag.get('name'):
                self.header_description = meta_tag.get('content')
            else:
                self.env['automated_seo.page_header_metadata'].create({
                    'view_version_id': self.active_version_id,
                    'view_id': self.id,
                    'property': meta_tag.get('property') if meta_tag.get('property') else None,
                    'content': meta_tag.get('content')
                })

        link_tags = header.find_all('link')
        for link_tag in link_tags:
            css_link = link_tag['href']
            if not self.env['automated_seo.page_header_link'].search(
                    [('css_link', '=', css_link),
                     ('view_version_id', '=', self.active_version_id.id),
                     ('view_id', '=', self.id)]):
                self.env['automated_seo.page_header_link'].create({
                    'view_version_id': self.active_version_id.id,
                    'css_link': css_link,
                    'view_id': self.id
                })


    def convert_php_tags(self,content):

        tags = self.env['automated_seo.php_to_snippet'].search([("php_tag","=",True)]).read(['php', 'snippet'])
        soup = BeautifulSoup(content, 'html.parser')
        base_url_php = "https://assets.bacancytechnology.com/"
        for img in soup.select('img'):
            url = re.sub(r'\s', '', img.get('src'))
            image_base = re.sub(r'\s', '', "<?php echo BASE_URL_IMAGE; ?>")

            img['src'] = url.replace(image_base, base_url_php)
            img['data-src'] = url.replace(image_base, base_url_php)

        anchor_base_url_php = "https://www.bacancytechnology.com/"
        for a in soup.select('a'):
            url = re.sub(r'\s', '', a.get('href'))
            base = re.sub(r'\s', '', "<?php echo BASE_URL; ?>")
            if url and url.startswith(base):
                a['href'] = url.replace(base, anchor_base_url_php)

        anchor_blog_url_php = "https://www.bacancytechnology.com/blog/"
        for a in soup.select('a.btn'):
            url = re.sub(r'\s', '', a.get('href'))
            base = re.sub(r'\s', '', "<?php echo BLOG_URL; ?>")
            if url and url.startswith(base):
                a['href'] = url.replace(base, anchor_blog_url_php)

        content = self.normalize_text(soup.prettify())
        for tag in tags:
            content = re.sub(pattern=tag.get('php'),repl=tag.get('snippet'),string=content)
            # content = content.replace(self.minify_php_tags(self.normalize_text(tag.get('php'))),tag.get('snippet'))

        content = self.replace_php_variables(content=content)
        content = self.replace_php_const_variables(content=content)
        if content.find("phpecho"):
            content = content.replace("phpecho","php echo ")


        soup = BeautifulSoup(content, 'html.parser')

        sections =  soup.find_all('section')
        content = ""
        tags = self.env['automated_seo.php_to_snippet'].search([("php_tag","=",False)]).read(['php', 'snippet','name'])
        for section in sections:
            classes = section.get('class',[])
            if not section.find_parent('section'):
                section.attrs['data-snippet'] = "s_banner"
                classes.append('o_automated_seo_php_variable')
                section['class']=classes
                new_section = str(section)
                for tag in tags:
                    new_php =self.normalize_text(tag.get('php'))
                    snippet = tag.get('snippet')
                    if re.search(new_php,new_section):
                        if classes and 'banner' in classes:
                            match = re.search(r'\$bannerDevName\s*=\s*"([^"]+)"', new_section)
                            if match:
                                snippet_soup = BeautifulSoup(snippet,'html.parser')
                                span_tag = snippet_soup.find("span")
                                if span_tag:
                                    span_tag.string = match.group(1)
                                snippet = snippet_soup.prettify()
                        elif tag.get('name')=='form':
                            tech_dark_form_heading = re.search(r'\$tech_dark_form_heading\s*=\s*[\'"]([^\'\"]+)[\'"]', new_section)
                            short_desc = re.search(r'\$short_desc\s*=\s*[\'"]([^\'\"]+)[\'"]', new_section)
                            snippet_soup = BeautifulSoup(snippet, 'html.parser')
                            h2_tag = snippet_soup.find(class_="o_au_php_var_tag_tech_dark_form_heading")
                            p_tag = snippet_soup.find(class_="o_au_php_var_tag_short_desc")
                            if tech_dark_form_heading and h2_tag:
                                h2_tag.string = tech_dark_form_heading.group(1)
                            if short_desc and p_tag:
                                p_tag.string = short_desc.group(1)
                            snippet = snippet_soup.prettify()

                        new_section = re.sub(tag.get('php'), snippet, new_section)
                        # else:
                        #     new_section=new_section.replace(new_php,snippet)
                content+=new_section
        soup = BeautifulSoup(content, 'html.parser')
        sections = soup.find_all('section')
        content =""
        for section in sections:

            if not section.find_parent('section'):
                classes = section.get('class',[])
                ids = section.get('id',[])
                if classes and 'tech-stack' in classes:
                    tbody = section.find('tbody')
                    tbody['class'] = ['o_sub_items_container']

                    #     # Transform table rows
                    rows = tbody.find_all('tr')
                    for row in rows:
                        # Update content cell class
                        content_cell = row.find_all('td')[1]
                        content_cell['class'] = ['o_tech_stack']
                        #
                        # Convert spans to pipe-separated text
                        spans = content_cell.find_all('span')
                        content_span = '|'.join(span.string for span in spans if span.string)
                        [span.decompose() for span in spans]
                        content_cell.string = content_span
                # if 'price-sec' in ids:
                #     spans = section.find_all(class_='o_au_php_var')

                #     for span in spans:
                #         span.string="2***"
                sub_snippets = None

                if section.find_all('div', class_='boxed'):
                    sub_snippets =section.find_all('div', class_='boxed')
                elif section.find_all('div',class_='accordian-tab'):
                    sub_snippets =section.find_all('div', class_='accordian-tab')
                elif section.find_all('div',class_='ind-box'):
                    sub_snippets =section.find_all('div', class_='ind-box')

                if sub_snippets:
                    container_tag = sub_snippets[0].find_parent()
                    container_classes = container_tag.get("class", [])
                    classes.append("o_automated_seo_snippet")
                    container_classes.append("o_sub_items_container")
                    container_tag["class"] = container_classes
                    section['class'] =classes
                    for sub_snippet in sub_snippets:
                        if sub_snippet:
                            sub_snippet_classes = sub_snippet.get("class", [])
                            sub_snippet_classes.append("o_replace_section_div")
                            sub_snippet["class"] = sub_snippet_classes
                            sub_snippet.name = "section"
                content += str(section)
        return content


    def get_approve_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&model={self._name}&view_type=form&action=approve"

    def unlink(self):

        for record in self:
            try:
                if self.env.user.id != record.create_uid.id and not self.env.user.has_group('base.group_system'):
                    raise UserError("You do not have permission to delete this page. Only the owner can edit it.")
                versions = self.env['website.page.version'].search([('view_id', '=', record.id)])
                if versions:
                    versions.unlink()
                # Delete associated website page
                if record.page_id:
                    website_page = self.env['website.page'].search([('view_id', 'in', record.page_id.ids)], limit=1)
                    if website_page:
                        website_page.unlink()
                seo_page = self.env['automated_seo.page'].search([('page_name', '=', record.name)])
                if seo_page:
                    seo_page.unlink()
                # self.delete_img_folder_from_s3(view_name=record.name)

            except Exception as e:
                print(f"Error while deleting associated records for view {record.name}: {str(e)}")
                raise

        return super(View, self).unlink()

    def process_image_with_params(self, attachment, img_tag):
        """
        Process image with cropping parameters and CSS transforms before uploading to S3

        Args:
            attachment: ir.attachment record containing the original image
            img_tag: BeautifulSoup tag containing the image parameters

        Returns:
            BytesIO object containing the processed image
        """
        try:
            # Get original image from attachment
            image_data = base64.b64decode(attachment.datas) if attachment.datas else None
            if not image_data:
                return None

            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))

            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background

            # Get image dimensions
            orig_width, orig_height = image.size

            # Get cropping parameters and convert to actual pixels
            x = float(img_tag.get('data-x', 0))
            y = float(img_tag.get('data-y', 0))
            width = float(img_tag.get('data-width', orig_width))
            height = float(img_tag.get('data-height', orig_height))

            # Convert percentages to pixels if values seem to be percentages
            if width < 100:  # Likely a percentage
                width = (width / 100.0) * orig_width
            if height < 100:  # Likely a percentage
                height = (height / 100.0) * orig_height
            if x < 100:  # Likely a percentage
                x = (x / 100.0) * orig_width
            if y < 100:  # Likely a percentage
                y = (y / 100.0) * orig_height

            # Ensure values are within image bounds
            x = max(0, min(x, orig_width))
            y = max(0, min(y, orig_height))
            width = max(1, min(width, orig_width - x))
            height = max(1, min(height, orig_height - y))

            # Apply cropping
            crop_box = (
                int(x),
                int(y),
                int(x + width),
                int(y + height)
            )
            image = image.crop(crop_box)

            # Get scaling parameters from both data attributes and CSS transform
            scale_x = float(img_tag.get('data-scale-x', 1))
            scale_y = float(img_tag.get('data-scale-y', 1))

            # Extract CSS transform scales if present
            style = img_tag.get('style', '')
            css_scale_x = 1
            css_scale_y = 1

            # Extract scaleX and scaleY from CSS transform
            scale_x_match = re.search(r'scaleX\(([\d.]+)\)', style)
            scale_y_match = re.search(r'scaleY\(([\d.]+)\)', style)

            if scale_x_match:
                css_scale_x = float(scale_x_match.group(1))
            if scale_y_match:
                css_scale_y = float(scale_y_match.group(1))

            # Combine both scaling factors
            final_scale_x = scale_x * css_scale_x
            final_scale_y = scale_y * css_scale_y

            # Apply scaling if needed
            if final_scale_x != 1 or final_scale_y != 1:
                new_width = int(image.width * final_scale_x)
                new_height = int(image.height * final_scale_y)
                if new_width > 0 and new_height > 0:
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Get quality parameter
            quality = int(img_tag.get('data-quality', 100))

            # Apply final resize if specified
            resize_width = img_tag.get('data-resize-width')
            if resize_width:
                try:
                    resize_width = int(resize_width)
                    if resize_width > 0:
                        resize_height = int((resize_width / image.width) * image.height)
                        image = image.resize((resize_width, resize_height), Image.Resampling.LANCZOS)
                except (ValueError, TypeError):
                    pass

            # Save processed image to BytesIO
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality)
            output.seek(0)
            # img_tag['height'] = int(height)
            # img_tag['width'] = int(width)
            return output

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            new_image_data = attachment.datas
            new_image = base64.b64decode(new_image_data)
            image_file = io.BytesIO(new_image)
            return image_file

    def generate_hash(self,length=6):
        """Generate a random string of fixed length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def action_compile_button(self):
        view_name = self.env.context.get('view_name')
        if view_name == None:
            view_name = self.name
        self.update_snippet_ids(view_name)
        html_parser  = self.handle_img_change(view_name=view_name)
        html_parser = self.replace_php_tags_in_html(html_parser=html_parser)
        html_parser = self.handle_dynamic_anchar_tag(html_parser=html_parser)
        if html_parser:
            html_parser = self.remove_bom(html_parser=html_parser)
            html_parser = self.remove_empty_tags(html_parser = html_parser)
            html_parser = self.handle_breadcrumbs(html_content=html_parser)
            html_parser = self.handle_itemprop_in_faq(html_content=html_parser)
            html_parser = self.add_head(html_parser)
            html_parser = self.add_js_scripts(html_parser)
            html_parser = self.remove_odoo_classes_from_tag(html_parser)
            soup = BeautifulSoup(html_parser, "html.parser")
            html_parser = soup.prettify()
            # html_parser = self.format_paragraphs(html_content=html_parser)
            # html_parser = self.remove_extra_spaces(html_parser = html_parser)
            html_parser = self.format_html_php(html_content=html_parser)
            html_parser = re.sub(r'itemscope=""', 'itemscope', html_parser)
            html_parser = html.unescape(html_parser)

            file = base64.b64encode(html_parser.encode('utf-8'))
            version = self.env['website.page.version'].search(['&',('view_id','=',self.id),("status", "=", True)],limit =1)
            file_name = f"{view_name}_{version.name}.php"
            self.write({
                'parse_html': html_parser,
                'parse_html_binary': file ,
                'parse_html_filename': file_name,

            })
            version.write({
                'parse_html': html_parser,
                'parse_html_binary':file,
                'parse_html_filename' : file_name
            })

    # def add_head(self, html_parser):
    #     # Add the title with proper indentation
    #     html_head = f"        <title>{self.header_title or 'Default Title'}</title>"
    #
    #     # Generate meta tags for all metadata entries with consistent indentation
    #     meta_tags = ""
    #     for metadata in self.header_metadata_ids:
    #         if metadata.name:  # For standard meta tags like description
    #             meta_tags += f"\n        <meta name=\"{metadata.name}\" content=\"{metadata.content or ''}\">"
    #         elif metadata.property:  # For Open Graph meta tags
    #             meta_tags += f"\n        <meta property=\"{metadata.property}\" content=\"{metadata.content or ''}\">"
    #
    #     # Combine everything into the final HTML structure with consistent indentation
    #     complete_html = f"""
    #     <!DOCTYPE html>
    #     <html lang="en">
    #         <head>
    #     {html_head}{meta_tags}
    #         </head>
    #         <body>
    #             {html_parser or ''}
    #         </body>
    #     </html>
    #     """
    #
    #     return complete_html

    def add_js_scripts(self,html_parser):
        soup = BeautifulSoup(html_parser, 'html.parser')

        js_scripts = """
        <?php include("template/common_js-tailwind.php"); ?>
        <?php include("tailwind/template/link-js.php"); ?>
        <?php include("main-boot-5/templates/localbusiness-schema.php"); ?>
        <?php include("main-boot-5/templates/chat-script.php"); ?>
        <script src="<?php echo BASE_URL; ?>tailwind/js/slider-one-item.js?V-7" defer></script>
        <script type="text/javascript" src="//cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.min.js" defer></script>
        """

        js_scripts = BeautifulSoup(js_scripts,'html.parser')
        soup.body.append(js_scripts)
        return soup.prettify()

    def add_head(self, html_parser):
        soup = BeautifulSoup('<html lang="en"><head></head><body></body></html>', 'html.parser')
        head_tag = soup.head
        page_name = self.name.strip().lower().replace(" ", "-")
        title_tag = soup.new_tag('title')
        title_tag.string = self.header_title or 'Default Title'
        head_tag.append(title_tag)

        description_meta = soup.new_tag('meta')
        description_meta['name'] = 'description'
        description_meta['content'] = self.header_description
        head_tag.append(description_meta)
        for metadata in self.header_metadata_ids:
            meta_tag = soup.new_tag('meta')
            if metadata.property:
                meta_tag['property'] = metadata.property
                meta_tag['content'] = metadata.content or ''
            head_tag.append(meta_tag)

        # link_css_php = BeautifulSoup('<?php include("tailwind/template/link-css.php"); ?>',"html.parser")
        # head_tag.append(link_css_php)
        link_css_php = BeautifulSoup('<?php include("tailwind/template/link-css.php"); ?>',"html.parser")
        head_tag.append(link_css_php)
        for link in self.filtered_header_link_ids:
            tag = soup.new_tag('link')
            tag['rel'] = "preload"
            tag['href'] = link.css_link
            tag['as'] = 'style'
            tag['onload'] = "this.onload=null;this.rel='stylesheet'"
            head_tag.append(tag)


        webpage_script = f"""
            <script type="application/ld+json">
            {{
                "@context": "https://schema.org",
                "@graph": [
                    {{
                        "@type": "WebSite",
                        "@id": "<?php echo BASE_URL; ?>#website",
                        "url": "<?php echo BASE_URL; ?>",
                        "name": "Bacancy",
                        "description": "Top product development company with Agile methodology. Hire software developers to get complete product development solution from the best agile software development company.",
                        "potentialAction": [
                            {{
                                "@type": "SearchAction",
                                "target": {{
                                    "@type": "EntryPoint",
                                    "urlTemplate": "<?php echo BASE_URL; ?>?s={{search_term_string}}"
                                }},
                                "query-input": "required name=search_term_string"
                            }}
                        ],
                        "inLanguage": "en-US"
                    }},
                    {{
                        "@type": "WebPage",
                        "@id": "<?php echo BASE_URL; ?>{page_name}/#webpage",
                        "url": "<?php echo BASE_URL; ?>{page_name}/",
                        "name": "{self.header_title}",
                        "isPartOf": {{
                            "@id": "<?php echo BASE_URL; ?>#website"
                        }},
                        "datePublished": "2013-04-15T13:23:16+00:00",
                        "dateModified": "2024-07-17T14:31:52+00:00",
                        "description": "{self.header_description}"
                    }}
                ]
            }}
            </script>
        """

        webpage_script_soup = BeautifulSoup(webpage_script,'html.parser')

        head_tag.append(webpage_script_soup)


        if html_parser:
            parsed_content = BeautifulSoup(html_parser, 'html.parser')
            soup.body.append(parsed_content)

        breadcrumb_items_tags = soup.find_all(class_="breadcrumb-item")

        breadcrumb_items = []

        for index, breadcrumb in enumerate(breadcrumb_items_tags):

            link = breadcrumb.find('a')
            position = index + 1
            if link and not link.get('href'):
                link['href']="#"

            url = link.get('href') if link else f"<?php echo BASE_URL; ?>{page_name}" if index == len(breadcrumb_items_tags)-1 else ValueError("breadcrumb url not set")

            if isinstance(url,ValueError):
                raise url
            id = url + '/'
            name = link.text.strip() if link else breadcrumb.text.strip()
            item = {
                "@type": "ListItem",
                "position": position,
                "item": {
                    "@type": "WebPage",
                    "@id": id
                }
            }
            if index > 0:
                item["item"]["url"] = url
            item["item"]["name"] = name

            breadcrumb_items.append(item)


        breadcrumb_items_json = self.format_json_with_tabs(breadcrumb_items)

        # Generate the final script
        breadcrumb_script = f"""
            <script type="application/ld+json">
            {{
                "@context": "http://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": {breadcrumb_items_json}
            }}
            </script>
        """
        breadcrumb_script_soup = BeautifulSoup(breadcrumb_script, 'html.parser')
        head_tag.append(breadcrumb_script_soup)
        return soup.prettify()

    def format_json_with_tabs(self, data, indent_tabs=16):
        """
        Format JSON with specified tab spaces per indentation level,
        ignoring the first line for indentation.
        """
        json_string = json.dumps(data, indent=4)  # Convert to JSON with default 4 spaces
        lines = json_string.splitlines()  # Split into individual lines
        # Add indentation only from the second line onward
        tabbed_json = "\n".join(lines[:1] + [" " * indent_tabs + line for line in lines[1:]])
        return tabbed_json

    def handle_breadcrumbs(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        for main_entity in soup.find_all(class_='breadcrumb'):
            active_item = main_entity.find_all(class_='breadcrumb-item')[-1]
            active_item["class"].append("active")
            active_item["aria-current"]="page"
            text_content = active_item.get_text()
            active_item.clear()
            active_item.append(text_content)

        return str(soup.prettify())


    def handle_itemprop_in_faq(self,html_content):

        soup = BeautifulSoup(html_content,"html.parser")
        for main_entity in soup.find_all(class_='o_answer_itemprop'):
            main_entity.find_all()[0]["itemprop"] = "text"

        return str(soup.prettify())

    def format_paragraphs(self,html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        paragraphs = soup.find_all('p')

        for p in paragraphs:
            contents = str(p)
            replacements = {
                '&amp;': '&',
                '&lt;': '<',
                '&gt;': '>',
                '&quot;': '"',
                '&apos;': "'",
                '&#39;': "'",
                '&nbsp;': ' '
            }
            for entity, char in replacements.items():
                contents = contents.replace(entity, char)

            opening_tag = re.match(r'<p[^>]*>', contents).group(0)
            closing_tag = '</p>'

            inner_content = contents[len(opening_tag):-len(closing_tag)]

            cleaned_content = ' '.join(inner_content.split())
            new_p = soup.new_tag('p')
            new_p.attrs = p.attrs
            new_p.append(cleaned_content)
            p.replace_with(new_p)

        return str(soup)

    def format_html_php(self,html_content, indent_size=4):        # Define tag sets
        inline_content_tags = {'p', 'span', 'li', 'b', 'i', 'strong', 'em', 'label', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6','title'}
        self_closing_tags = {'img', 'br', 'hr', 'input', 'meta', 'link'}
        structural_tags = {'div', 'section', 'nav', 'header', 'footer', 'main'}
        table_tags = {'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot'}

        # Store PHP blocks
        php_blocks = {}
        php_counter = 0

        def save_php(match):
            nonlocal php_counter
            placeholder = f"PHP_PLACEHOLDER_{php_counter}"
            php_blocks[placeholder] = match.group(0)
            php_counter += 1
            return placeholder

        def format_attributes(tag):
            if not tag.attrs:
                return ''
            attrs = []
            for key, value in tag.attrs.items():
                if isinstance(value, list):
                    value = ' '.join(value)
                if value is True:
                    attrs.append(key)
                else:
                    attrs.append(f'{key}="{value}"')
            return ' ' + ' '.join(attrs) if attrs else ''

        def should_inline_content(elem):
            # Check if element should be inlined
            has_structural = any(child.name in structural_tags for child in elem.children)
            has_only_text = all(isinstance(child, NavigableString) or child.name in inline_content_tags
                                for child in elem.children)
            return not has_structural and has_only_text

        def format_span_cell(elem, indent):
            """Special formatter for td elements containing spans"""
            spans = elem.find_all('span', recursive=False)
            if spans:
                # Join spans without newlines, preserving their text content
                span_contents = []
                for span in spans:
                    text = ' '.join(span.stripped_strings)
                    span_contents.append(f'<span>{text}</span>')
                return f"{indent}<td>{' '.join(span_contents)}</td>"
            return None

        def format_element(elem, level=0):
            if isinstance(elem, NavigableString):
                text = str(elem).strip()
                return text if text else ''

            indent = ' ' * (level * indent_size)
            attrs = format_attributes(elem)

            if elem.name == 'td':
                if elem.find_all('span', recursive=False):
                    return format_span_cell(elem, indent)
                else:
                    text = ' '.join(elem.stripped_strings)
                    return f"{indent}<td>{text}</td>"

            # Handle self-closing tags
            if elem.name in self_closing_tags:
                return f"{indent}<{elem.name}{attrs}/>"
            if elem.name == 'a':
                if should_inline_content(elem):
                    content = ' '.join(elem.stripped_strings)
                    return f"{indent}<{elem.name}{attrs}>{content}</{elem.name}>"
                else:
                    # Handle structural content inside anchor
                    lines = [f"{indent}<{elem.name}{attrs}>"]
                    for child in elem.children:
                        if isinstance(child, NavigableString):
                            text = child.strip()
                            if text:
                                lines.append(f"{indent}{' ' * indent_size}{text}")
                        else:
                            lines.append(format_element(child, level + 1))
                    lines.append(f"{indent}</{elem.name}>")
                    return '\n'.join(line for line in lines if line.strip())

            # Handle inline content tags
            if elem.name in inline_content_tags:
                # Collect all content including PHP blocks
                content_parts = []
                for child in elem.children:
                    if isinstance(child, NavigableString):
                        text = str(child).strip()
                        if text:
                            content_parts.append(text)
                    else:
                        # Preserve PHP blocks
                        content_parts.append(str(child))
                content = ' '.join(content_parts)
                content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                return f"{indent}<{elem.name}{attrs}>{content}</{elem.name}>"

            # Handle table row elements
            if elem.name == 'tr':
                lines = [f"{indent}<{elem.name}{attrs}>"]
                for child in elem.children:
                    if isinstance(child, NavigableString):
                        continue
                    if child.name == 'td':
                        cell_content = format_span_cell(child, indent + ' ' * indent_size)
                        if cell_content:
                            lines.append(cell_content)
                        else:
                            lines.append(format_element(child, level + 1))
                lines.append(f"{indent}</{elem.name}>")
                return '\n'.join(line for line in lines if line.strip())

            if elem.name == 'tr':
                lines = [f"{indent}<{elem.name}{attrs}>"]
                for child in elem.children:
                    if isinstance(child, NavigableString):
                        continue
                    if child.name == 'td':
                        cell_content = format_span_cell(child, indent + ' ' * indent_size)
                        if cell_content:
                            lines.append(cell_content)
                        else:
                            lines.append(format_element(child, level + 1))
                lines.append(f"{indent}</{elem.name}>")
                return '\n'.join(line for line in lines if line.strip())

            # Handle structural elements
            lines = [f"{indent}<{elem.name}{attrs}>"]
            for child in elem.children:
                if isinstance(child, NavigableString):
                    text = child.strip()
                    if text:
                        lines.append(f"{indent}{' ' * indent_size}{text}")
                else:
                    lines.append(format_element(child, level + 1))
            lines.append(f"{indent}</{elem.name}>")

            return '\n'.join(line for line in lines if line.strip())

        # Save PHP code
        html_with_placeholders = re.sub(r'<\?php.*?\?>', save_php, html_content, flags=re.DOTALL)

        # Parse HTML
        soup = BeautifulSoup(html_with_placeholders, 'html.parser')

        # Format HTML
        formatted = '\n'.join(
            format_element(child, 0)
            for child in soup.children
            if not isinstance(child, NavigableString) or child.strip()
        )

        # Restore PHP blocks
        for placeholder, php_code in php_blocks.items():
            formatted = formatted.replace(placeholder, php_code,1)

        return '<!DOCTYPE html>\n'+formatted
    # def format_html_php(self,html_content, indent_size=4):
    #
    # # Define tag sets
    #     inline_content_tags = {'p', 'span', 'li', 'b', 'i', 'strong', 'em', 'label', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
    #     self_closing_tags = {'img', 'br', 'hr', 'input', 'meta', 'link'}
    #     structural_tags = {'div', 'section', 'nav', 'header', 'footer', 'main'}
    #
    #     def format_attributes(tag):
    #         if not tag.attrs:
    #             return ''
    #         attrs = []
    #         for key, value in tag.attrs.items():
    #             if isinstance(value, list):
    #                 value = ' '.join(value)
    #             if value is True:
    #                 attrs.append(key)
    #             else:
    #                 attrs.append(f'{key}="{value}"')
    #         return ' ' + ' '.join(attrs) if attrs else ''
    #
    #     def should_inline_content(elem):
    #         # Check if element should be inlined
    #         has_structural = any(child.name in structural_tags for child in elem.children)
    #         has_only_text = all(isinstance(child, NavigableString) or child.name in inline_content_tags
    #                           for child in elem.children)
    #         return not has_structural and has_only_text
    #
    #     def format_element(elem, level=0):
    #         if isinstance(elem, NavigableString):
    #             text = str(elem).strip()
    #             return text if text else ''
    #
    #         indent = ' ' * (level * indent_size)
    #         attrs = format_attributes(elem)
    #
    #         # Handle self-closing tags
    #         if elem.name in self_closing_tags:
    #             return f"{indent}<{elem.name}{attrs}/>"
    #
    #         # Handle anchor tags
    #         if elem.name == 'a':
    #             if should_inline_content(elem):
    #                 content = ' '.join(elem.stripped_strings)
    #                 return f"{indent}<{elem.name}{attrs}>{content}</{elem.name}>"
    #             else:
    #                 # Handle structural content inside anchor
    #                 lines = [f"{indent}<{elem.name}{attrs}>"]
    #                 for child in elem.children:
    #                     if isinstance(child, NavigableString):
    #                         text = child.strip()
    #                         if text:
    #                             lines.append(f"{indent}{' ' * indent_size}{text}")
    #                     else:
    #                         lines.append(format_element(child, level + 1))
    #                 lines.append(f"{indent}</{elem.name}>")
    #                 return '\n'.join(line for line in lines if line.strip())
    #
    #         # Handle inline content tags
    #         if elem.name in inline_content_tags:
    #             content = ' '.join(elem.stripped_strings)
    #             return f"{indent}<{elem.name}{attrs}>{content}</{elem.name}>"
    #
    #         # Handle structural and nested elements
    #         lines = [f"{indent}<{elem.name}{attrs}>"]
    #         for child in elem.children:
    #             if isinstance(child, NavigableString):
    #                 text = child.strip()
    #                 if text:
    #                     lines.append(f"{indent}{' ' * indent_size}{text}")
    #             else:
    #                 lines.append(format_element(child, level + 1))
    #         lines.append(f"{indent}</{elem.name}>")
    #
    #         return '\n'.join(line for line in lines if line.strip())
    #
    #     # Store PHP blocks
    #     php_blocks = {}
    #     php_counter = 0
    #
    #     def save_php(match):
    #         nonlocal php_counter
    #         placeholder = f"PHP_PLACEHOLDER_{php_counter}"
    #         php_blocks[placeholder] = match.group(0)
    #         php_counter += 1
    #         return placeholder
    #
    #     # Save PHP code
    #     html_with_placeholders = re.sub(r'<\?php.*?\?>', save_php, html_content, flags=re.DOTALL)
    #
    #     # Parse HTML
    #     soup = BeautifulSoup(html_with_placeholders, 'html.parser')
    #
    #     # Format HTML
    #     formatted = '\n'.join(
    #         format_element(child, 0)
    #         for child in soup.children
    #         if not isinstance(child, NavigableString) or child.strip()
    #     )
    #
    #     # Restore PHP code
    #     for placeholder, php_code in php_blocks.items():
    #         formatted = formatted.replace(placeholder, php_code)
    #
    #     # Fix PHP tags
    #     formatted = formatted.replace("&lt;?php", "<?php")
    #     formatted = formatted.replace("?&gt;", "?>")
    #
    #     return formatted

    def remove_extra_spaces(self,html_parser):
        inline_tags = ['a', 'span', 'button', 'div', 'td', 'p','h3','h1','h2','h4','h5','h6','li','img','b']
        for tag in inline_tags:
            pattern = f'<{tag}([^>]*)>\s*([^<]*)\s*</{tag}>'
            html_parser = re.sub(pattern, lambda m: f'<{tag}{m.group(1)}>{m.group(2).strip()}</{tag}>', html_parser)

        return html_parser

    def remove_sub_snippet_sections(self,html_parser):
        # Parse the HTML content
        soup = BeautifulSoup(html_parser, 'html.parser')

        sections = soup.find_all('section', class_='o_replace_section_div')
        for sec in sections:
            sec.name = 'div'
        return soup.prettify()

    def update_snippet_ids(self, view_name):
        seo_view = self.env['automated_seo.view'].search([('name','=',view_name)],limit=1)
        website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)

        version = self.env['website.page.version'].search(['&',('view_id', '=', seo_view.id),('status', '=', True)],limit=1)

        page = self.env['automated_seo.page'].search(['&',('page_name', '=', view_name),('version_id','=',version.id)], limit=1)
        html_parser = website_page.view_id.arch_db
        soup = BeautifulSoup(html_parser, "html.parser")
        sections = soup.find_all('section', {'data-snippet': True})
        snippet_ids = []
        if not page:
            page = self.env['automated_seo.page'].create({
                'page_name': view_name,
                'version_id':version.id
            })
            for section in sections:
                new_data_snippet_id = section.get('data-snippet') + '-' + self.generate_hash()
                snippet_ids.append(new_data_snippet_id)
                section['data-snippet'] = new_data_snippet_id


            for section in sections:
                snippet_id = section.get('data-snippet')
                orginal_snippet_id = snippet_id.split('-')[0]
                snippet_records = self.env['automated_seo.mapper'].search([('snippet_id', '=', orginal_snippet_id)],limit=1).php_tags.read(['element_class', 'php_tag', 'image_name'])
                snippet_style_records = self.env['automated_seo.mapper'].search([('snippet_id', '=', orginal_snippet_id)],limit=1).style.read(['name', 'link'])
                for snippet_style_record in snippet_style_records:
                    css_link = snippet_style_record.get('link')
                    if not self.env['automated_seo.page_header_link'].search([('css_link','=',css_link),('view_version_id','=',version.id),('view_id','=',seo_view.id)]):
                        self.env['automated_seo.page_header_link'].create({
                            'view_version_id':version.id,
                            'css_link':css_link,
                            'view_id':seo_view.id
                        })
                for snippet_record in snippet_records:
                    php_class = snippet_record.get('element_class')
                    php_tags = section.find_all(class_=php_class)
                    if len(php_tags)>1:
                        for php_tag in php_tags:
                            new_php_tag_class = php_class + self.generate_hash(length=6)
                            php_tag['class'] = [new_php_tag_class if cls == php_class else cls for cls in php_tag['class']]
                            self.env['automated_seo.snippet_mapper'].create({
                                'snippet_id': snippet_id,
                                'php_tag': snippet_record.get('php_tag'),
                                'element_class': new_php_tag_class,
                                'image_name': snippet_record.get('image_name'),
                                'version_id':version.id,
                                'page':page.id
                            })
                    else:
                        self.env['automated_seo.snippet_mapper'].create({
                            'snippet_id': snippet_id,
                            'php_tag': snippet_record.get('php_tag'),
                            'element_class': php_class,
                            'image_name': snippet_record.get('image_name'),
                            'version_id':version.id,
                            'page': page.id

                        })
            for tag in soup.find_all(class_=True):
                tag['class'] = [cls for cls in tag['class']
                                if cls not in ['sub_card']]

                if not tag['class']:
                    del tag['class']
            website_page.view_id.arch_db = soup.prettify()
            website_page.view_id.arch = soup.prettify()
            return soup.prettify()

        for section in sections:
            if len(section.get('data-snippet').split('-')) != 2:
                new_data_snippet_id = section.get('data-snippet') + '-' + self.generate_hash()
                snippet_ids.append(new_data_snippet_id)
                section['data-snippet'] = new_data_snippet_id
                orginal_snippet_id = new_data_snippet_id.split('-')[0]
                snippet_records = self.env['automated_seo.mapper'].search([('snippet_id', '=', orginal_snippet_id)],
                                                                          limit=1).php_tags.read(
                    ['element_class', 'php_tag', 'image_name'])
                snippet_style_records = self.env['automated_seo.mapper'].search(
                    [('snippet_id', '=', orginal_snippet_id)], limit=1).style.read(['name', 'link'])
                for snippet_style_record in snippet_style_records:
                    css_link = snippet_style_record.get('link')
                    if not self.env['automated_seo.page_header_link'].search(
                            [('css_link', '=', css_link),
                             ('view_version_id', '=', version.id),
                             ('view_id', '=', seo_view.id)]):
                        self.env['automated_seo.page_header_link'].create({
                            'view_version_id': version.id,
                            'css_link': css_link,
                            'view_id': seo_view.id
                        })

                for snippet_record in snippet_records:
                    php_class = snippet_record.get('element_class')
                    php_tags = section.find_all(class_=php_class)
                    if len(php_tags)!=1:
                        for php_tag in php_tags:
                            new_php_tag_class = php_class + self.generate_hash(length=6)
                            php_tag['class'] = [new_php_tag_class if cls == php_class else cls for cls in php_tag['class']]
                            self.env['automated_seo.snippet_mapper'].create({
                                'snippet_id': new_data_snippet_id,
                                'php_tag': snippet_record.get('php_tag'),
                                'element_class': new_php_tag_class,
                                'image_name': snippet_record.get('image_name'),
                                'version_id':version.id,
                                'page': page.id

                            })
                    else:
                        self.env['automated_seo.snippet_mapper'].create({
                            'snippet_id': new_data_snippet_id,
                            'php_tag': snippet_record.get('php_tag'),
                            'element_class': php_class,
                            'image_name': snippet_record.get('image_name'),
                            'version_id': version.id,
                            'page': page.id

                        })
                for tag in soup.find_all(class_=True):
                    tag['class'] = [cls for cls in tag['class']
                                    if cls not in ['sub_card']]

                    if not tag['class']:
                        del tag['class']
                website_page.view_id.arch_db = soup.prettify()
                website_page.view_id.arch = soup.prettify()

    def handle_img_change(self, view_name):
        website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
        html_parser = website_page.view_id.arch_db
        soup = BeautifulSoup(html_parser, "html.parser")
        for img in soup.select('img'):
            url = img.get('src')
            img_tag_classes  = img.get("class",[])
            if url and url.startswith("/web/image/"):
                image_name = url.split('/')[-1]
                image_id = int(url.split('/')[-2].split('-')[0])
                attachment = self.env['ir.attachment'].search([('id', '=', image_id)])
                name, ext = image_name.rsplit('.', 1)
                hash_suffix = self.generate_hash()
                new_image_name = f"{name}_{hash_suffix}.{ext}"
                if f'o_au_img_{name}_{image_id}' not in img_tag_classes:
                    img['class'] = [cls for cls in img['class'] if
                                    not (cls.startswith('o_au_img_') or cls.startswith('o_imagename_'))]

                    img['class'].append(f'o_au_img_{name}_{image_id}')
                    img['class'].append(f'o_imagename_{new_image_name}')
                    if attachment:
                        processed_image = self.process_image_with_params(attachment=attachment, img_tag=img)
                        # print("uploaded successfully=======================")

                        # new_image_data = attachment.datas
                        # new_image = base64.b64decode(new_image_data)
                        # image_file = io.BytesIO(processed_image)
                        self.upload_file_to_s3(file=processed_image, view_name=view_name, s3_filename=new_image_name)

                        # temp_folder_path = Path('./temp')
                        # temp_folder_path.mkdir(parents=True, exist_ok=True)
                        # file_path = temp_folder_path / f"{new_image_name}"
                        # with open(file_path, 'wb') as image_file:
                        #     # Check if processed_image is BytesIO and get the byte content
                        #     if isinstance(processed_image, io.BytesIO):
                        #         processed_image.seek(0)  # Move to the start of the BytesIO stream
                        #         image_data = processed_image.read()  # Read as bytes
                        #     else:
                        #         image_data = processed_image  # Assume it's already in bytes
                        #     if image_data:
                        #         image_file.write(image_data)
                        #     else:
                        #         raise ValueError("Image data is None after processing.")

                        website_page.view_id.arch_db = soup.prettify()
                        website_page.view_id.arch = soup.prettify()
        return str(self.handle_dynamic_img_tag(view_name=view_name))

    def handle_dynamic_img_tag(self,view_name):
        website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
        html_parser = website_page.view_id.arch_db
        soup = BeautifulSoup(html_parser, "html.parser")

        for img in soup.select('img'):
            url = img.get('src')
            if url and url.startswith("/web/image/"):
                image_name = url.split('/')[-1]
                image_id = int(url.split('/')[-2].split('-')[0])
                attachment = self.env['ir.attachment'].search([('id', '=', image_id)])
                image_data = base64.b64decode(attachment.datas) if attachment.datas else None
                name, ext = image_name.rsplit('.', 1)
                height = None
                width = None
                if ext != 'svg':
                    try:
                        # Try to open the image directly with Pillow
                        image = Image.open(io.BytesIO(image_data))
                        width, height = image.size
                    except UnidentifiedImageError as e:
                        UserError(f"Error :- {e}")
                else:
                    try:
                        svg_content = image_data.decode("utf-8")
                        root = ET.fromstring(svg_content)

                        width = root.attrib.get("width")
                        height = root.attrib.get("height")

                        if not width or not height:
                            view_box = root.attrib.get("viewBox")
                            if view_box:
                                _, _, width, height = view_box.split()

                    except Exception as e:
                        UserError(f"Error :- {e}")
                if height:
                    img['heigth'] = int(float(height))

                if width:
                    img['width'] = int(float(width))

                img_tag_classes = img.get("class", [])
                element = next((cls for cls in img_tag_classes if cls.startswith('o_imagename')), None)

                if element:
                    new_image_name = element.split('_',2)[-1]
                    odoo_img_url = f"https://assets.bacancytechnology.com/inhouse/{view_name.replace(' ','').lower()}/{new_image_name}"
                    img['src'] = odoo_img_url
                    img['data-src'] = odoo_img_url



            for attr in ["data-mimetype", "data-original-id", "data-original-src", "data-resize-width",
                         "data-scale-x","data-scale-y","data-height","data-aspect-ratio","data-width",
                         "data-bs-original-title","aria-describedby","data-shape","data-file-name","data-shape-colors",
                         "data-gl-filter","data-quality","data-scroll-zone-start","data-scroll-zone-end","style"," data-shape-colors"]:

                if img.has_attr(attr):
                    del img[attr]

        return str(self.handle_dynamic_img_tag2(html_parser=str(soup.prettify())))


    def handle_dynamic_img_tag2(self,html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")
        base_url_php = "<?php echo BASE_URL_IMAGE; ?>"
        for img in soup.select('img'):
            url = img.get('src')

            img['src'] = url.replace("https://assets.bacancytechnology.com/", base_url_php)
            img['data-src'] = url.replace("https://assets.bacancytechnology.com/", base_url_php)
            try:
                if img.get('height') :
                    img['height'] = int(float(img.get('height')))
            except ValueError as e:
                img['height'] = img.get('height')
            try:
                if img.get('height') :
                    img['width'] = int(float(img.get('width')))
            except ValueError as e:
                img['width'] = img.get('width')

        return str(soup.prettify())

    # def update_images_in_html_and_php(self, view_name):
    #     website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
    #     html_parser = website_page.view_id.arch_db
    #     # html_parser = self.replace_section_with_div(html_content=html_parser)
    #     soup = BeautifulSoup(html_parser, "html.parser")
    #     sections = soup.find_all('section', {'data-snippet': True})
    #     snippet_ids = []
    #     for section in sections:
    #         snippet_ids.append(section.get('data-snippet'))
    #     for i in range(len(sections)):
    #         section = sections[i]
    #         snippet_records = self.env['automated_seo.snippet_mapper'].search([('snippet_id', '=', snippet_ids[i])])
    #         if snippet_records:
    #             for snippet_record in snippet_records:
    #                 element = snippet_record.read(['element_class', 'php_tag', 'image_name'])[0]
    #                 if element.get('image_name'):
    #                     tags = section.find_all(class_=element.get('element_class'))
    #                     for tag in tags:
    #                         new_src = tag.get('src')
    #                         old_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')
    #
    #                         if new_src:
    #                             new_image_name = new_src.split('/')[-1]  # Extract just the file name from the src
    #                             old_img_tag = old_tag_soup.find('img')
    #                             old_img_name = element.get('image_name')
    #                             if old_img_tag and old_img_name != new_image_name:
    #                                 hash_suffix = self.generate_hash()
    #                                 name, ext = new_image_name.rsplit('.', 1)
    #                                 new_image_name = f"{name}_{hash_suffix}.{ext}"
    #
    #                                 image_id = int(new_src.split('/')[-2].split('-')[0])
    #                                 attachment = self.env['ir.attachment'].search([('id', '=', image_id)])
    #
    #                                 if attachment:
    #                                     new_image_data = attachment.datas
    #                                     new_image = base64.b64decode(new_image_data)
    #                                     image_file = io.BytesIO(new_image)
    #                                     self.upload_file_to_s3(file=image_file,s3_filename=new_image_name)
    #
    #                                 image_path = '/'.join(new_src.split('/')[:-1])
    #                                 tag['src'] = image_path + '/' + new_image_name
    #                                 tag['data-src'] = image_path + '/' + new_image_name
    #
    #                                 website_page.view_id.arch = soup.prettify()
    #
    #                                 old_img_tag['src'] = f'<?php echo BASE_URL_IMAGE; ?>Inhouse/{new_image_name}'
    #                                 old_img_tag['data-src'] = f'<?php echo BASE_URL_IMAGE; ?>Inhouse/{new_image_name}'
    #                                 php_mapper_record = self.env['automated_seo.snippet_mapper'].browse(element['id'])
    #                                 php_mapper_record.write({
    #                                     'php_tag': str(old_tag_soup),
    #                                     'image_name': str(new_image_name)
    #                                 })
    #                                 attachment.write({
    #                                     'name': new_image_name
    #                                 })
    #
    #                                 tag.replace_with(old_tag_soup)
    #     return soup.prettify()

    def replace_php_tags_in_html(self, html_parser):

        soup = BeautifulSoup(html_parser, "html.parser")

        html_parser = self.remove_sub_snippet_sections(str(soup.prettify()))

        soup = BeautifulSoup(html_parser, "html.parser")

        sections = soup.find_all('section', {'data-snippet': True})
        snippet_ids = []

        for section in sections:
            snippet_ids.append(section.get('data-snippet'))


        for section in sections:
            updated_section = self.replace_php_var_tag(section)
            section = updated_section
            snippet_records = self.env['automated_seo.snippet_mapper'].search(
                [('snippet_id', '=', section.get('data-snippet'))])

            if snippet_records:
                for snippet_record in snippet_records:
                    element = snippet_record.read(['element_class', 'php_tag', 'image_name'])[0]
                    element_class = element.get('element_class')
                    tags = section.find_all(class_=element_class)
                    for tag in tags:
                        old_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')
                        if element_class.startswith("o_au_php_form_"):
                            contact_btn = tag.find('button', attrs={'name': 'contactBtn'})
                            if contact_btn:
                                if not len(contact_btn.find_all(
                                        class_=lambda x: x and x.startswith("o_au_php_var_tag_"))) > 0:
                                    contact_btn["class"].append("o_au_php_var_tag_btn_name")
                            php_var_tags = tag.find_all(class_=lambda x: x and x.startswith("o_au_php_var_tag_"))
                            old_tag_soup = self.replace_php_var_value(str(old_tag_soup),php_var_tags)
                        tag.replace_with(old_tag_soup)


        for tag in soup.find_all('t'):
            tag.unwrap()
        wrap_tag = soup.find(id="wrap")
        wrap_tag.unwrap()
        sections = soup.find_all(class_="ou_section")
        for section in sections:
            # if section:
            section.unwrap()
        body = soup.find("body")
        if body:
            body.unwrap()
        return str(soup)


    def replace_php_var_value(self,old_tag_soup,php_var_tags):

        for sub_tag in php_var_tags:
            tag_content = str(sub_tag.get_text(strip=True)).strip()
            var_name = next((cls for cls in sub_tag['class'] if cls.startswith("o_au_php_var_tag_")), None)[len("o_au_php_var_tag_"):]
            if var_name:
                pattern = rf'\${var_name}\s*=\s*(?:".*?"|null);'
                new_php_var = f'${var_name} = "{tag_content}";'
                old_tag_soup = re.sub(pattern, new_php_var, old_tag_soup)
        return BeautifulSoup(old_tag_soup, 'html.parser').prettify()


    def replace_php_var_tag(self, section):

        # updated_section = self.replace_strong_em_u_tag(section)
        soup = BeautifulSoup(str(section.prettify()), "html.parser")

        for tag in section.find_all(class_="o_au_php_var"):

            var_name = tag.get('data-php-var')
            var_type = tag.get("data-php-const-var")

            if var_name:

                if len(tag.find_all("strong")) > 0:
                    tag["class"].append("o_strong")
                if len(tag.find_all("b")) > 0:
                    tag["class"].append("o_b")
                if len(tag.find_all(class_="font-bold")) > 0:
                    tag["class"].append("font-bold")
                if len(tag.find_all(class_="text-underline")) > 0:
                    tag["class"].append("text-underline")

                for i_tag in tag.find_all("i"):
                    i_tag.unwrap()
                    tag.wrap(soup.new_tag('i'))
                    break

                php_tag = BeautifulSoup(
                    f'<?php echo constant("{var_name}") ?>' if var_type == "1" else f"<?php echo ${var_name} ?>",
                    'html.parser')

                if len(tag.find_all("a")) > 0:
                    new_a_tag = soup.new_tag('a')

                    new_a_tag['href'] = tag.find_all("a")[0]['href']
                    if tag.find_all("a")[0].get('target'):
                        new_a_tag['target'] = tag.find_all("a")[0].get('target')
                    new_a_tag.append(php_tag)
                    tag.replace_with(new_a_tag)
                elif "font-bold" in tag["class"] or "text-underline" in tag["class"]:
                    tag.string = ""
                    tag.append(php_tag)
                elif "o_strong" in tag["class"]:
                    new_strong_tag = soup.new_tag("strong")
                    new_strong_tag.append(php_tag)
                    tag.replace_with(new_strong_tag)
                elif "o_b" in tag["class"]:
                    new_b_tag = soup.new_tag("b")
                    new_b_tag.append(php_tag)
                    tag.replace_with(new_b_tag)
                else:
                    tag.replace_with(php_tag)

        return section


    def replace_strong_em_u_tag(self, section):
        soup = BeautifulSoup(str(section.prettify()), "html.parser")
        for tag in section.find_all(['strong', 'b']) + section.find_all(class_="font-bold"):
            new_tag_name = ""
            new_tag_class_name = ""
            if tag.name == "strong":
                new_tag_name = "strong"
            elif tag.name == "b":
                new_tag_name = "b"
            else:
                new_tag_name = "span"
                new_tag_class_name = "font-bold"

            new_tag = soup.new_tag(f'{new_tag_name}')
            new_tag["class"] = [f'{new_tag_class_name}']
            new_tag.extend(tag.contents)
            tag.replace_with(new_tag)

        for em_tag in section.find_all('em'):
            i_tag = soup.new_tag('i')
            i_tag.extend(em_tag.contents)
            em_tag.replace_with(i_tag)

        for u_tag in section.find_all('u'):
            span_tag = soup.new_tag('span')
            span_tag["class"] = ['text-underline']
            span_tag.extend(u_tag.contents)
            u_tag.replace_with(span_tag)

        return section

    def remove_odoo_classes_from_tag(self, html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")
        class_to_remove = ['oe_structure', 'remove', 'custom-flex-layout',
                           'custom-left-section', 'custom-right-section','float-start', 'rounded-circle', 'rounded','img', "img-fluid", "me-auto"]


        tech_stack_cells = soup.find_all('td', class_='o_tech_stack')

        # Iterate over each <td> element
        for cell in tech_stack_cells:
            # Get the text content, split by '|', and clear the cell's content
            descriptions = cell.text.split('|')
            cell.clear()

            # Create a <span> for each description and append it to the cell
            for description in descriptions:
                span = soup.new_tag('span')
                span.string = description.strip()  # Trim whitespace
                cell.append(span)
        for tag in soup.find_all():
            if tag.get('class'):
                tag['class'] = [cls for cls in tag['class']
                                if not cls.startswith('o_') and cls not in class_to_remove]

                if not tag['class']:
                    del tag['class']

            for attr in ['data-bs-original-title','aria-describedby', 'data-php-const-var','data-php-var','contenteditable', 'data-max-length']:
                if tag.has_attr(attr):
                    del tag[attr]
            for attr in ['data-name', 'data-snippet', 'style', 'order-1', 'md:order-1','title']:
                if tag.name!='img':
                    tag.attrs.pop(attr, None)

            # for tag in soup.find_all(class_=class_to_remove):
            #     # Replace the tag with its contents
            #     tag.replace_with(*tag.contents)
            # tag.replace_with( tag.decode_contents())


        for tag in soup.find_all(True):
            if 'itemscope' in tag.attrs and (tag.attrs['itemscope'] == 'itemscope' or tag.attrs['itemscope'] == 'acceptedAnswer'):
                tag.attrs['itemscope'] = None  # Keep as a flag attribute


        html_content = html.unescape(str(soup))

        # Convert remaining XML entities and &nbsp;
        xml_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&apos;': "'",
            '&quot;': '"',
            '&nbsp;': ' '
        }
        for entity, char in xml_entities.items():
            html_content = html_content.replace(entity, char)

        # Parse the modified content back into BeautifulSoup
        html_content = self.remove_br_tags(html_content=html_content)

        return html_content

    def action_download_parsed_html(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=automated_seo.view&id={}&field=parse_html_binary&filename_field=parse_html_filename&download=true'.format(
                self.id),
            'target': 'self',
        }

    def upload_file_to_s3(self, file, s3_filename, view_name=None):

        content_type, _ = mimetypes.guess_type(s3_filename)

        content_type = content_type or 'application/octet-stream'
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          )
        try:
            if view_name:
                s3_key = f'inhouse/{view_name.replace(" ","").lower()}/{s3_filename}'
            else:
                s3_key = f'inhouse/{s3_filename}'
            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, s3_key, ExtraArgs={
                'ContentType': content_type})


        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                print("Access Denied. Please check your AWS credentials and bucket permissions.")
            elif e.response['Error']['Code'] == 'NoSuchBucket':
                print(f"The bucket {AWS_STORAGE_BUCKET_NAME} does not exist.")
            else:
                print(f"An error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def delete_img_folder_from_s3(self,view_name):
        folder_name = view_name.replace(" ", "").lower()
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        try:
            response = s3.list_objects_v2(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=f'inhouse/{folder_name}/')

            if 'Contents' in response:
                objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                s3.delete_objects(
                    Bucket=AWS_STORAGE_BUCKET_NAME,
                    Delete={'Objects': objects_to_delete}
                )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def remove_br_tags(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all <br> tags
        br_tags = soup.find_all('br')

        # Iterate through each <br> tag
        for br in br_tags:
            # Check if the parent is a form tag
            if not br.find_parent('form'):
                br.decompose()  # Remove <br> tag

        # Return the modified HTML content
        return soup.prettify()

    def handle_dynamic_anchar_tag(self,html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")
        link_css_classes = ['text-primary', 'font-bold']
        base_url_php = "<?php echo BASE_URL; ?>"
        for a in soup.select('a:not(.btn)'):
            # Get current classes on the <a> tag or initialize with an empty list
            # current_classes = a.get('class', [])
            #
            # # Add each class from link_css_classes if it’s not already present
            # for css_class in link_css_classes:
            #     if css_class not in current_classes:
            #         current_classes.append(css_class)
            #
            # # Update the class attribute on the <a> tag
            # a['class'] = current_classes

            url = a.get('href')
            if url and url.startswith("https://www.bacancytechnology.com/"):
                a['href'] = url.replace("https://www.bacancytechnology.com/", base_url_php)

        return str(soup.prettify())

    def remove_empty_tags(self,html_parser):
        soup = BeautifulSoup(html_parser, 'html.parser')
        self_closing_tags = {"img", "input", "hr", "meta", "link"}

        def remove_empty(tag):
            if tag.name == "section" or tag.name in self_closing_tags:
                return

            if not tag.contents or all(
                    isinstance(content, str) and content.strip() == "" for content in tag.contents
            ):
                parent = tag.parent
                tag.decompose()  # Remove the tag
                if parent:  # Recursively check the parent
                    remove_empty(parent)

        all_tags = soup.find_all()
        for tag in all_tags:
            remove_empty(tag)

        return soup.prettify()
    # def remove_empty_tags(self, html_parser):
    #     soup = BeautifulSoup(html_parser, 'html.parser')
    #
    #     self_closing_tags = {"img", "input", "hr", "meta", "link"}
    #
    #     def is_empty_tag(tag):
    #
    #         if tag.name in self_closing_tags:
    #             return False
    #         pattern = f'<{tag.name}[^>]*?></\s*{tag.name}>'
    #         tag = self.normalize_text(tag)
    #         print("================")
    #         print(tag)
    #         print("================")
    #
    #         # pattern = r'^<([a-zA-Z][a-zA-Z0-9]*)[^>]*>\s*</\1>$'
    #
    #         if re.match(pattern, tag):
    #             return True
    #
    #     def remove_empty_tags_recursively(tag):
    #
    #         """Recursively removes a tag if it and its parent are empty."""
    #         if is_empty_tag(tag):
    #             parent = tag.find_parent()
    #             tag.decompose()
    #             if parent and is_empty_tag(parent):
    #                 remove_empty_tags_recursively(parent)
    #
    #     all_tags = soup.find_all()
    #     for tag in all_tags:
    #         remove_empty_tags_recursively(tag)
    #
    #     return soup.prettify()

    # def remove_empty_tags(self, html_parser):
    #
    #     soup = BeautifulSoup(html_parser, 'html.parser')
    #
    #     all_tags = soup.find_all()
    #
    #     for tag in all_tags:
    #         tag_string = str(tag)
    #
    #
    #         pattern = f'<{tag.name}[^>]*?></\s*{tag.name}>'
    #
    #         # Check if it's an empty tag
    #         if re.match(pattern, tag_string):
    #             tag.decompose()
    #         pattern = f'<{tag.name}></{tag.name}>'
    #         if re.match(pattern, tag_string):
    #             tag.decompose()
    #     return soup.prettify()


    # Function to remove BOM characters from all text elements
    def remove_bom(self,html_parser):

        soup = BeautifulSoup(html_parser, "html.parser")
        for element in soup.find_all(string=True):  # Iterate over all strings
            if "\ufeff" in element:  # Check if BOM character exists
                cleaned_text = element.replace("\ufeff", "")  # Remove BOM
                element.replace_with(cleaned_text)  # Replace with cleaned text
            elif "\u200b" in element:
                cleaned_text = element.replace("\u200b", "")  # Remove BOM
                element.replace_with(cleaned_text)


        return soup.prettify()



class IrUiView(models.Model):
    _inherit = 'ir.ui.view'
    page_id = fields.Many2one('automated_seo.view', string="View Record",ondelete='cascade')

    @api.model
    def create(self, vals):
        return super(IrUiView, self).create(vals)

    def write(self,vals):
        record = super(IrUiView, self).write(vals)
        seo_view = self.env['automated_seo.view'].search([('page_id','=',self.id)])
        version = self.env['website.page.version'].search(['&',('view_id', '=', seo_view.id),('status', '=', True)])
        if version:
            if 'arch' in vals:
                version.view_arch = self.arch

        return record




class WebsitePage(models.Model):
    _inherit = 'website.page'

    def _get_next_page_id(self):
        last_view = self.env['automated_seo.view'].search([], order='id desc', limit=1)
        if last_view and last_view.unique_page_id:
            last_id_num = int(last_view.unique_page_id[4:])
            return f'PAGE{str(last_id_num + 1).zfill(4)}'
        else:
            return 'PAGE0001'

    @api.model
    def create(self, vals):
        record = super(WebsitePage, self).create(vals)
        if not self.env.context.get('from_seo_view'):
            seo_view = self.env['automated_seo.view'].with_context(from_ir_view=True).create({
                'name': record.name,
                'website_page_id': record.id,
                'unique_page_id': self._get_next_page_id()
            })
            record.view_id.page_id = seo_view.id

        return record

