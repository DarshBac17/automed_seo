/** @odoo-module **/

import publicWidget from "web.public.widget";

publicWidget.registry.TestModuleOffers = publicWidget.Widget.extend({
    selector: ".offers-dynamic",
    start() {
        let default_offer = this.el.querySelector("#default-offer")
        if (default_offer) {
            default_offer.style.display = 'none';
        }


        let dynamic_offer_row = this.el.querySelector("#dynamic-offer")


        if (dynamic_offer_row){
            console.log("dynamic_offer_row exists")
            this._rpc({
                route: "/offers/",
                params:{}
            }).then(data=>{
                console.log("hello cities")
                let html = ""
                data.forEach(offer=>{
                    let benefit_html = ""
                    offer.benefits.forEach(benefit=>{
                        console.log(benefit)
                        console.log(benefit.benefit_title)
                        benefit_html += `<li>${benefit.benefit_title ? benefit.benefit_title : ""}</li>`
                    })
                    console.log(benefit_html)
                    html += `<div class="col-12">
                                <div class="cont-padding">
                                    <h2>${offer.title ? offer.title: ""}</h2>
                                    <p>${offer.description ? offer.description : ""}</p>
                                </div>
                                <div class="style-check">
                                    <ul>
                                        ${benefit_html}
                                    </ul>
                                    <a href="#form" class="btn btn-outline-primary mt-md">Talk to our Salesforce experts</a>
                                </div>
                            </div>
                        `
                })
                dynamic_offer_row.innerHTML = html
            })
        }
    },
});

export default publicWidget.registry.TestModuleOffers;
