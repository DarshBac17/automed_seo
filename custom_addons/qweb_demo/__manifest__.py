{
    'name': 'QWeb Demo',
    'version': '16.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'A dynamic QWeb snippet demo for Odoo 16',
    'description': """This module demonstrates a dynamic QWeb snippet in Odoo 16.""",
    'author': 'Your Name',
    'depends': ['website'],
    'data': [
        'views/snippets/qweb_demo_template.xml',
        'views/snippets/snippets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'qweb_demo/static/src/js/public_widget.js',
            'qweb_demo/static/src/xml/qweb_js_template.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}