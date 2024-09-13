$(document).ready(function(){
    $('.single-item-slider').slick({
          arrows: false,
          dots: true,
    });
      $('.center-slide').slick({
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
      // if ($(window).width() < 992){
      //   $('.center-slide .slick-track > div:first-child').css('margin-left','120px');
      // }
      
      $('.slick-track > div').not('footer .slick-track > div').css('margin-right','10px');
      $('.slick-track > div').not('footer .slick-track > div').css('margin-left','10px');      
  });