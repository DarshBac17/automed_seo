odoo.define('my_blog_snippet.blog_snippet', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.BlogSnippet = publicWidget.Widget.extend({
        selector: '.dynamic-blog-snippet',
        start: function () {
            var self = this;
            return this._rpc({
                route: '/dynamic_blog_snippet',
                params: {},
            }).then(function (renderedHtml) {
                if (renderedHtml) {
                    self.$el.html(renderedHtml);
                } else {
                    self.$el.html('<p>Unable to load blog posts. Please try again later.</p>');
                }
            }).guardedCatch(function (error) {
                self.$el.html('<p>Error loading blog posts. Please try again later.</p>');
                console.error('Error loading blog posts:', error);
            });
        },
    });
});