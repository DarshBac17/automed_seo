from odoo import api,models,fields
# from reportlab.graphics.renderbase import inverse


class Page(models.Model):
    _name = 'automated_seo.page'

    page_name = fields.Char(string="Page Name")
    snippet_id = fields.One2many('automated_seo.snippet_mapper',inverse_name='page',string="Snippet Id")
    version_id = fields.Char(string = "Version id")