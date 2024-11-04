odoo.define('automated_seo.snippet.editor', function (require) {
    'use strict';

    const websiteSnippetEditor = require('website.snippet.editor');
    const ajax = require('web.ajax');
    const Wysiwyg = require('web_editor.wysiwyg');

    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
            'click .o_we_website_top_actions button[data-action=version]': '_onVersionClick',

        }),

        start: function () {
            this._super.apply(this, arguments);
            console.log("Snippet editor started");

            if (!$('#versionModal').length) {
                this._appendModalToDOM();
            }

            this.$modal = $('#versionModal');
        },
        _onVersionClick: function (ev) {
            ev.preventDefault();
            console.log("Version modal opening...");
            this.$modal.modal('show');
        },

        _getPageContent: function() {
            // Get the current editor instance
            const editor = this.options.wysiwyg;
            if (!editor) {
                console.error("Editor not found");
                throw new Error('Editor instance not found');
            }

            // Try to get the editable content area
            let $editableContent = $('.o_editable[data-oe-model="ir.ui.view"]');

            if (!$editableContent.length) {
                // If not found, try to get content from the editor directly
                $editableContent = editor.$editable;
            }

            if (!$editableContent.length) {
                // Last resort: try to find the main content area
                $editableContent = $('#wrapwrap .oe_structure.oe_empty, #wrapwrap .oe_structure').first();
            }

            if ($editableContent.length) {
                console.log("Found editable content");

                // Create a clone to avoid modifying the actual content
                const $clone = $editableContent.clone();

                // Remove any editor-specific classes and data attributes
                $clone.find('*').each(function() {
                    const $el = $(this);
                    // Keep the essential structure but remove editor-specific attributes
                    $el.removeAttr('contenteditable')
                       .removeAttr('data-oe-model')
                       .removeAttr('data-oe-id')
                       .removeAttr('data-oe-field')
                       .removeAttr('data-oe-xpath')
                       .removeAttr('data-oe-source-id');
                });

                // Get the cleaned HTML content
                const content = $clone.html();

                // Verify we have meaningful content
                if (!content || content.trim().length === 0) {
                    throw new Error('Empty content found');
                }

                console.log("Content preview:", content.substring(0, 100));
                return content;
            }

            throw new Error('No editable content found on the page');
        },

        _saveVersion: function (ev) {
            const self = this;
            const name = this.$modal.find('#versionName').val();
            const description = this.$modal.find('#versionDescription').val();

            if (!name) {
                alert('Version name is required');
                return;
            }

            try {
                const content = this._getPageContent();

                // Debug log to check content
                console.log("=== Content Being Saved ===");
                console.log(content);
                console.log("==========================");

                ajax.jsonRpc('/website/version/save', 'call', {
                    'name': name,
                    'description': description,
                    'page_id': window.location.href,
                    'current_arch': content
                })
                .then((result) => {
                    if (result && result.error) {
                        throw new Error(result.error);
                    }
                    self._closeModal();
                    alert('Version saved successfully!');
                })
                .catch((error) => {
                    console.error("Error during save operation:", error);
                    alert(error.message || 'An error occurred while saving the version');
                });
            } catch (error) {
                console.error("Error getting page content:", error);
                alert('Could not find the page content. Please ensure you are on an editable page.');
            }
        },

        _closeModal: function () {
            this.$modal.modal('hide');
            this.$modal.find('#versionName').val('');
            this.$modal.find('#versionDescription').val('');
        },

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

            $('body').append(modalHTML);
            this.$modal = $('#versionModal');
            this.$modal.find('#closeModalButton, #closeModalButtonFooter').on('click', this._closeModal.bind(this));
            this.$modal.find('#saveVersionButton').on('click', this._saveVersion.bind(this));
        },
    });

    return {
        SnippetsMenu: aSnippetMenu,
    };
});

