/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from '@web/core/utils/hooks';

const { Component, useState, useEffect } = owl;

class SeoSystray extends Component {
    setup() {
        this.websiteService = useService('website');
        this.actionService = useService('action');
        this.menuService = useService('menu');
        this.rpc = useService('rpc');
        this.notification = useService('notification');
        this.websiteContext = useState(this.websiteService.context);

        this.state = useState({
            isLoading: false,
        });

        useEffect((edition) => {
            if (edition) {
                this.state.isLoading = true;
            }
        }, () => [this.websiteContext.edition]);

        useEffect((snippetsLoaded) => {
            if (snippetsLoaded) {
                this.state.isLoading = false;
            }
        }, () => [this.websiteContext.snippetsLoaded]);
    }

    get translatable() {
        return this.websiteService.currentWebsite && this.websiteService.currentWebsite.metadata.translatable;
    }

    get label() {
        return this.env._t("SEO Management");
    }

    async getCurrentPageViewId() {
        const path = window.location.pathname;
        console.log('Current path:', path);  // Debug log

        try {
            const result = await this.rpc('/automated_seo/get_page_view_id', {
                path: path,
            });

            console.log('RPC result:', result);  // Debug log

            if (result.error) {
                throw new Error(result.error);
            }

            return result.view_id;
        } catch (error) {
            console.error('Failed to get page view ID:', error);
            this.notification.add(this.env._t('Could not fetch page information. Please try again.'), {
                type: 'danger',
            });
            return false;
        }
    }

    async redirectPageSeoMenu() {
        try {
            // Get current page view_id
            const viewId = await this.getCurrentPageViewId();

            if (!viewId) {
                throw new Error('Could not find view ID for current page');
            }

            // Find the menu item by xmlid
            const menuItem = this.menuService.getAll().find(
                (item) => item.xmlid === 'automated_seo.menu_automated_view'
            );

            if (!menuItem) {
                throw new Error('Menu item not found');
            }

            // Do the actual navigation
            await this.actionService.doAction({
                type: 'ir.actions.act_window',
                name: 'Page Management',
                res_model: 'automated_seo.view',
                views: [[false, 'form']],
                target: 'current',
                res_id: viewId,
            }, {
                additionalContext: {
                    menu_id: menuItem.id,
                },
            });
        } catch (error) {
            console.error('Navigation error:', error);
            this.notification.add(this.env._t('Error opening SEO management page: ') + error.message, {
                type: 'danger',
            });
        }
    }
}

SeoSystray.template = "automated_seo.SeoSystray";

export const systrayItem = {
    Component: SeoSystray,
    isDisplayed: (env) => env.services.website.currentWebsite.metadata.editable,
};

registry.category("website_systray").add("Seo", systrayItem, { sequence: 6 });