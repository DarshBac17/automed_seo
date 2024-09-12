/** @odoo-module **/

import publicWidget from 'web.public.widget';

const DynamicSnippetDemo = publicWidget.Widget.extend({
    selector: '.s_dynamic_snippet',
    start: async function () {
        console.log("startcall===================================");
        const data = await this._rpc({
            route: '/qweb_demo/get_data',
            params: {},
        });
        console.log("=======================")
        console.log(data)
        console.log("=======================")
        const $template = $(this.env.qweb.render('qweb_demo.dynamic_snippet_template', {records: data}));
        this.$('.dynamic_snippet_template').html($template);
    },
});

publicWidget.registry.dynamicSnippetDemo = DynamicSnippetDemo;

export default DynamicSnippetDemo;

