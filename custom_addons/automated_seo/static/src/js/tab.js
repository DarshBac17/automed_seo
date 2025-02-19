console.log("tab called=========================")
odoo.define('website.custom.tabs', function (require) {
    'use strict';

    const websiteSnippetEditor = require('website.snippet.editor');
    const publicWidget = require('web.public.widget');
//    const websiteSnippetEditor = require('website.snippet.editor');
    const ajax = require('web.ajax');
    const Wysiwyg = require('web_editor.wysiwyg');

    const TabsWidget = websiteSnippetEditor.SnippetsMenu.include({
        events:_.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
            'click .tab-head': '_onTabClick'
        }),

         init: function () {
            console.log("init call================")
            this._super.apply(this, arguments);
        },

        start: function () {
            console.log("start call================")

            return this._super.apply(this, arguments);
        },

        _onTabClick: function (ev) {
            console.log("_onTabClick call================")


            const $tab = $(ev.currentTarget);
            const index = $tab.index();
            const $tabContainer = $tab.closest('.tab-head');

            // Update active states for tabs
            $tab
                .addClass('active')
                .siblings()
                .removeClass('active');

            // Update active states for content
            $tabContainer
                .find('.tab-head')
                .eq(index)
                .addClass('active')
                .siblings()
                .removeClass('active');
        }
    });

//    publicWidget.registry.WebsiteTabs = TabsWidget;
//
//    // Snippet options
//    const TabsSnippetOptions = websiteSnippetEditor.SnippetsMenu.include({
//        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
//            'click .o_we_customize_tabs_opts': '_onCustomizeTabs'
//        }),
//
//        start: function () {
//            this._super.apply(this, arguments);
//            console.log("Tab snippet options initialized");
//        },
//
//        _onCustomizeTabs: function (ev) {
//            console.log("Tab customization requested");
//            // Add tab customization logic here
//        }
//    });

    return {
        SnippetsMenu: TabsWidget,
//        TabsSnippetOptions: TabsSnippetOptions
    };
});