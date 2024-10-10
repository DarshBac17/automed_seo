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
        html_parser = self.php_mapper(html_parser=html_parser,page=page[0])
        if html_parser:
            html_parser = self.remove_odoo_classes_from_tag(html_parser)
        if html_parser:
            html_parser = html.unescape(html_parser)
            self.write({
                'parse_html': html_parser,
                'parse_html_binary': base64.b64encode(html_parser.encode('utf-8')),
                'parse_html_filename': f"{view_name}_parsed.html"
            })

    def php_mapper(self,html_parser, page):
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
                        print("===========================")
                        print(tag)
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