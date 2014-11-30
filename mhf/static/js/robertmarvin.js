/* on enter jquery plugin */
(function($) {
    $.fn.onEnter = function(func) {
        this.bind('keypress', function(e) {
            if (e.keyCode == 13) func.apply(this, [e]);
        });
        return this;
    };
})(jQuery);

$( document ).ready(function() {

    // hide all other pages and show this one
    function showPage(page) {
        $(".page").hide();
        $(".page[data-page='" + page + "']").show();
    }

    /* show the correct page */
    var cPage = window.location.pathname;
    showPage(cPage);

    // csrf protect
    /* csrf protection */
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    /* submit email */
    function submitEmail() {
        var email = $(".subscribe-input").val();
        $.post("/submit_email/", { email: email },function(data) {
            showPage("/thankyou/");
            setTimeout(function(){
                window.location.replace("/______/");
            }, 1500);
        });
    }

    $(".subscribe-input").focus();
    $(".subscribe-input").keypress(function() {
        $(".subscribe-button").css("display","block");
    });
    $(".subscribe-button").click(function() {
        submitEmail();
    });
    $(".subscribe-input").onEnter(function() {
        submitEmail();
    });
});