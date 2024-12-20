console.log("============sfsfsf==========save===============call")
odoo.define('website.custom.editor', function (require) {
    'use strict';

    const websiteSnippetEditor = require('website.snippet.editor');
    const ajax = require('web.ajax');
    const Wysiwyg = require('web_editor.wysiwyg');

    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
            'click .o_we_website_top_actions button[data-action=save]': '_onSaveRequest',
            'click .o_we_website_top_actions button[data-action=cancel]':'_onDiscardRequest'
        }),

        start: function () {
            this._super.apply(this, arguments);
            console.log("Snippet editor started");
        },

        _onSaveRequest: async function (ev) {
            console.log("Save button clicked");

            try {
                // Prevent default behavior
                ev.preventDefault();
                ev.stopPropagation();

                // Get the wysiwyg instance
                const wysiwyg = this.options.wysiwyg;

                // Save modified images first if any
                if (wysiwyg && wysiwyg.saveModifiedImages) {
                    await wysiwyg.saveModifiedImages();
                }

                // Call the original save function
                await this.trigger_up('request_save', {
                    reloadEditor: true,
                    onSuccess: () => {
                        console.log("Save completed successfully");
                        // Wait a bit before reloading to ensure save is complete
                        setTimeout(() => {
                            console.log("Reloading page...");
                            window.location.reload(true);
                        }, 500);
                    },
                    onFailure: () => {
                        console.error("Save operation failed");
                    },
                });

            } catch (error) {
                console.error("Save failed:", error);
            }
        },
        _onDiscardRequest: async function (ev) {
            try {
                await this.trigger_up('request_cancel');

            } catch (error) {
                console.error("Discard failed:", error);
            }
        }
    });

    return {
        SnippetsMenu: aSnippetMenu,
    };
});
//odoo.define('website.custom.editor', function (require) {
//    'use strict';
//
//    var core = require('web.core');
//    var websiteSnippetEditor = require('website.snippet.editor');
//    var ajax = require('web.ajax');
//    var Wysiwyg = require('web_editor.wysiwyg');
//
//    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
//        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
//            'click .o_we_website_top_actions button[data-action=save]': '_onSaveRequest'
//        }),
//
//        start: function () {
//            this._super.apply(this, arguments);
//            console.log("Snippet editor started");
//        },
//
//        _onSaveRequest: function (ev) {
//            console.log("Save button clicked");
//
//            // Get the wysiwyg instance
//            const wysiwyg = this.options.wysiwyg;
//
//            if (wysiwyg && wysiwyg.saveModifiedImages) {
//                // First save any modified images
//                wysiwyg.saveModifiedImages().then(() => {
//                    // Then save the content
//                    return this._savePage();
//                }).then(() => {
//                    console.log("Save completed, reloading...");
//                    window.location.reload();
//                }).catch((error) => {
//                    console.error("Error during save:", error);
//                });
//            } else {
//                // If no wysiwyg instance, just save the page
//                this._savePage().then(() => {
//                    console.log("Save completed, reloading...");
//                    window.location.reload();
//                }).catch((error) => {
//                    console.error("Error during save:", error);
//                });
//            }
//        },
//
//        _savePage: function () {
//            return new Promise((resolve, reject) => {
//                ajax.jsonRpc('/web_editor/save_grid', 'call', {
//                    'path': window.location.pathname,
//                }).then(() => {
//                    resolve();
//                }).catch((error) => {
//                    reject(error);
//                });
//            });
//        }
//    });
//
//    return {
//        SnippetsMenu: aSnippetMenu,
//    };
//});
/*odoo.define('website.custom.editor', function (require) {
    'use strict';

    const websiteSnippetEditor = require('website.snippet.editor');
    const ajax = require('web.ajax');
    const Wysiwyg = require('web_editor.wysiwyg');

    const aSnippetMenu = websiteSnippetEditor.SnippetsMenu.include({
        events: _.extend({}, websiteSnippetEditor.SnippetsMenu.prototype.events, {
            'click .o_we_website_top_actions button[data-action=save]': '_onSaveRequest'
        }),

        start: function () {
            this._super.apply(this, arguments);
            console.log("Snippet editor started");
        },

                _onSaveRequest: async function (ev) {
            console.log("Save button clicked");

            try {
            Promise.resolve(this._super.apply(this, arguments)).then(() => {
                console.log("Save completed, reloading...");
                 setTimeout(() => {
                            console.log("Reloading page...");
                            window.location.reload(true);
                        }, 500);
            });
//                await this._super.apply(this, arguments);
//                console.log("Save completed, reloading...");

            } catch (error) {
                console.error("Save failed:", error);
            }
        },


//        _onSaveRequest: function (ev) {
//            console.log("Save button clicked");
//                Promise.resolve(this._super.apply(this, arguments)).then(() => {
//                console.log("Save completed, reloading...");
//                 window.location.reload();
//            });
////                window.location = window.location.href;
//
////            var self = this;
////            console.log("Save button clicked");
////            return this._super.apply(this, arguments).then(function () {
////                console.log("Save completed, reloading...");
////                window.location = window.location.href;
////                return true;
////            });
//        },

    });

    return {
        SnippetsMenu: aSnippetMenu,
    };
});*/
//odoo.define('website.custom.editor', function (require) {
//    'use strict';
//
//    var WysiwygMultizone = require('web_editor.wysiwyg.multizone');
//
//    WysiwygMultizone.include({
//        /**
//         * @override
//         */
//        save: function (reload) {
//            console.log("inside============================================")
//            var self = this;
//            return this._super.apply(this, arguments).then(function () {
//                if (!reload) {
//                    window.location.reload();
//                }
//                return true;
//            });
//        },
//    });
//});
//odoo.define('website.custom.editor', function (require) {
//    'use strict';
//
//    var WebsiteEditor = require('website.editor');
//    var websiteNavbarData = require('website.navbar');
//
//    WebsiteEditor.include({
//        /**
//         * @override
//         */
//        _saveRequest: function () {
//            console.log("======================saveinside===============call")
//            return this._super.apply(this, arguments).then(() => {
//                // Reload the page after successful save
//                window.location.reload();
//            });
//        },
//    });
//
//    websiteNavbarData.WebsiteNavbar.include({
//        /**
//         * @override
//         */
//        _onSaveClick: function (ev) {
//            console.log("======================save inside 2===============call")
//            var self = this;
//            return this._super.apply(this, arguments).then(function () {
//                // Reload the page after successful save
//                window.location.reload();
//            });
//        },
//    });
//});