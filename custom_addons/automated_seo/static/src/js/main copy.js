$(document).ready(function() {
    // Navigation menu click event
    $(".nav-menu").click(function() {
        $(".nav-menu").removeClass("active");
        $(this).addClass("active");
        $(".dropdown-menu").removeClass("flex").addClass("hidden");
        $(this).find(".dropdown-menu").addClass("flex").removeClass("hidden");
    });

    // Set the top position for side-sticky
    var headerHeight = $("header").outerHeight(true);
    headerHeight += 100;
    $(".side-sticky").css({ top: headerHeight });

    // Window scroll event
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

    // Menu icon click event
    $(".menu-icon").click(function() {
        $(".sidebar_right_outer").slideToggle();
        $(this).toggleClass("active");
    });

    // Tabs click event
    $(".tabs .tab-header li,.tabs .tab-header .tab-head").click(function() {
        var tab = $(this);
        var index = tab.index();
        tab.addClass("active").siblings().removeClass("active");
        tab.closest(".tabs").find(".tab-content .tab-pane").eq(index).addClass("active").siblings().removeClass("active");
    });
    if (window.matchMedia('(max-width: 767px)').matches) {
        $('.tabbibg-sec .tab-header .tab-head').each(function(index) {
            $(this).append($('.tabbibg-sec .tab-content .tab-pane').eq(index));
        });
    }
    // Slide up and slide down for sidebars and accordion items
    $(".sidebar_right_outer, .accordion-item").find(".sub-side, .sub-side-two, .accordian-text").slideUp();
    $(".sidebar_right_outer, .accordion-item").find(".sub-side.active, .accordian-text.active").slideDown();

    // Sidebar submenu click event
    $(".sidebar_right_outer .res-submenu, .sidebar_right_outer .res-submenu, .accordion-item .faq-heading").on("click", function() {
        var parent = $(this).parent();
        parent.siblings().removeClass("active").find(".menu_parent, .sub-side, .res-submenu, .faq-heading").removeClass("active").end().find(".sub-side, .accordian-text").slideUp();
        parent.find(".sub-side, .accordian-text").slideToggle();
        parent.find(".menu_parent, .sub-side, .res-submenu, .accordian-text, .faq-heading").toggleClass("active");
        parent.toggleClass("active");
    });

    // Submenu two click event
    $(".res-submenu-two").on("click", function() {
        var parent = $(this).parent();
        parent.siblings().removeClass("active").find(".sub-side, .res-submenu-two").removeClass("active").end().find(".sub-side-two").slideUp();
        parent.find(".sub-side-two").slideToggle();
        parent.find(".sub-side-two, .res-submenu-two").toggleClass("active");
        parent.toggleClass("active");
    });

    // Footer address slick slider
    $(".footer-address").slick({
        arrows: true,
        dots: false,
        slidesToShow: 3,
        slidesToScroll: 2,
        responsive: [
            { breakpoint: 767, settings: { slidesToShow: 1, slidesToScroll: 1 } },
            { breakpoint: 992, settings: { slidesToShow: 2, slidesToScroll: 1 } },
        ]
    });

    // Footer slider slick slider
    $(".footer-slider").slick({
        infinite: false,
        customPaging: function(slider, i) {
            return '<button class="tab">' + $(slider.$slides[i]).attr("title") + "</button>";
        },
        arrows: true,
        dots: true,
        responsive: [{ breakpoint: 767, settings: { arrows: false } }]
    });

    // Media query adjustments
    if (window.matchMedia("(max-width: 767px)").matches) {
        $(".resp-btn").insertAfter(".resp-btn-outer");
        $(".resp-btn-two").insertAfter(".resp-btn-outer-two");
        $(".faq-head").insertAfter(".faq-head-outer");
    }
    // form hide-show price
    $('.shadow-form .boxed p.mb-0').each(function() {
        $(this).next('button').addBack().wrapAll('<div class="flex items-center justify-center"></div>');
    });

    function maskPrice(priceText) {
        return priceText.substring(0, 2) + '*'.repeat(priceText.length - 2);
    }

    function unmaskPrice(priceElement) {
        return priceElement.data('original-price');
    }

    $('.shadow-form').each(function(){
        var priceElement = $(this).find('.text-h1');
        var priceText = priceElement.text().trim();

        if (priceText.charAt(0) === '$') {
            priceElement.data('original-price', priceText);
            priceElement.text(maskPrice(priceText));

            // Append the "Toggle Price" button if it does not already exist
            if ($(this).find('.toggle-price').length === 0) {
                $(this).find('.boxed .text-h1').first().after(`
                    <div class="toggle-price svg-icon ml-sm">
                        <img src="https://assets.bacancytechnology.com/main-boot-5/images/close-eye.svg" 
                            alt="icon" width="40" height="40" class="price-hidden">
                    </div>
                `);
            }
        }
    });

    $(document).on('click', '.toggle-price', function(event){
        event.stopPropagation();
        event.preventDefault();   
        var isHidden = false;
        $('.shadow-form').each(function(){
            var priceElement = $(this).find('.text-h1');
            var priceText = priceElement.text().trim();
    
            // Check if the price text starts with a dollar sign
            if (priceText.charAt(0) === '$' && priceText.indexOf('*') !== -1) {
                isHidden = true;
                return false;  
            }
        });
    
        if (isHidden) {
            $('.shadow-form').each(function(){
                var priceElement = $(this).find('.text-h1');
                var originalPrice = priceElement.data('original-price');
    
                // Unmask the price only if it starts with a dollar sign
                if (originalPrice && originalPrice.charAt(0) === '$') {
                    priceElement.text(originalPrice);
                }
            });
            $('.toggle-price img').attr('src', 'https://assets.bacancytechnology.com/main-boot-5/images/open-eye.svg').attr('alt', 'Show Price');
        } else {
            $('.shadow-form').each(function(){
                var priceElement = $(this).find('.text-h1');
                var originalPrice = priceElement.data('original-price');
    
                // Mask the price only if it starts with a dollar sign
                if (originalPrice && originalPrice.charAt(0) === '$') {
                    priceElement.text(maskPrice(originalPrice));
                }
            });
            $('.toggle-price img').attr('src', 'https://assets.bacancytechnology.com/main-boot-5/images/close-eye.svg').attr('alt', 'Hide Price');
        }
    });

    // Equal height function
    function equalHeight(selector) {
        var currentTallest = 0,
            currentRowStart = 0,
            rowDivs = [],
            $el, topPosition = 0;

        $(selector).each(function() {
            $el = $(this);
            $($el).height("auto");
            topPosition = $el.position().top;

            if (currentRowStart != topPosition) {
                for (currentDiv = 0; currentDiv < rowDivs.length; currentDiv++) {
                    rowDivs[currentDiv].height(currentTallest);
                }
                rowDivs.length = 0;
                currentRowStart = topPosition;
                currentTallest = $el.height();
                rowDivs.push($el);
            } else {
                rowDivs.push($el);
                currentTallest = (currentTallest < $el.height()) ? $el.height() : currentTallest;
            }

            for (currentDiv = 0; currentDiv < rowDivs.length; currentDiv++) {
                rowDivs[currentDiv].height(currentTallest);
            }
        });
    }

    // Apply equal heights on load and resize
    $(window).load(function() {
        equalHeight(".small-heading");
        equalHeight(".small-heading-two");
        equalHeight(".small-heading-three");
        equalHeight(".small-heading-five");
        equalHeight(".small-heading-four");
    });

    $(window).resize(function() {
        equalHeight(".small-heading");
        equalHeight(".small-heading-two");
        equalHeight(".small-heading-three");
        equalHeight(".small-heading-five");
        equalHeight(".small-heading-four");
    });

    //popup close
    $('.close').click(function(){
        $('.modal').css('transform','translateY(-100%)')
    });
    //browser close open popup
    if (window.matchMedia('(min-width: 1199px)').matches) {
        var popuptabCloseShown = false;

        jQuery(document).on('mouseleave', function(e) {
            if (e.clientY < 1 && !popuptabCloseShown) {
                popuptabCloseShown = true;               
                $('#popup-close-window').addClass('show');
            }
        });
    }
});
