console.log("============snippet_optioncall================================")
odoo.define('website.snippets.php_variable_text_selector', function (require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');

    options.registry.PhpVariableTextSelector = options.Class.extend({
        events: _.extend({}, options.Class.prototype.events || {}, {
            'click [data-select-var]': '_onVariableSelect',
            'mouseup .o_editable': '_onSelectionChange',
            'change .o_au_php_var_const': '_onConstTypeChange',
        }),

        init: function () {
            this._super.apply(this, arguments);
            this.selectedVariable = null;
        },

        start: function () {
            var self = this;
            $(document).on('selectionchange', _.debounce(function() {
                self._onSelectionChange();
            }, 100));
            return this._super.apply(this, arguments);
        },

        /**
         * Helper to check if selection has a specific PHP variable
         */
         _cleanupEmptySpans: function(element) {
            const emptySpans = $(element).find('span[data-php-var]:empty');
            emptySpans.each(function() {
                $(this).remove();
            });
        },

        /**
         * Helper to check if selection has a specific PHP variable
         */
        _hasPhpVariable: function(selection) {
            if (!selection || !selection.rangeCount) return false;

            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;
            const $span = $(container).closest('span[data-php-var]');

            if ($span.length) {
                return {
                    name: $span.attr('data-php-var'),
                    class: $span.attr('class'),
                    element: $span[0]
                };
            }
            return false;
        },

        /**
         * Helper to get all text content from a node
         */
        _getAllTextContent: function(node) {
            return node.textContent || node.innerText || '';
        },

        /**
         * Remove PHP variable formatting from the selected text
         */
        _removePhpVariable: function(selection) {
            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const $span = $(range.commonAncestorContainer).closest('span[data-php-var]');

            if ($span.length) {
                const allText = this._getAllTextContent($span[0]);
                if (!allText.trim()) {
                    // If span is empty, just remove it
                    $span.remove();
                    return null;
                }

                const textNode = document.createTextNode(allText);
                $span[0].parentNode.insertBefore(textNode, $span[0]);
                $span.remove();

                // Clean up any empty spans in the parent
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



//        _update_value_for_var_type: function((selection){
//            if (!selection.rangeCount) return;
//            const range = selection.getRangeAt(0);
//            let selectedText = '';
//
//            // Get the complete text content
//            const container = range.commonAncestorContainer;
//            if (container.nodeType === Node.TEXT_NODE) {
//                selectedText = range.toString().trim();
//            } else {
//                const div = document.createElement('div');
//                div.appendChild(range.cloneContents());
//                selectedText = div.textContent.trim();
//            }
//
//            if (!selectedText) {
//                return;
//            }
//
//
//        }

        /**
         * Apply PHP variable formatting to the selected text
         */
        _applyPhpVariable: function(selection, variable) {
            if (!selection.rangeCount) return;
            if (variable.name === 'none') {
                return this._removePhpVariable(selection);
            }

            const range = selection.getRangeAt(0);
            let selectedText = '';

            // Get the complete text content
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

            // Create span element
            const span = document.createElement('span');
            span.className = variable.class;
            span.setAttribute('data-php-var', variable.name);

            const $button = this.$el.find('we-button[data-select-class="o_au_php_var_type"]');
            console.log($button)
            if ($button.hasClass('active')) {
                // Checkbox is active
                span.setAttribute('data-php-const-var', '1');
            }
            else{
                span.setAttribute('data-php-const-var', '0');
            }
            span.textContent = selectedText;

            // Remove any existing content and insert the new span
            range.deleteContents();
            range.insertNode(span);

            // Clean up any nested spans
            const $parentSpan = $(span).closest('span[data-php-var]').not(span);
            if ($parentSpan.length) {
                const parentText = this._getAllTextContent($parentSpan[0]);
                const textNode = document.createTextNode(parentText);
                $parentSpan[0].parentNode.replaceChild(span, $parentSpan[0]);
            }

            // Clean up any empty spans that might have been created
            if (span.parentNode) {
                this._cleanupEmptySpans(span.parentNode);
            }

            // Update selection to span
            selection.removeAllRanges();
            const newRange = document.createRange();
            newRange.selectNodeContents(span);
            selection.addRange(newRange);

            return span;
        },

        /**
         * Handle variable selection
         */
        _onVariableSelect: function(ev) {
            const $target = $(ev.currentTarget);
            const variableName = $target.data('select-var');
            const variableClass = $target.data('variable-class');

            const wysiwyg = this.options.wysiwyg;
            if (!wysiwyg) return;

            const selection = wysiwyg.odooEditor.document.getSelection();
            if (!selection || !selection.toString().trim()) {
                alert('Please select some text first');
                return;
            }

            // Check if selection is within editable area
            const range = selection.getRangeAt(0);
            const $editable = $(range.commonAncestorContainer).closest('.o_editable');
            if (!$editable.length) {
                alert('Please select text within the editable area');
                return;
            }

            try {
                const currentVar = this._hasPhpVariable(selection);

                if (variableName === 'none') {
                    // Always remove formatting when 'None' is selected
                    if (currentVar) {
                        this._removePhpVariable(selection);
                    }
                    this.$el.find('[data-select-var]').removeClass('active');
                    $target.addClass('active');
                } else {
                    // Handle toggle off same variable
                    if (currentVar && currentVar.name === variableName) {
                        this._removePhpVariable(selection);
                        $target.removeClass('active');
                    } else {
                        // Remove existing variable if present
                        if (currentVar) {
                            this._removePhpVariable(selection);
                        }

                        // Apply new variable
                        const span = this._applyPhpVariable(selection, {
                            name: variableName,
                            class: variableClass
                        });

                        if (span) {
                            // Update button state
                            this.$el.find('[data-select-var]').removeClass('active');
                            $target.addClass('active');
                        }
                    }
                }

                // Clean up any empty spans in the editable area
                this._cleanupEmptySpans($editable[0]);

                // Ensure proper cleanup and update
                wysiwyg.odooEditor.historyStep();
                this._onSelectionChange();

            } catch (error) {
                console.error('Error applying variable:', error);
                alert('An error occurred while applying the variable. Please try again.');
            }
        },
        _onConstTypeChange: function(ev) {
            const $checkbox = $(ev.currentTarget);
            if ($checkbox.is(':checked')) {
                $checkbox.addClass('o_au_php_var_const');
            } else {
                $checkbox.removeClass('o_au_php_var_const');
            }
        },
        _onSelectionChange: function() {
            const wysiwyg = this.options.wysiwyg;
            if (!wysiwyg) return;

            const selection = wysiwyg.odooEditor.document.getSelection();
            if (!selection) return;

            // Update UI to reflect current PHP variable state
            const currentVar = this._hasPhpVariable(selection);
            this.$el.find('[data-select-var]').each(function() {
                const $btn = $(this);
                const varName = $btn.data('select-var');
                const isActive = currentVar && currentVar.name === varName;

                // Special handling for 'None' button
                if (varName === 'none') {
                    $btn.toggleClass('active', !currentVar);
                } else {
                    $btn.toggleClass('active', isActive);
                }

                // Update the PHP Variables dropdown
                const $select = $btn.closest('we-select');
                if ($select.length) {
                    if (isActive) {
                        $select.find('we-selection-items we-button').removeClass('active');
                        $btn.addClass('active');
                        $select.find('we-toggler').text(varName);
                    } else if (!currentVar) {
                        $select.find('we-toggler').text('PHP Variables');
                        $select.find('[data-select-var="none"]').addClass('active');
                    }
                }
            });
        },

        destroy: function () {
            $(document).off('selectionchange');
            this._super.apply(this, arguments);
        }
    });
});