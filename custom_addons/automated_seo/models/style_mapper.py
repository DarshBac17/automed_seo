from odoo import api,models,fields

class StyleMapper(models.Model):
    _name = 'automated_seo.style_mapper'

    name = fields.Char(string="Snippet Name")
    link = fields.Char(string="Style Tag")