from odoo import api,models,fields
# from reportlab.graphics.renderbase import inverse


class PhpToSnippet(models.Model):
    _name = 'automated_seo.php_to_snippet'

    php = fields.Char(string="PHP Tag")
    snippet = fields.Char(string="Snippet Tag")