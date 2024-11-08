odoo.define('website.snippets.php_variable_text_selector', function (require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');

    options.registry.PhpVariableTextSelector = options.Class.extend({
        events: _.extend({}, options.Class.prototype.events || {}, {
            'click [data-select-var]': '_onVariableSelect',
            'mouseup .o_editable': '_onSelectionChange',
            'click [data-select-class="o_au_php_var_type"]': '_onConstButtonClick',
        }),

        init: function () {
            this._super.apply(this, arguments);
            this.selectedVariable = null;
            this.isConstVar = false;
        },

        start: function () {
            var self = this;
            $(document).on('selectionchange', _.debounce(function() {
                self._onSelectionChange();
            }, 100));
            return this._super.apply(this, arguments);
        },

        _cleanupEmptySpans: function(element) {
            const emptySpans = $(element).find('span[data-php-var]:empty');
            emptySpans.each(function() {
                $(this).remove();
            });
        },

        _hasPhpVariable: function(selection) {
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

        _getAllTextContent: function(node) {
            return node.textContent || node.innerText || '';
        },

        _removePhpVariable: function(selection) {
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

        _applyPhpVariable: function(selection, variable) {
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

            return span;
        },
        _onConstButtonClick: function(ev) {
                    const $button = $(ev.currentTarget);
                    $button.toggleClass('active');
                    this.isConstVar = $button.hasClass('active');

                    const wysiwyg = this.options.wysiwyg;
                    if (!wysiwyg) return;

                    const selection = wysiwyg.odooEditor.document.getSelection();
                    if (!selection) return;

                    const currentVar = this._hasPhpVariable(selection);
                    if (currentVar && currentVar.element) {
                        // Simply update the constant attribute on the existing span
                        $(currentVar.element).attr('data-php-const-var', this.isConstVar ? '1' : '0');
                        wysiwyg.odooEditor.historyStep();
                    }
        },
//        _onConstButtonClick: function(ev) {
//            const $button = $(ev.currentTarget);
//            $button.toggleClass('active');
//            this.isConstVar = $button.hasClass('active');
//
//            // Update existing PHP variable if one is selected
//            const wysiwyg = this.options.wysiwyg;
//            if (!wysiwyg) return;
//
//            const selection = wysiwyg.odooEditor.document.getSelection();
//            if (!selection) return;
//
//            const currentVar = this._hasPhpVariable(selection);
//            if (currentVar && currentVar.element) {
//                // Update the constant attribute
//                $(currentVar.element).attr('data-php-const-var', this.isConstVar ? '1' : '0');
//
//                // If there's an active variable, reapply it
//                const activeButton = this.$el.find('[data-select-var].active');
//                if (activeButton.length && activeButton.data('select-var') !== 'none') {
//                    this._applyPhpVariable(selection, {
//                        name: activeButton.data('select-var'),
//                        class: activeButton.data('variable-class')
//                    });
//                }
//
//                wysiwyg.odooEditor.historyStep();
//            }
//        },

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
                    this.$el.find('[data-select-var]').removeClass('active');
                    $target.addClass('active');
                } else {
                    if (currentVar && currentVar.name === variableName) {
                        this._removePhpVariable(selection);
                        $target.removeClass('active');
                    } else {
                        if (currentVar) {
                            this._removePhpVariable(selection);
                        }

                        const span = this._applyPhpVariable(selection, {
                            name: variableName,
                            class: variableClass
                        });

                        if (span) {
                            this.$el.find('[data-select-var]').removeClass('active');
                            $target.addClass('active');
                        }
                    }
                }

                this._cleanupEmptySpans($editable[0]);
                wysiwyg.odooEditor.historyStep();
                this._onSelectionChange();

            } catch (error) {
                console.error('Error applying variable:', error);
                alert('An error occurred while applying the variable. Please try again.');
            }
        },

        _onSelectionChange: function() {
            const wysiwyg = this.options.wysiwyg;
            if (!wysiwyg) return;

            const selection = wysiwyg.odooEditor.document.getSelection();
            if (!selection) return;

            const currentVar = this._hasPhpVariable(selection);

            // Update constant button state based on current selection
            const $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');
            if (currentVar) {
                $constButton.toggleClass('active', currentVar.isConst);
                this.isConstVar = currentVar.isConst;
            }

            this.$el.find('[data-select-var]').each(function() {
                const $btn = $(this);
                const varName = $btn.data('select-var');
                const isActive = currentVar && currentVar.name === varName;

                if (varName === 'none') {
                    $btn.toggleClass('active', !currentVar);
                } else {
                    $btn.toggleClass('active', isActive);
                }

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