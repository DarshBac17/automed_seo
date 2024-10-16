from odoo import api,models,fields

class Mapper(models.Model):
    _name = 'automated_seo.snippet_mapper'

    snippet_id = fields.Char(string="Snippet id")
    styles = fields.Many2many('automated_seo.style_mapper', string="Styles")
    element_class = fields.Text(string="Element Class")
    php_tag = fields.Text(string="Php Tag")
    image_name = fields.Char(string="Image Name")

