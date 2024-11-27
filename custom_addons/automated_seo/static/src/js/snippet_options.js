odoo.define('website.snippets.php_variable_text_selector', function (require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');



    options.registry.PhpVariableTextSelector = options.Class.extend({
        events: _.extend({}, options.Class.prototype.events || {}, {

            'mouseup .o_editable': '_onSelectionChange',

            'click [data-variable-class="strong-tag"]': '_onStrongTagClick',
            'click [data-variable-class="b-tag"]': '_onBTagClick',
            'click [data-variable-class="font-bold"]': '_onFontBoldClick',
            'click [data-variable-class="italic-tag"]': '_onItalicTagClick',
            'click [data-variable-class="underline-tag"]': '_onUnderlineTagClick',


            'click [data-variable-class="a-tag"]': '_onLinkButtonClick',
            'click [data-save-url]': '_onSaveUrl',
            'click [data-select-class="o_au_link_target"]': '_onLinkTargetButtonClick',
            'click [data-remove-url]': '_onRemoveUrl',
            'click [data-cancel-url]': '_onCancelUrl',

            'click .data-remove-php-var': '_onRemovePhpVariable',
            'input .data-variable-input': '_onVariableInputChange',
            'keydown .data-variable-input': '_onVariableKeyDown',
            'click [data-select-class="o_au_php_var_type"]': '_onConstButtonClick',


            'click .o_we_edit_link': '_onLinkButtonClick',
        }),



        init: function () {
            this._super.apply(this, arguments);
            this._bindSelectionChangeEvent();
            this.selectedVariable = null;
            this.isConstVar = false;
            this.wysiwyg = null;
            this.activeFormatting = null;  // Track currently active formatting
            this.urlDialog = null; // Store reference to URL dialog
            this.currentLink = null; // Store reference to current link being edited
            this.isTargetNewTab = false;
            this.typing = false;
            this.currentTarget = null;
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

                // $(document).on('selectionchange', _.debounce(() => {
                //     self._onSelectionChange();
                // }, 100));
            });
        },


        destroy: function () {
            $(document).off('selectionchange');
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
         * hide unnecessary toolbar's features
         */

        _hideUnnecessaryElements: function () {
            const $editor_toolbar_container = $('#o_we_editor_toolbar_container');
            $editor_toolbar_container.remove();
            const $imageToolsElement = $('.snippet-option-ImageTools');


            if ($imageToolsElement.length) {
                $imageToolsElement.parent().children().slice($imageToolsElement.index() + 1).each(function () {
                    $(this).hide().css({
                        'visibility': 'hidden',
                        'opacity': '0',
                        'display': 'none !important'
                    });
                });
            }
        },


        /**
         * Called on selection change
         * @returns 
         */
        _onSelectionChange: function (ev) {
            ev.preventDefault();

            this._hideUnnecessaryElements();
            const selection = this._getCurrentSelection();

            if (!selection || !selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const $target = $(document.activeElement);

            this.currentTarget = ev.target



            // Check if the active element is an input field being edited
            if ($target.is('input') || $target.is('textarea')) {
                return; // Ignore selection change when typing in input
            }



            // Run existing selection change handlers
            this._onBoldSelectionChange(ev);
            this._onLinkSelectionChange(ev);
            this._updateButtonState(ev, selection);

            this._onPhpVariableChange(ev);

            this.typing = false;

            /* if (!$editable.length) {
            } */
        },





        /**
         * Called when the php var input value changes (e.g., typing, deleting).
         * @param {Event} event
         */
        _onVariableInputChange: function (event) {
            this.typing = true

        },

        /**
         * Called when a key is pressed in the php var input field.
         * @param {Event} event
         */
        _onVariableKeyDown: function (event) {
            this.typing = true

            if (event.key === "Enter") {

                this._onApplyVariable(event);
            }
        },


        /**
         * Event function to apply php variable.
         * @param {Event} event
         */
        _onApplyVariable: function (ev) {
            ev.preventDefault();

            this.typing = false;

            // Locate the <we-input> element and get the value
            var inputField = this.$el.find('.data-variable-input');
            if (!inputField) {

                return;
            }

            var variableName = inputField.val();
            if (!variableName) {
                alert('Please enter a variable name');
                return;
            }

            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) {

                return;
            }

            const selection = this._getCurrentSelection();
            if (!selection || !selection.toString().trim()) {
                alert('Please select some text first');
                return;
            }

            const range = selection.getRangeAt(0);
            const $editable = $(range.commonAncestorContainer).closest('.o_editable');
            if (!$editable.length) {
                alert('Please select text within the editable area');
                return;
            }

            try {
                const currentVar = this._hasPhpVariable(selection);

                if (variableName === 'none') {
                    if (currentVar) {
                        this._removePhpVariable(selection);
                    }
                    // Remove active class from all variable buttons
                    this.$el.find('[data-select-var]').removeClass('active');
                } else {
                    if (currentVar && currentVar.name === variableName) {
                        // If the same variable is being applied, remove it
                        this._removePhpVariable(selection);
                    } else {
                        // Remove any existing variable before applying new one
                        if (currentVar) {
                            this._removePhpVariable(selection);
                        }

                        // Apply the new variable
                        this._applyPhpVariable(selection, {
                            name: variableName,
                            class: 'o_au_php_var'
                        });
                    }
                }

                // Clean up empty spans and update history
                this._cleanupEmptySpans($editable[0]);
                wysiwyg.odooEditor.historyStep();
                // this._onSelectionChange();

            } catch (error) {
                console.error('Error applying variable:', error);
                alert('An error occurred while applying the variable. Please try again.');
            }

        },


        /**
         * Event function to remove php variable.
         * @param {Event} event
         */

        _onRemovePhpVariable: function (ev) {


            ev.preventDefault();
            ev.stopPropagation();
            this.type = false
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            const selection = this._getCurrentSelection();
            if (!selection || !selection.toString().trim()) {
                return;
            }

            try {
                const currentVar = this._hasPhpVariable(selection);
                if (currentVar) {
                    this._removePhpVariable(selection);
                    wysiwyg.odooEditor.historyStep();
                    // this._onSelectionChange();
                    const $varInput = this.$el.find('.data-variable-input');
                    $varInput.val('');
                    const $cancelButton = this.$el.find('.data-remove-php-var');
                    $cancelButton.addClass('d-none');
                }
            } catch (error) {
                console.error('Error removing PHP variable:', error);
                alert('An error occurred while removing the PHP variable. Please try again.');
            }

        },


        /**
         * Event handler for php variable constant type toggle button
         * @param {Event} ev 
         * @returns 
         */
        _onConstButtonClick: function (ev) {

            const $button = $(ev.currentTarget);
            $button.toggleClass('active');
            this.isConstVar = $button.hasClass('active');

            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            const selection = this._getCurrentSelection();
            if (!selection) return;

            const currentVar = this._hasPhpVariable(selection);
            if (currentVar && currentVar.element) {
                // Simply update the constant attribute on the existing span
                $(currentVar.element).attr('data-php-const-var', this.isConstVar ? '1' : '0');
                wysiwyg.odooEditor.historyStep();
            }
        },

        /**
         * Clean up empty spans
         * @param {*} element 
         */
        _cleanupEmptySpans: function (element) {
            const emptySpans = $(element).find('span[data-php-var]:empty');
            emptySpans.each(function () {
                $(this).remove();
            });
        },

        /**
         * Check existing php variables
         * @param {*} selection 
         * @returns 
         */
        _hasPhpVariable: function (selection) {
            if (!selection || !selection.rangeCount) return false;

            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;
            const $span = $(container).closest('span[data-php-var]');

            if ($span.length) {
                return {
                    name: $span.attr('data-php-var'),
                    class: $span.attr('class'),
                    element: $span[0],
                    isConst: $span.attr('data-php-const-var') === '1'
                };
            }
            return false;
        },

        /**
         * Return text content from node
         * @param {*} node 
         * @returns 
         */
        _getAllTextContent: function (node) {
            return node.textContent || node.innerText || '';
        },

        /**
         * Removes php variables from selections
         * @param {*} selection 
         * @returns 
         */
        _removePhpVariable: function (selection) {
            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const $span = $(range.commonAncestorContainer).closest('span[data-php-var]');

            if ($span.length) {
                const allText = this._getAllTextContent($span[0]);
                if (!allText.trim()) {
                    $span.remove();
                    return null;
                }

                const textNode = document.createTextNode(allText);
                $span[0].parentNode.insertBefore(textNode, $span[0]);
                $span.remove();

                if ($span[0].parentNode) {
                    this._cleanupEmptySpans($span[0].parentNode);
                }

                const newRange = document.createRange();
                newRange.selectNode(textNode);
                selection.removeAllRanges();
                selection.addRange(newRange);

                return textNode;
            }
            return null;
        },


        /**
         * Apply php variable on selection
         * @param {*} selection 
         * @param {*} variable 
         * @returns 
         */
        _applyPhpVariable: function (selection, variable) {
            if (!selection.rangeCount) return;
            if (variable.name === 'none') {
                return this._removePhpVariable(selection);
            }

            const range = selection.getRangeAt(0);
            let selectedText = '';

            const container = range.commonAncestorContainer;
            if (container.nodeType === Node.TEXT_NODE) {
                selectedText = range.toString().trim();
            } else {
                const div = document.createElement('div');
                div.appendChild(range.cloneContents());
                selectedText = div.textContent.trim();
            }

            if (!selectedText) {
                return;
            }

            const span = document.createElement('span');
            span.className = `${variable.class} o_text-php-var-info`;
            span.setAttribute('data-php-var', variable.name);

            // Use the current state of the constant button
            const $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');
            span.setAttribute('data-php-const-var', $constButton.hasClass('active') ? '1' : '0');

            span.textContent = selectedText;

            range.deleteContents();
            range.insertNode(span);

            const $parentSpan = $(span).closest('span[data-php-var]').not(span);
            if ($parentSpan.length) {
                const parentText = this._getAllTextContent($parentSpan[0]);
                const textNode = document.createTextNode(parentText);
                $parentSpan[0].parentNode.replaceChild(span, $parentSpan[0]);
            }

            if (span.parentNode) {
                this._cleanupEmptySpans(span.parentNode);
            }

            selection.removeAllRanges();
            const newRange = document.createRange();
            newRange.selectNodeContents(span);
            selection.addRange(newRange);

            const $cancelButton = this.$el.find('.data-remove-php-var');
            $cancelButton.removeClass('d-none');

            return span;
        },



        /**
         * Handle php variable changes
         * @param {Event} ev 
         */
        _onPhpVariableChange: function (ev) {
            const selection = this._getCurrentSelection();
            const currentVar = this._hasPhpVariable(selection);
            const $removeButton = this.$el.find('.data-remove-php-var');
            const $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');
            const $varInput = this.$el.find('.data-variable-input');


            if (currentVar) {
                $removeButton.removeClass('d-none');
                $constButton.toggleClass('active', currentVar.isConst);
                this.isConstVar = currentVar.isConst;

                // Only update input if it's empty or different from current variable name
                if ($varInput.length && (!$varInput.val() || $varInput.val() !== currentVar.name)) {
                    $varInput.val(currentVar.name);
                }
            } else {
                $varInput.val('');
                $removeButton.addClass('d-none');
                $constButton.removeClass('active');
                this.isConstVar = false;
            }
        },


        /**
         * Event handler for Strong button click
         * @param {Event} ev 
         */
        _onStrongTagClick: function (ev) {
            ev.preventDefault();
            this._applyTextFormatting('strong-tag');
        },

        /**
         * Event handler for BTag button click
         * @param {Event} ev 
         */
        _onBTagClick: function (ev) {
            ev.preventDefault();
            this._applyTextFormatting('b-tag');
        },

        /**
         * Event handler for Font-bold button click
         * @param {Event} ev 
         */
        _onFontBoldClick: function (ev) {
            ev.preventDefault();
            this._applyTextFormatting('font-bold');
        },

        /**
         * Event handler for Italic button click
         * @param {Event} ev 
         */
        _onItalicTagClick: function (ev) {
            ev.preventDefault();
            this._applyTextFormatting('italic-tag');
        },

        /**
         * Event handler for Underline button click
         * @param {Event} ev 
         */
        _onUnderlineTagClick: function (ev) {
            ev.preventDefault();
            this._applyTextFormatting('underline-tag');
        },

        /**
         * Text formatting function for bold variants, italic, underline and links
         * @param {*} formatType 
         * @returns 
         */
        _applyTextFormatting: function (formatType) {
            const selection = this._getCurrentSelection();
            if (!selection || !selection.rangeCount) {
                alert('Please select some text first');
                return;
            }

            const range = selection.getRangeAt(0);
            const selectedText = range.toString().trim();

            if (!selectedText) {
                alert('Please select some text first');
                return;
            }

            const $currentButton = this.$el.find(`[data-variable-class="${formatType}"]`);
            const hasFormatting = this._hasFormatting(selection, formatType);

            const boldVariants = ['strong-tag', 'b-tag', 'font-bold'];
            const isBoldVariant = boldVariants.includes(formatType);

            if (hasFormatting) {
                // If the same formatting was active, just remove it
                this._removeSpecificFormatting(selection, formatType);
                $currentButton.removeClass('active btn-success').addClass('btn-primary');
            } else {
                // If it's a bold variant, remove only other bold variants
                if (isBoldVariant) {
                    boldVariants.forEach(variant => {
                        if (variant !== formatType) {
                            this._removeSpecificFormatting(selection, variant);
                            this.$el.find(`[data-variable-class="${variant}"]`)
                                .removeClass('active btn-success')
                                .addClass('btn-primary');
                        }
                    });
                }

                // Check for existing non-bold formatting
                const existingNonBoldFormats = ['italic-tag', 'underline-tag'];
                let existingNonBoldElement = null;

                existingNonBoldFormats.forEach(format => {
                    const $element = $(selection.getRangeAt(0).commonAncestorContainer).closest(
                        format === 'italic-tag' ? 'i' : 'u'
                    );
                    if ($element.length) {
                        existingNonBoldElement = $element[0];
                    }
                });

                // Apply new formatting
                const newElement = this._createFormattingElement(formatType);

                if (existingNonBoldElement) {
                    // If non-bold formatting exists, wrap it
                    const wrapper = document.createElement('span');
                    wrapper.appendChild(newElement);
                    existingNonBoldElement.parentNode.replaceChild(wrapper, existingNonBoldElement);
                    newElement.appendChild(existingNonBoldElement);
                } else {
                    const range = selection.getRangeAt(0);
                    const textContent = range.toString();
                    newElement.textContent = textContent;

                    range.deleteContents();
                    range.insertNode(newElement);
                }

                // Set this button as active
                $currentButton.removeClass('btn-primary').addClass('active btn-success');

                // Select the newly formatted text
                const newRange = document.createRange();
                newRange.selectNodeContents(newElement);
                selection.removeAllRanges();
                selection.addRange(newRange);
            }

            // Update history
            const wysiwyg = this._getWysiwygInstance();
            if (wysiwyg && wysiwyg.odooEditor) {
                wysiwyg.odooEditor.historyStep();
            }
        },


        /**
         * Checks existing formatting in selection
         * @param {*} selection 
         * @param {*} formatType 
         * @returns 
         */
        _hasFormatting: function (selection, formatType) {
            if (!selection || !selection.rangeCount) return false;

            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;
            let $element;

            switch (formatType) {
                case 'strong-tag':
                    $element = $(container).closest('strong');
                    break;
                case 'b-tag':
                    $element = $(container).closest('b');
                    break;
                case 'font-bold':
                    $element = $(container).closest('span.font-bold');
                    break;
                case 'italic-tag':
                    $element = $(container).closest('i');
                    break;
                case 'underline-tag':
                    $element = $(container).closest('u');
                    break;
            }

            return $element.length > 0;
        },


        /**
         * Remove spacific formatting from selection
         * @param {*} selection 
         * @param {*} formatType 
         * @returns 
         */
        _removeSpecificFormatting: function (selection, formatType) {
            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;
            let selector;

            switch (formatType) {
                case 'strong-tag':
                    selector = 'strong';
                    break;
                case 'b-tag':
                    selector = 'b';
                    break;
                case 'font-bold':
                    selector = 'span.font-bold';
                    break;
                case 'italic-tag':
                    selector = 'i';
                    break;
                case 'underline-tag':
                    selector = 'u';
                    break;
                default:
                    return;
            }

            const $element = $(container).closest(selector);
            if ($element.length) {
                const textContent = $element[0].textContent;
                const textNode = document.createTextNode(textContent);
                $element[0].parentNode.replaceChild(textNode, $element[0]);

                // Reselect the text
                const newRange = document.createRange();
                newRange.selectNodeContents(textNode);
                selection.removeAllRanges();
                selection.addRange(newRange);
            }
        },


        /**
         * Returns a element based on formatType
         * @param {*} formatType 
         * @returns 
         */
        _createFormattingElement: function (formatType) {
            switch (formatType) {
                case 'strong-tag':
                    return document.createElement('strong');
                case 'b-tag':
                    return document.createElement('b');
                case 'font-bold':
                    const element = document.createElement('span');
                    element.className = 'font-bold';
                    return element;
                case 'italic-tag':
                    return document.createElement('i');
                case 'underline-tag':
                    return document.createElement('u');
                default:
                    throw new Error('Unknown formatting type');
            }
        },


        /* _getCurrentFormatting: function (selection) {
            if (!selection || !selection.rangeCount) return null;

            const formatTypes = ['strong-tag', 'b-tag', 'font-bold', 'italic-tag', 'underline-tag'];
            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;

            for (const type of formatTypes) {
                let selector;
                switch (type) {
                    case 'strong-tag':
                        selector = 'strong';
                        break;
                    case 'b-tag':
                        selector = 'b';
                        break;
                    case 'font-bold':
                        selector = 'span.font-bold';
                        break;
                    case 'italic-tag':
                        selector = 'i';
                        break;
                    case 'underline-tag':
                        selector = 'u';
                        break;
                }
                if ($(container).closest(selector).length) {
                    return type;
                }
            }
            return null;
        }, */

        /* _removeAllFormatting: function (selection) {
            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const formatTypes = ['strong', 'b', 'span.font-bold', 'i', 'u'];

            // Find the outermost formatting element
            const container = range.commonAncestorContainer;
            let formattedElement = null;
            let textContent = '';

            for (const type of formatTypes) {
                const $element = $(container).closest(type);
                if ($element.length) {
                    formattedElement = $element[0];
                    textContent = this._getAllTextContent(formattedElement);
                    break;  // Take only the outermost formatting
                }
            }

            if (formattedElement) {
                const textNode = document.createTextNode(textContent);
                formattedElement.parentNode.replaceChild(textNode, formattedElement);

                // Reselect the text
                const newRange = document.createRange();
                newRange.selectNodeContents(textNode);
                selection.removeAllRanges();
                selection.addRange(newRange);
            }
        }, */


        /**
         * Updae button state [arrange classes] on selection change
         * @param {*} selection 
         * @returns 
         * 
         */
        _updateButtonState: function (ev, selection) {

            //TODO add link button

            if (!selection || !selection.rangeCount) {
                this.$el.find('[data-variable-class]').removeClass('active btn-success').addClass('btn-primary');
                return;
            }

            const formatTypes = ['strong-tag', 'b-tag', 'font-bold', 'italic-tag', 'underline-tag'];
            const boldVariants = ['strong-tag', 'b-tag', 'font-bold'];
            const $allButtons = this.$el.find('[data-variable-class]');

            // Reset all buttons first
            $allButtons.removeClass('active btn-success').addClass('btn-primary');

            // Track which bold variant is active
            let activeBoldVariant = null;

            formatTypes.forEach(formatType => {
                if (this._hasFormatting(selection, formatType)) {
                    const $button = this.$el.find(`[data-variable-class="${formatType}"]`);
                    $button.removeClass('btn-primary').addClass('active btn-success');

                    // Track the active bold variant
                    if (boldVariants.includes(formatType)) {
                        activeBoldVariant = formatType;
                    }
                }
            });

            // Ensure only one bold variant is highlighted
            if (activeBoldVariant) {
                boldVariants.forEach(variant => {
                    if (variant !== activeBoldVariant) {
                        this.$el.find(`[data-variable-class="${variant}"]`)
                            .removeClass('active btn-success')
                            .addClass('btn-primary');
                    }
                });
            }
        },

        /**
         * Handles changes in bold varients
         * @param {Event} ev 
         * @returns 
         */
        _onBoldSelectionChange: function (ev) {

            const selection = this._getCurrentSelection();
            if (!selection) return;

            // Update the state of each formatting button based on current selection
            ['strong-tag', 'b-tag', 'font-bold'].forEach(formatType => {
                const hasFormat = this._hasFormatting(selection, formatType);
                const $button = this.$el.find(`[data-variable-class="${formatType}"]`);

                if (hasFormat) {
                    $button.removeClass('btn-primary').addClass('active btn-success');
                } else {
                    $button.removeClass('active btn-success').addClass('btn-primary');
                }
            });
        },







        /**
         * Handles link button click event
         * @param {Event} ev 
         * @returns 
         */
        _onLinkButtonClick: function (ev) {
            ev.preventDefault();

            console.log("called")
            const $linkButton = this.$el.find('[data-variable-class="a-tag"]');
            const $urlSection = this.$el.find('.url-input-section');
            const $urlInput = $urlSection.find('.link-url-input');
            const $removeBtn = $urlSection.find('[data-remove-url="true"]');
            const $newTabCheckbox = this.$el.find('[data-select-class="o_au_link_target"]');

            // Toggle button state
            this._resetUrlInputSection();
            $linkButton.toggleClass('active');

            // Show/hide URL section based on button state
            if ($linkButton.hasClass('active')) {
                $urlSection.removeClass('d-none');

                // If clicked element is a link in the editable area  
                const existingLink = this._getExistingLink(this.currentTarget);

                if (existingLink) {

                    // Update input with clicked link's URL
                    $urlInput.val(existingLink.href);
                    $removeBtn.removeClass('d-none');

                    const isNewTab = existingLink.target === '_blank';
                    $newTabCheckbox.toggleClass('active', isNewTab);
                    // this.isTargetNewTab = isNewTab;

                    this.currentLink = existingLink.href;

                }
                $urlInput.focus();
            }

        },



        /**
         * Event handler to remove link 
         * @param {Event} ev 
         */
        _onRemoveUrl: function (ev) {
            ev.preventDefault();

            const selection = this._getCurrentSelection();
            if (selection) {

                this._removeLink(ev, selection);

                const wysiwyg = this._getWysiwygInstance();
                if (wysiwyg) {
                    wysiwyg.odooEditor.historyStep();
                }
            }
        },

        /**
         * Remove link formatting
         * @private
         */
        _removeLink: function (ev, selection) {
            // if (!selection.rangeCount) return;

            const link = this._getExistingLink(this.currentTarget);


            if (link) {
                if ($(link.element).hasClass("btn")) {
                    $(link.element).attr("href", "#")
                    $(link.element).removeAttr('target');
                }
                else {
                    const textNode = document.createTextNode(link.element.textContent);
                    link.element.parentNode.replaceChild(textNode, link.element);

                    // Reselect the text
                    const newRange = document.createRange();
                    newRange.selectNodeContents(textNode);
                    selection.removeAllRanges();
                    selection.addRange(newRange);
                }

                this._resetUrlInputSection();
                // Prevent default click behavior
                ev.preventDefault();
                ev.stopPropagation();
            }
        },


        /**
         * Get existing link from selection if it exists
         * @private
         */
        _getExistingLink: function (clickedElement) {
            // If element itself is <a> tag
            if (clickedElement && clickedElement.tagName === 'A') {
                return {
                    element: clickedElement,
                    href: clickedElement.getAttribute('href') ? clickedElement.getAttribute('href').toString().trim() : null,
                    target: clickedElement.getAttribute('target') ? clickedElement.getAttribute('target').toString().trim() : null
                };
            }

            return null;
        },



        /**
         * Event handler for link target toogler button click
         * @param {Event} ev 
         */
        _onLinkTargetButtonClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            const $button = $(ev.currentTarget);

            // Toggle active state
            $button.toggleClass('active');

            // Update isTargetNewTab variable
            // this.isTargetNewTab = $button.hasClass('active');
        },


        /**
         * Event handler for save url
         * @param {Event} ev 
         * @returns 
         */
        _onSaveUrl: function (ev) {
            ev.preventDefault();
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            const url = this.$el.find('.link-url-input').val();
            const $newTabCheckbox = this.$el.find('[data-select-class="o_au_link_target"]');

            if (!url) {
                alert('Please enter a URL');
                return;
            }


            const existingLink = this._getExistingLink(this.currentTarget);

            // Handle link update/creation
            if (existingLink) {
                $(existingLink.element).attr('href', url);

                if ($newTabCheckbox.hasClass('active')) {
                    $(existingLink.element).attr('target', '_blank');
                } else {
                    $(existingLink.element).removeAttr('target');
                }
            } else {
                const selection = this._getCurrentSelection();
                const range = selection.getRangeAt(0);
                const selectedText = range.toString();

                const link = document.createElement('a');
                link.href = url;
                link.textContent = selectedText;

                if ($newTabCheckbox.hasClass('active')) {
                    link.target = '_blank';
                }

                range.deleteContents();
                range.insertNode(link);
            }

            wysiwyg.odooEditor.historyStep();
            this._resetUrlInputSection();
        },

        /**
         * Event handler to close url input section
         * @param {Event} ev 
         */
        _onCancelUrl: function (ev) {
            this._resetUrlInputSection();
        },

        /**
         * reset default url input section
         */
        _resetUrlInputSection: function () {
            const $urlSection = this.$el.find('.url-input-section');
            const $urlInput = $urlSection.find('.link-url-input');
            const $removeBtn = $urlSection.find('[data-remove-url="true"]');
            const $newTabCheckbox = $urlSection.find('[data-select-class="o_au_link_target"]');

            // Reset all input values and states
            $urlInput.val('');
            $newTabCheckbox.removeClass('active');
            // this.isTargetNewTab = false;
            this.currentLink = null;

            // Hide the section and remove editing state
            $urlSection.addClass('d-none');
        },

        /**
         * Handle link editing block on selection change
         * @param {Event} ev 
         */
        _onLinkSelectionChange: function (ev) {
            const $linkButton = this.$el.find('[data-variable-class="a-tag"]');
            const $urlSection = this.$el.find('.url-input-section');
            const $removeBtn = $urlSection.find('[data-remove-url="true"]');
            const $urlInput = $urlSection.find('.link-url-input');
            const $newTabCheckbox = $urlSection.find('[data-select-class="o_au_link_target"]');

            // Get the current selection
            // const selection = this._getCurrentSelection();

            const existingLink = this._getExistingLink(this.currentTarget);

            // if ((selection && selection.toString().trim()) || this.currentLink) {
            if (existingLink) {

                $urlSection.removeClass('d-none');
                $removeBtn.removeClass('d-none');
                $linkButton.addClass('active');
                $urlInput.val(existingLink.href);

                /* if ($(existingLink.element).hasClass("btn")) {

                    $removeBtn.addClass('d-none');
                }
                else {
                    $removeBtn.removeClass('d-none');
                } */

                // Update new tab checkbox state based on the link's target attribute
                if (existingLink.target === '_blank') {
                    $newTabCheckbox.addClass('active');
                    // this.isTargetNewTab = true;
                } else {
                    $newTabCheckbox.removeClass('active');
                    // this.isTargetNewTab = false;
                }

                // Track the currently selected link for further modifications
                this.currentLink = $(existingLink);

            } else {
                this.currentLink = null
                // Only reset if we're not currently editing a link
                $linkButton.removeClass('active');
                $urlInput.val('');
                $removeBtn.addClass('d-none');
                $urlSection.addClass('d-none');
                $newTabCheckbox.removeClass('active');
                // this.isTargetNewTab = false;
            }


        },


    });
});