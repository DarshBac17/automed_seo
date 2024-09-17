from odoo import api,models,fields

class Author(models.Model):
    _name = 'automated_seo.php_mapper'

    name = fields.Char(string="Name")
    element_class = fields.Text(string="Element Class")
    php_tag = fields.Text(string="Php Tag")

