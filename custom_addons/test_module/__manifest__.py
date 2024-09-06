# -*- coding: utf-8 -*-
{
    'name': "Test module",
    'author': "Darsh",
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/snippets/offer_dynamic_snippet.xml',
        'views/snippets/offer_static_snippet.xml',
        'views/snippets/snippets.xml',
        'views/offer_benefits_website_view.xml',
        'views/offers_website_view.xml',
        'views/website_menus.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'test_module/static/src/css/*.css',
            'test_module/static/src/js/offers.js',
        ],
    },
}
