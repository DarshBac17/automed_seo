odoo.define('website.custom.editor', function (require) {
    'use strict';

    const websiteSnippetEditor = require('website.snippet.editor');
    const ajax = require('web.ajax');
    const Wysiwyg = require('web_editor.wysiwyg');

    const snippetPreview = websiteSnippetEditor.SnippetsMenu.include({
        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
            'mouseenter .ui-draggable': '_onSnippetHover',
            'mouseleave .ui-draggable': '_onSnippetLeave',

        }),

        init: function () {
            this._super.apply(this, arguments);
            this.previewPopup = null;
        },

        start: function () {
            this._super.apply(this, arguments);
            this._createPreviewPopup();
            return this._super.apply(this, arguments);
        },

        _createPreviewPopup: function () {
            if (!this.previewPopup) {
                this.previewPopup = $('<div/>', {
                    class: 'o_snippet_preview_popup',
                    css: {
                        'position': 'fixed',
                        'z-index': 1050,
                        'display': 'none',
                        'background': 'white',
                        'border': '1px solid #ccc',
                        'border-radius': '4px',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.1)',
                        'padding': '10px'
                    }
                }).appendTo('body');
            }
        },

       _onSnippetHover: function (ev) {
            clearTimeout(this.hoverTimeout);
            const $snippet = $(ev.currentTarget);

            const thumbnailUrl = $snippet.data('oe-thumbnail') ||
                                 $snippet.find('img').first().attr('src') ||
                                 $snippet.find('.oe_snippet_thumbnail img').first().attr('src') ||
                                 '/website/static/src/img/snippets_thumbs/' + $snippet.data('snippet') + '.svg';
            const snippetName = $snippet.attr('name') || 'Unnamed Snippet';

            const snippetTitle =$snippet.attr('name')||
                                 'Snippet Preview';
            const snippetOffset = $snippet.offset();
            const previewWidth = 300;
            const viewportWidth = $(window).width();
            let left = snippetOffset.left + $snippet.outerWidth() + 10;

            if (left + previewWidth > viewportWidth) {
                left = snippetOffset.left - previewWidth - 10;
            }

            // Debounced preview display
            this.hoverTimeout = setTimeout(() => {
                // Update popup content
                this.previewPopup.html(`
                    <div class="preview-header" style="margin-bottom: 10px; font-weight: bold;">
                        ${snippetTitle}
                    </div>
                    <div class="preview-content">
                        <img src="${thumbnailUrl}"
                             alt="${snippetTitle}"
                             style="max-width: 100%; height: auto;"
                             onload="console.log('✅ Preview image loaded successfully')"
                             onerror="console.error('❌ Preview image failed to load:', this.src); this.src='/web/static/src/img/placeholder.png'"/>
                    </div>
                `);

                this.previewPopup.css({
                    top: snippetOffset.top,
                    left: left,
                    width: previewWidth
                }).fadeIn(200);

                console.log('✨ Preview popup displayed');
            }, 150); // Add a small delay to debounce rapid hover actions
        },

        _onSnippetLeave: function () {
            clearTimeout(this.hoverTimeout);

            if (this.previewPopup) {
                this.previewPopup.stop(true).fadeOut(200, function () {
                });
            }
        },


         destroy: function () {
            if (this.previewPopup) {
                this.previewPopup.remove();
            }
            this._super.apply(this, arguments);
        },

    });

    return {
        SnippetsMenu: snippetPreview,
    };
});