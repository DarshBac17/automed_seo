$(document).ready(function() {
    $(".nav-menu").click(function() {
        $(".nav-menu").removeClass("active");
        $(this).addClass("active");
        $(".dropdown-menu").removeClass("flex").addClass("hidden");
        $(this).find(".dropdown-menu").addClass("flex").removeClass("hidden");
    });

    var headerHeight = $("header").outerHeight(true) + 100;
    $(".side-sticky").css({ top: headerHeight });

    function maskPrice(price) {
        return price.substring(0, 2) + "*".repeat(price.length - 2);
    }

    function getOriginalPrice(element) {
        return element.data("original-price");
    }

    function adjustHeights(selector) {
        var currentDiv, maxHeight = 0, currentTop = 0, elements = [];
        $(selector).each(function() {
            var $this = $(this);
            $this.height("auto");
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
    }

    $(window).scroll(function() {
        if ($(this).scrollTop() > 0) {
            $(".nav-menu").removeClass("active");
            $(this).addClass("active");
            $(".dropdown-menu").removeClass("flex").addClass("hidden");
            $(this).find(".dropdown-menu").addClass("flex").removeClass("hidden");
            $(".sidebar_right_outer").slideUp();
            $(".menu-icon").removeClass("active");
        } else {
            $(".nav-menu").click(function() {
                $(".nav-menu").removeClass("active");
                $(this).addClass("active");
                $(".dropdown-menu").removeClass("flex").addClass("hidden");
                $(this).find(".dropdown-menu").addClass("flex").removeClass("hidden");
            });
        }
    });

    $(".menu-icon").click(function() {
        $(".sidebar_right_outer").slideToggle();
        $(this).toggleClass("active");
    });

    $(".tabs .tab-header li, .tabs .tab-header .tab-head").click(function() {
        var $this = $(this);
        var index = $this.index();
        $this.addClass("active").siblings().removeClass("active");
        $this.closest(".tabs").find(".tab-content .tab-pane").eq(index).addClass("active").siblings().removeClass("active");
    });

    if (window.matchMedia("(max-width: 767px)").matches) {
        $(".tabbibg-sec .tab-header .tab-head").each(function(index) {
            $(this).append($(".tabbibg-sec .tab-content .tab-pane").eq(index));
        });
    }

    $(".sidebar_right_outer, .accordion-item").find(".sub-side, .sub-side-two, .accordian-text").slideUp();
    $(".sidebar_right_outer, .accordion-item").find(".sub-side.active, .accordian-text.active").slideDown();

    $(".sidebar_right_outer .res-submenu, .sidebar_right_outer .res-submenu, .accordion-item .faq-heading").on("click", function() {
        var $parent = $(this).parent();
        $parent.siblings().removeClass("active").find(".menu_parent, .sub-side, .res-submenu, .faq-heading").removeClass("active").end().find(".sub-side, .accordian-text").slideUp();
        $parent.find(".sub-side, .accordian-text").slideToggle();
        $parent.find(".menu_parent, .sub-side, .res-submenu, .accordian-text, .faq-heading").toggleClass("active");
        $parent.toggleClass("active");
    });

    $(".res-submenu-two").on("click", function() {
        var $parent = $(this).parent();
        $parent.siblings().removeClass("active").find(".sub-side, .res-submenu-two").removeClass("active").end().find(".sub-side-two").slideUp();
        $parent.find(".sub-side-two").slideToggle();
        $parent.find(".sub-side-two, .res-submenu-two").toggleClass("active");
        $parent.toggleClass("active");
    });

    $(".footer-address").slick({
        arrows: true,
        dots: false,
        slidesToShow: 3,
        slidesToScroll: 2,
        responsive: [
            { breakpoint: 767, settings: { slidesToShow: 1, slidesToScroll: 1 } },
            { breakpoint: 992, settings: { slidesToShow: 2, slidesToScroll: 1 } }
        ]
    });

    $(".footer-slider").slick({
        infinite: false,
        customPaging: function(slider, i) {
            return '<button class="tab">' + $(slider.$slides[i]).attr("title") + "</button>";
        },
        arrows: true,
        dots: true,
        responsive: [{ breakpoint: 767, settings: { arrows: false } }]
    });

    if (window.matchMedia("(max-width: 767px)").matches) {
        $(".resp-btn").insertAfter(".resp-btn-outer");
        $(".resp-btn-two").insertAfter(".resp-btn-outer-two");
        $(".faq-head").insertAfter(".faq-head-outer");
    }

    $(".shadow-form .boxed p.mb-0").each(function() {
        $(this).next("button").addBack().wrapAll('<div class="flex items-center justify-center"></div>');
    });

    $(".shadow-form").each(function() {
        var $this = $(this);
        var $price = $this.find(".text-h1");
        var priceText = $price.text().trim();
        if (priceText.charAt(0) === "$") {
            $price.data("original-price", priceText);
            $price.text(maskPrice(priceText));
            if ($this.find(".toggle-price").length === 0) {
                $this.find(".boxed .text-h1").first().after('<div class="toggle-price svg-icon ml-sm"><img src="https://assets.bacancytechnology.com/main-boot-5/images/close-eye.svg" alt="icon" width="40" height="40" class="price-hidden"></div>');
            }
        }
    });

    $(document).on("click", ".toggle-price", function(e) {
        e.stopPropagation();
        e.preventDefault();
        var isMasked = false;
        $(".shadow-form").each(function() {
            var $price = $(this).find(".text-h1").text().trim();
            if ($price.charAt(0) === "$" && $price.indexOf("*") !== -1) {
                isMasked = true;
                return false;
            }
        });

        if (isMasked) {
            $(".shadow-form").each(function() {
                var $price = $(this).find(".text-h1");
                var originalPrice = $price.data("original-price");
                if (originalPrice && originalPrice.charAt(0) === "$") {
                    $price.text(originalPrice);
                }
            });
            $(".toggle-price img").attr("src", "https://assets.bacancytechnology.com/main-boot-5/images/open-eye.svg").attr("alt", "Show Price");
        } else {
            $(".shadow-form").each(function() {
                var $price = $(this).find(".text-h1");
                var originalPrice = $price.data("original-price");
                if (originalPrice && originalPrice.charAt(0) === "$") {
                    $price.text(maskPrice(originalPrice));
                }
            });
            $(".toggle-price img").attr("src", "https://assets.bacancytechnology.com/main-boot-5/images/close-eye.svg").attr("alt", "Hide Price");
        }
    });

    $(window).load(function() {
        adjustHeights(".small-heading");
        adjustHeights(".small-heading-two");
        adjustHeights(".small-heading-three");
        adjustHeights(".small-heading-five");
        adjustHeights(".small-heading-four");
    });

    $(window).resize(function() {
        adjustHeights(".small-heading");
        adjustHeights(".small-heading-two");
        adjustHeights(".small-heading-three");
        adjustHeights(".small-heading-five");
        adjustHeights(".small-heading-four");
    });

    $(".close").click(function() {
        $(".modal").css("transform", "translateY(-100%)");
    });

    // if (window.matchMedia("(min-width: 1199px)").matches) {
    //     var popupShown = false;
    //     jQuery(document).on("mouseleave", function(e) {
    //         if (e.clientY < 1 && !popupShown) {
    //             popupShown = true;
    //             $("#popup-close-window").addClass("show");
    //         }
    //     });
    // }
});