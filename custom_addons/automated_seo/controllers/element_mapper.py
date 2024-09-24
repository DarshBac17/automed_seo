from odoo import http
import  json
from bs4 import BeautifulSoup

class WebPageController(http.Controller):
    @http.route('/automated_seo/php_mapper',auth='public',http=True,website=True)
    def php_mapper(self):
        html_content = '''
        <html>
            <head>
                <title>Sample Page</title>
            </head>
            <body>
                <h1 class="header">Original Header</h1>
                <h1 class="header">Original Header</h1>
                <p class="description">This is a sample description.</p>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html_content, "html.parser")
        elements = http.request.env['automated_seo.php_mapper'].search([]).read(['element_class', 'php_tag'])
        for element in elements:
            tags = None
            tags= soup.find_all(class_=element.get('element_class'))
            for tag in tags:
                new_tag_soup = BeautifulSoup(element.get('php_tag'), 'html.parser')
                # new_tag = new_tag_soup.find(class_=element.get('element_class'))
                # if new_tag:
                tag.replace_with(new_tag_soup)
        return str(soup)
