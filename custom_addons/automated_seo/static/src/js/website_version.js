//odoo.define('automated_seo.snippet.editor', function (require) {
//    'use strict';
//
//    const websiteSnippetEditor = require('website.snippet.editor');
//    const Dialog = require('web.Dialog');
//    const core = require('web.core');
//    const QWeb = core.qweb;
//    const _t = core._t;
//
//    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
//        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
//            'click .o_we_website_top_actions button[data-action=version]': '_onVersionClick'
//        }),
//
//        /**
//         * Initialize the modal when the editor is started
//         */
//        start: function () {
//            return this._super.apply(this, arguments).then(() => {
//                // Load the modal template
//                const modalHtml = QWeb.render('website_version_modal');
//                this.$modal = $(modalHtml);
//                $('body').append(this.$modal);
//                this._initializeVersionModal();
//            });
//        },
//
//        /**
//         * Initialize the version modal and its events
//         */
//        _initializeVersionModal: function () {
//            console.log("Initializing version modal");
//
//            if (!this.$modal || this.$modal.length === 0) {
//                console.error('Modal element not found in DOM');
//                return;
//            }
//
//            console.log("Modal element found:", this.$modal);
//
//            // Initialize Bootstrap modal
//            try {
//                this.versionModal = new bootstrap.Modal(this.$modal[0], {
//                    keyboard: true,
//                    backdrop: true
//                });
//
//                this.$saveBtn = this.$modal.find('#saveVersion');
//                this.$nameInput = this.$modal.find('#versionName');
//                this.$descriptionInput = this.$modal.find('#versionDescription');
//
//                // Bind save button click event
//                this.$saveBtn.off('click').on('click', () => this._saveVersion());
//
//                // Clear form when modal is hidden
//                this.$modal.off('hidden.bs.modal').on('hidden.bs.modal', () => {
//                    this.$nameInput.val('');
//                    this.$descriptionInput.val('');
//                });
//
//                console.log("Modal initialized successfully");
//            } catch (error) {
//                console.error('Error initializing modal:', error);
//            }
//        },
//
//        /**
//         * Handle version button click
//         * @param {Event} ev
//         */
//        _onVersionClick: function (ev) {
//            console.log("Version click handler called");
//            ev.preventDefault();
//
//            if (this.versionModal) {
//                console.log("Showing modal");
//                this.versionModal.show();
//            } else {
//                console.error('Bootstrap Modal instance not found');
//                // Try to reinitialize
//                this._initializeVersionModal();
//                if (this.versionModal) {
//                    this.versionModal.show();
//                }
//            }
//        },
//
//        /**
//         * Save the version
//         */
//        _saveVersion: function () {
//            const name = this.$nameInput.val().trim();
//            if (!name) {
//                this.displayNotification({
//                    type: 'warning',
//                    title: _t('Warning'),
//                    message: _t('Version name is required'),
//                });
//                return;
//            }
//
//            // Get current page ID from the URL
//            const pageId = this._getPageId();
//            if (!pageId) {
//                this.displayNotification({
//                    type: 'error',
//                    title: _t('Error'),
//                    message: _t('Could not determine page ID'),
//                });
//                return;
//            }
//
//            this._rpc({
//                route: '/website/version/save',
//                params: {
//                    name: name,
//                    description: this.$descriptionInput.val(),
//                    page_id: pageId,
//                },
//            }).then((result) => {
//                if (result.error) {
//                    this.displayNotification({
//                        type: 'error',
//                        title: _t('Error'),
//                        message: result.error,
//                    });
//                } else {
//                    this.displayNotification({
//                        type: 'success',
//                        title: _t('Success'),
//                        message: _t('Version saved successfully'),
//                    });
//                    this.versionModal.hide();
//                }
//            }).guardedCatch(() => {
//                this.displayNotification({
//                    type: 'error',
//                    title: _t('Error'),
//                    message: _t('Failed to save version'),
//                });
//            });
//        },
//
//        /**
//         * Get the current page ID from the URL
//         * @returns {string|null}
//         */
//        _getPageId: function () {
//            const match = window.location.pathname.match(/\/page\/(\d+)/);
//            return match ? match[1] : null;
//        },
//
//        /**
//         * Clean up when destroying the editor
//         */
//        destroy: function () {
//            if (this.$modal) {
//                this.$modal.remove();
//            }
//            this._super.apply(this, arguments);
//        },
//    });
//
//    return {
//        SnippetsMenu: aSnippetMenu,
//    };
//});
odoo.define('automated_seo.snippet.editor', function (require) {
    'use strict';

    const websiteSnippetEditor = require('website.snippet.editor');
    const ajax = require('web.ajax');

    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
            'click .o_we_website_top_actions button[data-action=version]': '_onVersionClick'
        }),

        start: function () {
            this._super.apply(this, arguments);
            console.log("Snippet editor started");

            // Inject modal HTML if it's not already in the DOM
            if (!$('#versionModal').length) {
                this._appendModalToDOM();
            }

            this.$modal = $('#versionModal');  // Reassign modal after appending it
        },

        // Handle version button click to show modal
        _onVersionClick: function (ev) {
            ev.preventDefault();
            console.log("Version modal opening...");
            this.$modal.modal('show');  // Show the modal

            // Fetch page ID when the modal is opened
//            this._fetchPageId();
        },

        // Function to fetch the page ID from the server
