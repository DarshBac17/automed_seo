odoo.define('automated_seo.reload_on_toggle', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const registry = require('web.field_registry');
    const core = require('web.core');

    // Extend the AbstractField widget to add custom behavior for the boolean field
    const BooleanToggleReload = AbstractField.extend({
        events: _.extend({}, AbstractField.prototype.events, {
            'click .o_field_boolean_toggle': '_onToggleClick',
        }),

        _onToggleClick: function (ev) {
            console.log("js======toggle clicked=======================js");

            // Reload the page after the toggle is clicked
            window.location.reload();
        },
    });

    // Register the new widget
    registry.add('boolean_reload_toggle', BooleanToggleReload);

    return BooleanToggleReload;
});
