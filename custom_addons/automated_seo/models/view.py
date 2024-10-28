from odoo import models, fields, api
from bs4 import BeautifulSoup
import  html
import base64
import boto3
import io
import random
import string
from odoo.exceptions import UserError
# import os
from botocore.exceptions import ClientError
import re
import random


# from dotenv import load_dotenv
AWS_ACCESS_KEY_ID = 'AKIA4XF7TG4AOK3TI2WY'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'bacancy-website-images'

class View(models.Model):
    _name = 'automated_seo.view'
    _description = 'Automated SEO View'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    page_id = fields.One2many('ir.ui.view', 'page_id', string="Views")
    unique_page_id = fields.Char(string="Page Id")
    website_page_id = fields.Many2one('website.page', string="Website Page", readonly=True)
    parse_html = fields.Text(string="Parse HTML")
    parse_html_binary = fields.Binary(string="Parsed HTML File", attachment=True)
    parse_html_filename = fields.Char(string="Parsed HTML Filename")
    version = fields.One2many('website.page.version','view_id',string="Version")


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
        record  = super(View, self).create(vals)
        self.env['website.page.version'].create({
            'name' : 'v1.0.0',
            'description' : 'First Version',
            'view_id':record.id,
            'page_id':website_page.id,
            'view_arch':website_page.view_id.arch,
            'user_id':self.env.user.id,
            'status':True
        })
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
                    vals['unique_page_id'] = formatted_name + str(random.randint(10000, 99999))
        return super(View, self).write(vals)

    def action_view_website_page(self):
        self.ensure_one()
        if not self.page_id:
            raise UserError("No website page associated with this record.")
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_page_id.url,
            'target': 'self',
        }

    def action_edit_website_page(self):
        """Opens the related website page in edit mode."""
        self.ensure_one()
        if not self.page_id:
            raise UserError("No website page associated with this record.")
        base_url = self.website_page_id.url
        # Remove trailing slash if present
        base_url = base_url.rstrip('/')

        return {
            'type': 'ir.actions.act_url',
            'url': f'{base_url}?enable_editor=1',
            'target': 'self',
        }

    def unlink(self):
        for view in self:
            try:
                versions = self.env['website.page.version'].search([('view_id', '=', view.id)])
                if versions:
                    versions.unlink()
                # Delete associated website page
                if view.page_id:
                    website_page = self.env['website.page'].search([('view_id', 'in', view.page_id.ids)], limit=1)
                    if website_page:
                        website_page.unlink()
                seo_page = self.env['automated_seo.page'].search([('page_name', '=', view.name)], limit=1)
                if seo_page:
                    seo_page.unlink()

            except Exception as e:
                print(f"Error while deleting associated records for view {view.name}: {str(e)}")
                raise

        return super(View, self).unlink()

    def generate_hash(self,length=6):
        """Generate a random string of fixed length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def action_custom_button(self):
        view_name = self.env.context.get('view_name', 'Unknown')
        # html_parser = self.php_mapper(view_name=view_name)
        self.update_snippet_ids(view_name)
        html_parser = self.update_images_in_html_and_php(view_name=view_name)
        html_parser = self.replace_php_tags_in_html(html_parser=html_parser)
        if html_parser:
            html_parser = self.remove_odoo_classes_from_tag(html_parser)
        if html_parser:
            soup = BeautifulSoup(html_parser, "html.parser")
            html_parser = soup.prettify()
            html_parser = html.unescape(html_parser)
            html_parser = self.remove_extra_spaces(html_parser = html_parser)
            file = base64.b64encode(html_parser.encode('utf-8'))
            version = self.env['website.page.version'].search(['&',('view_id','=',self.id),("status", "=", True)],limit =1)
            file_name = f"{view_name}_{version.id}_parsed.html"
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

    def remove_extra_spaces(self,html_parser):
        inline_tags = ['a', 'span', 'button', 'div', 'td', 'p','h3']
        for tag in inline_tags:
            pattern = f'<{tag}([^>]*)>\s*([^<]*)\s*</{tag}>'
            html_parser = re.sub(pattern, lambda m: f'<{tag}{m.group(1)}>{m.group(2).strip()}</{tag}>', html_parser)

        return html_parser

    def remove_sub_snippet_sections(self,html_parser):
        # Parse the HTML content
        soup = BeautifulSoup(html_parser, 'html.parser')

        # Find the <section> tag and unwrap it (remove the tag but keep its contents)
        section = soup.find(class_='remove')
        if section:
            section.unwrap()

        # Print the modified HTML
        print(soup.prettify())
        return soup.prettify()

    def update_snippet_ids(self, view_name):
        page = self.env['automated_seo.page'].search([('page_name', '=', view_name)], limit=1)
        website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
        html_parser = website_page.view_id.arch_db
        html_parser = self.remove_sub_snippet_sections(html_parser=html_parser)
        # html_parser  = self.replace_section_with_div(html_content=html_parser)
        soup = BeautifulSoup(html_parser, "html.parser")
        sections = soup.find_all('section', {'data-snippet': True})
        snippet_ids = []
        if not page:
            page = self.env['automated_seo.page'].create({
                'page_name': view_name
            })
            for section in sections:
                snippet_ids.append(section.get('data-snippet') + '-' + self.generate_hash())


            for i in range(len(sections)):
                sections[i]['data-snippet'] = snippet_ids[i]
                orginal_snippet_id = snippet_ids[i].split('-')[0]
                snippet_records = self.env['automated_seo.mapper'].search([('snippet_id', '=', orginal_snippet_id)],limit=1).php_tags.read(['element_class', 'php_tag', 'image_name'])

                for snippet_record in snippet_records:
                    php_class = snippet_record.get('element_class')
                    # php_tags = sections[i].find_all(class_=php_class)
                    # for php_tag in php_tags:
                        # new_php_tag_class = php_class + self.generate_hash(length=6)
                        # php_tag['class'] = [new_php_tag_class if cls == php_class else cls for cls in php_tag['class']]
                    self.env['automated_seo.snippet_mapper'].create({
                        'snippet_id': snippet_ids[i],
                        'php_tag': snippet_record.get('php_tag'),
                        'element_class': php_class,
                        'image_name': snippet_record.get('image_name'),
                    })
                website_page.view_id.arch = soup.prettify()            # html_parser = self.replace_div_with_section(html_content=str(soup))
            # soup = BeautifulSoup(html_parser, "html.parser")
            # website_page.view_id.arch = soup.prettify()
            # website_page.view_id.arch_db = soup.prettify()
            # print(website_page.view_id.arch_db)
            # print(website_page.view_id.arch)

        for section in sections:
            if len(section.get('data-snippet').split('-')) != 2:
                new_data_snippet_id = section.get('data-snippet') + '-' + self.generate_hash()
                snippet_ids.append(new_data_snippet_id)
                section['data-snippet'] = new_data_snippet_id
                orginal_snippet_id = new_data_snippet_id.split('-')[0]
                snippet_records = self.env['automated_seo.mapper'].search([('snippet_id', '=', orginal_snippet_id)],
                                                                          limit=1).php_tags.read(
                    ['element_class', 'php_tag', 'image_name'])
                for snippet_record in snippet_records:
                    self.env['automated_seo.snippet_mapper'].create({
                        'snippet_id': new_data_snippet_id,
                        'php_tag': snippet_record.get('php_tag'),
                        'element_class': snippet_record.get('element_class'),
                        'image_name': snippet_record.get('image_name'),
                    })
                website_page.view_id.arch = soup.prettify()

    def update_images_in_html_and_php(self, view_name):
        website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
        html_parser = website_page.view_id.arch_db
        # html_parser = self.replace_section_with_div(html_content=html_parser)
        soup = BeautifulSoup(html_parser, "html.parser")
        sections = soup.find_all('section', {'data-snippet': True})
        snippet_ids = []
        for section in sections:
            snippet_ids.append(section.get('data-snippet'))
        for i in range(len(sections)):
            section = sections[i]
            snippet_records = self.env['automated_seo.snippet_mapper'].search([('snippet_id', '=', snippet_ids[i])])
            if snippet_records:
                for snippet_record in snippet_records:
                    element = snippet_record.read(['element_class', 'php_tag', 'image_name'])[0]
                    if element.get('image_name'):
                        tags = section.find_all(class_=element.get('element_class'))
                        for tag in tags:
                            new_src = tag.get('src')
                            old_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')

                            if new_src:
                                new_image_name = new_src.split('/')[-1]  # Extract just the file name from the src
                                old_img_tag = old_tag_soup.find('img')
                                old_img_name = element.get('image_name')
                                if old_img_tag and old_img_name != new_image_name:

                                    hash_suffix = self.generate_hash()
                                    name, ext = new_image_name.rsplit('.', 1)
                                    new_image_name = f"{name}_{hash_suffix}.{ext}"

                                    image_id = int(new_src.split('/')[-2].split('-')[0])
                                    attachment = self.env['ir.attachment'].search([('id', '=', image_id)])

                                    if attachment:
                                        new_image_data = attachment.datas
                                        new_image = base64.b64decode(new_image_data)
                                        image_file = io.BytesIO(new_image)
                                        self.upload_file_to_s3(file=image_file,view_name=view_name,s3_filename=new_image_name)

                                    image_path = '/'.join(new_src.split('/')[:-1])
                                    tag['src'] = image_path + '/' + new_image_name
                                    tag['data-src'] = image_path + '/' + new_image_name

                                    website_page.view_id.arch = soup.prettify()

                                    old_img_tag['src'] = f'<?php echo BLOG_URL; ?>Inhouse/{new_image_name}'
                                    old_img_tag['data-src'] = f'<?php echo BLOG_URL; ?>Inhouse/{new_image_name}'
                                    php_mapper_record = self.env['automated_seo.snippet_mapper'].browse(element['id'])
                                    php_mapper_record.write({
                                        'php_tag': str(old_tag_soup),
                                        'image_name': str(new_image_name)
                                    })
                                    attachment.write({
                                        'name': new_image_name
                                    })

                                    tag.replace_with(old_tag_soup)
        return soup.prettify()

    def replace_php_tags_in_html(self, html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")
        sections = soup.find_all('section', {'data-snippet': True})
        snippet_ids = []
        for section in sections:
            snippet_ids.append(section.get('data-snippet'))

        for section in sections:
            snippet_records = self.env['automated_seo.snippet_mapper'].search(
                [('snippet_id', '=', section.get('data-snippet'))])

            if snippet_records:
                for snippet_record in snippet_records:
                    element = snippet_record.read(['element_class', 'php_tag', 'image_name'])[0]
                    element_class = element.get('element_class')
                    # print('====element=================')

                    # print(element)

                    tags = soup.find_all(class_=element_class)
                    for tag in tags:
                        # print('====tag=================')
                        # print(tag)
                        old_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')
                        # print('====element_class=================')

                        # print(element_class)
                        # print('====old_tag_soup=================')

                        # print(old_tag_soup)
                        tag.replace_with(old_tag_soup)
                        # print('=====================')


        for tag in soup.find_all('t'):
            tag.unwrap()
        wrap_tag = soup.find(id="wrap")
        wrap_tag.unwrap()
        return str(soup)

    def remove_odoo_classes_from_tag(self, html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")
        class_to_remove = ['oe_structure','data-bs-original-title', 'title', 'custom-flex-layout',
                           'custom-left-section', 'custom-right-section']

        for tag in soup.find_all(class_=True):
            tag['class'] = [cls for cls in tag['class']
                            if not cls.startswith('o_') and cls not in class_to_remove]

            if not tag['class']:
                del tag['class']

            for attr in ['data-name', 'data-snippet', 'style', 'order-1', 'md:order-1']:
                tag.attrs.pop(attr, None)
            sub_snippet_remove = ['remove']
            for tag in soup.find_all(class_=sub_snippet_remove):
                # Replace the tag with its contents
                tag.replace_with(*tag.contents)
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

    def upload_file_to_s3(self, file, s3_filename,view_name):
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          )
        try:
            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, f'Inhouse/{view_name}/{s3_filename}')
            print(f"File {s3_filename} uploaded successfully to bucket {AWS_STORAGE_BUCKET_NAME}!")
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDenied':
                print("Access Denied. Please check your AWS credentials and bucket permissions.")
            elif e.response['Error']['Code'] == 'NoSuchBucket':
                print(f"The bucket {AWS_STORAGE_BUCKET_NAME} does not exist.")
            else:
                print(f"An error occurred: {e}")
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


