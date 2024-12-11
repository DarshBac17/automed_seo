odoo.define('website.snippets.p_tag_constraints', function (require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var core = require('web.core');
    const Wysiwyg = require('web_editor.wysiwyg');

    options.registry.LengthConstraintSelector = options.Class.extend({
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
            console.log('Handling change in constrained element');

            // Get the max length from the attribute
            const maxLength = parseInt(element.getAttribute('data-max-length') || '100', 10);

            // Function to calculate text length while preserving HTML structure, ignoring whitespace
            const calculateTextLength = (node) => {
                if (node.nodeType === Node.TEXT_NODE) {
                    return node.textContent.replace(/\s+/g, '').length;
                }

                if (node.nodeType === Node.ELEMENT_NODE) {
                    return Array.from(node.childNodes)
                        .reduce((total, childNode) => total + calculateTextLength(childNode), 0);
                }

                return 0;
            };

            // Function to truncate content while preserving HTML structure
            const truncateContent = (node, remainingLength) => {
                if (remainingLength <= 0) {
                    return null;
                }

                if (node.nodeType === Node.TEXT_NODE) {
                    const textWithoutWhitespace = node.textContent.replace(/\s+/g, '');

                    if (textWithoutWhitespace.length <= remainingLength) {
                        return {
                            node: node.cloneNode(false),
                            remainingLength: remainingLength - textWithoutWhitespace.length
                        };
                    }

                    const truncatedNode = node.cloneNode(false);
                    let truncatedText = '';
                    let currentLength = 0;

                    for (let char of node.textContent) {
                        if (char.match(/\s/)) {
                            truncatedText += char;
                        } else {
                            if (currentLength < remainingLength) {
                                truncatedText += char;
                                currentLength++;
                            } else {
                                break;
                            }
                        }
                    }

                    truncatedNode.textContent = truncatedText;
                    return {
                        node: truncatedNode,
                        remainingLength: Math.max(0, remainingLength - currentLength)
                    };
                }

                if (node.nodeType === Node.ELEMENT_NODE) {
                    const truncatedElement = node.cloneNode(false);
                    let currentRemainingLength = remainingLength;

                    for (let childNode of node.childNodes) {
                        const result = truncateContent(childNode, currentRemainingLength);

                        if (result) {
                            truncatedElement.appendChild(result.node);
                            currentRemainingLength = result.remainingLength;
                        }

                        if (currentRemainingLength <= 0) {
                            break;
                        }
                    }

                    return {
                        node: truncatedElement,
                        remainingLength: currentRemainingLength
                    };
                }

                return null;
            };

            // Calculate current content length (ignoring whitespace)
            let currentLength = calculateTextLength(element);

            // If content exceeds max length
            if (currentLength > maxLength) {
                console.warn(`Content exceeds maximum length of ${maxLength} characters`);
                alert(`The content you've entered exceeds the maximum length of ${maxLength} characters (excluding spaces). Please shorten your text.`);

                // Get the Wysiwyg instance
                const wysiwyg = this._getWysiwygInstance();

                // Undo the last input operation


                while (currentLength > maxLength) {
                    console.log("+")
                    if (wysiwyg && wysiwyg.odooEditor) {
                        wysiwyg.odooEditor.historyUndo();
                    }
                    currentLength = calculateTextLength(element);
                }



                // Optionally, you can also truncate and set the content
                // const truncationResult = truncateContent(element, maxLength);

                // if (truncationResult) {
                //     element.innerHTML = truncationResult.node.innerHTML;

                //     // Move the cursor to the end of the text
                //     const selection = this._getCurrentSelection();
                //     if (selection && selection.rangeCount) {
                //         const range = selection.getRangeAt(0);
                //         range.selectNodeContents(element);
                //         range.collapse(false);
                //         selection.removeAllRanges();
                //         selection.addRange(range);
                //     }
                // }
            }
        },
    });
});

