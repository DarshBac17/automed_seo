from email.policy import default

from odoo import models, fields, api

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
        print("action call")


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
