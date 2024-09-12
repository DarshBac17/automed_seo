{
    'name': 'AutomedSEO',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'A simple QWeb demo',
    'description': """This module demonstrates a basic QWeb template in Odoo 16.""",
    'author': 'Hetul Patel',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        "views/snippets/automed_seo_offer.xml",
        'views/snippets/snippet.xml',
        'views/offer_benefits_website_view.xml',
        'views/offers_website_view.xml',
        'views/website_menus.xml',
    ],
    'assets': {
            'web.assets_frontend': [
            'automed_seo/static/src/css/*.css',
            'automed_seo/static/src/js/public_widget.js',
            ]
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}