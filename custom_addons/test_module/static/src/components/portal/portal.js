/** @odoo-module **/

import { registry } from '@web/core/registry';
const { Component, useState } = owl;

class OWLPortal extends Component {
    setup() {
        this.state = useState({value: 1});
    }
}

OWLPortal.template = 'test_module.custom_page';

registry.category('actions').add('test_module.OWLPortal', OWLPortal);