//        _fetchPageId: function () {
//            const self = this;
//            ajax.jsonRpc('/website/get_page_id', 'call', {}).then(function (result) {
//                if (result.page_id) {
//                    self.pageId = result.page_id;  // Store the fetched page ID
//                } else {
//                    alert('Could not retrieve page ID.');
//                }
//            }).catch(function (error) {
//                console.error('Error fetching page ID:', error);
//                alert('Error fetching page ID.');
//            });
//        },

        // Function to handle saving the version
        _saveVersion: function () {
            const self = this;

            const name = this.$modal.find('#versionName').val();  // Access the value from modal input field
            const description = this.$modal.find('#versionDescription').val();  // Access the description

            console.log('version name ==================', name);  // Log the value to check if it's being accessed
            console.log('version description ============', description);

            if (!name) {
                alert('Version name is required');
                return;
            }

            // Call the backend with the version data
            ajax.jsonRpc('/website/version/save', 'call', {
                'name': name,
                'description': description,
                'page_id': window.location.href,  // Use the fetched page ID
            }).then(function (result) {
                if (result.error) {
                    alert(result.error);
                } else {
                    alert('Version saved successfully!');
                    self._closeModal();  // Close modal after saving
                }
            });
        },

        // Function to handle closing the modal
        _closeModal: function () {
            this.$modal.modal('hide');  // Hide the modal
            this.$modal.find('#versionName').val('');  // Clear inputs
            this.$modal.find('#versionDescription').val('');
        },

        // Inject modal HTML into the DOM
        _appendModalToDOM: function () {
            const modalHTML = `
                <div id="versionModal" class="modal fade" tabindex="-1" role="dialog" aria-labelledby="versionModalLabel" aria-hidden="true">
                  <div class="modal-dialog" role="document">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title" id="versionModalLabel">Save Page Version</h5>
                        <button type="button" class="close" aria-label="Close" id="closeModalButton">
                          <span aria-hidden="true">&times;</span>
                        </button>
                      </div>
                      <div class="modal-body">
                        <div class="form-group">
                          <label for="versionName">Version Name</label>
                          <input type="text" class="form-control" id="versionName" placeholder="Enter version name">
                        </div>
                        <div class="form-group">
                          <label for="versionDescription">Version Description</label>
                          <textarea class="form-control" id="versionDescription" rows="3" placeholder="Enter version description"></textarea>
                        </div>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="closeModalButtonFooter">Close</button>
                        <button type="button" class="btn btn-primary" id="saveVersionButton">Save Version</button>
                      </div>
                    </div>
                  </div>
                </div>
            `;

            // Append modal to the body
            $('body').append(modalHTML);
            console.log("Modal HTML injected");

            // Reassign modal elements after injection
            this.$modal = $('#versionModal');

            // Bind the click event for closing the modal (both buttons)
            this.$modal.find('#closeModalButton, #closeModalButtonFooter').on('click', this._closeModal.bind(this));

            // Bind the click event for saving the version
            this.$modal.find('#saveVersionButton').on('click', this._saveVersion.bind(this));
        },
    });

    return {
        SnippetsMenu: aSnippetMenu,
    };
});





