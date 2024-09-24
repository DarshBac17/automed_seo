{
    'name': 'AutomatedSEO',
    'version': '1.0',
    'category': 'Extra Tools',
    'license':'LGPL-3',
    'summary': 'A simple QWeb demo',
    'description': """This module demonstrates a basic QWeb template in Odoo 16.""",
    'author': 'Hetul Patel',
    'depends': ['base',"web", 'website'],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        "views/views.xml",
        "views/php_mapper_view.xml",
        # "views/snippets/form/s_banner_form.xml",
        # "views/snippets/form/s_center_form.xml",
        # "views/snippets/form/s_footer_form.xml",
        "views/snippets/footer/s_footer_slider.xml",
        "views/snippets/footer/s_footer_slider_bg_white.xml",
        "views/snippets/footer/s_footer.xml",
        "views/snippets/footer/s_footer_bg_white.xml",
        # "views/snippets/s_angular_header.xml",
        # "views/snippets/s_angular_heir_tag.xml",
        # "views/snippets/s_about_angular_team.xml",
        # "views/snippets/s_angular_hire_steps.xml",
        # "views/snippets/s_angular_choose_developer.xml",
        # "views/snippets/s_angular_story.xml",
        # "views/snippets/s_offer.xml",
        # "views/snippets/s_angular_offer.xml",
        # "views/snippets/s_hire_angular_dev.xml",
        # "views/snippets/s_angular_offer.xml",
        # "views/snippets/s_schedule_interview.xml",
        # "views/snippets/s_angular_dev_expertise.xml",
        # "views/snippets/s_trusted.xml",
        "views/snippets/s_counting_sec.xml",
        # "views/snippets/s_banner.xml",
        # "views/snippets/s_full_stack_angular_type.xml",
        # "views/snippets/s_useful_links.xml",
        # "views/snippets/s_frequently_ask_questions.xml",
        # "views/snippets/s_footer.xml",
        # "views/snippets/s_help.xml",
        'views/snippets/snippets.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            'automated_seo/static/src/css/casestudy.css',
            'automated_seo/static/src/css/faq.css',
            'automated_seo/static/src/css/footer-slider.css',
            'automated_seo/static/src/css/style.css',
            'automated_seo/static/src/css/tech-stack.css',

        ],
        'website.assets_wysiwyg': [
            ('include', 'web._assets_helpers'),
            'automated_seo/static/src/js/angular_offer.js'
        ],
    },
}