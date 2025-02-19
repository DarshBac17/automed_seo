/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _lt } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class CardSelectionField extends Component {
    setup() {
        this.id = `card_selection_${++CardSelectionField.nextId}`;
    }

    get items() {
        return CardSelectionField.getItems(this.props.name, this.props.record);
    }

    get string() {
        return this.props.record.activeFields[this.props.name].string;
    }

    get value() {
        switch (this.props.type) {
            case "selection":
                return this.props.value;
            case "many2one":
                return Array.isArray(this.props.value) ? this.props.value[0] : this.props.value;
            default:
                return null;
        }
    }

    getDescription(item) {
        const options = this.props.record.activeFields[this.props.name].options || {};
        const descriptions = options.descriptions || {};
        return descriptions[item[0]] || "";
    }

    onChange(item) {
        switch (this.props.type) {
            case "selection":
                this.props.update(item[0]);
                break;
            case "many2one":
                this.props.update(item);
                break;
        }
    }
}

CardSelectionField.nextId = 0;
CardSelectionField.template = "automated_seo.CardSelectionField";
CardSelectionField.props = {
    ...standardFieldProps,
    orientation: { type: String, optional: true },
};
CardSelectionField.defaultProps = {
    orientation: "horizontal",
};

CardSelectionField.displayName = _lt("Card Selection");
CardSelectionField.supportedTypes = ["many2one", "selection"];

CardSelectionField.isEmpty = (record, fieldName) => record.data[fieldName] === false;
CardSelectionField.extractProps = ({ attrs }) => {
    return {
        orientation: attrs.options.horizontal ? "horizontal" : "vertical",
    };
};

CardSelectionField.getItems = (fieldName, record) => {
    switch (record.fields[fieldName].type) {
        case "selection":
            return record.fields[fieldName].selection;
        case "many2one": {
            const value = record.preloadedData[fieldName] || [];
            return value.map((item) => [item.id, item.display_name]);
        }
        default:
            return [];
    }
};

registry.category("fields").add("card_selection", CardSelectionField);