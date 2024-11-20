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
           const previewWidth = 600;
            const previewHeight = 400;
            const viewportWidth = $(window).width();
             const viewportHeight = $(window).height();
            let left = snippetOffset.left + $snippet.outerWidth() + 10;

            if (left + previewWidth > viewportWidth) {
                left = snippetOffset.left - previewWidth - 10;
            }
             if (top + previewHeight > viewportHeight) {
                top = viewportHeight - previewHeight - 10;
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
/*odoo.define('website.snippet.preview', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var options = require('web_editor.snippets.options');

    console.log('🚀 Snippet Preview Module Loading...');

    var SnippetPreview = options.Class.extend({
        selector: '.oe_snippet_thumbnail, .oe_snippet, .oe_snippet_body',

        *//**
         * @override
         *//*
        init: function () {
            console.log('📌 Init: Initializing Snippet Preview');
            this._super.apply(this, arguments);
            this.previewPopup = null;
            this._bindEvents();
        },

        *//**
         * @override
         *//*
        willStart: function () {
            console.log('🎯 WillStart: Beginning initialization...');
            return this._super.apply(this, arguments);
        },

        *//**
         * Bind click events to snippets
         * @private
         *//*
        _bindEvents: function () {
            console.log('🔗 Binding events to snippets');
            var self = this;

            $(document).on('click', '.oe_snippet_thumbnail, .oe_snippet, .oe_snippet_body', function(ev) {
                console.log('🖱️ Snippet clicked:', this);
                self._handleSnippetClick(ev);
            });
        },

        *//**
         * Create preview popup if it doesn't exist
         * @private
         *//*
        _createPreviewPopup: function () {
            console.log('🎨 Creating Preview Popup');
            if (!this.previewPopup) {
                this.previewPopup = $('<div/>', {
                    class: 'o_snippet_preview_popup',
                    css: {
                        'position': 'fixed',
                        'z-index': 9999,
                        'display': 'none',
                        'background': 'white',
                        'border': '1px solid #ccc',
                        'border-radius': '4px',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.1)',
                        'padding': '10px'
                    }
                }).appendTo('body');
                console.log('✅ Preview Popup Created:', this.previewPopup);
            }
        },

        *//**
         * Handle snippet click event
         * @private
         * @param {Event} ev
         *//*
        _handleSnippetClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            console.log('🎯 Handling snippet click');

            var $snippet = $(ev.currentTarget);
            console.log('📄 Clicked element:', $snippet[0]);

            // Create popup if it doesn't exist
            this._createPreviewPopup();

            // Find the thumbnail
            var $thumbnail = $snippet.find('.oe_snippet_thumbnail_img, .o_snippet_thumbnail_img').first();
            var thumbnailUrl = $thumbnail.length ? $thumbnail.attr('src') : null;

            // If no thumbnail found, try other sources
            if (!thumbnailUrl) {
                thumbnailUrl = $snippet.data('oe-thumbnail') ||
                             $snippet.find('img').first().attr('src') ||
                             '/web/image/website.s_' + $snippet.data('snippet') + '_thumbnail';
            }

            console.log('🖼️ Thumbnail URL:', thumbnailUrl);

            // Get title
            var snippetTitle = $snippet.attr('data-bs-original-title') ||
                             $snippet.attr('title') ||
                             $snippet.data('name') ||
                             $snippet.find('.oe_snippet_thumbnail_title').text() ||
                             'Snippet Preview';

            console.log('📝 Snippet Title:', snippetTitle);

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
                         onerror="console.error('❌ Preview image failed to load:', this.src); this.src='/web/static/img/placeholder.png'"/>
                </div>
            `);

            // Calculate position
            var snippetOffset = $snippet.offset();
            var previewWidth = 300;
            var viewportWidth = $(window).width();
            var left = snippetOffset.left + $snippet.outerWidth() + 10;

            console.log('📐 Position calculation:', {
                snippetOffset: snippetOffset,
                previewWidth: previewWidth,
                viewportWidth: viewportWidth,
                initialLeft: left
            });

            // Adjust position if needed
            if (left + previewWidth > viewportWidth) {
                left = snippetOffset.left - previewWidth - 10;
                console.log('↔️ Adjusted left position:', left);
            }

            // Show the popup
            this.previewPopup.css({
                top: snippetOffset.top,
                left: left,
                width: previewWidth
            }).fadeIn(200);

            // Handle click outside
            $(document).one('click', (e) => {
                if (!$(e.target).closest(this.previewPopup).length &&
                    !$(e.target).closest($snippet).length) {
                    console.log('👆 Click outside detected, hiding preview');
                    this.previewPopup.fadeOut(200);
                }
            });
        },

        *//**
         * @override
         *//*
        destroy: function () {
            console.log('🗑️ Destroying Snippet Preview');
            if (this.previewPopup) {
                this.previewPopup.remove();
            }
            $(document).off('click', '.oe_snippet_thumbnail, .oe_snippet, .oe_snippet_body');
            this._super.apply(this, arguments);
        },
    });

    options.registry.SnippetPreview = SnippetPreview;

    return SnippetPreview;
});*/
//console.log("======================save===============call")


//code that represent thumbnail code as preview
/*odoo.define('website.custom.editor', function (require) {
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
                        'padding': '10px',
                        'max-width': '600px',
                        'max-height': '400px',
                        'overflow': 'hidden'
                    }
                }).appendTo('body');
            }
        },

        _onSnippetHover: function (ev) {
            clearTimeout(this.hoverTimeout);

            const $snippet = $(ev.currentTarget);
            const $snippetBody = $snippet.siblings('.oe_snippet_body');

            // Get the actual snippet content
            const snippetContent = $snippet.html();
            const snippetName = $snippet.find('.oe_snippet_thumbnail_title').text() || 'Preview';
            console.log("==============================")
            console.log(snippetContent)
            console.log($snippetBody)
            console.log($snippet.html())

            // Calculate position
            const snippetOffset = $snippet.offset();
            const previewWidth = 600;
            const previewHeight = 400;
            const viewportWidth = $(window).width();
            const viewportHeight = $(window).height();

            let left = snippetOffset.left + $snippet.outerWidth() + 10;
            let top = snippetOffset.top;

            // Adjust position if preview would go off screen
            if (left + previewWidth > viewportWidth) {
                left = snippetOffset.left - previewWidth - 10;
            }
            if (top + previewHeight > viewportHeight) {
                top = viewportHeight - previewHeight - 10;
            }

            // Debounced preview display
            this.hoverTimeout = setTimeout(() => {
                // Create a container for the visual preview
                const previewHTML = `
                    <div class="preview-header" style="margin-bottom: 10px; font-weight: bold; border-bottom: 1px solid #ccc; padding-bottom: 5px;">
                        ${snippetName}
                    </div>
                    <div class="preview-content" style="transform: scale(0.5); transform-origin: top left; width: 200%; height: 200%;">
                        ${snippetContent}
                    </div>
                `;

                this.previewPopup.html(previewHTML);

                // Apply necessary styles and show the popup
                this.previewPopup.css({
                    top: top,
                    left: left,
                }).fadeIn(200);

                // Initialize any dynamic components or widgets within the preview
                this.trigger_up('widgets_start_request', {
                    $target: this.previewPopup.find('.preview-content'),
                });
            }, 150);
        },

        _onSnippetLeave: function () {
            clearTimeout(this.hoverTimeout);
            if (this.previewPopup) {
                this.previewPopup.stop(true).fadeOut(200);
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
});*/
//odoo.define('website.snippet.preview', function (require) {
//    'use strict';
//     const websiteSnippetEditor = require('website.snippet.editor');
//    console.log('🚀 Snippet Preview Module Loading...');
//
//    const aSnippetMenu2 = websiteSnippetEditor.SnippetsMenu.include({
//        selector: '.oe_snippet_thumbnail, [data-oe-type="snippet"], .oe_snippet.ui-draggable',
//        events: {
//            'click': '_onSnippetClick',
//        },
//
//        init: function () {
//            console.log('📌 Init: Initializing Snippet Preview Widget');
//            this._super.apply(this, arguments);
//            this.previewPopup = null;
//        },
//
//        start: function () {
//            console.log('🎯 Start: Widget Starting...');
//            console.log($('.oe_snippet_thumbnail, [data-oe-type="snippet"], .oe_snippet.ui-draggable'));
//            console.log('🔍 Found Elements:', {
//                'Total Snippets': this.$el.length,
//                'Elements': this.$el.toArray().map(el => ({
//                    'classes': el.className,
//                    'data-attrs': {
//                        'oe-type': $(el).data('oe-type'),
//                        'snippet-id': $(el).data('snippet-id'),
//                        'thumbnail': $(el).data('oe-thumbnail')
//                    }
//                }))
//            });
//
//            this._createPreviewPopup();
//            return this._super.apply(this, arguments);
//        },
//
//        _createPreviewPopup: function () {
//            console.log('🎨 Creating Preview Popup');
//            if (!this.previewPopup) {
//                this.previewPopup = $('<div/>', {
//                    class: 'o_snippet_preview_popup',
//                    css: {
//                        'position': 'fixed',
//                        'z-index': 1050,
//                        'display': 'none',
//                        'background': 'white',
//                        'border': '1px solid #ccc',
//                        'border-radius': '4px',
//                        'box-shadow': '0 2px 8px rgba(0,0,0,0.1)',
//                        'padding': '10px'
//                    }
//                }).appendTo('body');
//                console.log('✅ Preview Popup Created');
//            } else {
//                console.log('ℹ️ Preview Popup already exists');
//            }
//        },
//
//        _onSnippetClick: function (ev) {
//            console.log('🖱️ Snippet Clicked:', {
//                'Event Target': ev.currentTarget,
//                'Target Classes': ev.currentTarget.className,
//                'Target ID': ev.currentTarget.id
//            });
//
//            var $snippet = $(ev.currentTarget);
//
//            // Log all relevant data attributes
//            console.log('📄 Snippet Data:', {
//                'data-oe-thumbnail': $snippet.data('oe-thumbnail'),
//                'data-snippet': $snippet.data('snippet'),
//                'data-name': $snippet.data('name'),
//                'title': $snippet.attr('title'),
//                'data-bs-original-title': $snippet.attr('data-bs-original-title')
//            });
//
//            // Try to find thumbnail from different sources
//            var thumbnailUrl = $snippet.data('oe-thumbnail') ||
//                             $snippet.find('img').first().attr('src') ||
//                             $snippet.find('.oe_snippet_thumbnail img').first().attr('src') ||
//                             '/website/static/src/img/snippets_thumbs/' + $snippet.data('snippet') + '.svg';
//
//            console.log('🖼️ Thumbnail URL:', thumbnailUrl);
//
//            var snippetTitle = $snippet.attr('data-bs-original-title') ||
//                             $snippet.attr('title') ||
//                             $snippet.data('name') ||
//                             'Snippet Preview';
//
//            console.log('📝 Snippet Title:', snippetTitle);
//
//            // Update popup content
//            this.previewPopup.html(`
//                <div class="preview-header" style="margin-bottom: 10px; font-weight: bold;">
//                    ${snippetTitle}
//                </div>
//                <div class="preview-content">
//                    <img src="${thumbnailUrl}"
//                         alt="${snippetTitle}"
//                         style="max-width: 100%; height: auto;"
//                         onload="console.log('✅ Preview image loaded successfully')"
//                         onerror="console.error('❌ Preview image failed to load:', this.src); this.src='/web/static/src/img/placeholder.png'"/>
//                </div>
//            `);
//
//            // Calculate position
//            var snippetOffset = $snippet.offset();
//            var previewWidth = 300;
//            var viewportWidth = $(window).width();
//            var left = snippetOffset.left + $snippet.outerWidth() + 10;
//
//            console.log('📐 Position Calculation:', {
//                'snippetOffset': snippetOffset,
//                'previewWidth': previewWidth,
//                'viewportWidth': viewportWidth,
//                'initialLeft': left
//            });
//
//            // Adjust position if needed
//            if (left + previewWidth > viewportWidth) {
//                left = snippetOffset.left - previewWidth - 10;
//                console.log('↔️ Adjusted left position:', left);
//            }
//
//            // Show the popup
//            this.previewPopup.css({
//                top: snippetOffset.top,
//                left: left,
//                width: previewWidth
//            }).fadeIn(200);
//
//            console.log('✨ Preview popup displayed');
//
//            // Handle click outside
//            $(document).one('click', (e) => {
//                if (!$(e.target).closest(this.previewPopup).length &&
//                    !$(e.target).closest($snippet).length) {
//                    console.log('👆 Click outside detected, hiding preview');
//                    this.previewPopup.fadeOut(200);
//                }
//            });
//        },
//
//        destroy: function () {
//            console.log('🗑️ Destroying Snippet Preview Widget');
//            if (this.previewPopup) {
//                this.previewPopup.remove();
//            }
//            this._super.apply(this, arguments);
//        },
//    });
//
//    // Global error handler
//    window.addEventListener('error', function(event) {
//        console.error('🚨 Global error caught:', {
//            message: event.message,
//            filename: event.filename,
//            lineNo: event.lineno,
//            colNo: event.colno,
//            error: event.error
//        });
//    });
//    console.log($('.oe_snippet_thumbnail, [data-oe-type="snippet"], .oe_snippet.ui-draggable'));
//
//    console.log('✅ Snippet Preview Module Setup Complete');
//    return {
//        SnippetsMenu: aSnippetMenu2,
//    };
//});
/*
odoo.define('website.snippet.preview', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    console.log('Snippet Preview Module Loaded');

    publicWidget.registry.SnippetPreview = publicWidget.Widget.extend({
        // Update selector to match the actual snippet elements in your screenshot
        selector: '[data-oe-type="snippet"]',  // This targets all snippet elements
        events: {
            'mouseenter': '_onSnippetHover',
            'mouseleave': '_onSnippetLeave',
            'click [data-oe-type="snippet"]':'_onSnippetHover',
        },

        init: function () {
            console.log('Initializing Snippet Preview Widget');
            this._super.apply(this, arguments);
            this.previewTimeout = null;
            this.previewPopup = null;
        },

        start: function () {
            console.log('Starting Snippet Preview Widget');
            console.log('Found snippets:', this.$el.length);  // Log how many elements were found
            this._createPreviewPopup();
            return this._super.apply(this, arguments);
        },

        _createPreviewPopup: function () {
            console.log('Creating Preview Popup');
            if (this.previewPopup) {
                console.log('Preview Popup already exists');
                return;
            }
            this.previewPopup = $('<div/>', {
                class: 'o_snippet_preview_popup',
            }).appendTo('body');
            console.log('Preview Popup Created:', this.previewPopup);
        },

        _onSnippetHover: function (ev) {
            console.log('Snippet Hover Event Triggered');
            var self = this;
            var $snippet = $(ev.currentTarget);

            // Log all data attributes to help debug
            console.log('Snippet Element:', $snippet[0]);
            console.log('Snippet Data Attributes:', {
                'data-oe-type': $snippet.data('oe-type'),
                'data-oe-thumbnail': $snippet.data('oe-thumbnail'),
                'data-snippet': $snippet.data('snippet'),
                'data-name': $snippet.data('name'),
                'title': $snippet.attr('title'),
                'data-bs-original-title': $snippet.attr('data-bs-original-title')
            });

            // Clear existing timeout
            if (this.previewTimeout) {
                clearTimeout(this.previewTimeout);
            }

            // Get thumbnail URL - try multiple possible attributes
            var thumbnailUrl = $snippet.data('oe-thumbnail') ||
                             $snippet.find('img').attr('src') ||
                             '/website/static/src/img/snippets_thumbs/' + $snippet.data('snippet') + '.svg';

            // Get title - try multiple possible attributes
            var snippetTitle = $snippet.attr('data-bs-original-title') ||
                             $snippet.attr('title') ||
                             $snippet.data('name') ||
                             'Snippet Preview';

            console.log('Thumbnail URL:', thumbnailUrl);
            console.log('Snippet Title:', snippetTitle);

            this.previewTimeout = setTimeout(function () {
                console.log('Creating preview with:', {thumbnailUrl, snippetTitle});

                if (!thumbnailUrl) {
                    console.warn('No thumbnail URL found for snippet');
                    return;
                }

                self.previewPopup.html(`
                    <div class="o_preview_frame">
                        <div class="preview-header">${snippetTitle}</div>
                        <div class="preview-content">
                            <img src="${thumbnailUrl}" alt="${snippetTitle}"
                                 onload="console.log('Preview image loaded')"
                                 onerror="console.error('Preview image failed to load:', this.src)"/>
                        </div>
                    </div>
                `);

                // Position the preview
                var snippetOffset = $snippet.offset();
                var previewWidth = 300;
                var viewportWidth = $(window).width();
                var left = snippetOffset.left + $snippet.outerWidth() + 10;

                if (left + previewWidth > viewportWidth) {
                    left = snippetOffset.left - previewWidth - 10;
                }

                console.log('Positioning preview:', {
                    top: snippetOffset.top,
                    left: left,
                    snippetOffset: snippetOffset,
                    snippetWidth: $snippet.outerWidth()
                });

                self.previewPopup.css({
                    top: snippetOffset.top,
                    left: left,
                    width: previewWidth,
                }).fadeIn(200);

            }, 300);
        },

        _onSnippetLeave: function () {
            console.log('Snippet Leave Event Triggered');
            if (this.previewTimeout) {
                clearTimeout(this.previewTimeout);
            }
            if (this.previewPopup) {
                this.previewPopup.fadeOut(200);
            }
        },

        destroy: function () {
            console.log('Destroying Snippet Preview Widget');
            if (this.previewPopup) {
                this.previewPopup.remove();
            }
            this._super.apply(this, arguments);
        },
    });

    // Add global error handler
    window.addEventListener('error', function(event) {
        console.error('Global error caught:', event.error);
    });

    console.log('Snippet Preview Module Setup Complete');
});*/
