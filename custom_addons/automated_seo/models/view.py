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
from PIL import Image
import os
from pathlib import Path

from soupsieve.css_types import pickle_register

from automated_seo.odoo.tools import pickle
from automated_seo.temp.process_image import processed_image

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
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The name must be unique!')
    ]


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
            import re
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

            return output

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None
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
        # html_parser = self.update_images_in_html_and_php(view_name=view_name)
        html_parser  = self.handle_dynamic_img_tag(view_name=view_name)
        print("================1===========")
        print(html_parser)
        print("===========================")

        html_parser = self.replace_php_tags_in_html(html_parser=html_parser)
        print("============2===============")
        # print(html_parser)
        print("===========================")
        html_parser = self.handle_dynamic_anchar_tag(html_parser=html_parser)
        print("============3===============")
        print(html_parser)
        print("===========================")
        if html_parser:
            html_parser = self.remove_odoo_classes_from_tag(html_parser)
            print("============4===============")
            print(html_parser)
            print("===========================")
        if html_parser:
            soup = BeautifulSoup(html_parser, "html.parser")
            html_parser = soup.prettify()
            html_parser = self.remove_extra_spaces(html_parser = html_parser)
            html_parser = self.remove_empty_tags(html_parser = html_parser)
            html_parser = self.remove_extra_spaces(html_parser = html_parser)
            html_parser = html.unescape(html_parser)

            file = base64.b64encode(html_parser.encode('utf-8'))
            version = self.env['website.page.version'].search(['&',('view_id','=',self.id),("status", "=", True)],limit =1)
            file_name = f"{view_name}_{version.name}.html"
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
        inline_tags = ['a', 'span', 'button', 'div', 'td', 'p','h3','h1','h2','h4','h5','h6','li','img']
        for tag in inline_tags:
            pattern = f'<{tag}([^>]*)>\s*([^<]*)\s*</{tag}>'
            html_parser = re.sub(pattern, lambda m: f'<{tag}{m.group(1)}>{m.group(2).strip()}</{tag}>', html_parser)

        return html_parser

    def remove_sub_snippet_sections(self,html_parser):
        # Parse the HTML content
        soup = BeautifulSoup(html_parser, 'html.parser')

        section = soup.find(class_='remove')
        if section:
            section.unwrap()
        return soup.prettify()

    def update_snippet_ids(self, view_name):
        page = self.env['automated_seo.page'].search([('page_name', '=', view_name)], limit=1)
        website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
        html_parser = website_page.view_id.arch_db
        html_parser  = self.remove_sub_snippet_sections(html_parser=html_parser)
        soup = BeautifulSoup(html_parser, "html.parser")
        sections = soup.find_all('section', {'data-snippet': True})
        snippet_ids = []
        # breakpoint()
        if not page:
            page = self.env['automated_seo.page'].create({
                'page_name': view_name
            })
            for section in sections:
                snippet_ids.append(section.get('data-snippet') + '-' + self.generate_hash())


            for section in sections:
                snippet_id = section.get('data-snippet')
                # breakpoint()
                orginal_snippet_id = snippet_id.split('-')[0]
                snippet_records = self.env['automated_seo.mapper'].search([('snippet_id', '=', orginal_snippet_id)],limit=1).php_tags.read(['element_class', 'php_tag', 'image_name'])

                for snippet_record in snippet_records:
                    php_class = snippet_record.get('element_class')
                    php_tags = soup.find_all(class_=php_class)
                    if len(php_tags)!=1:
                        for php_tag in php_tags:
                            new_php_tag_class = php_class + self.generate_hash(length=6)
                            php_tag['class'] = [new_php_tag_class if cls == php_class else cls for cls in php_tag['class']]
                            self.env['automated_seo.snippet_mapper'].create({
                                'snippet_id': snippet_id,
                                'php_tag': snippet_record.get('php_tag'),
                                'element_class': new_php_tag_class,
                                'image_name': snippet_record.get('image_name'),
                            })
                    else:
                        # breakpoint()
                        self.env['automated_seo.snippet_mapper'].create({
                            'snippet_id': snippet_id,
                            'php_tag': snippet_record.get('php_tag'),
                            'element_class': php_class,
                            'image_name': snippet_record.get('image_name'),
                        })
            for tag in soup.find_all(class_=True):
                tag['class'] = [cls for cls in tag['class']
                                if cls not in ['sub_card']]

                if not tag['class']:
                    del tag['class']
            website_page.view_id.arch_db = soup.prettify()
            website_page.view_id.arch = soup.prettify()            # html_parser = self.replace_div_with_section(html_content=str(soup))
                # html_parser = self.replace_div_with_section(html_content=str(soup))
            # soup = BeautifulSoup(html_parser, "html.parser")
            # website_page.view_id.arch = soup.prettify()
            # website_page.view_id.arch_db = soup.prettify()
            # print(website_page.view_id.arch_db)
            # print(website_page.view_id.arch)
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

                for snippet_record in snippet_records:
                    php_class = snippet_record.get('element_class')
                    php_tags = soup.find_all(class_=php_class)
                    if len(php_tags)!=1:
                        for php_tag in php_tags:
                            new_php_tag_class = php_class + self.generate_hash(length=6)
                            php_tag['class'] = [new_php_tag_class if cls == php_class else cls for cls in php_tag['class']]
                            self.env['automated_seo.snippet_mapper'].create({
                                'snippet_id': new_data_snippet_id,
                                'php_tag': snippet_record.get('php_tag'),
                                    'element_class': new_php_tag_class,
                                'image_name': snippet_record.get('image_name'),
                            })
                    else:
                        self.env['automated_seo.snippet_mapper'].create({
                            'snippet_id': new_data_snippet_id,
                            'php_tag': php_tags,
                            'element_class': php_class,
                            'image_name': snippet_record.get('image_name'),
                        })
                for tag in soup.find_all(class_=True):
                    tag['class'] = [cls for cls in tag['class']
                                    if cls not in ['sub_card']]

                    if not tag['class']:
                        del tag['class']
                website_page.view_id.arch_db = soup.prettify()
                website_page.view_id.arch = soup.prettify()

    def handle_dynamic_img_tag(self, view_name):
        website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
        html_parser = website_page.view_id.arch_db
        soup = BeautifulSoup(html_parser, "html.parser")
        base_url_php = "<?php echo BASE_URL_IMAGE; ?>"
        for img in soup.select('img'):

            url = img.get('src')
            if url and url.startswith("/web/image/"):
                new_image_name = url.split('/')[-1]
                image_id = int(url.split('/')[-2].split('-')[0])
                attachment = self.env['ir.attachment'].search([('id', '=', image_id)])
                hash_suffix = self.generate_hash()
                name, ext = new_image_name.rsplit('.', 1)
                new_image_name = f"{name}_{hash_suffix}.{ext}"
                if attachment:
                    processed_image
                    print("uploaded succesfully=======================")
                    # new_image_data = attachment.datas
                    # new_image = base64.b64decode(new_image_data)
                    # image_file = io.BytesIO(new_image)
                    # self.upload_file_to_s3(file=image_file, view_name=view_name, s3_filename=new_image_name)
                odoo_img_url = f"https://assets.bacancytechnology.com/Inhouse/{new_image_name}"
                img['src'] = odoo_img_url
                img['data-src'] = odoo_img_url
                for attr in ["data-mimetype", "data-original-id", "data-original-src", "data-resize-width"]:
                    if img.has_attr(attr):
                        del img[attr]
                website_page.view_id.write({
                    'arch_db' : soup.prettify(),
                    'arch' : soup.prettify()
                })
                # website_page.view_id.arch_db = soup.prettify()
                # website_page.view_id.arch = soup.prettify()
            print("============soup============================")
            print(soup)
            print("============soup============================")
            img['src'] = url.replace("https://assets.bacancytechnology.com/", base_url_php)
            img['data-src'] = url.replace("https://assets.bacancytechnology.com/", base_url_php)
            print("============img============================")
            print(img)
            print("============img============================")
            print("============soup============================")
            print(soup)
            print("============soup============================")

        return str(soup.prettify())

    # def handle_dynamic_img_tag(self,view_name):
    #     website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
    #     html_parser = website_page.view_id.arch_db
    #     # breakpoint()
    #
    #     # TODO:
    #     soup = BeautifulSoup(html_parser, "html.parser")
    #     base_url_php = "<?php echo BASE_URL_IMAGE; ?>"
    #     for img in soup.select('img'):
    #
    #         url = img.get('src')
    #         if url and url.startswith("/web/image/"):
    #             new_image_name = url.split('/')[-1]
    #             image_id = int(url.split('/')[-2].split('-')[0])
    #             attachment = self.env['ir.attachment'].search([('id', '=', image_id)])
    #             hash_suffix = self.generate_hash()
    #             name, ext = new_image_name.rsplit('.', 1)
    #             new_image_name = f"{name}_{hash_suffix}.{ext}"
    #             if attachment:
    #                 print("uploaded succesfully=======================")
    #                 # new_image_data = attachment.datas
    #                 # new_image = base64.b64decode(new_image_data)
    #                 # image_file = io.BytesIO(new_image)
    #                 # self.upload_file_to_s3(file=image_file, view_name=view_name, s3_filename=new_image_name)
    #             odoo_img_url = f"https://assets.bacancytechnology.com/Inhouse/{new_image_name}"
    #             img['src'] = odoo_img_url
    #             img['data-src'] = odoo_img_url
    #             for attr in ["data-mimetype", "data-original-id", "data-original-src", "data-resize-width"]:
    #                 if img.has_attr(attr):
    #                     del img[attr]
    #             website_page.view_id.arch_db = soup.prettify()
    #             website_page.view_id.arch = soup.prettify()
    #         print("==================================")
    #         print(img)
    #         img['src'] = url.replace("https://assets.bacancytechnology.com/", base_url_php)
    #         img['data-src'] = url.replace("https://assets.bacancytechnology.com/", base_url_php)
    #         print(img)
    #         print("==================================")
    #
    #     return str(soup.prettify())
    # def handle_dynamic_img_tag(self,view_name):
    #     breakpoint()
    #     website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
    #     html_parser = website_page.view_id.arch_db
    #     soup = BeautifulSoup(html_parser, "html.parser")
    #     base_url_php = "<?php echo BASE_URL_IMAGE; ?>"
    #     for img in soup.select('img'):
    #
    #         url = img.get('src')
    #         if url and url.startswith("/web/image/"):
    #             new_image_name = url.split('/')[-1]
    #             image_id = int(url.split('/')[-2].split('-')[0])
    #             attachment = self.env['ir.attachment'].search([('id', '=', image_id)])
    #             hash_suffix = self.generate_hash()
    #             name, ext = new_image_name.rsplit('.', 1)
    #             new_image_name = f"{name}_{hash_suffix}.{ext}"
    #             if attachment:
    #                 print("uploaded succesfully=======================")
    #                 processed_image = self.process_image_with_params(attachment, img)
    #                 temp_folder_path = Path('./temp')
    #                 # Ensure the temp folder exists
    #                 temp_folder_path.mkdir(parents=True, exist_ok=True)
    #
    #                 # Define the full file path including filename and extension
    #                 file_path = temp_folder_path / f"{new_image_name}"
    #
    #                 # Write the processed image data to the file
    #                 with open(file_path, 'wb') as image_file:
    #                     # Check if processed_image is BytesIO and get the byte content
    #                     if isinstance(processed_image, io.BytesIO):
    #                         processed_image.seek(0)  # Move to the start of the BytesIO stream
    #                         image_data = processed_image.read()  # Read as bytes
    #                     else:
    #                         image_data = processed_image  # Assume it's already in bytes
    #
    #                     # Ensure image_data is valid before writing
    #                     if image_data:
    #                         image_file.write(image_data)
    #                     else:
    #                         raise ValueError("Image data is None after processing.")
    #                 # image_file = io.BytesIO(new_image)
    #                 print("=======================================")
    #                 # new_image_data = attachment.datas
    #                 # new_image = base64.b64decode(new_image_data)
    #                 # image_file = io.BytesIO(new_image)
    #                 # self.upload_file_to_s3(file=image_file, view_name=view_name, s3_filename=new_image_name)
    #             odoo_img_url = f"https://assets.bacancytechnology.com/Inhouse/{new_image_name}"
    #             img['src'] = odoo_img_url
    #             img['data-src'] = odoo_img_url
    #
    #             website_page.view_id.arch_db = soup.prettify()
    #             website_page.view_id.arch = soup.prettify()
    #
    #             for attr in ["data-mimetype", "data-original-id", "data-original-src", "data-resize-width"]:
    #                 if img.has_attr(attr):
    #                     del img[attr];
    #         print("img=====================================")
    #         print(img)
    #         print("====================================")
    #         img['src'] = url.replace("https://assets.bacancytechnology.com/", base_url_php)
    #         img['data-src'] = url.replace("https://assets.bacancytechnology.com/", base_url_php)
    #         print("img=====================================")
    #         print(img)
    #         print("====================================")
    #
    #     return str(soup.prettify())

    # def update_snippet_ids(self, view_name):
    #     page = self.env['automated_seo.page'].search([('page_name', '=', view_name)], limit=1)
    #     website_page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
    #     html_parser = website_page.view_id.arch_db
    #     html_parser  = self.remove_sub_snippet_sections(html_parser=html_parser)
    #     soup = BeautifulSoup(html_parser, "html.parser")
    #     sections = soup.find_all('section', {'data-snippet': True})
    #     snippet_ids = []
    #     if not page:
    #         page = self.env['automated_seo.page'].create({
    #             'page_name': view_name
    #         })
    #         for section in sections:
    #             snippet_ids.append(section.get('data-snippet') + '-' + self.generate_hash())
    #
    #
    #         for i in range(len(sections)):
    #             sections[i]['data-snippet'] = snippet_ids[i]
    #             orginal_snippet_id = snippet_ids[i].split('-')[0]
    #             snippet_records = self.env['automated_seo.mapper'].search([('snippet_id', '=', orginal_snippet_id)],limit=1).php_tags.read(['element_class', 'php_tag', 'image_name'])
    #
    #             for snippet_record in snippet_records:
    #                 php_class = snippet_record.get('element_class')
    #                 # php_tags = sections[i].find_all(class_=php_class)
    #                 # for php_tag in php_tags:
    #                     # new_php_tag_class = php_class + self.generate_hash(length=6)
    #                     # php_tag['class'] = [new_php_tag_class if cls == php_class else cls for cls in php_tag['class']]
    #                 self.env['automated_seo.snippet_mapper'].create({
    #                     'snippet_id': snippet_ids[i],
    #                     'php_tag': snippet_record.get('php_tag'),
    #                     'element_class': php_class,
    #                     'image_name': snippet_record.get('image_name'),
    #                 })
    #             website_page.view_id.arch = soup.prettify()            # html_parser = self.replace_div_with_section(html_content=str(soup))
    #         # soup = BeautifulSoup(html_parser, "html.parser")
    #         # website_page.view_id.arch = soup.prettify()
    #         # website_page.view_id.arch_db = soup.prettify()
    #         # print(website_page.view_id.arch_db)
    #         # print(website_page.view_id.arch)
    #
    #     for section in sections:
    #         if len(section.get('data-snippet').split('-')) != 2:
    #             new_data_snippet_id = section.get('data-snippet') + '-' + self.generate_hash()
    #             snippet_ids.append(new_data_snippet_id)
    #             section['data-snippet'] = new_data_snippet_id
    #             orginal_snippet_id = new_data_snippet_id.split('-')[0]
    #             snippet_records = self.env['automated_seo.mapper'].search([('snippet_id', '=', orginal_snippet_id)],
    #                                                                       limit=1).php_tags.read(
    #                 ['element_class', 'php_tag', 'image_name'])
    #             for snippet_record in snippet_records:
    #                 self.env['automated_seo.snippet_mapper'].create({
    #                     'snippet_id': new_data_snippet_id,
    #                     'php_tag': snippet_record.get('php_tag'),
    #                     'element_class': snippet_record.get('element_class'),
    #                     'image_name': snippet_record.get('image_name'),
    #                 })
    #             website_page.view_id.arch = soup.prettify()

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
                                        self.upload_file_to_s3(file=image_file,s3_filename=new_image_name)

                                    image_path = '/'.join(new_src.split('/')[:-1])
                                    tag['src'] = image_path + '/' + new_image_name
                                    tag['data-src'] = image_path + '/' + new_image_name

                                    website_page.view_id.arch = soup.prettify()

                                    old_img_tag['src'] = f'<?php echo BASE_URL_IMAGE; ?>Inhouse/{new_image_name}'
                                    old_img_tag['data-src'] = f'<?php echo BASE_URL_IMAGE; ?>Inhouse/{new_image_name}'
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
        print("=============++inside+++++asfdsff++++++++++++++++")

        for section in sections:
            snippet_ids.append(section.get('data-snippet'))

        for section in sections:
            snippet_records = self.env['automated_seo.snippet_mapper'].search(
                [('snippet_id', '=', section.get('data-snippet'))])
            print("=============++inside+++++++++++++++++++++")
            print(snippet_records)
            print("=============+++++++++++++++++++++++")

            if snippet_records:
                for snippet_record in snippet_records:
                    element = snippet_record.read(['element_class', 'php_tag', 'image_name'])[0]
                    element_class = element.get('element_class')
                    tags = soup.find_all(class_=element_class)
                    for tag in tags:
                        old_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')
                        tag.replace_with(old_tag_soup)

        for tag in soup.find_all('t'):
            tag.unwrap()
        wrap_tag = soup.find(id="wrap")
        wrap_tag.unwrap()
        return str(soup)

    def remove_odoo_classes_from_tag(self, html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")
        class_to_remove = ['oe_structure', 'remove', 'custom-flex-layout',
                           'custom-left-section', 'custom-right-section']

        for tag in soup.find_all(class_=True):
            tag['class'] = [cls for cls in tag['class']
                            if not cls.startswith('o_') and cls not in class_to_remove]

            if not tag['class']:
                del tag['class']

            for attr in ['data-bs-original-title', 'title','aria-describedby']:
                if tag.has_attr(attr):
                    del tag[attr]

            for attr in ['data-name', 'data-snippet', 'style', 'order-1', 'md:order-1']:
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

    def upload_file_to_s3(self, file, s3_filename,view_name = None):
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          )
        try:
            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, f'Inhouse/{s3_filename}')
            # s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, f'Inhouse/{view_name}/{s3_filename}')
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

    def handle_dynamic_anchar_tag(self,html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")
        link_css_classes = ['text-primary', 'font-bold']
        base_url_php = "<?php echo BASE_URL; ?>"
        for a in soup.select('a:not(.btn)'):
            # Get current classes on the <a> tag or initialize with an empty list
            current_classes = a.get('class', [])

            # Add each class from link_css_classes if it’s not already present
            for css_class in link_css_classes:
                if css_class not in current_classes:
                    current_classes.append(css_class)

            # Update the class attribute on the <a> tag
            a['class'] = current_classes

            url = a.get('href')
            if url and url.startswith("https://www.bacancytechnology.com/"):
                a['href'] = url.replace("https://www.bacancytechnology.com/", base_url_php)

        return str(soup.prettify())

    def remove_empty_tags(self, html_parser):

        soup = BeautifulSoup(html_parser, 'html.parser')

        all_tags = soup.find_all()

        for tag in all_tags:
            tag_string = str(tag)


            pattern = f'<{tag.name}[^>]*?></\s*{tag.name}>'

            # Check if it's an empty tag
            if re.match(pattern, tag_string):
                print(pattern, tag_string)
                tag.decompose()
            pattern = f'<{tag.name}></{tag.name}>'
            if re.match(pattern, tag_string):
                print("============================")
                print(pattern, tag_string)
                tag.decompose()


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

