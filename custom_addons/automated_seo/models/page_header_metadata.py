from dataclasses import field

from odoo import api,models,fields

class PageHeader(models.Model):
    _name = 'automated_seo.page_header'

    page = fields.Char(string="Page", required=True)
    # name = fields.Char(string="Name")
    title = fields.Text(string="Title")

    # One-to-Many relationship: A page can have multiple metadata entries
    metadata_ids = fields.One2many(
        'automated_seo.header_metadata',  # Target model
        'page_header_id',  # Field in the target model pointing to PageHeader
        string="Metadata"
    )


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