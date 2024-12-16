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
            this.wysiwyg = null;
            this.currentTarget = null;
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
                self._bindSelectionChangeEvent();
                self._bindSelectAllEvent();
            });
        },

        destroy: function () {
            this._unbindSelectionChangeEvent();
            this._unbindSelectAllEvent();

            this.$('.o_editable_box').each(function () {
                console.log("***********")
                $(this).removeClass('o_editable_box');
                $(this).removeAttr('contenteditable');
            });

            this._super.apply(this, arguments);
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

        _bindSelectAllEvent: function () {
            const self = this;

            this._selectAllHandler = function (event) {
                if (event.ctrlKey && event.key === 'a') {
                    event.preventDefault();
                    event.stopPropagation();
                    console.log("ctrl+a pressed")

                    const $focusedEditableBox = self.currentTarget;


                    console.log(self.currentTarget);

                    if ($focusedEditableBox) {
                        console.log("Found editable-box", $focusedEditableBox);

                        const selection = window.getSelection();
                        const range = document.createRange();

                        range.selectNodeContents($focusedEditableBox);

                        console.log(range)
                        selection.removeAllRanges();
                        selection.addRange(range);

                        console.log("Selected text:", selection.toString());
                    }
                }
            };

            document.addEventListener('keydown', this._selectAllHandler);
        },

        _unbindSelectAllEvent: function () {
            // Remove the global Ctrl+A event listener
            if (this._selectAllHandler) {
                document.removeEventListener('keydown', this._selectAllHandler);
            }
        },

        _unbindSelectionChangeEvent: function () {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            // Remove the specific event listener
            wysiwyg.odooEditor.document.removeEventListener('click', this._selectionChangeHandler);
        },

        _bindSelectionChangeEvent() {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            // Create a bound handler to ensure we can remove it later
            this._selectionChangeHandler = _.debounce((event) => {
                const clickedElement = event.target;
                if (clickedElement.closest('.o_editable')) {
                    this._onSelectionChange.bind(this)(event);
                }
            }, 100);

            // Add the event listener
            wysiwyg.odooEditor.document.addEventListener('click', this._selectionChangeHandler);
        },

        _onSelectionChange: function (ev) {

            try {

                ev.preventDefault();
                ev.stopPropagation();

                console.log('Selection changed', ev.target)

                const selection = this._getCurrentSelection();

                if (!selection || !selection.rangeCount) return;

                const range = selection.getRangeAt(0);
                const $target = $(document.activeElement);


                $(this.currentTarget).removeAttr('contenteditable');
                $(this.currentTarget).removeClass('o_editable_box');

                this.$('.o_editable_box').each(function () {
                    console.log("***********")
                    $(this).removeClass('o_editable_box');
                    $(this).removeAttr('contenteditable');
                });

                this.currentTarget = ev.target;

                this._createEditableTarget(this.currentTarget);

            }
            catch (error) {
                console.error('Error in selection change handler:', error);
            }

        },


        _createEditableTarget: function (target) {

            if ($(target).is('section') ||
                $(target).is('img') ||
                $(target).is('svg') ||
                $(target).is('.o_snippet_editor') ||
                $(target).is('.oe_structure') ||
                $(target).is('[data-oe-type]') ||
                $(target).is('[data-snippet]') ||
                $(target).is('.container') ||
                $(target).is('.o_not_editable')) {
                console.log('(target) not editable');
                return;
            }

            $(target).addClass('o_editable_box');


            $(target).attr("contenteditable", "true");

            this._addEventsOntarget(target);
        },

        _addEventsOntarget: function (target) {
            $(target).on('paste', this._handlePasteEvent.bind(this));
        },


        _handlePasteEvent: function (event) {
            console.log("Paste event triggered");

            event.preventDefault();
            event.stopPropagation();

            const target = event.target;
            console.log("Target element:", target);
            target.focus();
            if (!target.isContentEditable) {
                console.error("The target element is not editable.");
                return;
            }

            const clipboardData = event.originalEvent.clipboardData || window.clipboardData;
            const pastedText = clipboardData.getData('text'); // Get plain text

            const selection = this._getCurrentSelection();

            if (!selection || !selection.rangeCount) {
                console.error("No selection range found. Ensure the element is focused.");
                return;
            }

            const range = selection.getRangeAt(0);
            range.deleteContents(); // Remove the selected content

            const textNode = document.createTextNode(pastedText); // Insert as plain text
            range.insertNode(textNode);

            range.setStartAfter(textNode);
            range.setEndAfter(textNode);
            selection.removeAllRanges();
            selection.addRange(range);

            console.log("Pasted text:", pastedText);
        },

    });
});