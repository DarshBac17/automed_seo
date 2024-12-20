from dataclasses import field

from odoo import api,models,fields

class PageHeader(models.Model):
    _name = 'automated_seo.page_header'

    page = fields.Char(string="Page", required=True)
    # name = fields.Char(string="Name")


    def action_save(self):
        pass



class HeaderMeta(models.Model):
    _name = 'automated_seo.header_metadata'

    name = fields.Char(string="Name")
    property = fields.Char(string="Property")
    content = fields.Text(string="Content")

    # Many-to-One relationship: Metadata belongs to a page header
    page_header_id = fields.Many2one(
        'automated_seo.page_header',
        string="Page Header",
        ondelete='cascade',
    )