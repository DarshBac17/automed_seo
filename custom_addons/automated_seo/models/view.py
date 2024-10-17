from odoo import models, fields, api
from bs4 import BeautifulSoup
import  html
import base64
import boto3
import io
import random
import string
# import os
from botocore.exceptions import ClientError
# from dotenv import load_dotenv
AWS_ACCESS_KEY_ID = 'AKIA4XF7TG4AOK3TI2WY'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'bacancy-website-images'

class View(models.Model):
    _inherit = 'ir.ui.view'
    parse_html = fields.Text(string="Parse HTML")
    parse_html_binary = fields.Binary(string="Parsed HTML File", attachment=True)
    parse_html_filename = fields.Char(string="Parsed HTML Filename")


    def generate_hash(self,length=6):
        """Generate a random string of fixed length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def action_custom_button(self):
        view_name = self.env.context.get('view_name', 'Unknown')
        html_parser = self.php_mapper(view_name=view_name)
        if html_parser:
            html_parser = self.remove_odoo_classes_from_tag(html_parser)
        if html_parser:
            soup = BeautifulSoup(html_parser, "html.parser")
            html_parser = soup.prettify()
            html_parser = html.unescape(html_parser)
            self.write({
                'parse_html': html_parser,
                'parse_html_binary': base64.b64encode(html_parser.encode('utf-8')),
                'parse_html_filename': f"{view_name}_parsed.html"
            })

    def php_mapper(self,view_name):
        page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
        html_parser = page.view_id.arch
        print(html_parser)
        soup = BeautifulSoup(html_parser, "html.parser")

        sections = soup.find_all('section', {'data-snippet': True})

        snippet_ids = []
        for section in sections:
            snippet_ids.append(section.get('data-snippet'))
        for snippet_id in snippet_ids:
            snippet_record = self.env['automated_seo.mapper'].search([('snippet_id', '=', snippet_id)], limit=1)

            if snippet_record:
                elements = snippet_record.php_tags.read(['element_class', 'php_tag', 'image_name'])
                for element in elements:
                    tags = soup.find_all(class_=element.get('element_class'))
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
                                    self.upload_file_to_s3(file=image_file, s3_filename=new_image_name)

                                image_path = '/'.join(new_src.split('/')[:-1])
                                tag['src'] = image_path + '/' + new_image_name
                                tag['data-src'] = image_path + '/' + new_image_name
                                page.view_id.arch = soup
                                old_img_tag['src'] = f'Inhouse/{new_image_name}'
                                old_img_tag['data-src'] = f'Inhouse/{new_image_name}'
                                php_mapper_record = self.env['automated_seo.php_mapper'].browse(element['id'])
                                php_mapper_record.write({
                                    'php_tag': str(old_tag_soup),
                                    'image_name': str(new_image_name)
                                })
                                attachment.write({
                                    'name': new_image_name
                                })

                        tag.replace_with(old_tag_soup)

        for tag in soup.find_all('t'):
            tag.unwrap()
        wrap_tag = soup.find(id="wrap")
        wrap_tag.unwrap()
        return str(soup)

    def remove_odoo_classes_from_tag(self, html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")

        for tag in soup.find_all(class_=True):
            tag['class'] = [cls for cls in tag['class'] if not cls.startswith('o_')] + [cls for cls in tag['class'] if not cls.startswith('oe')]

            if not tag['class']:
                del tag['class']

            for attr in ['data-name', 'data-snippet', 'style', 'order-1', 'md:order-1']:
                tag.attrs.pop(attr, None)

            class_to_remove = ['oe_structure', 'remove', 'data-bs-original-title','title']
            for tag in soup.find_all(class_=class_to_remove):
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

        return html_content

    def action_download_parsed_html(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=ir.ui.view&id={}&field=parse_html_binary&filename_field=parse_html_filename&download=true'.format(
                self.id),
            'target': 'self',
        }

    def upload_file_to_s3(self, file, s3_filename):
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          )
        try:
            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, f'Inhouse/{s3_filename}')
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