/*odoo.define('automated_seo.snippet.editor', function (require) {
    'use strict';

    const websiteSnippetEditor = require('website.snippet.editor');
    const ajax = require('web.ajax');
    const Wysiwyg = require('web_editor.wysiwyg');

    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
            'click .o_we_website_top_actions button[data-action=version]': '_onVersionClick'
        }),

        start: function () {
            this._super.apply(this, arguments);
            console.log("Snippet editor started");

            if (!$('#versionModal').length) {
                this._appendModalToDOM();
            }

            this.$modal = $('#versionModal');
        },

        _onVersionClick: function (ev) {
            ev.preventDefault();
            console.log("Version modal opening...");
            this.$modal.modal('show');
        },



        _saveVersion: function (ev) {


            const self = this;
            const name = this.$modal.find('#versionName').val();
            const description = this.$modal.find('#versionDescription').val();

            if (!name) {
                alert('Version name is required');
                return;
            }

    // Use jQuery to select <main> and check if it exists
            const $main = $('main');
                if ($main.length) {
                    // Optionally select a specific child div inside <main>, if required
                    const $contentDiv = $main.find('div'); // Adjust selector as needed
                    if ($contentDiv.length) {
                        const content = $contentDiv.html(); // Get the HTML content safely
                        console.log("==========================");
                        console.log(content);
                        console.log("==========================");

                        ajax.jsonRpc('/website/version/save', 'call', {
                            'name': name,
                            'description': description,
                            'page_id': window.location.href,
                            'current_arch': content
                        })
                        .then((result) => {
                            if (result && result.error) {
                                throw new Error(result.error);
                            }

                            // Close the version modal
                            self._closeModal();

                            alert('Version saved successfully!');
                        })
                        .catch((error) => {
                            console.error("Error during save operation:", error);
                            alert(error.message || 'An error occurred while saving the version');
                        });
                    } else {
                        console.error("No <div> found inside <main>");
                        alert('Could not find the content to save.');
                    }
                } else {
                    console.error("<main> element not found");
                    alert('Could not find the main content.');
                }
            },


        _closeModal: function () {
            this.$modal.modal('hide');
            this.$modal.find('#versionName').val('');
            this.$modal.find('#versionDescription').val('');
        },

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

            $('body').append(modalHTML);
            console.log("Modal HTML injected");

            this.$modal = $('#versionModal');
            this.$modal.find('#closeModalButton, #closeModalButtonFooter').on('click', this._closeModal.bind(this));
            this.$modal.find('#saveVersionButton').on('click', this._saveVersion.bind(this));
        },
    });

    return {
        SnippetsMenu: aSnippetMenu,
    };
});*/
/*odoo.define('automated_seo.snippet.editor', function (require) {
    'use strict';

    const core = require('web.core');
    const WebsiteEditor = require('website.editor');
    const ajax = require('web.ajax');
    const _t = core._t;

    WebsiteEditor.include({
        events: _.extend({}, WebsiteEditor.prototype.events, {
            'click button[data-action="version"]': '_onSaveVersionClick',
        }),

        *//**
         * @override
         *//*
        start: async function () {
            await this._super(...arguments);
            this._initializeVersioning();
        },

        *//**
         * Initialize versioning functionality
         * @private
         *//*
        _initializeVersioning: function () {
            if (!$('#versionModal').length) {
                this._appendVersionModalToDOM();
            }
            this.$versionModal = $('#versionModal');
        },

        *//**
         * Click handler for version button
         * @private
         * @param {Event} ev
         *//*
        _onSaveVersionClick: function (ev) {
            ev.preventDefault();
            if (this.$versionModal) {
                this.$versionModal.modal('show');
            }
        },

        *//**
         * Get current content from editor
         * @private
         * @returns {Promise<string>}
         *//*
        _getEditableContent: async function () {
            try {
                // Get the main editable content
                const $mainContent = this.$el.find('#wrapwrap #wrap').first();

                if (!$mainContent.length) {
                    console.error('Main content area not found');
                    return false;
                }

                // Clone to avoid modifying original
                const $clone = $mainContent.clone();

                // Clean up editor artifacts
                $clone.find('.o_snippet_editor, .o_handle, .o_we_overlay').remove();
                $clone.find('.o_editable').removeClass('o_editable o_dirty');
                $clone.find('[contenteditable]').removeAttr('contenteditable');
                $clone.find('[data-oe-model]').removeAttr('data-oe-model data-oe-id data-oe-field data-oe-type data-oe-expression');

                return $clone.html();
            } catch (err) {
                console.error('Error getting editable content:', err);
                return false;
            }
        },

        *//**
         * Save the current version
         * @private
         *//*
        _saveVersion: async function (ev) {


            const name = this.$versionModal.find('#versionName').val();
            const description = this.$versionModal.find('#versionDescription').val();

            if (!name) {
                this.displayNotification({
                    type: 'warning',
                    title: _t('Warning'),
                    message: _t('Version name is required'),
                });
                return;
            }

            try {
                const content = await this._getEditableContent();
                if (!content) {
                    throw new Error(_t('Could not get page content'));
                }

                const result = await ajax.jsonRpc('/website/version/save', 'call', {
                    name: name,
                    description: description,
                    page_id: window.location.href,
                    current_arch: content,
                });

                if (result.error) {
                    throw new Error(result.error);
                }

                this.$versionModal.modal('hide');
                this.displayNotification({
                    type: 'success',
                    title: _t('Success'),
                    message: _t('Version saved successfully!'),
                });
            } catch (error) {
                console.error('Version save error:', error);
                this.displayNotification({
                    type: 'danger',
                    title: _t('Error'),
                    message: error.message || _t('Failed to save version'),
                });
            }
        },

        *//**
         * Append version modal to DOM
         * @private
         *//*
        _appendVersionModalToDOM: function () {
            const modalHTML = `
                <div id="versionModal" class="modal fade" tabindex="-1" role="dialog">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Save Page Version</h5>
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                <div class="form-group">
                                    <label for="versionName">Version Name</label>
                                    <input type="text" class="form-control" id="versionName" required>
                                </div>
                                <div class="form-group">
                                    <label for="versionDescription">Description</label>
                                    <textarea class="form-control" id="versionDescription" rows="3"></textarea>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" id="saveVersionBtn">Save Version</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            $(document.body).append(modalHTML);

            // Bind save button click
            $('#saveVersionButton').on('click', () => this._saveVersion());
        },
    });
});*/
/*odoo.define('automated_seo.snippet.editor', function (require) {
    'use strict';

    const websiteSnippetEditor = require('website.snippet.editor');
    const ajax = require('web.ajax');
    const Wysiwyg = require('web_editor.wysiwyg');

    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
            'click .o_we_website_top_actions button[data-action=version]': '_onVersionClick'
        }),

        start: function () {
            this._super.apply(this, arguments);
            console.log("Snippet editor started");

            if (!$('#versionModal').length) {
                this._appendModalToDOM();
            }

            this.$modal = $('#versionModal');
        },

        _onVersionClick: function (ev) {
            ev.preventDefault();
            console.log("Version modal opening...");
            this.$modal.modal('show');
        },

        // Get current editor content without saving
        _getCurrentContent: function() {
            return new Promise((resolve) => {
                try {
                    // Get the main editable area
                    const $editable = $('[data-oe-model="ir.ui.view"]').first();

                    if (!$editable.length) {
                        console.error('No editable content found');
                        resolve(false);
                        return;
                    }

                    // Clone the content to avoid modifying the actual editor
                    const $contentClone = $editable.clone();

                    // Clean up editor-specific elements and attributes
                    $contentClone.find('.o_snippet_editor, .o_handle').remove();
                    $contentClone.find('[data-oe-model]').removeAttr('data-oe-model');
                    $contentClone.find('[data-oe-id]').removeAttr('data-oe-id');
                    $contentClone.find('[data-oe-field]').removeAttr('data-oe-field');
                    $contentClone.find('[data-oe-type]').removeAttr('data-oe-type');
                    $contentClone.find('[data-oe-expression]').removeAttr('data-oe-expression');
                    $contentClone.find('.o_editable').removeClass('o_editable');
                    $contentClone.find('[contenteditable]').removeAttr('contenteditable');
                    $contentClone.find('.o_dirty').removeClass('o_dirty');

                    // Alternative method to get content if needed
                    let content;
                    if (this.options && this.options.wysiwyg) {
                        content = this.options.wysiwyg.getValue();
                    } else {
                        content = $contentClone.html();
                    }

                    resolve(content);
                } catch (error) {
                    console.error('Error getting current content:', error);
                    resolve(false);
                }
            });
        },

        _saveVersion: function () {
            const self = this;
            const name = this.$modal.find('#versionName').val();
            const description = this.$modal.find('#versionDescription').val();

            if (!name) {
                alert('Version name is required');
                return;
            }

            // Get current content without saving
            this._getCurrentContent().then((content) => {
                if (!content) {
                    alert('Error getting current page content');
                    return;
                }

                return ajax.jsonRpc('/website/version/save', 'call', {
                    'name': name,
                    'description': description,
                    'page_id': window.location.href,
                    'current_arch': content
                });
            })
            .then((result) => {
                if (result && result.error) {
                    throw new Error(result.error);
                }

                // Close the version modal
                self._closeModal();

                alert('Version saved successfully!');
            })
            .catch((error) => {
                console.error("Error during save operation:", error);
                alert(error.message || 'An error occurred while saving the version');
            });
        },

        _closeModal: function () {
            this.$modal.modal('hide');
            this.$modal.find('#versionName').val('');
            this.$modal.find('#versionDescription').val('');
        },

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

            $('body').append(modalHTML);
            console.log("Modal HTML injected");

            this.$modal = $('#versionModal');
            this.$modal.find('#closeModalButton, #closeModalButtonFooter').on('click', this._closeModal.bind(this));
            this.$modal.find('#saveVersionButton').on('click', this._saveVersion.bind(this));
        },
    });

    return {
        SnippetsMenu: aSnippetMenu,
    };
});*/
/*odoo.define('automated_seo.snippet.editor', function (require) {
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

            if (!$('#versionModal').length) {
                this._appendModalToDOM();
            }

            this.$modal = $('#versionModal');
        },

        _onVersionClick: function (ev) {
            ev.preventDefault();
            console.log("Version modal opening...");
            this.$modal.modal('show');
        },

        // Function to ensure the website editor save is complete
        _ensureWebsiteEditorSave: function() {
            const self = this;
            return new Promise((resolve, reject) => {
                try {
                    // Get the save and close buttons
                    const $saveButton = self.$('.o_we_website_top_actions button[data-action=save]');

                    if (!$saveButton.length) {
                        console.warn('Save button not found');
                        reject(new Error('Save button not found'));
                        return;
                    }

                    // Function to check if save is needed
                    const needsSave = !$saveButton.prop('disabled');
                    console.log('Needs save:', needsSave);

                    if (!needsSave) {
                        console.log('No save needed, proceeding...');
                        resolve();
                        return;
                    }

                    // Set up event listeners for save completion
                    const saveCompletionHandler = function() {
                        console.log('Save completion detected');
                        $(document).off('website_save_done.editor', saveCompletionHandler);
                        resolve();
                    };

                    $(document).on('website_save_done.editor', saveCompletionHandler);

                    // Trigger the save
                    console.log('Triggering save button click');
                    $saveButton.trigger('click');

                    // Backup timeout in case the event doesn't fire
                    setTimeout(() => {
                        $(document).off('website_save_done.editor', saveCompletionHandler);
                        console.log('Save timeout reached, proceeding...');
                        resolve();
                    }, 5000);

                } catch (error) {
                    console.error('Error in _ensureWebsiteEditorSave:', error);
                    reject(error);
                }
            });
        },

        _saveVersion: function () {
            const self = this;
            const name = this.$modal.find('#versionName').val();
            const description = this.$modal.find('#versionDescription').val();

            console.log('version name ==================', name);
            console.log('version description ============', description);

            if (!name) {
                alert('Version name is required');
                return;
            }

            // First ensure the website editor is saved
            self._ensureWebsiteEditorSave()
                .then(() => {
                    console.log("Website save completed, proceeding with version save...");
                    return ajax.jsonRpc('/website/version/save', 'call', {
                        'name': name,
                        'description': description,
                        'page_id': window.location.href,
                    });
                })
                .then((result) => {
                    if (result.error) {
                        throw new Error(result.error);
                    }

                    // Close the version modal
                    self._closeModal();

                    // Find the close button
                    const $closeButton = self.$('.o_we_website_top_actions button[data-action=close]');

                    // Show success message
                    alert('Version saved successfully!');

                    // Ensure the edit tab is closed
                    if ($closeButton.length) {
                        console.log('Triggering close button');
                        $closeButton.trigger('click');
                    } else {
                        console.warn('Close button not found');
                        // Fallback: try to reload the page
                        window.location.reload();
                    }
                })
                .catch((error) => {
                    console.error("Error during save operation:", error);
                    alert(error.message || 'An error occurred while saving the version');
                });
        },

        _closeModal: function () {
            this.$modal.modal('hide');
            this.$modal.find('#versionName').val('');
            this.$modal.find('#versionDescription').val('');
        },

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

            $('body').append(modalHTML);
            console.log("Modal HTML injected");

            this.$modal = $('#versionModal');
            this.$modal.find('#closeModalButton, #closeModalButtonFooter').on('click', this._closeModal.bind(this));
            this.$modal.find('#saveVersionButton').on('click', this._saveVersion.bind(this));
        },
    });

    return {
        SnippetsMenu: aSnippetMenu,
    };
});*/
/*
in odoo i make versioning system in which is there any way by which when i get current page arch content without saving it.

this is my model

class WebsitePageVersion(models.Model):
    _name = 'website.page.version'
    _description = 'Website Page Version'
    _order = 'create_date desc'

    name = fields.Char('Version Name', required=True)
    description = fields.Text('Description')
    view_id =  fields.Many2one('automated_seo.view', string='View', required=True)
    page_id = fields.Many2one('website.page', string='Website Page', required=True)
    view_arch = fields.Text('Saved View Architecture', required=True)
    parse_html = fields.Text(string="Parse HTML")
    parse_html_binary = fields.Binary(string="Parsed HTML File", attachment=True)
    parse_html_filename = fields.Char(string="Parsed HTML Filename")
    user_id = fields.Many2one('res.users', string='Created by')
    status = fields.Boolean('Status',default=False)

    def action_version(self):

        id =self.env.context.get('id', 'Unknown')
        current_version  = self.env['website.page.version'].search([('status','=',True)],limit=1)
        if current_version:
            current_version.status = False
        active_version  = self.env['website.page.version'].search([('id','=',id)],limit=1)
        if active_version:
            active_version.status = True
            view = self.env['automated_seo.view'].search([('id','=',active_version.view_id.id)],limit=1)
            # view.parse_html = active_version.parse_html
            view.page_id.arch_db = active_version.view_arch
            view.parse_html_filename = active_version.parse_html_filename if active_version.parse_html_filename else "first"

this is controller
class WebsiteVersion(http.Controller):
    @http.route(['/website/version/save'], type='json', auth="user", website=True)
    def save_version(self, **kwargs):
        name = kwargs.get('name')
        description = kwargs.get('description')
        page_id = kwargs.get('page_id')
        url = page_id.split('/')[-1]
        page = request.env['website.page'].search([('url', '=', f'/{url}')], limit=1)
        view = request.env['automated_seo.view'].search([('website_page_id', '=', page.id)], limit=1)


        # page_id = page.id
        if not name or not page_id:
            return {'error': 'Missing required fields'}

        # page = request.env['website.page'].browse(int(page_id))
        if not page.exists():
            return {'error': 'Page not found'}

        version = request.env['website.page.version'].create({
            'name': name,
            'description': description,
            'page_id': page.id,
            'view_arch': page.view_id.arch,
            'view_id':view.id,
            'user_id': request.env.user.id
        })

        return {
            'success': True,
            'version_id': version.id
        }
this is js
*/