//odoo.define('automated_seo.snippet.editor', function (require) {
//    'use strict';
//
//    const websiteSnippetEditor = require('website.snippet.editor');
//    const ajax = require('web.ajax');
//
//    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
//        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
//            'click .o_we_website_top_actions button[data-action=version]': '_onVersionClick',
//            'click #saveVersionButton': '_onSaveVersion'
//        }),
//
//        start: function () {
//            this._super.apply(this, arguments);
//            console.log("Snippet editor started");
//
//            // Inject modal HTML if it's not already in the DOM
//            if (!$('#versionModal').length) {
//                this._appendModalToDOM();
//            }
//
//            this.$modal = $('#versionModal');  // Make sure this is reassigned after appending modal
//        },
//
//        _onVersionClick: function (ev) {
//            ev.preventDefault();
//            console.log("Version modal opening...");  // Ensure this logs in the console
//            this.$modal.modal('show');  // Ensure modal is correctly assigned
//        },
//
//        _onSaveVersion: function (ev) {
//            ev.preventDefault();
//            const self = this;
//
//            const name = this.$('#versionName').val();
//            const description = this.$('#versionDescription').val();
//
//            if (!name) {
//                alert('Version name is required');
//                return;
//            }
//
//            ajax.jsonRpc('/website/version/save', 'call', {
//                'name': name,
//                'description': description,
//                'page_id': this._getPageId(),
//            }).then(function (result) {
//                if (result.error) {
//                    alert(result.error);
//                } else {
//                    alert('Version saved successfully!');
//                    self.$modal.modal('hide');
//                    self.$('#versionName').val('');
//                    self.$('#versionDescription').val('');
//                }
//            });
//        },
//
//        _getPageId: function () {
//            return $('html').data('website-page-id');
//        },
//
//        _appendModalToDOM: function () {
//            const modalHTML = `
//                <div id="versionModal" class="modal fade" tabindex="-1" role="dialog" aria-labelledby="versionModalLabel" aria-hidden="true">
//                  <div class="modal-dialog" role="document">
//                    <div class="modal-content">
//                      <div class="modal-header">
//                        <h5 class="modal-title" id="versionModalLabel">Save Page Version</h5>
//                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
//                          <span aria-hidden="true">&times;</span>
//                        </button>
//                      </div>
//                      <div class="modal-body">
//                        <div class="form-group">
//                          <label for="versionName">Version Name</label>
//                          <input type="text" class="form-control" id="versionName" placeholder="Enter version name">
//                        </div>
//                        <div class="form-group">
//                          <label for="versionDescription">Version Description</label>
//                          <textarea class="form-control" id="versionDescription" rows="3" placeholder="Enter version description"></textarea>
//                        </div>
//                      </div>
//                      <div class="modal-footer">
//                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
//                        <button type="button" class="btn btn-primary" id="saveVersionButton">Save Version</button>
//                      </div>
//                    </div>
//                  </div>
//                </div>
//            `;
//            $('body').append(modalHTML);
//            console.log("Modal HTML injected");
//            this.$modal = $('#versionModal');  // Reassign the modal after injection
//        },
//    });
//
//    return {
//        SnippetsMenu: aSnippetMenu,
//    };
//});


