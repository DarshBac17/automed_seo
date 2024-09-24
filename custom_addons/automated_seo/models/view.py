from odoo import models, fields, api
from bs4 import BeautifulSoup
import  html



class View(models.Model):
    _inherit = 'ir.ui.view'
    parse_html = fields.Text(string="Parse HTML")

    # @api.model
    # def create(self, vals):
    #     if 'app_name' not in vals:
    #         vals['app_name'] = 'automated_seo'  # Set dynamic default value
    #     return super(View, self).create(vals)


    def action_custom_button(self):
        view_name = self.env.context.get('view_name', 'Unknown')
        page = self.env['ir.ui.view'].search([('name', '=', view_name)]).read(['arch'])
        html_parser =  page[0].get('arch')
        html_parser = self.php_mapper(html_parser=html_parser)
        if html_parser:
            html_parser = self.remove_odoo_classes_from_tag(html_parser)
        if html_parser:
            html_parser = html.unescape(html_parser)
            self.write({'parse_html': html_parser})

    def php_mapper(self,html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")
        elements = self.env['automated_seo.php_mapper'].search([]).read(['element_class', 'php_tag'])
        for element in elements:
            tags = None
            tags = soup.find_all(class_=element.get('element_class'))
            for tag in tags:
                new_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')
                tag.replace_with(new_tag_soup)

        for tag in soup.find_all('t'):
            tag.unwrap()
        wrap_tag = soup.find(id="wrap")
        wrap_tag.unwrap()
        return  str(soup)



    def remove_odoo_classes_from_tag(self,html_parser):
        soup = BeautifulSoup(html_parser, "html.parser")

        for tag in soup.find_all(class_=True):
            tag['class'] = [cls for cls in tag['class'] if not cls.startswith('o_')]

            if not tag['class']:
                del tag['class']

            for attr in ['data-name', 'data-snippet', 'style', 'order-1','md:order-1']:
                tag.attrs.pop(attr, None)

        return  soup.prettify()