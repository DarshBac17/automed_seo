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
            this.editableBoxes = [];

            // Unique identifier for event listener to ensure proper removal
            this._selectionChangeEventId = 'selection-change-' + _.uniqueId();
            this._selectAllEventId = 'select-all-' + _.uniqueId();



            console.log("dynamic_editable_box.js initialized")
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
                // Setup the selection change event listener
                self._bindSelectionChangeEvent();

                // Setup the global Ctrl+A select all event listener
                self._bindSelectAllEvent();

                self._bindPasteEvent();
            });
        },

        destroy: function () {
            // Remove event listener to prevent multiple bindings
            this._unbindSelectionChangeEvent();

            // Setup the global Ctrl+A select all event listener
            this._unbindSelectAllEvent();

            this._unbindPasteEvent();

            // Remove all editable boxes when the option is destroyed
            this.$('.o_editable').off('click');
            console.log("dynamic_editable_box.js destroyed")
            this.editableBoxes.forEach($editableBox => {
                $editableBox.parent().html($editableBox.html());
                $editableBox.remove();
            });

            // Clear the array
            this.editableBoxes = [];

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

                    // Ensure there's an editable box in focus
                    const $focusedEditableBox = self.editableBoxes && self.editableBoxes.length ? self.editableBoxes[0] : null;

                    if ($focusedEditableBox) {
                        console.log("Found editable-box");

                        const selection = window.getSelection();
                        const range = document.createRange();

                        // Select only the contents of the focused editable-box
                        range.selectNodeContents($focusedEditableBox[0]);

                        // Clear any existing selections and apply the new range
                        selection.removeAllRanges();
                        selection.addRange(range);

                        // Optional: Log the selected text
                        console.log("Selected text:", selection.toString());
                    }
                }
            };

            document.addEventListener('keydown', this._selectAllHandler);
        },


        _bindPasteEvent: function () {
            const self = this;

            this._pasteHandler = function (event) {
                const $focusedEditableBox = self.editableBoxes && self.editableBoxes.length ? self.editableBoxes[0] : null;

                if ($focusedEditableBox) {
                    event.preventDefault(); // Prevent default paste behavior

                    // Get pasted text from the clipboard
                    const clipboardData = (event.clipboardData || window.clipboardData);
                    const pastedText = clipboardData.getData('text'); // Extract plain text

                    // Insert the pasted text while preserving the parent tag
                    document.execCommand('insertText', false, pastedText);

                    // Optional: Log the inserted text for debugging
                    console.log("Pasted text:", pastedText);
                }
            };

            document.addEventListener('paste', this._pasteHandler);
        },


        _unbindPasteEvent: function () {
            if (this._pasteHandler) {
                document.removeEventListener('keydown', this._pasteHandler);
            }
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

                console.log('Selection changed')

                const selection = this._getCurrentSelection();

                if (!selection || !selection.rangeCount) return;

                const range = selection.getRangeAt(0);
                const $target = $(document.activeElement);

                this.currentTarget = ev.target;

                // Remove all existing editable boxes
                this._clearEditableBoxes();

                // Create editable boxes for all valid child elements
                // Create the new editable box inside the currently selected element
                const $newEditableBox = this._createEditableBox(ev.target);

                // Store the new editable box in the array
                if ($newEditableBox) {
                    this.editableBoxes.push($newEditableBox);
                    range.selectNodeContents($newEditableBox[0]);
                    range.collapse(false);
                    selection.removeAllRanges();
                    selection.addRange(range);
                }
            }
            catch (error) {
                console.error('Error in selection change handler:', error);
            }

        },

        _clearEditableBoxes: function () {
            // Remove all existing editable boxes
            this.editableBoxes.forEach($editableBox => {
                $editableBox.parent().html($editableBox.html());
                $editableBox.remove();
            });

            // Clear the array
            this.editableBoxes = [];
        },


        _createEditableBox: function (currentElement) {


            if ($(this.currentTarget).is('section') ||
                $(this.currentTarget).is('img') ||
                $(this.currentTarget).is('svg') ||
                $(this.currentTarget).is('.o_snippet_editor') ||
                $(this.currentTarget).is('.oe_structure') ||
                $(this.currentTarget).is('[data-oe-type]') ||
                $(this.currentTarget).is('[data-snippet]') ||
                $(this.currentTarget).is('.container') ||
                $(this.currentTarget).is('.o_not_editable')) {
                console.log('(this.currentTarget) not editable');
                return null;
            }


            // Create the new editable box
            const $editableBox = $('<div class="editable-box" contenteditable="true"></div>');
            $editableBox.css({
                'position': 'relative',
                'border': '2px solid blue',
                'padding': '5px',
                'z-index': '9999',
            });

            // Add the content to the new div
            $editableBox.html($(this.currentTarget).html());

            // Append the editable box inside the selected element
            $(this.currentTarget).empty();
            $(this.currentTarget).append($editableBox);

            // Add event listeners to the editable box
            $editableBox.on('click', (event) => {
                event.stopPropagation();
            });

            $editableBox.on('mouseup', (event) => {
                event.stopPropagation();
            });

            $editableBox.on('keyup', (event) => {
                // Handle keyboard events inside the editable box
                console.log('Editable box content:', $editableBox.text());
            });

            $editableBox.focus();
            return $editableBox;
        },
    });
});