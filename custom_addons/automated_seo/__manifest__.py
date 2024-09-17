{
    'name': 'AutomatedSEO',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'A simple QWeb demo',
    'description': """This module demonstrates a basic QWeb template in Odoo 16.""",
    'author': 'Hetul Patel',
    'depends': ['base', 'web'],
    'data': [
        "views/snippets/s_angular_header.xml",
        "views/snippets/s_angular_heir_tag.xml",
        "views/snippets/s_about_angular_team.xml",
        "views/snippets/s_angular_hire_steps.xml",
        "views/snippets/s_angular_choose_developer.xml",
        "views/snippets/s_angular_story.xml",
        "views/snippets/s_offer.xml",
        "views/snippets/s_angular_offer.xml",
        "views/snippets/s_hire_angular_dev.xml",
        "views/snippets/s_angular_offer.xml",
        "views/snippets/s_schedule_interview.xml",
        "views/snippets/s_angular_dev_expertise.xml",
        "views/snippets/s_trusted.xml",
        "views/snippets/s_banner.xml",
        "views/snippets/s_full_stack_angular_type.xml",
        "views/snippets/s_useful_links.xml",
        "views/snippets/s_frequently_ask_questions.xml",
        "views/snippets/s_footer.xml",
        "views/snippets/s_help.xml",
        'views/snippets/snippets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'automated_seo/static/src/css/casestudy.css',
            'automated_seo/static/src/css/faq.css',
            'automated_seo/static/src/css/footer-slider.css',
            'automated_seo/static/src/css/style.css',
            'automated_seo/static/src/css/tech-stack.css',
            # 'automated_seo/static/src/js/angular_story.js',

        ],
        'website.assets_wysiwyg': [
            ('include', 'web._assets_helpers'),
            'automated_seo/static/src/js/angular_offer.js'
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}