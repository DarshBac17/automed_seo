odoo.define('website.snippets.php_variable_text_selector3', function (require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');
    options.registry.PhpVariableTextSelector = options.Class.extend({
        events: _.extend({}, options.Class.prototype.events || {}, {
            'click .o_we_php_dropdown_toggle': '_onToggleDropdown',
            'input .o_we_php_search': '_onSearch',
            'click [data-select-var]': '_onVariableSelect',
            'mouseup .o_editable': '_onSelectionChange',
            'click .o_au_php_var_type': '_onConstButtonClick',
            'click [data-select-class="o_au_php_var_type"]': '_onConstButtonClick',
        }),
        init: function () {
            this._super.apply(this, arguments);
            this.selectedVariable = null;
            this.isDropdownOpen = false;
            this.currentOffset = 0;
            this.limit = 5;
            this.isLoading = false;
            this.hasMore = true; 
            this._bindSelectionChangeEvent()
            this.isConstVar = false;

        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {

                self._createDropdown();
                $(document).on('click.php_dropdown', function (e) {
                    if (!$(e.target).closest('.o_we_php_dropdown').length && self.isDropdownOpen) {
                        self._closeDropdown();
                    }
                });

                var $constButton = self.$el.find('[data-select-class="o_au_php_var_type"]');
                self._originalConstVarState = $constButton.hasClass('active');

                self._preventExternalStateChange();


            });
        },
        _getWysiwygInstance: function () {
            return this.wysiwyg || (this.options && this.options.wysiwyg);
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
        _fetchVariables: function(search = '') {
            var self = this;
            
            return $.get('/php-variables/', {
                offset: this.currentOffset,
                limit: this.limit,
                search: search
            }).then((result) => {  // Use arrow function to preserve 'this'
                if (result.error) {
                    return;
                }
                
                // Update offset and variables
                self.variables = result.variable_names;
                self.currentOffset += result.variable_names.length;
                self.hasMore = result.variable_names.length >= self.limit;
                
                // Update UI
                self._updateVariablesList();
                self._setValue();
                
            }).fail((jqXHR, textStatus, errorThrown) => {
            });
        },

        _onConstButtonClick: function (ev) {
            const $button = $(ev.currentTarget);

            // Prevent other widgets from changing the state
            ev.stopPropagation();
            ev.preventDefault();

            // Toggle the state
            $button.toggleClass('active');
            this.isConstVar = $button.hasClass('active');

            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg) return;

            const selection = this._getCurrentSelection();
            if (!selection) return;

            const currentVar = this._hasPhpVariable(selection);
            if (currentVar && currentVar.element) {
                // Update the constant attribute on the existing span
                $(currentVar.element).attr('data-php-const-var', this.isConstVar ? '1' : '0');
                wysiwyg.odooEditor.historyStep();
            }
        },



        _getCurrentSelection: function () {
            const wysiwyg = this._getWysiwygInstance();
            if (!wysiwyg || !wysiwyg.odooEditor) {
                return null;
            }

            return wysiwyg.odooEditor.document.getSelection();
        },
        _updateVariablesList: function() {
            
            this.$variablesList.empty();
        
            // Add "None" option
            this.$variablesList.append(
                $('<we-button/>', {
                    'data-select-var': 'none',
                    class: 'o_we_destroy_btn'
                }).text('None')
            );
        
            // Add variables from server
            _.each(this.variables, (varName) => {
                this.$variablesList.append(
                    $('<we-button/>', {
                        'data-select-var': varName,
                        'data-variable-class': varName.toLowerCase()
                    }).text(varName)
                );
            });
        },
        // Update the _createDropdown function
        _createDropdown: function () {
            // Create checkbox
            const $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');
//             $('<div/>', {
//                class: 'mt-2'
//            }).append(
//                $('<label/>', {
//                    class: 'o_we_checkbox_wrapper'
//                }).append(
//                    $('<input/>', {
//                        type: 'checkbox',
//                        class: 'o_au_php_var_type',
//                        'data-no-preview': 'true'
//                    }),
//                    $('<span/>', {
//                        class: 'o_we_checkbox_label'
//                    }).text('Constant var?')
//                )
//            );
            
            // Create dropdown
            this.$dropdown = $('<div/>', {
                class: 'o_we_php_dropdown'
            });
        
            this.$toggle = $('<div/>', {
                class: 'o_we_php_dropdown_toggle'
            }).append(
                $('<span/>').text('PHP Variables'),
                $('<i/>', { class: 'fa fa-chevron-down' })
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
        
            this.$loadingIndicator = $('<div/>', {
                class: 'o_we_php_loading_indicator',
                text: 'Loading...'
            }).css({
                'text-align': 'center',
                'padding': '8px',
                'display': 'none'
            });
        
            // Build structure
            this.$menu.append(
                $('<div/>', { class: 'o_we_php_search_wrapper' }).append(this.$search),
                this.$variablesList,
                this.$loadingIndicator
            );
        
            // Add scroll handler
            this.$variablesList.on('scroll', _.throttle(() => {
                this._onScroll();
            }, 200));
        
            // Assemble dropdown
            this.$dropdown
                .append(this.$toggle)
                .append(this.$menu);
        
            // Add to DOM
//            this.$el.append(this.$constButton);
            this.$el.append(this.$dropdown);
        },

        // Add scroll handler
        _onScroll: function() {
            
            if (!this.$variablesList || !this.$variablesList[0]) {
                return;
            }
        
            const $list = this.$variablesList;
            const scrollTop = $list.scrollTop();
            const scrollHeight = $list[0].scrollHeight;
            const clientHeight = $list.height();
            const threshold = 30;
        
            if (!this.isLoading && this.hasMore && (scrollHeight - scrollTop - clientHeight) < threshold) {
                this._loadMoreVariables();
            }
        },


        _loadMoreVariables: function() {
            if (this.isLoading || !this.hasMore) {
                return;
            }
            this.isLoading = true;
            this.$loadingIndicator.show();
        
            $.get('/php-variables/', {
                offset: this.currentOffset,
                limit: this.limit,
                search: this.$search.val().trim()
            }).then((response) => {
                
                if (response.variable_names && response.variable_names.length) {
                    this._appendVariables(response.variable_names);
                     this.currentOffset += response.variable_names.length;
                    this.hasMore = response.variable_names.length >= this.limit;
                } else {
                    this.hasMore = false;
                }
            }).fail((error) => {
            }).always(() => {
                this.isLoading = false;
                this.$loadingIndicator.hide();
            });
        },

        _appendVariables: function (variables) {
            variables.forEach(varName => {
                this.$variablesList.append(
                    $('<we-button/>', {
                        'data-select-var': varName,
                        'data-variable-class': varName.toLowerCase()
                    }).text(varName)
                );
            });
        },

        _onToggleDropdown: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if (this.isDropdownOpen) {
                this._closeDropdown();
            } else {
                this._openDropdown(ev);
            }
        },

        _openDropdown: function (ev) {
            if (!this.$menu.length) {
                return;
            }

            this.isDropdownOpen = true;
            this.$menu.addClass('show');
            this.$search.val('').focus();
            this._fetchVariables();

        },

        _closeDropdown: function () {
            if (!this.$menu.length) {
                return;
            }
            this.isDropdownOpen = false;
            this.currentOffset = 0;
            this.limit = 5;
            this.isLoading = false;
            this.hasMore = true;
            this.$menu.removeClass('show');
        },
        _onSearch: _.debounce(function (ev) {
            var searchTerm = $(ev.currentTarget).val().trim();

            // Reset pagination
            this.currentOffset = 0;
            this.hasMore = true;
            this.isLoading = false;

            // Clear existing list
            this.$variablesList.empty();
            this.$variablesList.scrollTop(0);

            // Show loading
            this.$loadingIndicator.show();

            // Fetch new results
            this._fetchVariables(searchTerm).then(() => {
                this.$loadingIndicator.hide();

                // Show no results message if needed
                if (!this.$variablesList.children().length) {
                    this.$variablesList.append(
                        $('<div/>', {
                            class: 'o_we_php_no_results',
                            text: 'No variables found'
                        })
                    );
                }
            });
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
        _cleanupEmptySpans: function (element) {
            const emptySpans = $(element).find('span[data-php-var]:empty');
            emptySpans.each(function () {
                $(this).remove();
            });
        },

        /**
         * Helper to check if selection has a specific PHP variable
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
         * Helper to get all text content from a node
         */
        _getAllTextContent: function (node) {
            return node.textContent || node.innerText || '';
        },
        /**
         * Remove PHP variable formatting from the selected text
         */
        _removePhpVariable: function (selection) {
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
        _applyPhpVariable: function (selection, variable) {
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
            const $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');
            span.setAttribute('data-php-const-var', $constButton.hasClass('active') ? '1' : '0');
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
        _onVariableSelect: function (ev) {
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
                            class: 'o_au_php_var'
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
                alert('An error occurred while applying the variable. Please try again.');
            }
        },
        _onSelectionChange: function (event) {
            this._closeDropdown();

            const wysiwyg = this.options.wysiwyg;
            if (!wysiwyg) return;

            const selection = wysiwyg.odooEditor.document.getSelection();
            if (!selection) return;

            // Get current PHP variable if any
            const currentVar = this._hasPhpVariable(selection);
            const $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');
            // Update dropdown toggle text
            //            const $toggle = this.$('.o_we_php_dropdown_toggle span');
            if (currentVar && currentVar.name) {
                this.$toggle.text(currentVar.name);
                $(this).closest('we-select').find('we-toggler').text(currentVar);
                $constButton.toggleClass('active', currentVar.isConst);
                this.isConstVar = currentVar.isConst;
            } else {
                this.$toggle.text('PHP Variables');
                $constButton.removeClass('active');
                this.isConstVar = false;

            }

            // Update button states
            this.$variablesList.find('[data-select-var]').each(function () {
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
        _setValue: function () {
            const wysiwyg = this.options.wysiwyg;
            if (!wysiwyg) return;

            const selection = wysiwyg.odooEditor.document.getSelection();
            if (!selection) return;

            // Get current PHP variable if any
            const currentVar = this._hasPhpVariable(selection);
            const $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');

            if (currentVar && currentVar.name) {
                this.$toggle.text(currentVar.name);
                $(this).closest('we-select').find('we-toggler').text(currentVar.name);
                 $constButton.toggleClass('active', currentVar.isConst);
                this.isConstVar = currentVar.isConst;
            } else {
                this.$toggle.text('PHP Variables');
                     $constButton.removeClass('active');

            }

            // Update button states
            this.$variablesList.find('[data-select-var]').each(function () {
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
            var $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');

            // Ensure the button is in its original state when the snippet is destroyed
            $constButton.toggleClass('active', this._originalConstVarState);

            this._super.apply(this, arguments);
        },


        // Add a method to prevent external state changes
        _preventExternalStateChange: function () {
            var $constButton = this.$el.find('[data-select-class="o_au_php_var_type"]');

            // Implement a mutation observer to revert unwanted changes
            this._stateObserver = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        // Check if the state has been changed unexpectedly
                        const currentState = $constButton.hasClass('active');
                        if (currentState !== this.isConstVar) {
                            // Revert to the known state
                            $constButton.toggleClass('active', this.isConstVar);
                        }
                    }
                });
            });

            // Start observing the button for class changes
            this._stateObserver.observe($constButton[0], {
                attributes: true,
                attributeFilter: ['class']
            });
        },

    });
});