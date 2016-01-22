

$(document).ready(function() {

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


    $(".click-to-delete").click(function(e) {
        var r = confirm("Are you sure you want to turn off this alert?");
        if (r == true) {
            var wrapper = $(this).parents('.alert');
            var phonediv = wrapper.find('.phone');
            var fbdiv = wrapper.find('.fblink');
            $.post("/bass_remove_alert/", {
                phone: phonediv.data('phone'),
                fblink: fbdiv.data('fblink')
            }, function (data) {
                location.reload();
            });
        }
    });

    $(".set-new-alert-button").click(function(e) {
        var phone = $('.phone-input').val();
        var fblink = $('.fb-input').val();
        $.post("/bass_add_alert/", {
            phone: phone,
            fblink: fblink
        },function(data) {
            alert(data);
            location.reload();
        });
    });
});