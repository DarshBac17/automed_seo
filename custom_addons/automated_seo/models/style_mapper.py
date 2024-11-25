from odoo import api,models,fields

class StyleMapper(models.Model):
    _name = 'automated_seo.style_mapper'

    name = fields.Char(string="Snippet Name")
    style_tag = fields.Char(string="Style Tag")