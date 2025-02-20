from email.policy import default
# from multiprocessing.managers import view_type

from odoo import models, fields, api
from odoo.addons.test_convert.tests.test_env import record
from odoo.exceptions import UserError
import json
import os
from bs4 import BeautifulSoup, NavigableString
from itertools import zip_longest
import  html
import io
import xml.etree.ElementTree as ET
from PIL import Image, UnidentifiedImageError
from .ftp_setup import transfer_file_via_scp
import re
import  base64
from odoo.tools.populate import compute
from .ftp_setup import transfer_file_via_scp
import difflib

class VersionCompareWizard(models.TransientModel):
    _name = "automated_seo.version_compare_wizard"
    _description = "Wizard for Comparing two versions"

    view_id = fields.Many2one('automated_seo.view', string='View', required=True)

    base_version = fields.Many2one(
        'website.page.version',
        string="Base version",
        domain = "[('view_id', '=', view_id)]",
    )

    compare_version = fields.Many2one(
        'website.page.version',
        string="Compare version",
        domain="[('id', '!=', base_version),('view_id', '=', view_id)]",
    )
    diff_html = fields.Html(string='Differences', readonly=True)

    def is_php_content(self,text):
                # Check if content is PHP tag/include
        return '<?php' in text or text.strip().startswith('php')
    def highlight_differences(self, base_soup, compare_soup):
        def compare_elements(base_elem, compare_elem):
            # Handle text nodes
            if compare_elem and compare_elem.name == 'img':
                base_src = base_elem.get('src') if base_elem else None 
                compare_src = compare_elem.get('src')
                if base_src != compare_src:
                    compare_elem['class'] = compare_elem.get('class', []) + ['ae_img_highlight']
                return compare_elem
             
            if isinstance(base_elem, NavigableString) and isinstance(compare_elem, NavigableString):
                base_text = str(base_elem).strip()
                compare_text = str(compare_elem).strip()
                
                if self.is_php_content(base_text) or self.is_php_content(compare_text):
                    return compare_elem
                    
                if base_text != compare_text:
                    base_words = base_text.split()
                    compare_words = compare_text.split()
                    result = []
                    
                    for base_word, compare_word in zip_longest(base_words, compare_words):
                        if compare_word and not base_word:
                            # New word
                            result.append(f'<span class="ae_new_section">{compare_word}</span>')
                        elif base_word != compare_word:
                            # Changed word in existing section
                            result.append(f'<span class="ae_highlight">{compare_word or ""}</span>')
                        else:
                            result.append(base_word)
                            
                    return BeautifulSoup(' '.join(result), 'html.parser')
                return compare_elem
                
            # Handle elements
            if hasattr(base_elem, 'children') and hasattr(compare_elem, 'children'):
                base_children = list(base_elem.children)
                compare_children = list(compare_elem.children)

                if len(compare_children) > len(base_children):
                    for i in range(len(base_children), len(compare_children)):
                        if isinstance(compare_children[i], NavigableString):
                            continue
                        new_elem = compare_children[i]
                        if new_elem.get('class'):
                            new_elem['class'] = new_elem.get('class', []) + ['ae_new_section']
                        else:
                            new_elem['class'] = ['ae_new_section']
                        
                for base_child, compare_child in zip_longest(list(base_elem.children), list(compare_elem.children)):
                    if base_child and compare_child:
                        result = compare_elements(base_child, compare_child)
                        if result != compare_child:
                            compare_child.replace_with(result)
                            
            return compare_elem

        return compare_elements(base_soup, compare_soup)
                
    def compare_sections(self, base_soup, compare_soup):
    # Get all sections
        base_sections = base_soup.find_all('section',{'data-snippet': True})
        compare_sections = compare_soup.find_all('section', {'data-snippet': True})
        
        # Create dict of section_type: hash pairs from base
        base_section_data = {
            section.get('data-snippet').split('-')[0]: section.get('data-snippet').split('-')[1] 
            for section in base_sections
        }
        
        matched_sections = set()
        css = """
        <style>
            .ae_highlight { background-color: #ffcccc; }
            .ae_new_section { background-color: #ccffcc; }
            .ae_missing_section { background-color: #ffcccc; opacity: 0.7; }
        </style>
        """
        
        for compare_section in compare_sections:
            compare_type = compare_section.get('data-snippet').split('-')[0]
            
            if compare_type not in base_section_data:
                # New section type
                compare_section['class'] = compare_section.get('class', []) + ['ae_new_section']
            else:
                # Find matching base section with same hash
                base_hash = base_section_data[compare_type]
                base_section = base_soup.find('section', {'data-snippet': f"{compare_type}-{base_hash}"})
                # base_section = next(
                #     (section for section in base_sections 
                #     if section.get('data-snippet') == f"{compare_type}-{base_hash}"),
                #     None
                # )
                
                if base_section:
                    # Compare content and highlight differences
                    highlighted = self.highlight_differences(base_section, compare_section)
                    if highlighted:
                        compare_section.replace_with(highlighted)
                    matched_sections.add(base_section)
        
        return  str(compare_soup)
    

    def add_head(self, html_parser, seo_view_id):
        soup = BeautifulSoup('<html lang="en"><head></head><body></body></html>', 'html.parser')
        head_tag = soup.head
        seo_view = self.env['automated_seo.view'].browse(seo_view_id)
        base_version = self.env['website.page.version'].search([('id', '=', self.base_version.id)], limit=1)
        page_name = seo_view.name.strip().lower().replace(" ", "-")
        title_tag = soup.new_tag('title')
        title_tag.string = base_version.header_title
        head_tag.append(title_tag)

        description_meta = soup.new_tag('meta')
        description_meta['name'] = 'description'
        description_meta['content'] = base_version.header_description
        head_tag.append(description_meta)
        common_meta_tag = BeautifulSoup('<?php include("tailwind/template/common-meta.php"); ?>',"html.parser")
        head_tag.append(common_meta_tag)

        og_title_meta = soup.new_tag('meta')
        og_title_meta['property'] = 'og:title'
        og_title_meta['content'] = base_version.header_title
        head_tag.append(og_title_meta)

        og_desc_meta = soup.new_tag('meta')
        og_desc_meta['property'] = 'og:description'
        og_desc_meta['content'] = base_version.header_description
        head_tag.append(og_desc_meta)

        image_url = f'inhouse/{base_version.view_id.name.replace(" ", "").lower()}/{base_version.image_filename.replace(" ", "-").replace("%20", "-").lower()}' if base_version.view_id.name and base_version.image_filename and base_version.image else None

        if  image_url:
            og_image_meta = soup.new_tag('meta')
            og_image_meta['property'] = 'og:image'
            og_image_meta['content'] = f'<?php echo BASE_URL_IMAGE; ?>{image_url}'
            head_tag.append(og_image_meta)


        og_url_meta = soup.new_tag('meta')
        og_url_meta['property'] = 'og:url'

        # if not self.publish_url:
        #     self.publish_url = f"https://www.bacancytechnology.com/{self.name}"
        og_url_meta['content'] = base_version.view_id.publish_url.replace("https://www.bacancytechnology.com/","<?php echo BASE_URL; ?>")

        head_tag.append(og_url_meta)


        # for metadata in self.header_metadata_ids:
        #     meta_tag = soup.new_tag('meta')
        #     if metadata.property:
        #         meta_tag['property'] = metadata.property
        #         meta_tag['content'] = metadata.content or ''
        #     head_tag.append(meta_tag)

        # link_css_php = BeautifulSoup('<?php include("tailwind/template/link-css.php"); ?>',"html.parser")
        # head_tag.append(link_css_php)
        link_css_php = BeautifulSoup('<?php include("tailwind/template/link-css.php"); ?>',"html.parser")
        head_tag.append(link_css_php)
        for link in base_version.header_link_ids:
            tag = soup.new_tag('link')
            tag['rel'] = "preload"
            tag['href'] = link.css_link
            tag['as'] = 'style'
            tag['onload'] = "this.onload=null;this.rel='stylesheet'"
            head_tag.append(tag)

        css = """
            <style>
                .ae_highlight { background-color: #ffcccc; }
                .ae_new_section { background-color: #ccffcc; }
                .ae_missing_section { background-color: #ffcccc; opacity: 0.7; }
                .ae_img_highlight { background-color: #ffcccc; padding:15px; }
            </style>
            """
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
                        "name": "{base_version.header_title}",
                        "isPartOf": {{
                            "@id": "<?php echo BASE_URL; ?>#website"
                        }},
                        "datePublished": "2013-04-15T13:23:16+00:00",
                        "dateModified": "2024-07-17T14:31:52+00:00",
                        "description": "{base_version.header_description}"
                    }}
                ]
            }}
            </script>
            {css}
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
            if not link:
                if len(breadcrumb_items_tags)-1 == index:
                    url  = f"<?php echo BASE_URL; ?>{page_name}"
                    id = url + '/'
                    name = breadcrumb.text.strip()
                    item = {
                        "@type": "ListItem",
                        "position": position,
                        "item": {
                            "@type": "WebPage",
                            "@id": id
                        }
                    }
                    item["item"]["url"] = url
                    item["item"]["name"] = name
                    breadcrumb_items.append(item)
                else:
                    message = f"Please add a link in {breadcrumb.text.strip()} breadcrumb"
                    raise UserError(message)

            if link:

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


        breadcrumb_items_json = seo_view.format_json_with_tabs(breadcrumb_items)

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


    def remove_sub_snippet_sections(self,html_parser):
        # Parse the HTML content
        soup = BeautifulSoup(html_parser, 'html.parser')

        sections = soup.find_all('section', class_='o_replace_section_div')
        for sec in sections:
            sec.name = 'div'
        return soup.prettify()

    def handle_dynamic_img_tag(self,view_name,html_parser):
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
                    img['height'] = int(float(height))

                if width:
                    img['width'] = int(float(width))

                img_tag_classes = img.get("class", [])
                element = next((cls for cls in img_tag_classes if cls.startswith('o_imagename')), None)

                if element:
                    new_image_name = element.split('_',2)[-1]
                    odoo_img_url = f"https://assets.bacancytechnology.com/inhouse/{view_name.replace(' ','').lower()}/{new_image_name.replace('%20','-').replace('_','-').lower()}"
                    img['src'] = odoo_img_url
                    img['data-src'] = odoo_img_url



            for attr in ["data-mimetype", "data-original-id", "data-original-src", "data-resize-width",
                         "data-scale-x","data-scale-y","data-height","data-aspect-ratio","data-width",
                         "data-bs-original-title","aria-describedby","data-shape","data-file-name","data-shape-colors",
                         "data-gl-filter","data-quality","data-scroll-zone-start","data-scroll-zone-end","style"," data-shape-colors"]:

                if img.has_attr(attr):
                    del img[attr]

        return str(soup.prettify())


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

            if not img.get('title'):
                del img['title']
            if not img.get('alt'):
                img['alt'] = ""
            if img.get('alt') == '' or img.get('alt') == "":
                raise UserError("Please add alt tag to the image")

        return str(soup.prettify())


    def action_compile_button(self,version_compare_parser):
        # view = View()
        seo_view_id = self.compare_version.view_id.id
        seo_view = self.env['automated_seo.view'].browse(seo_view_id)
        html_parser = self.handle_dynamic_img_tag(html_parser=version_compare_parser, view_name=seo_view.name)
        html_parser = self.handle_dynamic_img_tag2(html_parser = html_parser)
        html_parser = seo_view.replace_php_tags_in_html(html_parser=html_parser)
        html_parser = seo_view.handle_dynamic_anchar_tag(html_parser=html_parser)
        if html_parser:
            html_parser = seo_view.remove_bom(html_parser=html_parser)
            html_parser = seo_view.remove_empty_tags(html_parser = html_parser)
            html_parser = seo_view.handle_breadcrumbs(html_content=html_parser)
            html_parser = seo_view.handle_itemprop_in_faq(html_content=html_parser)
            html_parser = self.add_head(html_parser = html_parser, seo_view_id = seo_view_id)
            html_parser = seo_view.add_js_scripts(html_parser)
            html_parser = seo_view.remove_odoo_classes_from_tag(html_parser)
            soup = BeautifulSoup(html_parser, "html.parser")
            html_parser = soup.prettify()
            html_parser = seo_view.format_paragraphs(html_content=html_parser)
            html_parser = seo_view.remove_extra_spaces(html_parser = html_parser)
            html_parser = seo_view.format_html_php(html_content=html_parser)
            html_parser = re.sub(r'itemscope=""', 'itemscope', html_parser)
            html_parser = html.unescape(html_parser)
            return html_parser

            # file = base64.b64encode(html_parser.encode('utf-8'))
            # version = self.env['website.page.version'].search(['&',('view_id','=',self.id),("status", "=", True)],limit =1)
            # file_name = f"{view_name}_{self.active_version.name}.php"
    # @api.onchange('base_version_id', 'compare_version_id')


    def remove_anchor_tags(self, html_content):

        soup = BeautifulSoup(html_content, 'html.parser')
        
        for anchor in soup.find_all('a'):
            if not ('btn' in anchor.get('class', [])):
                anchor.unwrap()
            
        return str(soup)

    # def action_compare_versions(self):
    #     if self.base_version and self.compare_version:
    #         base_content = self.base_version.view_arch or ''
    #         compare_content = self.compare_version.view_arch or ''
    #          # Remove anchor tags before comparison
    #         base_content = self.remove_anchor_tags(base_content)
    #         compare_content = self.remove_anchor_tags(compare_content)
    #
    #         base_content = self.remove_sub_snippet_sections(html_parser=base_content)
    #         compare_content = self.remove_sub_snippet_sections(html_parser=compare_content)
    #         if base_content and compare_content:
    #             base_content = html.unescape(base_content)
    #             compare_content = html.unescape(compare_content)
    #             base_content = self.handle_dynamic_img_tag(html_parser=base_content, view_name=self.base_version.view_id.name)
    #             compare_content = self.handle_dynamic_img_tag(html_parser=compare_content, view_name=self.base_version.view_id.name)
    #             base_soup = BeautifulSoup(base_content, 'html.parser')
    #             compare_soup = BeautifulSoup(compare_content, 'html.parser')
    #             result = self.compare_sections(compare_soup, base_soup)
    #             html_parser = self.action_compile_button(version_compare_parser=result)
    #             file = base64.b64encode(html_parser.encode('utf-8'))
    #             compare_file_name = f"{self.base_version.view_id.name}_version_compare.php"
    #             result = transfer_file_via_scp(page_name = compare_file_name, file_data=file)
    #             if result:
    #                 seo_view = self.env['automated_seo.view'].browse(self.base_version.view_id.id)
    #                 seo_view.write({
    #                     "diff_html" : html_parser,
    #                     "diff_html_binary" : file,
    #                     "diff_html_filename" : compare_file_name,
    #                     "diff_url" : f"https://automatedseo.bacancy.com/{compare_file_name}"
    #                 })

    @api.onchange('base_version', 'compare_version')
    def action_compare_versions(self):
        if self.base_version and self.compare_version:
            # Get HTML content with null checks
            base_content = self.base_version.parse_html or ''
            compare_content = self.compare_version.parse_html or ''
            # base_content = html.unescape(base_content)
            # compare_content = html.unescape(compare_content)

            # Convert to string if needed
            base_html = str(base_content) if base_content else ''
            compare_html = str(compare_content) if compare_content else ''

            # Create BeautifulSoup objects
            # base_soup = BeautifulSoup(base_html, 'html.parser')
            # compare_soup = BeautifulSoup(compare_html, 'html.parser')

            # Convert to pretty format
            # base_pretty = base_soup.prettify() if base_soup else ''
            # compare_pretty = compare_soup.prettify() if compare_soup else ''

            # Generate diff with custom styling
            if base_html and compare_html:
                diff = difflib.HtmlDiff()
                diff_html = diff.make_file(
                    base_html.splitlines(),
                    compare_html.splitlines(),
                    f"Version {self.base_version.name}",
                    f"Version {self.compare_version.name}"
                )

                # Add custom CSS for red highlighting
                css = """
                <style>
                    .diff_add {background-color: #ffcccc !important;}
                    .diff_chg {background-color: #ffcccc !important;}
                    .diff_sub {background-color: #ffcccc !important;}
                    td.diff_header {display: none;}
                </style>
                """

                self.diff_html = css + diff_html
            else:
                self.diff_html = '<p>No content available for comparison</p>'





