from odoo import models, fields

class BlogSnippet(models.Model):
    _name = 'blog.snippet'
    _description = 'Dynamic Blog Snippet'

    title = fields.Char('Title', required=True)
    content = fields.Text('Content')
    blog_image = fields.Binary('Image')
