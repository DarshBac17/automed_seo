odoo.define('website.autosave', function (require) {
    'use strict';

    var Wysiwyg = require('web_editor.wysiwyg');

    Wysiwyg.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.autoSaveInterval = 60000; // Auto-save interval in milliseconds
            this.contentChanged = false;
            this.lastContent = null;
            this.autoSaveTimer = null;
        },

        /**
         * @override
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.setupAutoSave();
                return Promise.resolve();
            });
        },

        /**
         * Setup auto-save functionality
         */
        setupAutoSave: function () {
            if (this.autoSaveTimer) {
                clearInterval(this.autoSaveTimer);
            }

            try {
                this.lastContent = this._getPageContent();

                // Setup content change detection
                this._setupContentChangeDetection();

                // Start auto-save timer
                this.autoSaveTimer = setInterval(() => {

                    this.performAutoSave();
                }, this.autoSaveInterval);
            } catch (error) {
                console.warn('[Website Editor] Setup postponed:', error);
                // Retry setup after a short delay
                setTimeout(() => this.setupAutoSave(), 1000);
            }
        },

        /**
         * Perform auto-save
         */
        performAutoSave: function () {
            if (!this.contentChanged) {

                return Promise.resolve();
            }

            const content = this._getPageContent();
            if (!content) {
                return Promise.resolve();
            }

            return this._rpc({
                route: '/website/autosave_content',
                params: {
                    html_content: content,
                },
            }).then(() => {
                this.contentChanged = false;
                this.$autoSaveIcon = $('.o_we_website_top_actions button[data-action=autosave]');
                console.log(this.$autoSaveIcon)
                if (this.$autoSaveIcon.length) {
                    const $icon = this.$autoSaveIcon.find('i');
                    // Check if the current icon is fa-cloud, and change to fa-check if true
                    if ($icon.hasClass('fa-spinner')) {
                        $icon.removeClass('fa-spinner').addClass('fa-cloud');
                    } else {
                        $icon.addClass('fa-cloud');
                    }
                }
//                this._showAutoSaveNotification()
                console.log('[Website Editor] Content saved successfully');
            }).catch((error) => {
                console.error('[Website Editor] Save failed:', error);
            });
        },

//        _showAutoSaveNotification: function () {
//            const notification = new Notification(this, {
//                type: 'success',
//                title: 'Content Auto-Saved',
//                message: 'Your changes have been auto-saved.',
//                sticky: false,
//                duration: 3000,  // Time in ms
//            });
//            notification.mount($('#wrapwrap')[0]); // Append to the body or any specific container
//        },
        /**
         * Detect content changes
         * @private
         */
        _setupContentChangeDetection: function () {
            const $editableContent = this._findEditableContent();

            if (!$editableContent.length) {
                console.warn('[Website Editor] No editable content found');
                return;
            }

            $editableContent.on('input change keyup mouseup', () => {
                this.$autoSaveIcon = $('.o_we_website_top_actions button[data-action=autosave]');
                console.log(this.$autoSaveIcon)
                if (this.$autoSaveIcon.length) {
                    const $icon = this.$autoSaveIcon.find('i');
                    // Check if the current icon is fa-cloud, and change to fa-check if true
                     if ($icon.hasClass('fa-cloud')) {
                        $icon.removeClass('fa-cloud').addClass('fa-spinner');
                    } else {
                        $icon.addClass('fa-spinner');
                    }
                }
                const currentContent = this._getPageContent();
                if (currentContent !== this.lastContent) {
                    this.contentChanged = true;
                    this.lastContent = currentContent;
                }
            });
        },

        /**
         * Find editable content area
         * @returns {jQuery}
         * @private
         */
        _findEditableContent: function () {
            let $editableContent = $('.o_editable[data-oe-model="ir.ui.view"]');

            if (!$editableContent.length && this.$editable) {
                $editableContent = this.$editable;
            }

            if (!$editableContent.length) {
                $editableContent = $('#wrapwrap .oe_structure.oe_empty, #wrapwrap .oe_structure').first();
            }

            if (!$editableContent.length) {
                console.warn('[Website Editor] No editable content found');
            }

            return $editableContent;
        },

        /**
         * Get current page content
         * @returns {string}
         * @private
         */
        _getPageContent: function () {
            const $editableContent = this._findEditableContent();

            if (!$editableContent.length) {
                console.warn('[Website Editor] No editable content found');
                return '';
            }

            const $clone = $editableContent.clone();

//            $clone.find('*').each(function () {
//                $(this).removeAttr('contenteditable')
//                    .removeAttr('data-oe-model')
//                    .removeAttr('data-oe-id')
//                    .removeAttr('data-oe-field')
//                    .removeAttr('data-oe-xpath')
//                    .removeAttr('data-oe-source-id');
//            });

            const content = $clone.html();
            return content ? content.trim() : '';
        },

        /**
         * @override
         */
        destroy: function () {
            if (this.autoSaveTimer) {
                clearInterval(this.autoSaveTimer);
            }

            const $editableContent = this._findEditableContent();
            if ($editableContent.length) {
                $editableContent.off('input change keyup mouseup');
            }

            this._super.apply(this, arguments);
        },
    });
});
