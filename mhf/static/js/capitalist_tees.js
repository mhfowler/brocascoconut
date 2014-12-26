
$( document ).ready(function() {

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

    // get stripeKey from page
    var stripeDiv = $(".stripeKey");
    var stripePublishableKey = stripeDiv.attr("data-stripe");

    function startLoading() {
        window.scrollTo(0, 0);
        $(".main-div").hide();
        $(".loading-div").show();
    }
    function showThankyou() {
        $(".main-div").hide();
        $(".thankyou-div").show();
    }

    // show the purchase div to start
    $(".purchase-div").show();

    var handler = StripeCheckout.configure({
        key: stripePublishableKey,
        image: '/square-image.png',
        token: function (token) {
            // Use the token to create the charge with a server-side script.
            // You can access the token ID with `token.id`
            var json_token = JSON.stringify(token, null, 2);
            var color = $(".selected-color").html();
            var size = $(".selected-size").html();
            var style = $(".selected-style").html();
            var address = $(".shipping-input").val();
            var cost = $(".shirtCost").attr("data-cost");
            startLoading();
            $.post("/buyShirt/", { stripeToken: json_token,
                color:color,
                size:size,
                style:style,
                address:address,
                cost:cost},function(data) {
                showThankyou();
            });
        }
    });

    $(".purchaseButton").click( function (e) {
        e.preventDefault();
        var address = $(".shipping-input").val();
        var bonusNumber = $(".number-input").val();
        if (bonusNumber == "" || address == "") {
            alert("You must enter a number to be printed on the shirt and a shipping address X_X");
            return;
        }
        var cost = $(".shirtCost").attr("data-cost");
        var costInCents = Math.floor(parseFloat(cost)*100);
        // Open Checkout with further options
        handler.open({
            name: 'RobertMarvin.com',
            description: 'Capitalist T-Shirt ($' + cost + ')',
            amount: costInCents
        });
    });

    // focus on input
    $(".number-input").focus();

    // set new bonus price
    function setBonusPrice(newNumber) {
        var base_price = 10;
        if (newNumber == "") {
            var total_price = 10;
            $(".shirtCost").attr("data-cost",total_price);
            $(".bonus-price").html("?");
            $(".shirt-img-number").html("?");
            $(".total-price").html("What You Pay");
        }
        else {
            var total_price = base_price + parseInt(newNumber);
            $(".shirtCost").attr("data-cost",total_price);
            $(".bonus-price").html("$" + newNumber);
            $(".shirt-img-number").html(newNumber);
            $(".total-price").html("$" + total_price);
        }
    }

    // keypress in number input
    $(".number-input").keypress(function(e) {
        e.preventDefault();
        var c = String.fromCharCode(e.which);
        if (['1','2', '3','4','5','6','7','8','9','0'].indexOf(c) == -1) {
            return;
        }
        var oldNumber = $(this).val();
        var newNumber = oldNumber.concat(c);
        $(this).val(newNumber);
        setBonusPrice(newNumber);

    });

    $('.number-input').keyup(function(e){
        if(e.keyCode == 8) {
            var newNumber = $(this).val();
            setBonusPrice(newNumber);
        }
    });

    $(".color-button").click(function(e) {
        e.preventDefault();
        $(".color-button").removeClass("selected-color");
        $(this).addClass("selected-color");

        if ($(this).hasClass("black-button")) {
            $(".black-male-shirt-img").addClass("selected");
            $(".white-male-shirt-img").removeClass("selected");
            $(".shirt-img-number").css("color","white");
            $(".black-shirt-back").addClass("selected");
            $(".white-shirt-back").removeClass("selected");
        }
        else {
            $(".black-male-shirt-img").removeClass("selected");
            $(".white-male-shirt-img").addClass("selected");
            $(".shirt-img-number").css("color","black");
            $(".black-shirt-back").removeClass("selected");
            $(".white-shirt-back").addClass("selected");
        }

    });
    $(".size-button").click(function(e) {
        e.preventDefault();
        $(".size-button").removeClass("selected-size");
        $(this).addClass("selected-size");
    });
    $(".style-button").click(function(e) {
        e.preventDefault();
        $(".style-button").removeClass("selected-style");
        $(this).addClass("selected-style");
    });
    $(".see-the-back").click(function(e) {
        e.preventDefault();
        $(".shirt-back-wrapper").show();
        $(".shirt-front-wrapper").hide();
    });
    $(".see-the-front").click(function(e) {
        e.preventDefault();
        $(".shirt-back-wrapper").hide();
        $(".shirt-front-wrapper").show();
    });

    $(".new-order").click(function(e) {
        $(".main-div").hide();
        $("purchase-div").show();
    });

});