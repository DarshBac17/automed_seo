from dataclasses import field

from odoo import api,models,fields


class PageHeaderMeta(models.Model):
    _name = 'automated_seo.page_header_metadata'

    property = fields.Char(string="Property")
    content = fields.Text(string="Content")
    view_id = fields.Many2one(
        'automated_seo.view',
        string="View id"
    )
    view_version_id =  fields.Many2one(
        'website.page.version',
        string="View version id"
    )
    is_active = fields.Boolean(string="Active", default=True)

    # @api.model
    # def create(self, vals):
    #     if 'view_id' in vals:
    #         page = self.env['automated_seo.view'].search([('id','=',vals['view_id'])],limit=1)
    #         vals['view_version_id'] = page.active_version[0].id
    #     record = super(PageHeaderMeta, self).create(vals)
    #     return record



class PageHeaderLink(models.Model):
    _name = 'automated_seo.page_header_link'

    view_id = fields.Many2one('automated_seo.view',string="View id")
    css_link = fields.Text(string="Css Link")
    view_version_id = fields.Many2one(
        'website.page.version',
        string="View version id"
    )
    is_active = fields.Boolean(string="Active", default=True)