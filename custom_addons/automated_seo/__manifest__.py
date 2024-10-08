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
        "views/snippets/footer/s_footer_slider_bg_gray.xml",
        "views/snippets/header/s_header.xml",
        "views/snippets/footer/s_footer_slider_bg_white.xml",
        "views/snippets/footer/s_footer_bg_gray.xml",
        "views/snippets/footer/s_footer_bg_white.xml",
        "views/snippets/page/s_counting_sec.xml",
        "views/snippets/page/s_hire_steps_bg_gray.xml",
        "views/snippets/page/s_hire_steps_bg_white.xml",
        "views/snippets/page/s_technical_stack.xml",
        "views/snippets/page/s_trusted_bg_gray.xml",
        "views/snippets/page/s_trusted_bg_white.xml",
        "views/snippets/page/s_useful_links_bg_gray.xml",
        "views/snippets/page/s_useful_links_bg_white.xml",
        "views/snippets/page/s_ask_questions_bg_white.xml",
        "views/snippets/side_image/s_side_image_bg_gray.xml",
        "views/snippets/side_image/s_side_image_bg_white.xml",
        "views/snippets/side_image/s_left_side_image_bg_gray.xml",
        "views/snippets/side_image/s_left_side_image_bg_white.xml",
        "views/snippets/side_image/s_side_img_list_bg_white.xml",
        "views/snippets/side_image/s_side_img_list_bg_gray.xml",
        "views/snippets/side_image/s_right_side_img_list_bg_gray.xml",
        "views/snippets/side_image/s_right_side_img_list_bg_white.xml",
        "views/snippets/side_image/s_side_img_cards_bg_gray.xml",
        "views/snippets/side_image/s_side_img_cards_bg_white.xml",
        "views/snippets/banner/s_banner_cta_bg_gray.xml",
        "views/snippets/banner/s_banner_cta_bg_white.xml",
        "views/snippets/banner/s_banner_health_bg_gray.xml",
        "views/snippets/services/s_banner_cards_bg_white.xml",
        "views/snippets/services/s_banner_cards_bg_gray.xml",
        "views/snippets/services/s_hire_developer_bg_white.xml",
        "views/snippets/services/s_hire_developer_bg_gray.xml",
        "views/snippets/services/s_hire_expertise_developer_bg_white.xml",
        "views/snippets/cards/s_card_kick_start_bg_gray.xml",
        "views/snippets/cards/s_card_kick_start_bg_white.xml",
        "views/snippets/cards/s_card_success_core_bg_gray.xml",
        "views/snippets/cards/s_card_success_core_bg_white.xml",
        "views/snippets/cards/s_card_hire_model_bg_gray.xml",
        "views/snippets/cards/s_card_hire_model_bg_white.xml",
        "views/snippets/cards/s_card_2_box_list_bg_white.xml",
        "views/snippets/cards/s_card_2_box_list_bg_gray.xml",
        "views/snippets/cards/s_card_hire_dedicated_dev_bg_gray.xml",
        "views/snippets/cards/s_card_hire_dedicated_dev_bg_white.xml",
        "views/snippets/leadership/s_leadership_bg_gray.xml",
        "views/snippets/leadership/s_leadership_bg_white.xml",
        "views/snippets/internal_linking/s_internal_leverage_bg_gray.xml",
        "views/snippets/internal_linking/s_internal_leverage_bg_white.xml",
        "views/snippets/internal_linking/s_internal_other_service_bg_white.xml",
        "views/snippets/internal_linking/s_internal_other_service_bg_gray.xml",
        "views/snippets/industries/s_enable_growth_bg_gray.xml",
        "views/snippets/industries/s_enable_growth_bg_white.xml",
        "views/snippets/video_section/s_solution_health_bg_white.xml",
        "views/snippets/video_section/s_solution_health_bg_gray.xml",
        "views/snippets/video_section/s_build_software_bg_white.xml",
        "views/snippets/video_section/s_build_software_bg_gray.xml",
        "views/snippets/vertical_tab/s_vertical_tab_healthcare_bg_white.xml",
        "views/snippets/vertical_tab/s_vertical_tab_healthcare_bg_gray.xml",
        "views/snippets/testimonials/s_client_feedback_bg_white.xml",
        "views/snippets/testimonials/s_client_feedback_bg_gray.xml",
        "views/snippets/image_section/s_image_hire_expert_bg_white.xml",
        "views/snippets/image_section/s_image_hire_expert_bg_gray.xml",
        "views/snippets/horizontal_tab/s_salesforce_tech_bg_white.xml",
        "views/snippets/horizontal_tab/s_salesforce_tech_bg_gray.xml",
        "views/snippets/horizontal_tab/s_hire_dedicated_dev_bg_white.xml",
        "views/snippets/horizontal_tab/s_hire_dedicated_dev_bg_gray.xml",
        "views/snippets/sub_cards/s_card.xml",
        "views/snippets/case_study/s_case_study_bg_gray.xml",
        "views/snippets/case_study/s_case_study_bg_white.xml",
        "views/snippets/combination/s_combination_bg_white.xml",
        "views/snippets/combination/s_combination_bg_gray.xml",
        "views/snippets/developer/s_profile_bg_gray.xml",
        "views/snippets/developer/s_profile_bg_white.xml",
        "views/snippets/form/s_banner_form.xml",
        "views/snippets/form/s_footer_form.xml",
        "views/snippets/form/s_center_form.xml",
        "views/snippets/developer_price/s_developer_price_bg_gray.xml",
        "views/snippets/developer_price/s_developer_price_bg_orange.xml",
        "views/snippets/trusted_parties/s_trusted_parties_bg_gray.xml",
        "views/snippets/trusted_parties/s_trusted_parties_bg_white.xml",
        'views/snippets/snippets.xml',

        # "views/snippets/s_angular_offer.xml",
        # "views/snippets/page/s_developer_pricing_bg_white.xml",
        # "views/snippets/s_angular_header.xml",
        # "views/snippets/s_angular_heir_tag.xml",
        # "views/snippets/s_about_angular_team.xml",
        # "views/snippets/s_angular_hire_steps.xml",
        # "views/snippets/s_angular_choose_developer.xml",
        # "views/snippets/s_angular_story.xml",
        # "views/snippets/s_offer.xml",
        # "views/snippets/s_hire_angular_dev.xml",
        # "views/snippets/s_angular_offer.xml",
        # "views/snippets/s_schedule_interview.xml",
        # "views/snippets/page/s_angular_dev_expertise_bg_white.xml",
        # "views/snippets/s_counting_sec.xml",
        # "views/snippets/s_banner.xml",
        # "views/snippets/s_full_stack_angular_type.xml",
        # "views/snippets/s_useful_links.xml",
        # "views/snippets/s_frequently_ask_questions.xml",
        # "views/snippets/s_footer.xml",
        # "views/snippets/s_help.xml",

    ],
    'assets': {
        'web.assets_frontend': [
            'automated_seo/static/src/css/casestudy.css',
            'automated_seo/static/src/css/faq.css',
            'automated_seo/static/src/css/footer-slider.css',
            'automated_seo/static/src/css/style.css',
            'automated_seo/static/src/css/tech-stack.css',
            'automated_seo/static/src/css/header.css',
            'automated_seo/static/src/css/footer.css',
            'automated_seo/static/src/css/form.css',
            'automated_seo/static/src/css/hiring-modal-table.css',
            'automated_seo/static/src/css/indu-sec.css',
            'automated_seo/static/src/css/tab-sec.css',
            'automated_seo/static/src/js/main.js',
        ],
        'website.assets_wysiwyg': [
            ('include', 'web._assets_helpers'),
            'automated_seo/static/src/js/angular_offer.js'
        ],
    },
}
