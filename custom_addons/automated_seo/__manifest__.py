{
    'name': 'AutomatedSEO',
    'version': '1.0',
    'category': 'Extra Tools',
    'license':'LGPL-3',
    'summary': 'A simple QWeb demo',
    'description': """This module demonstrates a basic QWeb template in Odoo 16.""",
    'author': 'Hetul Patel',
    'depends': ['website', 'web_editor','base',"web"],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        "views/website/footer.xml",
        "views/website/header.xml",
        # "views/page_header_metadata.xml",
        'views/version.xml',
        "views/views.xml",
        "views/tags.xml",
        "views/cron_job.xml",
        "views/email_wizard_view.xml",

        'views/templates.xml',
        "views/mapper_view.xml",
        "views/php_to_snippet.xml",
        "views/php_mapper_view.xml",
        "views/php_variables_view.xml",
        "views/style_view.xml",
        "views/website/header.xml",
        "views/website/footer.xml",
        "views/snippets/steps/s_steps_bg_white.xml",
        "views/snippets/steps/s_steps_bg_gray.xml",
        "views/snippets/steps/s_sub_step_white.xml",
        "views/snippets/steps/s_sub_step_gray.xml",
        "views/snippets/footer/s_slider_form_footer_white.xml",
        "views/snippets/footer/s_footer_slider_bg_gray.xml",
        "views/snippets/header/s_header.xml",
        "views/snippets/footer/s_footer_slider_bg_white.xml",
        "views/snippets/footer/s_footer_bg_gray.xml",
        "views/snippets/footer/s_footer_bg_white.xml",
        "views/snippets/counting_sec/s_counting_sec.xml",
        "views/snippets/tech_stack/s_technical_stack_bg_gray.xml",
        "views/snippets/tech_stack/s_technical_stack_bg_white.xml",
        "views/snippets/tech_stack/s_sub_tech_stack.xml",
        "views/snippets/trusted/s_trusted_bg_gray.xml",
        "views/snippets/trusted/s_trusted_bg_white.xml",
        "views/snippets/breadcrumb/s_breadcrumb.xml",
        "views/snippets/useful_links/s_useful_links_bg_gray.xml",
        "views/snippets/useful_links/s_useful_links_bg_white.xml",
        "views/snippets/useful_links/s_sub_useful_link.xml",
        "views/snippets/faq/s_faq_bg_white.xml",
        "views/snippets/faq/s_faq_bg_gray.xml",
        "views/snippets/faq/s_faq_with_button_bg_white.xml",
        "views/snippets/faq/s_faq_with_button_bg_gray.xml",
        "views/snippets/faq/s_faq_with_list_bg_gray.xml",
        "views/snippets/faq/s_faq_with_list_bg_white.xml",
        "views/snippets/faq/s_sub_faq_tab_white.xml",
        "views/snippets/faq/s_sub_faq_tab_gray.xml",
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
        "views/snippets/side_image/s_side_img_sub_card_gray.xml",
        "views/snippets/side_image/s_side_img_sub_card_white.xml",
        "views/snippets/side_image/s_side_video_bg_white.xml",
        "views/snippets/side_image/s_side_video_bg_gray.xml",
        "views/snippets/side_image/s_sub_video_card_gray.xml",
        "views/snippets/side_image/s_sub_video_card_white.xml",
        "views/snippets/cta/s_dark_cta_bg_white.xml",
        "views/snippets/cta/s_dark_cta_bg_gray.xml",
        "views/snippets/banner/s_banner_health_bg_gray.xml",
        "views/snippets/banner/s_banner_side_image_with_2_button.xml",
        "views/snippets/banner/s_banner_side_image_with_2_button_and_bg.xml",
        "views/snippets/banner/s_banner_side_image_with_button.xml",
        "views/snippets/banner/s_banner_side_image_with_form_and_bg.xml",
        "views/snippets/banner/s_banner_side_image_with_icons.xml",
        "views/snippets/banner/s_banner_side_matrix_with_button_and_icon.xml",
        "views/snippets/banner/s_banner_side_matrix_with_button.xml",
        "views/snippets/banner/s_banner_side_matirx_with_form.xml",
        "views/snippets/services/s_service_card_bg_gray.xml",
        "views/snippets/services/s_service_sub_card_gray.xml",
        "views/snippets/services/s_service_card_bg_white.xml",
        "views/snippets/services/s_service_sub_card_white.xml",
        "views/snippets/services/s_service_tab_bg_white.xml",
        "views/snippets/services/s_service_sub_tab_white.xml",
        "views/snippets/services/s_service_tab_bg_gray.xml",
        "views/snippets/services/s_service_sub_tab_gray.xml",
        "views/snippets/services/s_service_list_bg_white.xml",
        "views/snippets/cards/s_card_with_icon_bg_gray.xml",
        "views/snippets/cards/s_card_with_icon_bg_white.xml",
        "views/snippets/cards/s_sub_card_with_icon_gray.xml",
        "views/snippets/cards/s_sub_card_with_icon_white.xml",
        "views/snippets/cards/s_card_with_list_bg_gray.xml",
        "views/snippets/cards/s_card_with_list_bg_white.xml",
        "views/snippets/cards/s_sub_card_with_list_white.xml",
        "views/snippets/cards/s_sub_card_with_list_gray.xml",
        "views/snippets/cards/s_card_with_list_and_button_bg_gray.xml",
        "views/snippets/cards/s_card_with_list_and_button_bg_white.xml",
        "views/snippets/cards/s_sub_card_with_list_and_button_gray.xml",
        "views/snippets/cards/s_sub_card_with_list_and_button_white.xml",
        "views/snippets/cards/s_card_2_box_list_bg_white.xml",
        "views/snippets/cards/s_card_2_box_list_bg_gray.xml",
        "views/snippets/cards/s_card_with_icon_grid_2_bg_white.xml",
        "views/snippets/cards/s_card_bg_white.xml",
        "views/snippets/cards/s_card_bg_gray.xml",
        "views/snippets/cards/s_sub_card_gray.xml",
        "views/snippets/cards/s_sub_card_white.xml",
        "views/snippets/hiring_model/s_hiring_model_bg_white.xml",
        "views/snippets/hiring_model/s_hiring_model_bg_gray.xml",
        "views/snippets/hiring_model/s_sub_hiring_model.xml",
        "views/snippets/leadership/s_leadership_bg_gray.xml",
        "views/snippets/leadership/s_leadership_bg_white.xml",
        "views/snippets/internal_linking/s_internal_linking_box_with_arrow_bg_gray.xml",
        "views/snippets/internal_linking/s_internal_linking_box_with_arrow_bg_white.xml",
        "views/snippets/internal_linking/s_sub_internal_link_box_arrow_gray.xml",
        "views/snippets/internal_linking/s_sub_internal_link_box_arrow_white.xml",
        "views/snippets/internal_linking/s_internal_linking_list_bg_white.xml",
        "views/snippets/internal_linking/s_internal_linking_list_bg_gray.xml",
        "views/snippets/industries/s_industries_gray.xml",
        "views/snippets/industries/s_industries_white.xml",
        "views/snippets/industries/s_sub_industry.xml",
        "views/snippets/video_section/s_solution_health_bg_white.xml",
        "views/snippets/video_section/s_solution_health_bg_gray.xml",
        "views/snippets/testimonials/s_client_feedback_2_bg_white.xml",
        "views/snippets/testimonials/s_client_feedback_2_bg_gray.xml",
        "views/snippets/testimonials/s_sub_client_feedback_2_white.xml",
        "views/snippets/testimonials/s_sub_client_feedback_2_gray.xml",
        "views/snippets/testimonials/s_client_feedback_bg_white.xml",
        "views/snippets/testimonials/s_client_feedback_bg_gray.xml",
        "views/snippets/testimonials/s_sub_client_feedback_gray.xml",
        "views/snippets/testimonials/s_sub_client_feedback_white.xml",
        "views/snippets/image_section/s_hire_expert_bg_white.xml",
        "views/snippets/image_section/s_hire_expert_bg_gray.xml",
        "views/snippets/tab/s_horizontal_tab_bg_white.xml",
        "views/snippets/tab/s_vertical_tab_bg_gray.xml",
        "views/snippets/tab/s_vertical_tab_bg_white.xml",
        "views/snippets/tab/s_horizontal_tab_bg_gray.xml",
        "views/snippets/tab/s_dedicated_dev_tack_stack_bg_gray.xml",
        "views/snippets/tab/s_dedicated_dev_tack_stack_bg_white.xml",
        "views/snippets/tab/s_sub_dedicated_dev_tack_stack_bg_white.xml",
        "views/snippets/tab/s_sub_dedicated_dev_tack_stack_bg_gray.xml",
        "views/snippets/case_study/s_case_study_bg_gray.xml",
        "views/snippets/case_study/s_case_study_bg_white.xml",
        "views/snippets/case_study/s_sub_case_study.xml",
        "views/snippets/slider/s_combination_slider_bg_white.xml",
        "views/snippets/slider/s_combination_slider_bg_gray.xml",
        "views/snippets/slider/s_slider_list_bg_gray.xml",
        "views/snippets/slider/s_slider_list_bg_white.xml",
        "views/snippets/slider/s_sub_combination_slider_white.xml",
        "views/snippets/slider/s_sub_combination_slider_gray.xml",
        "views/snippets/developer/s_profile_bg_gray.xml",
        "views/snippets/developer/s_profile_bg_white.xml",
        "views/snippets/developer/s_sub_worked_with_image.xml",
        "views/snippets/developer/s_sub_profile_gray.xml",
        "views/snippets/developer/s_sub_profile_white.xml",
        "views/snippets/form/s_footer_form.xml",
        "views/snippets/form/s_single_form.xml",
        "views/snippets/form/s_form_with_price_gray.xml",
        "views/snippets/form/s_form_with_price_orange.xml",
        "views/snippets/fortune/s_fortune.xml",

        "views/snippets/trusted_parties/s_trusted_parties_bg_gray.xml",
        "views/snippets/trusted_parties/s_trusted_parties_bg_white.xml",
        'views/snippets/snippet_options.xml',
        "views/snippets/php_variable_option.xml",
        'views/snippets/snippets.xml',
        # "views/assets.xml"
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
            'automated_seo/static/src/css/custom.css',
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
            # 'automated_seo/static/src/js/website_version.js',
            # 'automated_seo/static/src/js/website_save.js',
            'automated_seo/static/src/js/snippet_options.js',
            'automated_seo/static/src/js/website_autosave.js',
            'automated_seo/static/src/js/snippet_preview.js',
            'automated_seo/static/src/js/php_variable_options.js',
            'automated_seo/static/src/js/p_tag_len_constraints.js',
            'automated_seo/static/src/js/dynamic_editable_box.js',
            'automated_seo/static/src/js/handle_tabs.js',
            # 'automated_seo/static/src/js/angular_offer.js'
        ],
        'web.assets_backend': [
            'automated_seo/static/src/css/automated_seo.css',
            'automated_seo/static/src/xml/view_list_button.xml',
            'automated_seo/static/src/js/views_tree_extend.js',
            'automated_seo/static/src/js/char_length_validator.js',
            'automated_seo/static/src/xml/char_length.xml',
            'automated_seo/static/src/css/char_length.scss',
        ],
        'website.assets_editor': [
            'automated_seo/static/src/systray_items/*',
        ],
    },
}
