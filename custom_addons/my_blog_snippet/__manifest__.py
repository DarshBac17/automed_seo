{
    'name': 'Dynamic Blog Snippet',
    'version': '16.0.1.0.0',
    'category': 'Website',
    'summary': 'Dynamic snippet to display blog posts',
    'description': 'A custom dynamic snippet that displays recent blogs in a carousel or grid format.',
    'author': 'Your Name',
    'depends': ['website'],
    'data': [
        'views/blog_snippet_views.xml',
        'views/blog_snippet_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'my_blog_snippet/static/src/js/blog_snippet.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
