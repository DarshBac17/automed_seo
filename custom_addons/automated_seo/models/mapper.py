from odoo import api,models,fields

class Parser(models.Model):
    _name = 'automated_seo.mapper'

    name = fields.Char(string="Snippet Name")
    snippet_id = fields.Char(string="Snippet id")
    tags = fields.Many2many('automated_seo.style_mapper', string="Tags")

