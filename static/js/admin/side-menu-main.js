$(document).ready(function(){

    // Menu dropdown code

    $("body").on("click", ".parent-show-child", function(){

        var num = $(this).data("number");
        
        $(".child-"+num).css({
            "display": "block",
            "transition": "5s !important",
            "transition-delay": "5s !important"
        });

        $(this).removeClass("parent-show-child-"+num, true);
        $(this).addClass("parent-hide-child-"+num, true);

        $(this).addClass("parent-hide-child", true);
        $(this).removeClass("parent-show-child", true);

        $(".menu-icon-"+num).removeClass("fa-angle-right", true);
        $(".menu-icon-"+num).addClass("fa-angle-down", true);
    });

    $("body").on("click", ".parent-hide-child", function(){
        var num = $(this).data("number");

        $(".child-"+num).css({
            "display": "none",
            "transition": "5s !important",
            "transition-delay": "5s !important"
        });

        $(this).removeClass("parent-hide-child-"+num, true);
        $(this).addClass("parent-show-child-"+num, true);

        $(this).addClass("parent-show-child", true);
        $(this).removeClass("parent-hide-child", true);

        $(".menu-icon-"+num).removeClass("fa-angle-down", true);
        $(".menu-icon-"+num).addClass("fa-angle-right", true);
    });


})