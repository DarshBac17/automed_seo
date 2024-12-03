odoo.define('website.snippets.p_tag_constraints', function (require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');


    options.registry.PhpVariableTextSelector = options.Class.extend({
        events: _.extend({}, options.Class.prototype.events || {}, {
            'mouseup .o_editable': '_onSelectionChange',
        }),

        init: function () {
            this._super.apply(this, arguments);
            this._bindSelectionChangeEvent();
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
            });
        },

        destroy: function () {
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

            const selection = this._getCurrentSelection();

            if (!selection || !selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const $target = $(document.activeElement);

            this.currentTarget = ev.target

            console.log('selection change:', this.currentTarget)

            this._applyConstraints(ev.target)
        },

        _applyConstraints: function (element) {
            const $element = $(element);

            if ($element.hasClass('o_au_len_constraints')) {
                console.log('tag has constraints');

                let observer;

                // Check if the element already has an observer
                if (!$element.data('observer')) {
                    // Create a new observer if it doesn't exist
                    observer = new MutationObserver(_.debounce((mutations) => {
                        mutations.forEach(mutation => {
                            if (mutation.type === 'characterData' ||
                                mutation.type === 'childList') {
                                console.log('Content changed in constrained element:', element);
                                this._handleConstrainedElementChange(element);
                            }
                        });
                    }, 300));

                    // Store the observer in the element's data
                    $element.data('observer', observer);

                    // Start observing the element
                    observer.observe(element, {
                        childList: true,
                        characterData: true,
                        subtree: true
                    });
                } else {
                    // Retrieve the existing observer
                    observer = $element.data('observer');
                }
            }
        },

        _handleConstrainedElementChange: function (element) {
            // Custom logic for handling changes in constrained elements
            console.log('Handling change in constrained element');

            // Example: Validate content length
            const maxLength = element.getAttribute('data-max-length') || 10;
            const currentLength = element.textContent.trim().length;

            if (currentLength > maxLength) {
                console.warn(`Content exceeds maximum length of ${maxLength} characters`);
                alert(`The content you've entered exceeds the maximum length of ${maxLength} characters. Please shorten your text.`);


                // Truncate the content to the maximum length
                element.textContent = element.textContent.trim().slice(0, maxLength);

                // Move the cursor to the end of the text
                const selection = this._getCurrentSelection();
                if (selection && selection.rangeCount) {
                    const range = selection.getRangeAt(0);
                    range.selectNodeContents(element);
                    range.collapse(false);
                    selection.removeAllRanges();
                    selection.addRange(range);
                }
            }
        },

    });
});