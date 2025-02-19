from odoo import api,models,fields
from odoo.fields import Many2one


class ViewTags(models.Model):
    _name = 'automated_seo.view_tags'

    name = fields.Char(string="Tag Name")

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The name must be unique!')]