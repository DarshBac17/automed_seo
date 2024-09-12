/** @odoo-module **/

import publicWidget from 'web.public.widget';

const QwebContainer = publicWidget.Widget.extend({
    selector: '.offers-container',
    async willStart(){
        console.log("willstart  widget started successfully");
    },
    start() {
        console.log("QwebContainer widget started successfully");
    },
});

publicWidget.registry.qwebContainer = QwebContainer;

export default QwebContainer;