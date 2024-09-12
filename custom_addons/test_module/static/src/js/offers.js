
/** @odoo-module **/

import publicWidget from "web.public.widget";

publicWidget.registry.TestModuleOffers = publicWidget.Widget.extend({
    selector: ".offers-dynamic",

    start() {
        console.log("Widget started");
        let default_offer = this.el.querySelector("#default-offer");
        if (default_offer) {
             default_offer.style.display = 'none';
        }
        this._onSaveOfferClick();
    },

    _loadOffers() {
        let dynamic_offer = this.el.querySelector("#dynamic-offer");

        if (dynamic_offer) {
            this._rpc({
                route: "/offers/",
                params: {}
            }).then(data => {
                let html = this._buildOfferHTML(data);
                dynamic_offer.innerHTML = html;
            });
        }
    },

    _buildOfferHTML(data) {
        let html = "";
        data.forEach(offer => {
            let benefits_html = this._buildBenefitsHTML(offer.benefits);
            html += `
                <div class="col-12">
                    <div class="cont-padding" id="offer_${offer.id || ''}">
                        <div style="display:none" id='offer_id'>${offer.id || ''}</div>
                        <h2>${offer.title || ''}</h2>
                        <p>${offer.description || ''}</p>
                    </div>
                    <div class="style-check">
                        <ul>${benefits_html}</ul>
                        <a href="#form" class="btn btn-outline-primary mt-md">Talk to our Salesforce experts</a>
                    </div>
                </div>`;
        });
        return html;
    },

    _buildBenefitsHTML(benefits) {
        let benefits_html = "";
        benefits.forEach(benefit => {
            benefits_html += `<li>${benefit || ""}</li>`;
        });
        return benefits_html;
    },

    _onSaveOfferClick() {
        console.log("Save offer click triggered");
        let dynamic_offer_row = this.el.querySelector("#dynamic-offer");
        let offer_id = dynamic_offer_row.querySelector("offer_id");
        if (dynamic_offer_row && offer_id) {
            let title = dynamic_offer_row.querySelector("h2").textContent;
            let description = dynamic_offer_row.querySelector("p").textContent;
            let benefits = Array.from(dynamic_offer_row.querySelectorAll("ul li")).map(li => li.textContent);
            let offer_id = 1;
            this._saveOfferChanges(offer_id,title, description, benefits);
        }
    },

    _saveOfferChanges(offer_id,title, description, benefits) {
        console.log("Saving offer data...");
        this._rpc({
            route: '/offers/save',
            params: {
                title: title,
                description: description,
                benefits: benefits,
                id:offer_id,
            },
        }).then(() => {
             this._loadOffers();  // Reload offers after saving
        });
    },
//    _onUpdateOfferClick() {
//        console.log("update offer click triggered");
//        let dynamic_offer_row = this.el.querySelector("#dynamic-offer");
//
//        if (dynamic_offer_row) {
//            let title = dynamic_offer_row.querySelector("h2").textContent;
//            let description = dynamic_offer_row.querySelector("p").textContent;
//            let offerId = dynamic_offer_row.querySelector("#offer_id").textContent;
//            let benefits = Array.from(dynamic_offer_row.querySelectorAll("ul li")).map(li => li.textContent);
//
//            this._saveOfferChanges(offerId, title, description, benefits);
//        }
//    },
//
//    _saveUpdateChanges(offerId, title, description, benefits) {
//        console.log("Saving offer data...");
//        this._rpc({
//            route: '/offers/save',
//            params: {
//                id: offerId,
//                title: title,
//                description: description,
//                benefits: benefits,
//            },
//        }).then(() => {
//             this._loadOffers();  // Reload offers after saving
//        });
//    },

});

export default publicWidget.registry.TestModuleOffers;
