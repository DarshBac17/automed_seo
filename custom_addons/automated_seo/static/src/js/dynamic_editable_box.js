odoo.define('website.snippets.dynamic_editable_box', function (require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');

    options.registry.EditableBoxSelector = options.Class.extend({
        events: _.extend({}, options.Class.extend.prototype.events || {}, {

        }),

        init: function () {
            this._super.apply(this, arguments);
            this._bindSelectionChangeEvent();
            this.wysiwyg = null;
            this.currentTarget = null;
            this.$editableBox = null;
        },

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
            if (this.$editableBox) {
                console.log("found existing editableBox")
                this.$editableBox.parent().html(this.$editableBox.html());
                // Remove the editable box
                this.$editableBox.remove();
            }
        },

        _getWysiwygInstance: function () {
            return this.wysiwyg || (this.options && this.options.wysiwyg);
        },

        _getCurrentSelection: function () {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg || !wysiwyg.odooEditor) {
                return null;
            }

            return wysiwyg.odooEditor.document.getSelection();
        },

        _bindSelectionChangeEvent() {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            wysiwyg.odooEditor.document.addEventListener('click', _.debounce((event) => {
                const clickedElement = event.target;
                if (clickedElement.closest('.o_editable')) {
                    this._onSelectionChange.bind(this)(event);
                }
            }, 100));
        },

        _onSelectionChange: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            const selection = this._getCurrentSelection();

            if (!selection || !selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const $target = $(document.activeElement);

            this.currentTarget = ev.target;

            // Find all existing editable boxes
            if (this.$editableBox) {
                console.log("found existing editableBox")
                this.$editableBox.parent().html(this.$editableBox.html());
                // Remove the editable box
                this.$editableBox.remove();
            }


            // Create the new editable box inside the currently selected element
            this._createEditableBox(ev.target);
        },

        _createEditableBox: function (currentElement) {
            // Create the new editable box
            this.$editableBox = $('<div class="editable-box"></div>');
            this.$editableBox.css({
                'position': 'relative',
                'border': '2px solid blue',
                'padding': '5px',
                'background-color': 'rgba(255, 255, 255, 0.8)',
                'z-index': '9999',
            });



            // Add the content to the new div
            this.$editableBox.html($(this.currentTarget).html());
            // Append the editable box inside the selected element
            $(this.currentTarget).empty();
            $(this.currentTarget).append(this.$editableBox);

            // Add event listeners to the editable box
            this.$editableBox.on('click', (event) => {
                event.stopPropagation();
            });

            this.$editableBox.on('mouseup', (event) => {
                event.stopPropagation();
            });

            this.$editableBox.on('keyup', (event) => {
                // Handle keyboard events inside the editable box
                console.log('Editable box content:', this.$editableBox.text());
            });
        },
    });
});