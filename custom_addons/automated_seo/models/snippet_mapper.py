from odoo import api,models,fields

class SnippetMapper(models.Model):
    _name = 'automated_seo.snippet_mapper'

    snippet_id = fields.Char(string="Snippet id")
    element_class = fields.Text(string="Element Class")
    php_tag = fields.Text(string="Php Tag")
    image_name = fields.Char(string="Image Name")
    page = fields.Many2one('automated_seo.page',string ='Page')