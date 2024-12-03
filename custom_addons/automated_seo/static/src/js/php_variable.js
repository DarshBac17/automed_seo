console.log("============snippet_optioncall================================")
odoo.define('website.snippets.php_variable_text_selector2', function (require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');

         options.registry.PhpVariableTextSelector = options.Class.extend({
//        xmlDependencies: ['/website/static/src/snippets/s_php_variable/options.xml'],
        
        events: _.extend({}, options.Class.prototype.events || {}, {
            'click .o_we_php_dropdown_toggle': '_onToggleDropdown',
            'input .o_we_php_search': '_onSearch',
            'click .o_we_php_variables_list we-button': '_onVariableSelect',
            'click [data-select-var]': '_onVariableSelect',
            'mouseup .o_editable': '_onSelectionChange',
        }),

        init: function () {
            this._super.apply(this, arguments);
            this.selectedVariable = null;
            this.isDropdownOpen = false;
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self._createDropdown();
                // Handle click outside
                $(document).on('click.php_dropdown', function(e) {
                    if (!$(e.target).closest('.o_we_php_dropdown').length && self.isDropdownOpen) {
                        self._closeDropdown();
                    }
                });
            });
        },

        _createDropdown: function() {
            console.log('Creating dropdown...');

            // Create elements using jQuery
            this.$dropdown = $('<div/>', {
                class: 'o_we_php_dropdown'
            });

            this.$toggle = $('<div/>', {
                class: 'o_we_php_dropdown_toggle'
            }).append(
                $('<span/>').text('PHP Variables'),
                $('<i/>', {class: 'fa fa-chevron-down'})
            );

            this.$menu = $('<div/>', {
                class: 'o_we_php_dropdown_menu'
            });

            this.$search = $('<input/>', {
                type: 'text',
                class: 'o_we_php_search',
                placeholder: 'Search variables...'
            });

            this.$variablesList = $('<div/>', {
                class: 'o_we_php_variables_list'
            });

            // Build structure
            this.$menu.append(
                $('<div/>', {class: 'o_we_php_search_wrapper'}).append(this.$search),
                this.$variablesList
            );

            // Add variables
            this.$variablesList.append(
                $('<we-button/>', {
                    'data-select-var': 'none',

                    class: 'o_we_destroy_btn'
                }).text('None'),
                $('<we-button/>', {
                    'data-select-var': 'VAR_1',
                    'data-variable-class':"VAR_1",
                }).text('Variable 1'),
                $('<we-button/>', {
                    'data-select-var': 'VAR_2',
                    'data-variable-class':"VAR_2",
                }).text('Variable 2')
            );

            // Assemble dropdown
            this.$dropdown
                .append(this.$toggle)
                .append(this.$menu);

            // Add to DOM
            this.$el.append(this.$dropdown);

            console.log('Dropdown elements:', {
                dropdown: this.$dropdown.length,
                toggle: this.$toggle.length,
                menu: this.$menu.length,
                search: this.$search.length,
                list: this.$variablesList.length
            });
        },

        _onToggleDropdown: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            console.log('Toggle clicked', {
                isOpen: this.isDropdownOpen,
                hasMenu: this.$menu.length
            });

            if (this.isDropdownOpen) {
                this._closeDropdown();
            } else {
                this._openDropdown();
            }
        },

        _openDropdown: function () {
            if (!this.$menu.length) {
                console.error('Menu element not found');
                return;
            }
            this.isDropdownOpen = true;
            this.$menu.addClass('show');
            this.$search.val('').focus();
        },

        _closeDropdown: function () {
            if (!this.$menu.length) {
                console.error('Menu element not found');
                return;
            }
            this.isDropdownOpen = false;
            this.$menu.removeClass('show');
        },

        _onSearch: function (ev) {
            const searchTerm = $(ev.currentTarget).val().toLowerCase();
            this.$variablesList.each(function() {
                const $btn = $(this);
                const text = $btn.text().toLowerCase();
                $btn.toggle(text.includes(searchTerm));
            });
        },
        _updateVariablesList: function (searchTerm = '') {
            this.$variablesList.find('we-button').each(function() {
                const $btn = $(this);
                const text = $btn.text().toLowerCase();
                $btn.toggle(text.includes(searchTerm));
            });
        },

        _onClickAway: function (ev) {
            if (this.isDropdownOpen && 
                !$(ev.target).closest('.o_we_php_dropdown').length) {
                this._closeDropdown();
            }
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
            console.log("_hasPhpVariable call......")
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
        /**
         * Apply PHP variable formatting to the selected text
         */
        _applyPhpVariable: function(selection, variable) {
            console.log("_applyPhpVariable.................")
            if (!selection.rangeCount) return;
            if (variable.name === 'none') {
                return this._removePhpVariable(selection);
            }
            const range = selection.getRangeAt(0);
            console.log("selection================",selection)
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
            console.log("=================",selection)
            return span;
        },
        /**
         * Handle variable selection
         */
        _onVariableSelect: function(ev) {
            console.log("_onVariableSelect call...............")
            const $target = $(ev.currentTarget);
            const variableName = $target.data('select-var');
            console.log("variableName:",variableName)
            const variableClass = $target.data('variable-class');
            console.log("variableClass:",variableClass)

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
                console.log("currnetvar",currentVar)
                if (variableName === 'none') {
                    // Always remove formatting when 'None' is selected
                    if (currentVar) {
                        this._removePhpVariable(selection);
                    }
                    this.$el.find('[data-select-var]').removeClass('active');
                    $target.addClass('active');
                } else {
                        console.log("else===================")

                    // Handle toggle off same variable
                    if (currentVar && currentVar.name === variableName) {
                        this._removePhpVariable(selection);
                        $target.removeClass('active');
                    } else {
                        // Remove existing variable if present
                        if (currentVar) {
                            this._removePhpVariable(selection);
                        }
                        console.log("inside span===================")
                        // Apply new variable
                        const span = this._applyPhpVariable(selection, {
                            name: variableName,
                            class: variableClass
                        });
//                        if (span) {
//                            console.log("span=================inside",span)
//                            console.log("target=================inside",$target)
//                            // Update button state
//                            this.$el.find('[data-select-var]').removeClass('active');
//                            $target.addClass('active');
//                        }
                    }
                }
                // Clean up any empty spans in the editable area
//                this._cleanupEmptySpans($editable[0]);
                // Ensure proper cleanup and update
                wysiwyg.odooEditor.historyStep();
//                this._onSelectionChange();
            } catch (error) {
                console.error('Error applying variable:', error);
                alert('An error occurred while applying the variable. Please try again.');
            }
        },
        _onSelectionChange: function() {
             console.log("call after create section======================")
            const wysiwyg = this.options.wysiwyg;
            if (!wysiwyg) return;
            const selection = wysiwyg.odooEditor.document.getSelection();
            if (!selection) return;
            // Update UI to reflect current PHP variable state
            const currentVar = this._hasPhpVariable(selection);
            console.log()
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
            // this.$toggle.off('click');
            $(document).off('click.php_dropdown');
            $(document).off('selectionchange');
            this._super.apply(this, arguments);
        }
    });
});
