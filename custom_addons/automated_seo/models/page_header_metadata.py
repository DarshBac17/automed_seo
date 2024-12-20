from dataclasses import field

from odoo import api,models,fields


class PageHeaderMeta(models.Model):
    _name = 'automated_seo.page_header_metadata'

    property = fields.Char(string="Property")
    content = fields.Text(string="Content")

    # Many-to-One relationship: Metadata belongs to a page header
    page_id = fields.Many2one(
        'automated_seo.view',
        string="Page id"
    )

    page_version_id =  fields.Many2one(
        'website.page.version',
        string="Page version id"
    )

    @api.model
    def create(self, vals):
        if 'page_id' in vals:
            page = self.env['automated_seo.view'].search([('id','=',vals['page_id'])],limit=1)
            vals['page_version_id'] = page.active_version_id[0].id
        record = super(PageHeaderMeta, self).create(vals)
        return record