class WebsitePageVersion(models.Model):
    _name = 'website.page.version'
    _description = 'Website Page Version'
    _order = 'create_date desc'

    name = fields.Char('Version Name', store=True)
    # description = fields.Text('Description')
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
    # change = fields.Selection([
    #     ('major_change', 'Major Changes'),
    #     ('minor_change', 'Minor Changes'),
    #     ('patch_change', 'Patch Changes'),
    # ], string="Change", default='major_change')
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('publish', 'Publish'),
        ('unpublish', 'Unpublish'),
    ], string="Stage", default="draft", tracking=True)
    # major_version = fields.Integer('Major Version', default=1)
    # minor_version = fields.Integer('Minor Version', default=0)
    # patch_version = fields.Integer('Patch Version', default=0)
    image = fields.Binary(string="Upload Image")
    image_filename = fields.Char(string="Image Filename")
    header_title = fields.Char(string="Title")
    header_description = fields.Text(string="page description")

    publish_url = fields.Char(string='Publish URL', help="Publish URL")
    selected_filename = fields.Char(string="Selected file name")
    # One-to-Many relationship: A page can have multiple metadata entries
    # header_metadata_ids = fields.One2many(
    #     'automated_seo.page_header_metadata',
    #     'view_version_id',
    #     string="Metadata"
    # )

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

    stage_url = fields.Char(string='Stage URL', help="Stage URL")

    # @api.depends('major_version', 'minor_version', 'patch_version')
    # def _compute_version_number(self):
    #     for record in self:
    #         record.name = f"v{record.major_version}.{record.minor_version}.{record.patch_version}"

    # @api.depends('view_id')
    def _compute_version_name(self):
        self.ensure_one()

        # if self.change:
        #     if self.change == 'major_change':
        #         max_major_version = self.env['website.page.version'].search(
        #             [('view_id', '=', self.view_id.id)],
        #             order='major_version desc',
        #             limit=1
        #         )
        #         self.major_version = max_major_version.major_version + 1
        #         self.minor_version = 0
        #         self.patch_version = 0
        #
        #     elif self.change == 'minor_change':
        #         self.major_version = self.base_version.major_version
        #         # Find highest minor version for this major version
        #         max_minor_version = self.env['website.page.version'].search([
        #             ('view_id', '=', self.view_id.id),
        #             ('major_version', '=', self.major_version)
        #         ], order='minor_version desc', limit=1)
        #         self.minor_version = max_minor_version.minor_version + 1 if max_minor_version else 1
        #         self.patch_version = 0
        #
        #     elif self.change == 'patch_change':
        #         self.major_version = self.base_version.major_version
        #         self.minor_version = self.base_version.minor_version
        #         # Find highest patch version for this major.minor version
        #         max_patch_version = self.env['website.page.version'].search([
        #             ('view_id', '=', self.view_id.id),
        #             ('major_version', '=', self.major_version),
        #             ('minor_version', '=', self.minor_version)
        #         ], order='patch_version desc', limit=1)
        #         self.patch_version = max_patch_version.patch_version + 1 if max_patch_version else 1

        version_count = self.env['website.page.version'].search_count([
            ('view_id', '=', self.view_id.id)
        ])

        self.name = f"v{version_count}"

    # @api.onchange('base_version')
    # def _onchange_base_version(self):
    #     self.ensure_one()
    #     self._compute_version_name()

    # @api.onchange('change')
    # def _onchange_change(self):
    #     self.ensure_one()
    #     self._compute_version_name()


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

    def name_get(self):
        result = []
        for record in self:
            # Combine 'name' and 'stage' fields in the dropdown display
            display_name = f"{record.name} ({(record.create_date.date())})"
            result.append((record.id, display_name))
        return result


    @api.model
    def create(self, vals):
        if not vals.get('view_id'):
            raise UserError('View ID is required to create a version')
        seo_view = self.env['automated_seo.view'].search([('id','=',vals['view_id'])])
        initial_version = self.env.context.get('initial_version')
        current_version = self.env['website.page.version'].search(
            ['&', ('status', '=', True), ('view_id', '=', seo_view.id)])
        view_arch = vals.get('view_arch') if vals.get('view_arch') else seo_view.website_page_id.arch_db if seo_view.website_page_id else False

        version_count = self.env['website.page.version'].search_count([
            ('view_id', '=', vals.get('view_id'))
        ])
        vals['name'] = f"v{version_count+1}"
        if current_version and seo_view:
            current_version.stage = seo_view.stage
            current_version.header_title = seo_view.header_title
            current_version.header_description = seo_view.header_description
            current_version.image = seo_view.image
            current_version.image_filename = seo_view.image_filename
            current_version.publish_url = seo_view.publish_url
            current_version.view_arch = seo_view.page_id.arch_db  if seo_view.page_id.arch_db else None
            current_version.status = False
            # current_version.header_metadata_ids.write({'is_active': False})
            current_version.header_link_ids.write({'is_active': False})

        if initial_version and seo_view:
            seo_view.page_id.arch_db = view_arch if view_arch else None
            # seo_view.stage = 'draft'/
            # seo_view.parse_html_filename = None
            # seo_view.parse_html_binary = None
            # seo_view.parse_html = None

            vals.update({
                'page_id': seo_view.website_page_id.id,
                'view_arch': view_arch,
                'user_id': self.env.user.id,
                'header_title': seo_view.header_title,
                'header_description': seo_view.header_description,
                'publish_url':seo_view.publish_url
            })
        else:
            base_version = self.browse(int(vals.get('base_version')))
            if not base_version:
                raise UserError('Base version is required')

            if not base_version.header_title or not base_version.header_description:
                raise UserError("Selected base version has missing header data")

            base_version_vals = base_version.read([
                'view_id',
                'page_id',
                'view_arch',
                'parse_html',
                'parse_html_binary',
                'parse_html_filename',
                'header_title',
                'header_description',
                'image',
                'image_filename',
                'publish_url',
                'selected_filename',
                # 'header_metadata_ids',
                'header_link_ids'
            ])[0]

            base_version_vals['view_id'] = base_version_vals['view_id'][0] if base_version_vals['view_id'] else False
            base_version_vals['page_id'] = base_version_vals['page_id'][0] if base_version_vals['page_id'] else False

            vals.update(base_version_vals)

            for o2m_field in ['header_link_ids']:
                if o2m_field in base_version_vals:
                    # Create copies of the related records
                    copied_ids = []
                    for record in base_version[o2m_field]:
                        # Create new records by copying the fields
                        copied_record = record.copy()
                        copied_ids.append(copied_record.id)

                    # Update the vals with the copied record IDs
                    vals[o2m_field] = [(6, 0, copied_ids)]

            #
            # change = vals.get('change')
            #
            # if not change:
            #     raise UserError('Change is required')
            #
            # description = vals.get('description')

            vals.update({
                'status' : True,
                'user_id' : self.env.user.id,
                'stage' : 'in_progress',
                'publish' : False
            })

            # base_version.header_metadata_ids.write({'is_active': False})
            base_version.header_link_ids.write({'is_active': False})

        record = super(WebsitePageVersion, self).create(vals)



        seo_view.write({
            'parse_html': record.parse_html,
            'parse_html_filename': record.parse_html_filename,
            'parse_html_binary': record.parse_html_binary,
            'publish': False,
            'stage':record.stage,
            'header_title': record.header_title,
            'header_description': record.header_description,
            'image':record.image,
            'image_filename':record.image_filename,
            'publish_url': record.publish_url
        })

        if seo_view.website_page_id and record.view_arch:
            seo_view.website_page_id.arch_db = record.view_arch

        record.view_id.message_post(body=f"Version '{record.name}' created and activated")

        seo_view.active_version = record.id


        if initial_version and not record.selected_filename:
            self.env['automated_seo.page_header_link'].create({
                'view_id': record.view_id.id,
                'css_link': "//cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.css",
                'view_version_id': record.id
            })
        else:
            # record.header_metadata_ids.write({'is_active': True})
            record.header_link_ids.write({'is_active': True})
            seo_view.update_stage_file()

        return record


    # def create_default_version_metadata(self, record):
    #     if not record.view_id.header_metadata_ids:
    #         image_url = f'inhouse/{record.view_id.name.replace(" ","").lower()}/{record.view_id.image_filename.replace(" ", "-").replace("%20", "-").lower()}' if record.view_id.image  else 'main/img/og/DEFAULT_PAGE_IMAGE.jpg'
    #         self.env['automated_seo.page_header_metadata'].create([
    #             {
    #                 'property': 'og:title',
    #                 'content': f'{record.header_title}',
    #                 'view_id': record.view_id.id,
    #                 'view_version_id': record.id
    #             },
    #             {
    #                 'property': 'og:description',
    #                 'content': 'Default page description',
    #                 'view_id': record.view_id.id,
    #                 'view_version_id': record.id
    #             },
    #             {
    #                 'property': 'og:image',
    #                 'content': f'<?php echo BASE_URL_IMAGE; ?>{image_url}',
    #                 'view_id': record.view_id.id,
    #                 'view_version_id': record.id
    #             },
    #             {
    #                 'property': 'og:url',
    #                 'content': f'<?php echo BASE_URL; ?>{record.view_id.name}',
    #                 'view_id': record.view_id.id,
    #                 'view_version_id': record.id
    #             }
    #         ])
    #
    #         self.env['automated_seo.page_header_link'].create({
    #             'view_id' : record.view_id.id,
    #             'css_link' : "//cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.css",
    #             'view_version_id': record.id
    #         })



    def action_version(self):

        self.ensure_one()
        # id =self.env.context.get('id', 'Unknown')
        view_id = self.env.context.get('view_id')
        current_version = self.env['website.page.version'].search(
            ['&', ('status', '=', True), ('view_id', '=', view_id)], limit=1)
        view = self.env['automated_seo.view'].search([('id', '=', current_version.view_id.id)])

        if view.has_edit_permission:
            if current_version:
                current_version.write({
                    'status': False,
                    'stage': view.stage,
                    'parse_html': view.parse_html if view.parse_html else None,
                    'parse_html_filename': view.parse_html_filename if view.parse_html_filename else None,
                    'parse_html_binary': view.parse_html_binary if view.parse_html_binary else None,
                    'header_title': view.header_title,
                    "header_description": view.header_description,
                    'image': view.image,
                    'image_filename': view.image_filename,
                    'publish_url': view.publish_url
                    # "stage_url":None
                })

            self.status = True
            if self.stage in ['approved', 'publish', 'in_review', 'unpublish']:
                selected_file_version = None
                if view.selected_filename:
                    base_name, ext = os.path.splitext(view.selected_filename.name)
                    selected_file_version = f'{base_name}_{self.name}{ext}'

                page_name = f'{selected_file_version}' if selected_file_version else f"{view.name}_{self.name}.php"
                upload_success = transfer_file_via_scp(
                    page_name=page_name,
                    file_data=self.parse_html_binary
                )

                if not upload_success:
                    self.message_post(body=f"{page_name} file upload failed.")
                    raise UserError(f"{page_name} file upload failed.")

                self.stage_url = f"https://automatedseo.bacancy.com/{page_name}"

                # if upload_success:
                #
                #     self.stage_url = f"https://automatedseo.bacancy.com/{page_name}"
                #     # self.message_post(body="Record sent for review")
                #
                #     # self.message_post(body="Record moved to the done approved")
                # else:
                #     self.message_post(body=f"{page_name} file upload failed.")
                #     raise UserError(f"{page_name} file upload failed.")

            view.write({
                'active_version': self.id,
                'parse_html': self.parse_html if self.parse_html else None,
                'parse_html_filename': self.parse_html_filename if self.parse_html_filename else None,
                'parse_html_binary': self.parse_html_binary if self.parse_html_binary else None,
                'image': self.image,
                'image_filename': self.image_filename,
                'publish': self.publish if self.publish else False,
                'header_title': self.header_title,
                'header_description': self.header_description,
                'publish_url': self.publish_url,
                'stage': self.stage
            })

            view.page_id.arch_db = self.view_arch if self.view_arch else None

            # if current_version.header_metadata_ids:
            #     current_version.header_metadata_ids.write({'is_active': False})

            # if self.header_metadata_ids:
            #     self.header_metadata_ids.write({'is_active': True})

            if current_version.header_link_ids:
                current_version.header_link_ids.write({'is_active': False})

            if self.header_link_ids:
                self.header_link_ids.write({'is_active': True})

            self.view_id.message_post(body=f"Version '{self.name}' activated")

    def action_download_html(self):
        """Download the parsed HTML file"""
        self.ensure_one()
        if not self.parse_html_binary:
            raise UserError('No HTML file available for download')

        page_name = self.view_id.name.replace(' ', '_')
        file_name = f"{page_name}_{self.name}.php"
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=website.page.version&id={self.id}&field=parse_html_binary&filename={file_name}&download=true',
            'target': 'self',
        }

    # @api.model
    # def default_get(self, fields_list):
    #     context = self.env.context
    #     view_id = context.get('view_id', False)
    #     description = context.get('description', False)
    #     change = context.get('change', False)
    #     base_version = context.get('base_version', False)
    #
    #     defaults = super(WebsitePageVersion, self).default_get(fields_list)
    #
    #     if 'view_id' in fields_list:
    #         defaults.update({'view_id': view_id})
    #     if 'description' in fields_list:
    #         defaults.update({'description': description})
    #     if 'change' in fields_list:
    #         defaults.update({'change': change})
    #     if 'base_version' in fields_list:
    #         defaults.update({'base_version': base_version})
    #
    #     return defaults
