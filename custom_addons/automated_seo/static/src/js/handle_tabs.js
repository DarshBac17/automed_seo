odoo.define('website.snippets.tabs_handler', function (require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');


    options.registry.MultipleTabs = options.Class.extend({
        events: _.extend({}, options.Class.prototype.events || {}, {
            'mouseup .o_editable': '_onSelectionChange',
            'click [data-variable-class="add-tab"]': '_onAddTabButtonClick',
            'click [data-variable-class="remove-tab"]': '_onRemoveTabButtonClick',
        }),



        init: function () {
            this._super.apply(this, arguments);
            this._bindSelectionChangeEvent();
            this.wysiwyg = null;
        },


        /**
         * @override
         */
        async willStart() {
            await this._super(...arguments);
            if (this.options.wysiwyg) {
                this.wysiwyg = this.options.wysiwyg;
            }
        },



        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (!self.wysiwyg && self.options.wysiwyg) {
                    self.wysiwyg = self.options.wysiwyg;
                }
            });
        },


        destroy: function () {
            this._super.apply(this, arguments);
        },


        /**
        * Get the current Wysiwyg instance safely
        * @private
        */
        _getWysiwygInstance: function () {
            return this.wysiwyg || (this.options && this.options.wysiwyg);
        },


        /**
        * Get the current selection instance safely
        * @private
        */
        _getCurrentSelection: function () {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg || !wysiwyg.odooEditor) {
                return null;
            }

            return wysiwyg.odooEditor.document.getSelection();
        },


        /**
         * Binds selectionChange event
         * @returns 
         */
        _bindSelectionChangeEvent() {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            // Optional: Also handle clicks within editable areas
            wysiwyg.odooEditor.document.addEventListener('click', _.debounce((event) => {
                const clickedElement = event.target;
                if (clickedElement.closest('.o_editable')) {
                    this._onSelectionChange.bind(this)(event);
                }

            }, 100));
        },


        /**
         * Called on selection change
         * @returns 
         */
        _onSelectionChange: function (ev) {
            ev.preventDefault();

            const selection = this._getCurrentSelection();

            if (!selection || !selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const $target = $(document.activeElement);

            this.currentTarget = ev.target

        },



        _onAddTabButtonClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            const tabContent = $(this.currentTarget).closest('.tab-content')

            // Get the last tab-head and generate a new one
            const tabHeaders = tabContent.find('.tab-header');
            const lastTabHead = tabHeaders.find('.tab-head:last-child');
            const newTabHead = lastTabHead.clone();
            lastTabHead.removeClass('active');
            newTabHead.find('.head').text('Title Title');
            tabHeaders.append(newTabHead);

            // Get the last tab-pane and generate a new one
            const tabPanesContainer = tabContent.find('> div:last-child');
            const lastTabPane = tabPanesContainer.find('.tab-pane:last-child');
            const newTabPane = lastTabPane.clone();
            lastTabPane.removeClass('active');

            // Add the new tab-pane
            tabPanesContainer.append(newTabPane);

            console.log('Tab added successfully');
        },

        _onRemoveTabButtonClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation()

            const tabContent = $(this.currentTarget).closest('.tab-content')
            // Get the number of existing tabs
            const tabHeaders = tabContent.find('.tab-header .tab-head');
            const tabPanes = tabContent.find('> div:last-child .tab-pane');

            // Prevent removing if only one tab remains
            if (tabHeaders.length <= 1) {
                console.log('Cannot remove the last tab');
                return;
            }

            // Remove the last tab-head and tab-pane
            tabHeaders.last().remove();
            tabPanes.last().remove();

            // Activate the last remaining tab if no active tab
            if (tabContent.find('.tab-head.active').length === 0) {
                tabHeaders.last().addClass('active');
                tabPanes.last().addClass('active');
            }

            console.log('Tab removed successfully');
        }



    });
});