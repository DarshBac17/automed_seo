from odoo import api,models,fields


class PhpVariables(models.Model):
    _name = 'automated_seo.php_variables'

    name = fields.Char(string="Name") # data-php-var value
    type = fields.Integer(string="PHP Tag") # data-php-const-var