/*
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
        init: function () {
            this._super.apply(this, arguments);
            this._isSaveRequestCompleted = false;  // Flag to track when save is complete
        },

        // Modified _onSaveRequest to set a flag after completion
        _onSaveRequest: function (ev) {
            const data = ev.data || {};
            if (ev.target === this && !data._toMutex) {
                return;
            }
            delete data._toMutex;
            ev.stopPropagation();
            this._buttonClick(async (after) => {
                await this.postSnippetDropPromise;
                return this._execWithLoadingEffect(async () => {
                    console.log("ir.ui.view saved");

                    // Set onFailure callback to trigger after completion
                    const oldOnFailure = data.onFailure;
                    data.onFailure = () => {
                        if (oldOnFailure) {
                            oldOnFailure();
                        }
                        after();
                    };
                    this.trigger_up('request_save', data);

                    // Set the completion flag
                    this._isSaveRequestCompleted = true;
                }, true);
            }, this.$el[0].querySelector('button[data-action=save]'));
        },

        // _saveVersion function with dependency on _onSaveRequest completion
        _saveVersion: function () {
            const self = this;
            const name = this.$modal.find('#versionName').val();
            const description = this.$modal.find('#versionDescription').val();

            if (!name) {
                alert('Version name is required');
                return;
            }

            // Step 1: Trigger Save Click
            this._triggerSaveClick(() => {
                // Check periodically if _onSaveRequest has completed
                const checkSaveCompletion = setInterval(() => {
                    if (this._isSaveRequestCompleted) {
                        clearInterval(checkSaveCompletion);  // Stop checking

                        // Reset the flag for future uses
                        this._isSaveRequestCompleted = false;

                        // Step 2: Call the backend with the version data after Save completes
                        ajax.jsonRpc('/website/version/save', 'call', {
                            'name': name,
                            'description': description,
                            'page_id': window.location.href,
                        }).then(function (result) {
                            if (result.error) {
                                console.log("got error!");
                                alert(result.error);
                            } else {
                                console.log("saved successfully!");
                                alert('Version saved successfully!');
                                self._closeModal();  // Close modal after saving
                            }
                        }).catch(function (error) {
                            console.error("Error occurred during RPC:", error);
                            alert("An error occurred while saving the version.");
                        });
                    }
                }, 100);  // Check every 100ms
            });
        },

        // Helper function to trigger save button click and wait for completion
        _triggerSaveClick: function (callback) {
            this.$('.o_we_website_top_actions button[data-action=save]').trigger('click');
            callback();
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
});*/
