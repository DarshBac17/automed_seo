from odoo import models, fields, api
import difflib
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup, NavigableString
from itertools import zip_longest
import  html
from .ftp_setup import transfer_file_via_scp
import re
import  base64
class VersionCompareWizard(models.TransientModel):
    _name = 'version.compare.wizard'
    _description = 'Version Comparison Wizard'

    base_version_id = fields.Many2one('website.page.version', string='Base Version', required=True)
    compare_version_id = fields.Many2one('website.page.version', string='Compare Version', required=True)
    diff_html = fields.Html(string='Differences', readonly=True)


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
    @api.onchange('base_version_id', 'compare_version_id')
    def compute_diff(self):
        if self.base_version_id and self.compare_version_id:
            base_content = self.base_version_id.parse_html or ''
            compare_content = self.compare_version_id.parse_html or ''
            def is_php_content(text):
                # Check if content is PHP tag/include
                return '<?php' in text or text.strip().startswith('php')
            def highlight_differences(base_soup, compare_soup):
                if isinstance(base_soup, NavigableString) and isinstance(compare_soup, NavigableString):
                    base_text = str(base_soup).strip()
                    compare_text = str(compare_soup).strip()
                    if is_php_content(base_text) or is_php_content(compare_text):
                        return compare_soup
                    if base_text != compare_text:
                        # Split texts while preserving whitespace
                        base_words = base_text.split(' ')
                        compare_words = compare_text.split(' ')
                        result = []
                        for i, (base_word, compare_word) in enumerate(zip_longest(base_words, compare_words)):
                            if base_word != compare_word:
                                # Only wrap different word in span
                                result.append(f'<span class="ae_highlight">{compare_word or ""}</span>')
                            else:
                                # Keep unchanged word as-is
                                result.append(base_word)
                                
                            # Preserve original spacing
                            if i < len(compare_words) - 1:
                                result.append(' ')
                                
                        return BeautifulSoup(''.join(result), 'html.parser')
                    return compare_soup
                
                if hasattr(base_soup, 'children') and hasattr(compare_soup, 'children'):
                    base_children = list(base_soup.children)
                    compare_children = list(compare_soup.children)
                    
                    for base_child, compare_child in zip_longest(base_children, compare_children):
                        if base_child and compare_child:
                            highlighted = highlight_differences(base_child, compare_child)
                            if highlighted:
                                compare_child.replace_with(highlighted)
                
                return compare_soup

            if base_content and compare_content:
                base_soup = BeautifulSoup(base_content, 'html.parser')
                compare_soup = BeautifulSoup(compare_content, 'html.parser')
                
                result = highlight_differences(base_soup, compare_soup)

                css = """
                <style>
                    .ae_highlight { background-color: #ffcccc; }
                </style>
                """
                print("==============================")
                print(result)
                print("==============================")
                html_parser = str(result)
                file = base64.b64encode(html_parser.encode('utf-8'))
                result2 = transfer_file_via_scp(page_name="version_compare.php",file_data=file  )
                print("Result=======================")
                print(result2)
                self.diff_html =str(result)
            else:
                self.diff_html = '<p>No content available for comparison</p>'

    def action_upload_compare_to_stage_version(self):
        print("===============action_upload_compare_to_stage_version================")
        print(self.diff_html)