odoo.define('automated_seo.angular_stories_static_template', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.AngularStoriesSlider = publicWidget.Widget.extend({
        selector: '.overflow-hidden',
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._initSliders();
            });
        },
        _initSliders: function () {
            this.$('.single-item-slider').slick({
                arrows: false,
                dots: true,
            });

            this.$('.center-slide').slick({
                dots: true,
                infinite: false,
                arrows: false,
                slidesToShow: 3,
                slidesToScroll: 3,
                responsive: [
                    {
                        breakpoint: 991,
                        settings: {
                            slidesToShow: 2,
                            slidesToScroll: 1
                        }
                    },
                    {
                        breakpoint: 767,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1
                        }
                    }
                ]
            });

            this.$('.slick-track > div').not('footer .slick-track > div').css({
                'margin-right': '10px',
                'margin-left': '10px'
            });
        },
    });
});