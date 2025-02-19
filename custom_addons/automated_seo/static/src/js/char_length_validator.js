/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useInputField } from "@web/views/fields/input_field_hook";
const { Component, useState,useRef } = owl;
export class CharLengthValidator extends Component {
    static template = 'CharLengthValidator';

    setup() {
        this.state = useState({
            currentLength: this.props.value ? this.props.value.length : 0,
            isOverLimit: false
        });

        this.input = useRef('input');
        useInputField({ getValue: () => this.props.value || "" });
    }

    _onInput(ev) {
        const value = ev.target.value;
        this.state.currentLength = value.length;
        this.state.isOverLimit = value.length > 60;
        this.props.update(value);
    }
}
export class DescriptionLengthValidator extends Component {
    static template = 'DescriptionLengthValidator';

    setup() {
        this.state = useState({
            currentLength: this.props.value ? this.props.value.length : 0,
            isOverLimit: false
        });

        this.input = useRef('input');
        useInputField({ getValue: () => this.props.value || "" });
    }

    _onInput(ev) {
        const value = ev.target.value;
        this.state.currentLength = value.length;
        this.state.isOverLimit = value.length > 160;
        this.props.update(value);
    }
}

registry.category("fields").add("description_length_validator", DescriptionLengthValidator);
registry.category("fields").add("char_length_validator", CharLengthValidator);

