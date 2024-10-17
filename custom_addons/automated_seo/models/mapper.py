from odoo import api,models,fields

class Mapper(models.Model):
    _name = 'automated_seo.mapper'

    name = fields.Char(string="Snippet Name")
    snippet_id = fields.Char(string="Snippet id")
    styles = fields.Many2many('automated_seo.style_mapper', string="Styles")
    php_tags = fields.Many2many('automated_seo.php_mapper', string ="PHP Tags")

