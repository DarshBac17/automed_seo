console.log("============snippet_optioncall================================")
odoo.define('website.snippets.php_variable_text_selector3', function (require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');
    options.registry.PhpVariableTextSelector2 = options.Class.extend({
        events: _.extend({}, options.Class.prototype.events || {}, {
            'click .o_we_php_dropdown_toggle': '_onToggleDropdown',
               'input .o_we_php_search': '_onSearch',
//            'click [data-select-var]': '_onVariableSelect',
//            'click .o_we_php_variables_list we-button': '_onVariableSelect',
            'click [data-select-var]': '_onVariableSelect',
            'mouseup .o_editable': '_onSelectionChange',
        }),
        init: function () {
            this._super.apply(this, arguments);
            this.selectedVariable = null;
            this.isDropdownOpen = false;
            this._bindSelectionChangeEvent()

        },
        start: function () {
            var self = this;

//            return this._super.apply(this, arguments);
            return this._super.apply(this, arguments).then(function() {
                self._createDropdown();
                self._fetchVariables();
                // Handle click outside
                $(document).on('click.php_dropdown', function(e) {
                    if (!$(e.target).closest('.o_we_php_dropdown').length && self.isDropdownOpen) {
                        self._closeDropdown();
                    }
                });

                $(document).on('click.php_dropdown', function(e) {
                    if (!$(e.target).closest('.o_we_php_dropdown').length && self.isDropdownOpen) {
                        self._closeDropdown();
                    }
                });
//            $(document).on('selectionchange', _.debounce(function() {
//                self.1();
//            }, 100));
            });
        },
        _getWysiwygInstance: function () {
    return this.wysiwyg || (this.options && this.options.wysiwyg);
},
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

        _fetchVariables: function(search = '') {
    var self = this;
    return $.get('/php-variables/', {
        offset: this.currentOffset,
        limit: this.limit,
        search: search
    }).then(function(result) {
        if (result.error) {
            console.error('Error fetching variables:', result.error);
            return;
        }
        self.variables = result.variable_names;
        self._updateVariablesList();
//        self._setValue();
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.error('Failed to fetch variables:', textStatus, errorThrown);
    });
},
        _updateVariablesList: function() {
            var self = this;
            this.$variablesList.empty();

            // Add "None" option
            this.$variablesList.append(
                $('<we-button/>', {
                    'data-select-var': 'none',
                    class: 'o_we_destroy_btn'
                }).text('None')
            );

            // Add variables from server
            _.each(this.variables, function(varName) {
                self.$variablesList.append(
                    $('<we-button/>', {
                        'data-select-var': varName,
                        'data-variable-class': varName.toLowerCase()
                    }).text(varName)
                );
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
                this._openDropdown(ev);
            }
        },

        _openDropdown: function (ev) {
            if (!this.$menu.length) {
                console.error('Menu element not found');
                return;
            }
            this.isDropdownOpen = true;
            this.$menu.addClass('show');
            this.$search.val('').focus();
            this._fetchVariables();

        },

        _closeDropdown: function () {
            if (!this.$menu.length) {
                console.error('Menu element not found');
                return;
            }
            this.isDropdownOpen = false;
            this.$menu.removeClass('show');
        },

        _phpVariables: function(){
                   return this._rpc({
                route: '/website/autosave_content',
                params: {
                    html_content: content,
                },
            }).then(() => {
                this.contentChanged = false;
                this._updateIcon('fa-check-circle fa-lg','Auto Saved');
            }).catch((error) => {
                console.error('[Website Editor] Save failed:', error);
                // Keep content changed flag true on error
                this.contentChanged = true;
            });
        },
        _onSearch: _.debounce(function(ev) {
            var searchTerm = $(ev.currentTarget).val().trim();
            this.currentOffset = 0; // Reset offset on new search
            this._fetchVariables(searchTerm);
        }, 300),
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
            span.className = `${variable.class} o_text-php-var-info`;
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
                this._onSelectionChange(ev);
            } catch (error) {
                console.error('Error applying variable:', error);
                alert('An error occurred while applying the variable. Please try again.');
            }
        },
        _onSelectionChange: function(event) {
//            this._closeDropdown()
            console.log("Selection change called");
            const wysiwyg = this.options.wysiwyg;
            if (!wysiwyg) return;

            const selection = wysiwyg.odooEditor.document.getSelection();
            if (!selection) return;

            // Get current PHP variable if any
            const currentVar = this._hasPhpVariable(selection);
            console.log("Current variable:", currentVar);

            // Update dropdown toggle text
            const $toggle = this.$('.o_we_php_dropdown_toggle span');
            if (currentVar && currentVar.name) {
                $toggle.text(currentVar.name);
                $(this).closest('we-select').find('we-toggler').text(currentVar);
            } else {
                $toggle.text('PHP Variables');
            }

            // Update button states
            this.$variablesList.find('[data-select-var]').each(function() {
                const $btn = $(this);
                const varName = $btn.data('select-var');
                const isActive = currentVar && currentVar.name === varName;

                // Handle active states
                if (varName === 'none') {
                    $btn.toggleClass('active', !currentVar);
                } else {
                    $btn.toggleClass('active', isActive);
                }
            });
        },
        _setValue() : function(){
        console.log("Selection change called");
            const wysiwyg = this.options.wysiwyg;
            if (!wysiwyg) return;

            const selection = wysiwyg.odooEditor.document.getSelection();
            if (!selection) return;

            // Get current PHP variable if any
            const currentVar = this._hasPhpVariable(selection);
            console.log("Current variable:", currentVar);

            // Update dropdown toggle text
            const $toggle = this.$('.o_we_php_dropdown_toggle span');
            if (currentVar && currentVar.name) {
                $toggle.text(currentVar.name);
                $(this).closest('we-select').find('we-toggler').text(currentVar.name);
            } else {
                $toggle.text('PHP Variables');
            }

            // Update button states
            this.$variablesList.find('[data-select-var]').each(function() {
                const $btn = $(this);
                const varName = $btn.data('select-var');
                const isActive = currentVar && currentVar.name === varName;

                // Handle active states
                if (varName === 'none') {
                    $btn.toggleClass('active', !currentVar);
                } else {
                    $btn.toggleClass('active', isActive);
                }
            });

        },
        destroy: function () {
            $(document).off('selectionchange');
            this._super.apply(this, arguments);
        }
    });
});