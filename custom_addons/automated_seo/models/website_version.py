from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import UserError

from automated_seo.odoo.modules.module import current_test


class WebsitePageVersion(models.Model):
    _name = 'website.page.version'
    _description = 'Website Page Version'
    _order = 'create_date desc'

    name = fields.Char('Version Name', required=True)
    description = fields.Text('Description')
    view_id =  fields.Many2one('automated_seo.view', string='View', required=True)
    page_id = fields.Many2one('website.page', string='Website Page', required=True)
    view_arch = fields.Text('Saved View Architecture', required=True)
    parse_html = fields.Text(string="Parse HTML")
    parse_html_binary = fields.Binary(string="Parsed HTML File", attachment=True)
    parse_html_filename = fields.Char(string="Parsed HTML Filename")
    user_id = fields.Many2one('res.users', string='Created by')
    status = fields.Boolean('Status',default=False)

    def action_version(self):
        print("==========================")
        # print(self.env.context)
        # id = self.env.context.get('params', 'Unknown')
        # id = int(id.get('id'))
        # print(id)
        # print("==========================")
        #
        # current_version  = self.env['website.page.version'].search([('status','=',True)],limit=1)
        # current_version.status = False
        # active_version  = self.env['website.page.version'].search([('id','=',id)],limit=1)
        # active_version.status = True





    # def get_formview_id(self, access_uid=None):
    #     """Disable form view"""
    #     return False

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """Override to prevent form view from loading"""
        result = super(WebsitePageVersion, self).get_view(view_id, view_type, **options)
        if view_type == 'form':
            raise UserError('Form view is not available for you')
        return result

    def write(self):
        print("writecall==============================")

    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     result = super(WebsitePageVersion, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                              submenu=submenu)
    #     if view_type == 'form':
    #         print("=============insdie")
    #         # Return tree view instead of form view
    #         return super(WebsitePageVersion, self).fields_view_get(
    #             view_id=self.env.ref('your_module.view_version_tree').id, view_type='tree', toolbar=toolbar,
    #             submenu=submenu)
    #     return result

# from odoo import models, fields, api
#
# class WebsitePageVersion(models.Model):
#     _name = 'website.page.version'
#     _description = 'Website Page Version'
#     _order = 'create_date desc'
#
#     name = fields.Char('Version Name', required=True)
#     description = fields.Text('Description')
#     view_id =  fields.Many2one('automated_seo.view', string='View', required=True)
#     page_id = fields.Many2one('website.page', string='Website Page', required=True)
#     view_arch = fields.Text('Saved View Architecture', required=True)
#     parse_html = fields.Text(string="Parse HTML")
#     parse_html_binary = fields.Binary(string="Parsed HTML File", attachment=True)
#     parse_html_filename = fields.Char(string="Parsed HTML Filename")
#     create_uid = fields.Many2one('res.users', string='Created By', readonly=True)