//});
//$(document).ready(function() {
//    console.log("DOM fully loaded");
//
//    // Use event delegation since the button might be loaded dynamically
//    $(document).on('click', '#version-btn', function(e) {
//        console.log("Button is clicked!");
//        e.preventDefault();
//    });
//
//    // For debugging - check if button exists in intervals
//    setTimeout(function() {
//        var button = $('#version-btn');
//        console.log("Button check after timeout:", button.length);
//    }, 1000);
//
//    console.log("after===============");
//});
//console.log("Loading version button script...");
//
//$(document).ready(function() {
//    console.log("DOM ready triggered");
//
//    // Debug: Log all buttons on the page
//    console.log("All buttons found:", $('button').length);
//    $('button').each(function() {
//        console.log("Button:", this.id, this.className);
//    });
//
//    // Multiple timing checks
//    checkButton();
//
//    // Monitor DOM changes for button appearance
//    const observer = new MutationObserver(function(mutations) {
//        mutations.forEach(function(mutation) {
//            if (mutation.addedNodes.length) {
//                checkButton();
//            }
//        });
//    });
//
//    observer.observe(document.body, {
//        childList: true,
//        subtree: true
//    });
//});
//
//function checkButton() {
//    const button = $('#version-btn');
//    console.log("Button check:", {
//        found: button.length > 0,
//        timestamp: new Date().toISOString(),
//        buttonObject: button
//    });
//
//    if (button.length > 0) {
//        console.log("Button found! Adding click handler...");
//        button.off('click').on('click', function(e) {
//            console.log("Button clicked!");
//            e.preventDefault();
//        });
//    }
//}
//button.addEventListener("click", versionclick);
//function versionclick() {
//        console.log("=========================version")
//    }
//odoo.define('website.version', function (require) {
//    'use strict';
//
//    var core = require('web.core');
//    var Dialog = require('web.Dialog');
//    var publicWidget = require('web.public.widget');
//    var utils = require('web.utils');
//    var ajax = require('web.ajax');
//    var _t = core._t;
//
//    var VersionDialog = Dialog.extend({
//        template: 'website.version_dialog',
//        events: _.extend({}, Dialog.prototype.events, {
//            'click .btn-primary': '_onSave',
//        }),
//
//        init: function (parent, options) {
//            options = _.extend({
//                title: _t("Save Version"),
//                buttons: [
//                    {
//                        text: _t("Save"),
//                        classes: 'btn-primary',
//                        click: this._onSave.bind(this),
//                    },
//                    {
//                        text: _t("Discard"),
//                        close: true,
//                    },
//                ],
//                size: 'medium',
//            }, options || {});
//            this._super(parent, options);
//        },
//
//        _onSave: function () {
//            var name = this.$('#versionName').val();
//            var description = this.$('#versionDescription').val();
//
//            if (!name) {
//                this.displayNotification({
//                    type: 'danger',
//                    title: _t("Error"),
//                    message: _t("Version name is required"),
//                });
//                return;
//            }
//
//            this.trigger_up('version_save', {
//                name: name,
//                description: description,
//            });
//            this.close();
//        },
//    });
//
//    var WebsiteVersionButton = publicWidget.Widget.extend({
//        selector: '#version-btn',
//        events: {
//            'click': '_onVersionClick',
//        },
//
//        /**
//         * @override
//         */
//        start: function () {
//            var def = this._super.apply(this, arguments);
//            this.pageId = $('html').data('website-page-id');
//            return def;
//        },
//
//        //--------------------------------------------------------------------------
//        // Handlers
//        //--------------------------------------------------------------------------
//
//        /**
//         * @private
//         * @param {MouseEvent} ev
//         */
//        _onVersionClick: function (ev) {
//            ev.preventDefault();
//            var self = this;
//
//            var dialog = new VersionDialog(this, {});
//            dialog.on('version_save', this, function (ev) {
//                return ajax.jsonRpc('/website/version/save', 'call', {
//                    name: ev.data.name,
//                    description: ev.data.description,
//                    page_id: self.pageId,
//                }).then(function (result) {
//                    if (result.error) {
//                        self.displayNotification({
//                            type: 'danger',
//                            title: _t("Error"),
//                            message: result.error,
//                        });
//                    } else {
//                        self.displayNotification({
//                            type: 'success',
//                            title: _t("Success"),
//                            message: _t("Version saved successfully!"),
//                        });
//                    }
//                });
//            });
//            dialog.open();
//        },
//    });
//
//    publicWidget.registry.WebsiteVersion = WebsiteVersionButton;
//
//    return {
//        VersionDialog: VersionDialog,
//        WebsiteVersionButton: WebsiteVersionButton,
//    };
//});
//document.addEventListener('DOMContentLoaded', function() {
//    console.log("call====================================");
//    // Initialize the version functionality
//    const VersionManager = {
//        init: function() {
//            this.versionBtn = document.getElementById('version-btn');
//            this.modal = document.getElementById('versionModal');
//            this.saveVersionBtn = document.getElementById('saveVersion');
//            this.versionNameInput = document.getElementById('versionName');
//            this.versionDescriptionInput = document.getElementById('versionDescription');
//
//            this.bindEvents();
//        },
//
//        bindEvents: function() {
//            // Version button click handler
//            this.versionBtn.addEventListener('click', (ev) => {
//                ev.preventDefault();
//                console.log("versioncall====================================");
//                this.showModal();
//            });
//
//            // Save version button click handler
//            this.saveVersionBtn.addEventListener('click', (ev) => {
//                ev.preventDefault();
//                this.saveVersion();
//            });
//        },
//
//        showModal: function() {
//            // Using Bootstrap modal
//            $(this.modal).modal('show');
//        },
//
//        hideModal: function() {
//            $(this.modal).modal('hide');
//        },
//
//        getPageId: function() {
//            return document.documentElement.dataset.websitePageId;
//        },
//
//        saveVersion: function() {
//            const name = this.versionNameInput.value;
//            const description = this.versionDescriptionInput.value;
//
//            if (!name) {
//                alert('Version name is required');
//                return;
//            }
//
//            // Make the AJAX request
//            fetch('/website/version/save', {
//                method: 'POST',
//                headers: {
//                    'Content-Type': 'application/json',
//                },
//                body: JSON.stringify({
//                    name: name,
//                    description: description,
//                    page_id: this.getPageId()
//                })
//            })
//            .then(response => response.json())
//            .then(result => {
//                if (result.error) {
//                    alert(result.error);
//                } else {
//                    this.hideModal();
//                    this.versionNameInput.value = '';
//                    this.versionDescriptionInput.value = '';
//                    alert('Version saved successfully!');
//                }
//            })
//            .catch(error => {
//                console.error('Error:', error);
//                alert('An error occurred while saving the version');
//            });
//        }
//    };
//
//    // Initialize the version manager
//    VersionManager.init();
//});