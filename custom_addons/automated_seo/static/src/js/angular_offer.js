odoo.define('automated_seo.angular_offer_snippet_options', function (require) {
'use strict';

const options = require('web_editor.snippets.options');

const angularOfferSnippetOptions = options.Class.extend({
/**
* This type defines the template infos retrieved from
* @see /website/snippet/filter_templates
* Used for
* @see this.dynamicFilterTemplates
* @typedef {Object} Template - definition of a dynamic snippet template
* @Property {string} key - key of the template
* @Property {string} numOfEl - number of elements on desktop
* @Property {string} numOfElSm - number of elements on mobile
* @Property {string} numOfElFetch - number of elements to fetch
* @Property {string} rowPerSlide - number of rows per slide
* @Property {string} arrowPosition - position of the arrows
* @Property {string} extraClasses - classes to be added to the


*/
/**
 * @override
 */
init: function () {
    this._super.apply(this, arguments);
    console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
},
/**
 * @override
 */
async willStart() {
    const _super = this._super.bind(this);
    console.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    return _super(...arguments);
},
/**
 *
 * @override
 */
async onBuilt() {
    console.log("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");
//    this._initNavMenu();
//    this._setSideStickyPosition();
//    this._initScrollFunctionality();
//    this._initMenuIcon();
//    this._initTabs();
//    this._initMobileTabContent();
//    this._initSidebarAndAccordion();
//    this._initSlickSliders();
    this._initMobileElementRearrangement();
//    this._initFormElementWrapping();
//    this._initPriceMasking();
//    this._initPriceToggle();
//    this._initHeightAdjustment();
//    this._initModalClose();
//
//    return this._super.apply(this, arguments);
},




//--------------------------------------------------------------------------
// Public
//--------------------------------------------------------------------------

/**
 * See from updateUI in s_website_form
 *
 * @override
 */
async updateUI() {

},

 _initNavMenu: function() {
    this.$('.nav-menu').click(function() {
        $('.nav-menu').removeClass('active');
        $(this).addClass('active');
        $('.dropdown-menu').removeClass('flex').addClass('hidden');
        $(this).find('.dropdown-menu').addClass('flex').removeClass('hidden');
    });
},

_setSideStickyPosition: function() {
    var headerHeight = this.$('header').outerHeight(true) + 100;
    this.$('.side-sticky').css({ top: headerHeight });
},

_maskPrice: function(price) {
    return price.substring(0, 2) + '*'.repeat(price.length - 2);
},

_getOriginalPrice: function(element) {
    return element.data('original-price');
},

_adjustHeights: function(selector) {
    var currentDiv, maxHeight = 0, currentTop = 0, elements = [];
    this.$(selector).each(function() {
        var $this = $(this);
        $this.height('auto');
        var top = $this.position().top;
        if (currentTop !== top) {
            elements.forEach(function(el) { el.height(maxHeight); });
            elements = [];
            currentTop = top;
            maxHeight = $this.height();
            elements.push($this);
        } else {
            elements.push($this);
            maxHeight = Math.max(maxHeight, $this.height());
        }
    });
    elements.forEach(function(el) { el.height(maxHeight); });
},

_initScrollFunctionality: function() {
    var self = this;
    $(window).scroll(function() {
        if ($(this).scrollTop() > 0) {
            self.$('.nav-menu').removeClass('active');
            $(this).addClass('active');
            self.$('.dropdown-menu').removeClass('flex').addClass('hidden');
            $(this).find('.dropdown-menu').addClass('flex').removeClass('hidden');
            self.$('.sidebar_right_outer').slideUp();
            self.$('.menu-icon').removeClass('active');
        } else {
            self.$('.nav-menu').click(function() {
                self.$('.nav-menu').removeClass('active');
                $(this).addClass('active');
                self.$('.dropdown-menu').removeClass('flex').addClass('hidden');
                $(this).find('.dropdown-menu').addClass('flex').removeClass('hidden');
            });
        }
    });
},

_initMenuIcon: function() {
    this.$('.menu-icon').click(function() {
        $('.sidebar_right_outer').slideToggle();
        $(this).toggleClass('active');
    });
},

_initTabs: function() {
    this.$('.tabs .tab-header li, .tabs .tab-header .tab-head').click(function() {
        var $this = $(this);
        var index = $this.index();
        $this.addClass('active').siblings().removeClass('active');
        $this.closest('.tabs').find('.tab-content .tab-pane').eq(index).addClass('active').siblings().removeClass('active');
    });
},

_initMobileTabContent: function() {
    if (window.matchMedia('(max-width: 767px)').matches) {
        this.$('.tabbibg-sec .tab-header .tab-head').each(function(index) {
            $(this).append($('.tabbibg-sec .tab-content .tab-pane').eq(index));
        });
    }
},

_initSidebarAndAccordion: function() {
    this.$('.sidebar_right_outer, .accordion-item').find('.sub-side, .sub-side-two, .accordian-text').slideUp();
    this.$('.sidebar_right_outer, .accordion-item').find('.sub-side.active, .accordian-text.active').slideDown();

    this.$('.sidebar_right_outer .res-submenu, .sidebar_right_outer .res-submenu, .accordion-item .faq-heading').on('click', function() {
        var $parent = $(this).parent();
        $parent.siblings().removeClass('active').find('.menu_parent, .sub-side, .res-submenu, .faq-heading').removeClass('active').end().find('.sub-side, .accordian-text').slideUp();
        $parent.find('.sub-side, .accordian-text').slideToggle();
        $parent.find('.menu_parent, .sub-side, .res-submenu, .accordian-text, .faq-heading').toggleClass('active');
        $parent.toggleClass('active');
    });

    this.$('.res-submenu-two').on('click', function() {
        var $parent = $(this).parent();
        $parent.siblings().removeClass('active').find('.sub-side, .res-submenu-two').removeClass('active').end().find('.sub-side-two').slideUp();
        $parent.find('.sub-side-two').slideToggle();
        $parent.find('.sub-side-two, .res-submenu-two').toggleClass('active');
        $parent.toggleClass('active');
    });
},

_initSlickSliders: function() {
    this.$('.footer-address').slick({
        arrows: true,
        dots: false,
        slidesToShow: 3,
        slidesToScroll: 2,
        responsive: [
            { breakpoint: 767, settings: { slidesToShow: 1, slidesToScroll: 1 } },
            { breakpoint: 992, settings: { slidesToShow: 2, slidesToScroll: 1 } }
        ]
    });

    this.$('.footer-slider').slick({
        infinite: false,
        customPaging: function(slider, i) {
            return '<button class="tab">' + $(slider.$slides[i]).attr('title') + '</button>';
        },
        arrows: true,
        dots: true,
        responsive: [{ breakpoint: 767, settings: { arrows: false } }]
    });
},

_initMobileElementRearrangement: function() {
    console.log("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5");
    console.log(window.matchMedia('(max-width: 767px)').matches);
    console.log("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5");
    if (window.matchMedia('(max-width: 767px)').matches) {
        console.log("inside if================================");
        this.$('.resp-btn').insertAfter('.resp-btn-outer');
        this.$('.resp-btn-two').insertAfter('.resp-btn-outer-two');
        this.$('.faq-head').insertAfter('.faq-head-outer');
    }
},

_initFormElementWrapping: function() {
    console.log("_initforelementwrappingcall================================");
    this.$el.find('.shadow-form .boxed p.mb-0').each(function() {
        $(this).next('button').addBack().wrapAll('<div class="flex items-center justify-center"></div>');
    });
},

_initPriceMasking: function() {
    var self = this;
    this.$('.shadow-form').each(function() {
        var $this = $(this);
        var $price = $this.find('.text-h1');
        var priceText = $price.text().trim();
        if (priceText.charAt(0) === '$') {
            $price.data('original-price', priceText);
            $price.text(self._maskPrice(priceText));
            if ($this.find('.toggle-price').length === 0) {
                $this.find('.boxed .text-h1').first().after('<div class="toggle-price svg-icon ml-sm"><img src="https://assets.bacancytechnology.com/main-boot-5/images/close-eye.svg" alt="icon" width="40" height="40" class="price-hidden"></div>');
            }
        }
    });
},

_initPriceToggle: function() {
    var self = this;
    $(document).on('click', '.toggle-price', function(e) {
        e.stopPropagation();
        e.preventDefault();
        var isMasked = false;
        self.$('.shadow-form').each(function() {
            var $price = $(this).find('.text-h1').text().trim();
            if ($price.charAt(0) === '$' && $price.indexOf('*') !== -1) {
                isMasked = true;
                return false;
            }
        });

        if (isMasked) {
            self.$('.shadow-form').each(function() {
                var $price = $(this).find('.text-h1');
                var originalPrice = $price.data('original-price');
                if (originalPrice && originalPrice.charAt(0) === '$') {
                    $price.text(originalPrice);
                }
            });
            self.$('.toggle-price img').attr('src', 'https://assets.bacancytechnology.com/main-boot-5/images/open-eye.svg').attr('alt', 'Show Price');
        } else {
            self.$('.shadow-form').each(function() {
                var $price = $(this).find('.text-h1');
                var originalPrice = $price.data('original-price');
                if (originalPrice && originalPrice.charAt(0) === '$') {
                    $price.text(self._maskPrice(originalPrice));
                }
            });
            self.$('.toggle-price img').attr('src', 'https://assets.bacancytechnology.com/main-boot-5/images/close-eye.svg').attr('alt', 'Hide Price');
        }
    });
},

_initHeightAdjustment: function() {
    var self = this;
    $(window).on('load resize', function() {
        self._adjustHeights('.small-heading');
        self._adjustHeights('.small-heading-two');
        self._adjustHeights('.small-heading-three');
        self._adjustHeights('.small-heading-five');
        self._adjustHeights('.small-heading-four');
    });
},

_initModalClose: function() {
    this.$('.close').click(function() {
        $('.modal').css('transform', 'translateY(-100%)');
    });
}
});

options.registry.angular_offer_widget = angularOfferSnippetOptions;

return angularOfferSnippetOptions;
});