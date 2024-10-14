from docutils.nodes import image
from lxml.html import html_parser
from odoo import models, fields, api
from bs4 import BeautifulSoup
import  html
import base64
import random
import string

class View(models.Model):
    _inherit = 'ir.ui.view'
    parse_html = fields.Text(string="Parse HTML")
    parse_html_binary = fields.Binary(string="Parsed HTML File", attachment=True)
    parse_html_filename = fields.Char(string="Parsed HTML Filename")

    # @api.model
    # def create(self, vals):
    #     if 'app_name' not in vals:
    #         vals['app_name'] = 'automated_seo'  # Set dynamic default value
    #     return super(View, self).create(vals)



    def generate_hash(self,length=6):
        """Generate a random string of fixed length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def action_custom_button(self):
        view_name = self.env.context.get('view_name', 'Unknown')
        page = self.env['ir.ui.view'].search([('name', '=', view_name),('website_id','!=', 'False',)]).read(['arch'])
        html_parser =  page[0].get('arch')
        # html_parser = self.php_mapper(html_parser=html_parser,page=page[0])
        html_parser = self.updated_php_mapper(view_name=view_name)

        if html_parser:
            html_parser = self.remove_odoo_classes_from_tag(html_parser)
        if html_parser:
            html_parser = html.unescape(html_parser)
            self.write({
                'parse_html': html_parser,
                'parse_html_binary': base64.b64encode(html_parser.encode('utf-8')),
                'parse_html_filename': f"{view_name}_parsed.html"
            })

    def updated_php_mapper(self, view_name):
        # breakpoint()
        # image_id = 268  # Replace with the ID from your image src
        # result = self.find_changed_snippet_image(image_id)
        # if result:
        #     print("Changed image found:")
        #     for key, value in result.items():
        #         print(f"{key}: {value}")
        # else:
        #     print("Image not found")
        # snippet_name = "Left Side Image Gray"
        # page_url ='/demo-5'  # Replace with your actual page URL
        # result = self.find_snippet_image_comprehensive(page_url=page_url, snippet_name = snippet_name)
        # if result:
        #     print(f"Recently replaced image for page {page_url}:")
        #     print(f"Name: {result['name']}")
        #     print(f"URL: {result['url']}")
        #     print(f"Created on: {result['create_date']}")
        #     print(f"MIME Type: {result['mimetype']}")
        # else:
        #     print(f"No recently replaced image found for page {page_url}")
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
                                image_path = '/'.join(new_src.split('/')[:-1])
                                tag['src'] = image_path + '/' + new_image_name
                                tag['data-src'] = image_path + '/' + new_image_name
                                page.view_id.arch = soup
                                old_img_tag['src'] = f'path/to/images/{new_image_name}'

                                old_img_tag['data-src'] = f'path/to/images/{new_image_name}'
                                php_mapper_record = self.env['automated_seo.php_mapper'].browse(element['id'])
                                php_mapper_record.write({
                                    'php_tag': str(old_tag_soup),
                                    'image_name': str(new_image_name)
                                })
                                print(self.env['ir.attachment'].search([('id', '=', image_id)]).read(['name']))
                                self.env['ir.attachment'].search([('id', '=', image_id)]).write({
                                    'name': new_image_name
                                })
                                print(self.env['ir.attachment'].search([('id', '=', image_id)]).read(['name']))

                        tag.replace_with(old_tag_soup)

        for tag in soup.find_all('t'):
            tag.unwrap()
        wrap_tag = soup.find(id="wrap")
        wrap_tag.unwrap()
        return str(soup)

    def updated_image_php_mapper(self, view_name):
        # breakpoint()
        # image_id = 268  # Replace with the ID from your image src
        # result = self.find_changed_snippet_image(image_id)
        # if result:
        #     print("Changed image found:")
        #     for key, value in result.items():
        #         print(f"{key}: {value}")
        # else:
        #     print("Image not found")
        # snippet_name = "Left Side Image Gray"
        # page_url ='/demo-5'  # Replace with your actual page URL
        # result = self.find_snippet_image_comprehensive(page_url=page_url, snippet_name = snippet_name)
        # if result:
        #     print(f"Recently replaced image for page {page_url}:")
        #     print(f"Name: {result['name']}")
        #     print(f"URL: {result['url']}")
        #     print(f"Created on: {result['create_date']}")
        #     print(f"MIME Type: {result['mimetype']}")
        # else:
        #     print(f"No recently replaced image found for page {page_url}")
        page = self.env['website.page'].search([('name', '=', view_name)], limit=1)
        html_parser = page.view_id.arch
        soup = BeautifulSoup(html_parser, "html.parser")

        sections = soup.find_all('section', {'data-snippet': True})
        snippet_ids = []
        for section in sections:
            snippet_ids.append(section.get('data-snippet'))

        for snippet_id in snippet_ids:
            snippet_record = self.env['automated_seo.mapper'].search([('snippet_id', '=', snippet_id)], limit=1)

            if snippet_record:
                elements = snippet_record.php_tags.search(['image_name','!=', 'False',]).read(['element_class', 'php_tag', 'image_name'])
                for element in elements:
                    tags = soup.find_all(class_=element.get('element_class'))
                    for tag in tags:
                        new_src = tag.get('src')
                        old_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')
                        if new_src:
                            new_image_name = new_src.split('/')[-1]  # Extract just the file name from the src
                            old_img_tag = old_tag_soup.find('img')
                            # old_img_name = old_img_tag.get('src').split('/')[-1]
                            old_img_name = element.get('image_name')

                            # temp = self.env['ir.attachment'].search([('name', '=',old_img_name )])
                            if old_img_tag and old_img_name != new_image_name:
                                hash_suffix = self.generate_hash()
                                name, ext = new_image_name.rsplit('.', 1)
                                new_image_name = f"{name}_{hash_suffix}.{ext}"
                                image_id = new_src.split('/')[-2].split('-')[0]

                                page.view_id.arch = str(soup)
                                old_img_tag['src'] = f'path/to/images/{new_image_name}'

                                old_img_tag['data-src'] = f'path/to/images/{new_image_name}'
                                php_mapper_record = self.env['automated_seo.php_mapper'].browse(element['id'])
                                php_mapper_record.write({
                                    'php_tag': str(old_tag_soup),
                                    'image_name': str(new_image_name)
                                })
                                self.env['ir.attachment'].search(['id','=',image_id]).write({
                                    'name':new_image_name
                                })
                        tag.replace_with(old_tag_soup)

        page.view_id.arch = str(soup)
        breakpoint()
        return page.view_id.arch
    def php_mapper(self,html_parser, page):
        # breakpoint()
        # image_id = 268  # Replace with the ID from your image src
        # result = self.find_changed_snippet_image(image_id)
        # if result:
        #     print("Changed image found:")
        #     for key, value in result.items():
        #         print(f"{key}: {value}")
        # else:
        #     print("Image not found")
        # snippet_name = "Left Side Image Gray"
        # page_url ='/demo-5'  # Replace with your actual page URL
        # result = self.find_snippet_image_comprehensive(page_url=page_url, snippet_name = snippet_name)
        # if result:
        #     print(f"Recently replaced image for page {page_url}:")
        #     print(f"Name: {result['name']}")
        #     print(f"URL: {result['url']}")
        #     print(f"Created on: {result['create_date']}")
        #     print(f"MIME Type: {result['mimetype']}")
        # else:
        #     print(f"No recently replaced image found for page {page_url}")
        soup = BeautifulSoup(html_parser, "html.parser")
        sections = soup.find_all('section', {'data-snippet': True})
        snippet_ids=[]
        for section in sections:
            snippet_ids.append(section.get('data-snippet'))

        for snippet_id in snippet_ids:
            snippet_record = self.env['automated_seo.mapper'].search([('snippet_id', '=', snippet_id)], limit=1)

            if snippet_record:
                elements = snippet_record.php_tags.read(['element_class', 'php_tag','image_name'])
                for element in elements:
                    tags = soup.find_all(class_=element.get('element_class'))
                    for tag in tags:
                        new_src = tag.get('src')
                        old_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')
                        if new_src:
                            new_image_name = new_src.split('/')[-1]  # Extract just the file name from the src
                            old_img_tag = old_tag_soup.find('img')
                            # old_img_name = old_img_tag.get('src').split('/')[-1]
                            old_img_name = element.get('image_name')

                            # temp = self.env['ir.attachment'].search([('name', '=',old_img_name )])
                            if old_img_tag and old_img_name!=new_image_name:
                                hash_suffix = self.generate_hash()
                                name, ext = new_image_name.rsplit('.', 1)
                                new_image_name = f"{name}_{hash_suffix}.{ext}"
                                image_id = new_src.split('/')[-2].split('-')[0]
                                old_img_tag['src'] = f'path/to/images/{new_image_name}'

                                old_img_tag['data-src'] = f'path/to/images/{new_image_name}'
                                php_mapper_record = self.env['automated_seo.php_mapper'].browse(element['id'])
                                php_mapper_record.write({
                                    'php_tag': str(old_tag_soup),
                                    'image_name':str(new_image_name)
                                })


                        tag.replace_with(old_tag_soup)

        for tag in soup.find_all('t'):
            tag.unwrap()
        wrap_tag = soup.find(id="wrap")
        wrap_tag.unwrap()
        return  str(soup)

    def remove_odoo_classes_from_tag(self, html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")

        for tag in soup.find_all(class_=True):
            tag['class'] = [cls for cls in tag['class'] if not cls.startswith('o_')]

            if not tag['class']:
                del tag['class']

            for attr in ['data-name', 'data-snippet', 'style', 'order-1', 'md:order-1']:
                tag.attrs.pop(attr, None)

            class_to_remove = ['oe_structure', 'remove']
            for tag in soup.find_all(class_=class_to_remove):
                # Replace the tag with its contents
                tag.replace_with(*tag.contents)
                # tag.replace_with( tag.decode_contents())


        for tag in soup.find_all(True):
            if 'itemscope' in tag.attrs and (tag.attrs['itemscope'] == 'itemscope' or tag.attrs['itemscope'] == 'acceptedAnswer'):
                tag.attrs['itemscope'] = None  # Keep as a flag attribute

        return soup.prettify()

    def action_download_parsed_html(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=ir.ui.view&id={}&field=parse_html_binary&filename_field=parse_html_filename&download=true'.format(
                self.id),
            'target': 'self',
        }

    def find_snippet_image_comprehensive(self, snippet_name, page_url):
        # Find the page
        page = self.env['website.page'].search([('url', '=', page_url)], limit=1)
        if not page:
            return "Page not found"

        # Check ir.attachment
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'ir.ui.view'),
            ('res_id', '=', page.view_id.id),
            ('mimetype', 'like', 'image/%')
        ], order='create_date desc', limit=1)

        if attachment:
            return f"Image found in ir.attachment: {attachment.name}"

        # Check view arch for background image
        view_arch = page.view_id.arch
        if 'background-image' in view_arch:
            return "Image might be a CSS background image in the view arch"

        # Check for custom snippet template
        custom_snippet = self.env['ir.ui.view'].search([
            ('name', '=', snippet_name),
            ('type', '=', 'qweb'),
            ('website_id', '=', page.website_id.id)
        ], limit=1)

        if custom_snippet:
            return f"Custom snippet template found: {custom_snippet.name}"

        # Check theme assets
        theme_attach = self.env['ir.attachment'].search([
            ('name', 'like', snippet_name),
            ('res_model', '=', 'theme.ir.attachment')
        ], limit=1)

        if theme_attach:
            return f"Image might be in theme assets: {theme_attach.name}"

        return "Image location not found. It might be dynamically loaded or require further investigation."

    def find_changed_snippet_image(self, image_id):
        attachment = self.env['ir.attachment'].sudo().browse(image_id)
        if attachment.exists():
            return {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': attachment.mimetype,
                'url': attachment.url,
                'create_date': attachment.create_date,
                'res_model': attachment.res_model,
                'res_id': attachment.res_id
            }
        return None