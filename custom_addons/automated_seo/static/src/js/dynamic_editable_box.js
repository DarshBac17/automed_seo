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
                // self._bindPastEvent();
            });
        },

        destroy: function () {
            this._unbindSelectionChangeEvent();
            this._unbindSelectAllEvent();
            // this._unbindPastEvent();
            this._removeEventsOnTarget();
            this._removeEditableBoxes();
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

            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

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

                        const selection = self._getCurrentSelection();
                        const range = wysiwyg.odooEditor.document.createRange();

                        range.selectNodeContents($focusedEditableBox);

                        console.log(range)
                        selection.removeAllRanges();
                        selection.addRange(range);

                        console.log("Selected text:", selection.toString());
                    }
                }
            };

            // Handle triple-click event
            this._tripleClickHandler = function (event) {
                if (event.detail === 3) { // Triple-click event
                    console.log("Triple-click detected");

                    const $focusedEditableBox = self.currentTarget;

                    if ($focusedEditableBox) {
                        console.log("Found editable-box", $focusedEditableBox);

                        const selection = self._getCurrentSelection();
                        const range = wysiwyg.odooEditor.document.createRange();

                        range.selectNodeContents($focusedEditableBox);

                        console.log(range);
                        selection.removeAllRanges();
                        selection.addRange(range);

                        console.log("Selected text:", selection.toString());
                    }
                }
            };

            // Bind events
            wysiwyg.odooEditor.document.addEventListener('keydown', this._selectAllHandler);
            wysiwyg.odooEditor.document.addEventListener('click', this._tripleClickHandler);
        },

        _unbindSelectAllEvent: function () {
            // Remove the global Ctrl+A event listener

            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;
            if (this._selectAllHandler) {
                wysiwyg.odooEditor.document.removeEventListener('keydown', this._selectAllHandler);
                wysiwyg.odooEditor.document.removeEventListener('click', this._tripleClickHandler);
            }
        },

        _bindPastEvent: function () {

            // unused
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            const self = this;

            this._handlePasteEvent = function (event) {
                console.log("Paste event triggered");

                // Prevent default paste behavior
                event.preventDefault();
                event.stopPropagation();

                const $focusedEditableBox = self.currentTarget;
                console.log("Target element:", $focusedEditableBox);

                if (!$focusedEditableBox) {
                    console.error("No focused editable box found");
                    return;
                }

                $focusedEditableBox.focus();

                if (!$focusedEditableBox.isContentEditable) {
                    console.error("The target element is not editable.");
                    return;
                }

                // Use multiple methods to get clipboard data
                const clipboardData =
                    event.clipboardData ||
                    event.originalEvent?.clipboardData ||
                    window.clipboardData;

                if (!clipboardData) {
                    console.error("Could not access clipboard data");
                    return;
                }

                const pastedText = clipboardData.getData('text/plain') || clipboardData.getData('text');

                const selection = self._getCurrentSelection();

                if (!selection || !selection.rangeCount) {
                    console.error("No selection range found. Ensure the element is focused.");
                    return;
                }

                const range = selection.getRangeAt(0);
                range.deleteContents(); // Remove the selected content

                const textNode = wysiwyg.odooEditor.document.createTextNode(pastedText); // Insert as plain text
                range.insertNode(textNode);

                // Move cursor after the inserted text
                range.setEndAfter(textNode);
                selection.removeAllRanges();
                selection.addRange(range);

                console.log("Pasted text:", pastedText);
            };

            wysiwyg.odooEditor.document.addEventListener('paste', this._handlePasteEvent);
        },

        _unbindPastEvent: function () {

            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;


            if (this._handlePasteEvent) {
                wysiwyg.odooEditor.document.removeEventListener('paste', this._handlePasteEvent);
            }
        },

        _bindSelectionChangeEvent() {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            this._selectionChangeHandler = _.debounce((event) => {
                const clickedElement = event.target;
                if (clickedElement.closest('.o_editable')) {
                    this._onSelectionChange.bind(this)(event);
                }
            }, 100);

            wysiwyg.odooEditor.document.addEventListener('click', this._selectionChangeHandler);
        },


        _unbindSelectionChangeEvent: function () {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            wysiwyg.odooEditor.document.removeEventListener('click', this._selectionChangeHandler);
        },



        _onSelectionChange: function (ev) {

            try {

                ev.preventDefault();
                ev.stopPropagation();

                console.log('Selection changed', ev.target)

                const wysiwyg = this._getWysiwygInstance();
                if (!wysiwyg) return;

                const selection = this._getCurrentSelection();

                if (!selection || !selection.rangeCount) return;

                const range = selection.getRangeAt(0);
                const $target = $(wysiwyg.odooEditor.document.activeElement);

                this._removeEventsOnTarget();
                this._removeEditableBoxes();

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

            this._boundPasteHandler = this._handlePasteEvent.bind(this);

            $(target).on('paste', this._boundPasteHandler);

            target.addEventListener('paste', this._boundPasteHandler);
        },


        _removeEventsOnTarget: function () {
            if (!this.currentTarget) return;

            try {
                $(this.currentTarget).off('paste', this._boundPasteHandler);

                this.currentTarget.removeEventListener('paste', this._boundPasteHandler);
            } catch (error) {
                console.error('Error removing paste event:', error);
            }

            this.currentTarget = null;
            this._boundPasteHandler = null;
        },

        _handlePasteEvent: function (event) {

            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;
            console.log("Paste event triggered");

            wysiwyg.odooEditor.historyStep();

            event.preventDefault();
            event.stopPropagation();

            const $focusedEditableBox = event.target;
            console.log("Target element:", $focusedEditableBox);

            if (!$focusedEditableBox) {
                console.error("No focused editable box found");
                return;
            }

            $focusedEditableBox.focus();

            if (!$focusedEditableBox.isContentEditable) {
                console.error("The target element is not editable.");
                return;
            }

            const clipboardData =
                event.clipboardData ||
                event.originalEvent?.clipboardData ||
                window.clipboardData;

            if (!clipboardData) {
                console.error("Could not access clipboard data");
                return;
            }

            const pastedText = clipboardData.getData('text/plain') || clipboardData.getData('text');

            const selection = this._getCurrentSelection();

            if (!selection || !selection.rangeCount) {
                console.error("No selection range found. Ensure the element is focused.");
                return;
            }

            const range = selection.getRangeAt(0);
            range.deleteContents();

            const textNode = wysiwyg.odooEditor.document.createTextNode(pastedText);
            range.insertNode(textNode);

            range.setEndAfter(textNode);
            selection.removeAllRanges();
            selection.addRange(range);

            console.log("Pasted text:", pastedText);
        },

        _removeEditableBoxes: function () {
            $(this.currentTarget).removeAttr('contenteditable');
            $(this.currentTarget).removeClass('o_editable_box');

            this.$('.o_editable_box').each(function () {
                $(this).removeClass('o_editable_box');
                $(this).removeAttr('contenteditable');
            });
        },
    });
});