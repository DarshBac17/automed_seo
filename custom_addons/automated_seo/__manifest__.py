{
    'name': 'AutomatedSEO',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'A simple QWeb demo',
    'description': """This module demonstrates a basic QWeb template in Odoo 16.""",
    'author': 'Hetul Patel',
    'depends': ['base', 'web'],
    'data': [
        "views/snippets/s_offer.xml",
        "views/snippets/s_angular_offer.xml",
        "views/snippets/s_hire_angular_offer.xml",
        "views/snippets/s_schedule_interview.xml",
        "views/snippets/s_trusted.xml",
        "views/snippets/s_banner.xml",
        'views/snippets/snippets.xml',
    ],
    'assets': {
            'web.assets_frontend': [
                'automated_seo/static/src/css/casestudy.css',
                'automated_seo/static/src/css/faq.css',
                'automated_seo/static/src/css/footer-slider.css',
                'automated_seo/static/src/css/style.css',
            ]
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}