odoo.define('website.autosave', function (require) {
    'use strict';

    var Wysiwyg = require('web_editor.wysiwyg');

    Wysiwyg.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.autoSaveInterval = 5000; // Auto-save interval in milliseconds
            this.contentCheckInterval = 1000; // Content check interval in milliseconds
            this.contentChanged = false;
            this.lastContent = null;
            this.autoSaveTimer = null;
            this.contentCheckTimer = null;
        },

        /**
         * @override
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.lastContent = self._getPageContent();
                self._setupContentChangeDetection();
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

            // Start auto-save timer
            this.autoSaveTimer = setInterval(() => {
                this.performAutoSave();
            }, this.autoSaveInterval);
        },

        /**
         * Update icon state
         * @private
         * @param {string} iconClass - The icon class to set ('fa-spinner' or 'fa-cloud')
         */
        _updateIcon: function(iconClass) {
            this.$autoSaveIcon = $('.o_we_website_top_actions button[data-action=autosave]');
            if (this.$autoSaveIcon.length) {
                const $icon = this.$autoSaveIcon.find('i');
                $icon.removeClass('fa-spinner fa-cloud').addClass(iconClass);
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
                this._updateIcon('fa-cloud');
            }).catch((error) => {
                console.error('[Website Editor] Save failed:', error);
                // Keep content changed flag true on error
                this.contentChanged = true;
            });
        },

        /**
         * Detect content changes
         * @private
         */
        _setupContentChangeDetection: function () {
            if (this.contentCheckTimer) {
                clearInterval(this.contentCheckTimer);
            }

            this.contentCheckTimer = setInterval(() => {
                const $editableContent = this._findEditableContent();

                if ($editableContent.length) {
                    const currentContent = this._getPageContent();

                    if (currentContent !== this.lastContent) {
                        this.contentChanged = true;
                        this.lastContent = currentContent;
                        this._updateIcon('fa-spinner');
                    } else if (!this.contentChanged) {
                        this._updateIcon('fa-cloud');
                    }
                }
            }, this.contentCheckInterval);
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
            if (this.contentCheckTimer) {
                clearInterval(this.contentCheckTimer);
            }

            this._super.apply(this, arguments);
        },
    });
});