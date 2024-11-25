from odoo import api,models,fields
# from reportlab.graphics.renderbase import inverse


class PhpToSnippet(models.Model):
    _name = 'automated_seo.php_to_snippet'

    name = fields.Char(string="Name")
    php = fields.Char(string="PHP Tag")
    snippet = fields.Text(string="Snippet Tag")
    php_tag = fields.Boolean(string="PHP tag")
