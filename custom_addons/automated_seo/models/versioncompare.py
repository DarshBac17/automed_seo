from odoo import models, fields, api
import difflib
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup, NavigableString
from itertools import zip_longest
import  html
from .ftp_setup import transfer_file_via_scp
import re
import  base64
from ..models.view import View
from odoo.exceptions import UserError
class VersionCompareWizard(models.TransientModel):
    _name = 'version.compare.wizard'
    _description = 'Version Comparison Wizard'

    base_version_id = fields.Many2one('website.page.version', string='Base Version', required=True)
    compare_version_id = fields.Many2one('website.page.version', string='Compare Version', required=True)
    diff_html = fields.Html(string='Differences', readonly=True)


    def format_html_php(self,html_content, indent_size=4):        # Define tag sets
        inline_content_tags = {'p', 'li', 'b', 'i', 'strong', 'em', 'label', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6','title'}
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

        def format_nested_content(elem, indent, level):
            """Helper to format nested content with proper indentation"""
            lines = [f"{indent}<{elem.name}{format_attributes(elem)}>"]
            for child in elem.children:
                if isinstance(child, NavigableString):
                    text = child.strip()
                    if text:
                        lines.append(f"{indent}{' ' * indent_size}{text}")
                else:
                    lines.append(format_element(child, level + 1))
            lines.append(f"{indent}</{elem.name}>")
            return '\n'.join(line for line in lines if line.strip())

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
                # For FAQ links or structural content, preserve HTML structure
                if 'faq-head' in elem.get('class', []) or not should_inline_content(elem):
                    return format_nested_content(elem, indent, level)

                # For simple links, inline the content
                content = ' '.join(elem.stripped_strings)
                return f"{indent}<{elem.name}{attrs}>{content}</{elem.name}>"

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


        
    def is_php_content(self,text):
                # Check if content is PHP tag/include
        return '<?php' in text or text.strip().startswith('php')

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
                pattern = rf'\${var_name}\s*=\s*(?:".*?"|\'.*?\'|null);'
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

    def remove_empty_tags(self,html_parser):
        soup = BeautifulSoup(html_parser, 'html.parser')
        self_closing_tags = {"img", "input", "hr", "meta", "link"}

        def remove_empty(tag):
            if tag.name == "section" or tag.name in self_closing_tags:
                return

            if tag.name == 'span' and tag.get('class',[]) == ['bg-rightarrowLineBlack']:
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
    
    def handle_breadcrumbs(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        breadcrumb_navs = soup.find_all( attrs={"aria-label":"breadcrumb"})
        for nav in breadcrumb_navs:
            nav.name = "nav"

        for main_entity in soup.find_all(class_='breadcrumb'):
            breadcrumb_items_tags = main_entity.find_all(class_="breadcrumb-item")
            for index, breadcrumb in enumerate(breadcrumb_items_tags):
                if len(breadcrumb_items_tags) - 1 == index:
                    breadcrumb["class"].append("active")
                    breadcrumb["aria-current"]="page"
                    text_content = breadcrumb.get_text()
                    breadcrumb.clear()
                    breadcrumb.append(text_content)
                else:
                    a = breadcrumb.find('a')
                    if not a or not a.get('href') or a["href"] == "#":
                        clean_text = ' '.join(breadcrumb.text.replace('&amp;','&').replace('&nbsp;', ' ').split()).strip()
                        message = f"Please add a link in {clean_text} breadcrumb"
                        raise UserError(message)
                    next_sibling = a.next_sibling
                    if not next_sibling or (isinstance(next_sibling, str) and '/' not in next_sibling):
                        separator = soup.new_string(" / ")
                        a.insert_after(separator)
        return str(soup.prettify())

    def handle_itemprop_in_faq(self,html_content):

        soup = BeautifulSoup(html_content,"html.parser")
        for main_entity in soup.find_all(class_='o_answer_itemprop'):
            main_entity.find_all()[0]["itemprop"] = "text"

        return str(soup.prettify())
    
    def remove_sub_snippet_sections(self,html_parser):
        # Parse the HTML content
        soup = BeautifulSoup(html_parser, 'html.parser')

        sections = soup.find_all('section', class_='o_replace_section_div')
        for sec in sections:
            sec.name = 'div'
        return soup.prettify()
    def remove_odoo_classes_from_tag(self, html_parser):
            soup = BeautifulSoup(html_parser, "html.parser")

            for section in soup.find_all('section',class_='remove'):
                section.unwrap()

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
    
    def remove_br_tags(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all <br> tags
        br_tags = soup.find_all('br')

        # Iterate through each <br> tag
        for br in br_tags:
            # Check if the parent is a form tag
            if not br.find_parent('form'):
                br.decompose()  # Remove <br> tag

        # Return the modified HTML contentrecord.view_id.update_stage_file()
        return soup.prettify()


    def add_head(self, html_parser, seo_view_id):
        soup = BeautifulSoup('<html lang="en"><head></head><body></body></html>', 'html.parser')
        head_tag = soup.head
        seo_view = self.env['automated_seo.view'].browse(seo_view_id)
        page_name = seo_view.name.strip().lower().replace(" ", "-")
        title_tag = soup.new_tag('title')
        title_tag.string = seo_view.header_title
        head_tag.append(title_tag)

        description_meta = soup.new_tag('meta')
        description_meta['name'] = 'description'
        description_meta['content'] = seo_view.header_description
        head_tag.append(description_meta)
        common_meta_tag = BeautifulSoup('<?php include("tailwind/template/common-meta.php"); ?>',"html.parser")
        head_tag.append(common_meta_tag)

        og_title_meta = soup.new_tag('meta')
        og_title_meta['property'] = 'og:title'
        og_title_meta['content'] = seo_view.header_title
        head_tag.append(og_title_meta)

        og_desc_meta = soup.new_tag('meta')
        og_desc_meta['property'] = 'og:description'
        og_desc_meta['content'] = seo_view.header_description
        head_tag.append(og_desc_meta)

        image_url = f'inhouse/{seo_view.name.replace(" ", "").lower()}/{seo_view.image_filename.replace(" ", "-").replace("%20", "-").lower()}' if seo_view.name and seo_view.image_filename and seo_view.image else None

        if  image_url:
            og_image_meta = soup.new_tag('meta')
            og_image_meta['property'] = 'og:image'
            og_image_meta['content'] = f'<?php echo BASE_URL_IMAGE; ?>{image_url}'
            head_tag.append(og_image_meta)


        og_url_meta = soup.new_tag('meta')
        og_url_meta['property'] = 'og:url'

        # if not self.publish_url:
        #     self.publish_url = f"https://www.bacancytechnology.com/{self.name}"
        og_url_meta['content'] = seo_view.publish_url.replace("https://www.bacancytechnology.com/","<?php echo BASE_URL; ?>")

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
        for link in seo_view.header_link_ids:
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
                        "name": "{seo_view.header_title}",
                        "isPartOf": {{
                            "@id": "<?php echo BASE_URL; ?>#website"
                        }},
                        "datePublished": "2013-04-15T13:23:16+00:00",
                        "dateModified": "2024-07-17T14:31:52+00:00",
                        "description": "{seo_view.header_description}"
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
    
    def remove_extra_spaces(self,html_parser):
        inline_tags = ['a', 'span', 'button', 'div', 'td', 'p','h3','h1','h2','h4','h5','h6','li','img','b']
        for tag in inline_tags:
            pattern = f'<{tag}([^>]*)>\s*([^<]*)\s*</{tag}>'
            html_parser = re.sub(pattern, lambda m: f'<{tag}{m.group(1)}>{m.group(2).strip()}</{tag}>', html_parser)

        return html_parser
    

    # def action_compile_button(self,version_compare_parser):
    #     # view = View()
    #     seo_view_id = self.compare_version_id.view_id.id
    #     seo_view = self.env['automated_seo.view'].browse(seo_view_id)
    #     html_parser = seo_view.replace_php_tags_in_html(html_parser=version_compare_parser)
    #     html_parser = seo_view.handle_dynamic_anchar_tag(html_parser=html_parser)
    #     if html_parser:
    #         html_parser = seo_view.remove_bom(html_parser=html_parser)
    #         html_parser = seo_view.remove_empty_tags(html_parser = html_parser)
    #         html_parser = seo_view.handle_breadcrumbs(html_content=html_parser)
    #         html_parser = seo_view.handle_itemprop_in_faq(html_content=html_parser)
    #         html_parser = seo_view.add_head(html_parser = html_parser, seo_view_id = seo_view.compare_version_id.view_id.id)
    #         html_parser = seo_view.add_js_scripts(html_parser)
    #         html_parser = seo_view.remove_odoo_classes_from_tag(html_parser)
    #         soup = BeautifulSoup(html_parser, "html.parser")
    #         html_parser = soup.prettify()
    #         html_parser = seo_view.format_paragraphs(html_content=html_parser)
    #         html_parser = seo_view.remove_extra_spaces(html_parser = html_parser)
    #         html_parser = seo_view.format_html_php(html_content=html_parser)
    #         html_parser = re.sub(r'itemscope=""', 'itemscope', html_parser)
    #         html_parser = html.unescape(html_parser)
    #         print("html_parser====================")
    #         print(html_parser)
    #         return html_parser
    #
    #         file = base64.b64encode(html_parser.encode('utf-8'))
            # version = self.env['website.page.version'].search(['&',('view_id','=',self.id),("status", "=", True)],limit =1)
            # file_name = f"{view_name}_{self.active_version.name}.php"
            # self.write({
            #     'parse_html': html_parser,
            #     'parse_html_binary': file ,
            #     'parse_html_filename': file_name,

            # }
            # self.active_version.write({
            #     'parse_html': html_parser,
            #     'parse_html_binary':file,
            #     'parse_html_filename' : file_name
            # })
    def highlight_differences(self, base_soup, compare_soup):
        def compare_elements(base_elem, compare_elem):
            # Handle text nodes
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
                        if base_word != compare_word:
                            result.append(f'<span class="ae_highlight">{compare_word or ""}</span>')
                        else:
                            result.append(base_word)
                            
                    return BeautifulSoup(' '.join(result), 'html.parser')
                return compare_elem
                
            # Handle elements
            if hasattr(base_elem, 'children') and hasattr(compare_elem, 'children'):
                for base_child, compare_child in zip_longest(list(base_elem.children), list(compare_elem.children)):
                    if base_child and compare_child:
                        result = compare_elements(base_child, compare_child)
                        if result != compare_child:
                            compare_child.replace_with(result)
                            
            return compare_elem

        # Start comparison from root
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

    @api.onchange('base_version_id', 'compare_version_id')
    def compute_diff(self):
        if self.base_version_id and self.compare_version_id:
            base_content = self.base_version_id.view_arch or ''
            compare_content = self.compare_version_id.view_arch or ''
            if base_content and compare_content:
                base_soup = BeautifulSoup(base_content, 'html.parser')
                compare_soup = BeautifulSoup(compare_content, 'html.parser')
                result = self.compare_sections(base_soup, compare_soup)
                
                print("Resul================================")
                print(result)
                print("=======================pasrse content===============")
                print()
                html_parser = self.action_compile_button(version_compare_parser=result)
                file = base64.b64encode(html_parser.encode('utf-8'))
                result2 = transfer_file_via_scp(page_name="version_compare.php",file_data=file)
                print("Result=======================")
                print(result2)
            # def is_php_content(text):
            #     # Check if content is PHP tag/include
            #     return '<?php' in text or text.strip().startswith('php')
            # def highlight_differences(base_soup, compare_soup):
            #     if isinstance(base_soup, NavigableString) and isinstance(compare_soup, NavigableString):
            #         base_text = str(base_soup).strip()
            #         compare_text = str(compare_soup).strip()
            #         if is_php_content(base_text) or is_php_content(compare_text):
            #             return compare_soup
            #         if base_text != compare_text:
            #             # Split texts while preserving whitespace
            #             base_words = base_text.split(' ')
            #             compare_words = compare_text.split(' ')
            #             result = []
            #             for i, (base_word, compare_word) in enumerate(zip_longest(base_words, compare_words)):
            #                 if base_word != compare_word:
            #                     # Only wrap different word in span
            #                     result.append(f'<span class="ae_highlight">{compare_word or ""}</span>')
            #                 else:
            #                     # Keep unchanged word as-is
            #                     result.append(base_word)
                                
            #                 # Preserve original spacing
            #                 if i < len(compare_words) - 1:
            #                     result.append(' ')
                                
            #             return BeautifulSoup(''.join(result), 'html.parser')
            #         return compare_soup
                
            #     if hasattr(base_soup, 'children') and hasattr(compare_soup, 'children'):
            #         base_children = list(base_soup.children)
            #         compare_children = list(compare_soup.children)
                    
            #         for base_child, compare_child in zip_longest(base_children, compare_children):
            #             if base_child and compare_child:
            #                 highlighted = highlight_differences(base_child, compare_child)
            #                 if highlighted:
            #                     compare_child.replace_with(highlighted)
                
            #     return compare_soup

            # if base_content and compare_content:
            #     base_soup = BeautifulSoup(base_content, 'html.parser')
            #     compare_soup = BeautifulSoup(compare_content, 'html.parser')
                
            #     result = highlight_differences(base_soup, compare_soup)

            #     css = """
            #     <style>
            #         .ae_highlight { background-color: #ffcccc; }
            #     </style>
            #     """
            #     print("=============base version=================")
            #     print(base_content)
            #     print("==============================")
            #     print("=============compare version=================")
            #     print(compare_content)
            #     print("==============================")
            #     print("==============================")
            #     print(result)
            #     print("==============================")
            #     html_parser = str(result)
            #     file = base64.b64encode(html_parser.encode('utf-8'))
            #     result2 = transfer_file_via_scp(page_name="version_compare.php",file_data=file  )
            #     print("Result=======================")
            #     print(result2)
            #     self.diff_html =str(result)
            # else:
            #     self.diff_html = '<p>No content available for comparison</p>'

    def action_upload_compare_to_stage_version(self):
        print("===============action_upload_compare_to_stage_version================")
        print(self.diff_html)