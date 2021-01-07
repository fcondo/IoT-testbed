
$(window).scroll(function() {    
    var scroll = $(window).scrollTop();

    if (scroll >= 100) {
        $(".nav-fixed").addClass("nav-fixed-new");
    } else {
        $(".nav-fixed").removeClass("nav-fixed-new");
    }
});

$(document).ready(function(){
    $(".ideal_design_pricing .onoffswitch-label").click(function() {
        $(".ideal_design_pricing .monthly, .ideal_design_pricing .yearly").toggle();
    });
  });