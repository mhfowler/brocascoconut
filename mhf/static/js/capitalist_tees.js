function shirtPage() {
    $(".shirt-contingent").show();
    $(".print-contingent").hide();
    $(".booty-contingent").hide();
    $(".booty-button").show();
    $(".tshirt-button").hide();
    $(".print-button").show();
    which_product = "tshirt";
    setBasePrice(10);
    $(".booty-coming-soon").hide();
    $(".buttons-wrapper").show();
}
function printPage() {
    $(".shirt-contingent").hide();
    $(".print-contingent").show();
    $(".booty-contingent").hide();
    $(".booty-button").show();
    $(".tshirt-button").show();
    $(".print-button").hide();
    which_product = "print";
    if ($(".small-print-button").hasClass("selected-printsize")) {
        setBasePrice(5);
    }
    else if ($(".medium-print-button").hasClass("selected-printsize")) {
        setBasePrice(20);
    }
    else if ($(".large-print-button").hasClass("selected-printsize")) {
        setBasePrice(100);
    }
    $(".booty-coming-soon").hide();
    $(".buttons-wrapper").show();
//    history.pushState('data', '', 'https://brocascoconut.com/the_capitalist_print/');
}
function bootyPage() {
    $(".shirt-contingent").hide();
    $(".print-contingent").hide();
    $(".booty-contingent").show();
    $(".booty-button").hide();
    $(".tshirt-button").show();
    $(".print-button").show();
    which_product = "booty";
    setBasePrice(10);
    $(".booty-coming-soon").show();
    $(".buttons-wrapper").hide();
//    history.pushState('data', '', 'https://brocascoconut.com/the_capitalist_booty/');
}


// set new base price
function setBasePrice(newBasePrice) {
    base_price = newBasePrice;
    $(".base-price-num").html(base_price);
}

// base brice of product
var base_price = 5;
var which_product = "";

$( document ).ready(function() {

    // force https
    if (window.location.protocol != 'https:') {
//        window.location.replace("https:" + window.location.href.replace("http:",""));
    }

    console.log("page: " + window.location.pathname);
    if (window.location.pathname === "/the_capitalist_tshirt/") {
        shirtPage();
    }
    else if (window.location.pathname === "/the_capitalist_print/") {
        printPage();
    }
    else if (window.location.pathname === "/the_capitalist_booty/") {
        bootyPage()
    }

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
        image: '/static/img/small_triangle.png',
        token: function (token) {
            // Use the token to create the charge with a server-side script.
            // You can access the token ID with `token.id`
            var json_token = JSON.stringify(token, null, 2);
            var color = $(".selected-color").html();
            var shirtsize = $(".selected-size").html();
            var bootysize = $(".selected-bootysize").html();
            var printsize = $(".selected-printsize").html();
            var style = $(".selected-style").html();
            var address = $(".shipping-input").val();
            var cost = $(".shirtCost").attr("data-cost");
            startLoading();
            $.post("/buyShirt/", { stripeToken: json_token,
                which_product:which_product,
                color:color,
                bootysize:bootysize,
                printsize:printsize,
                shirtsize:shirtsize,
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
            alert("You must enter a number to be printed and a shipping address X_X");
            return;
        }
        var cost = $(".shirtCost").attr("data-cost");
        var size = $(".selected-size").html();
        var bootysize = $(".selected-bootysize").html();
        var printsize = $(".selected-printsize").html();
        var color = $(".selected-color").html();
        var costInCents = Math.floor(parseFloat(cost)*100);
        // figure out which product
        var description = '';
        if (which_product === "tshirt") {
            description = 'Capitalist T-Shirt (Size: ' + size + ", Number: " + bonusNumber + ')';
        }
        else if (which_product === "print") {
            description = 'Capitalist Print (Size: ' + printsize + ", Number: " + bonusNumber + ')';
        }
        else if (which_product === "booty") {
            description = 'Shorts (Size: ' + bootysize + ", Number: " + bonusNumber + ')';
        }
        // Open Checkout with further options
        handler.open({
            name: 'brocascoconut.com',
            description: description,
            amount: costInCents
        });
    });

    // focus on input
    $(".number-input").focus();


    // set new bonus price
    function setBonusPrice(newNumber) {
        // remove leading zeros
        if (newNumber.length > 1) {
            while (newNumber.indexOf("0") == 0) {
                newNumber = newNumber.substring(1, newNumber.length)
            }
        }
        $(".number-input").val(newNumber);
        // remove old font classes
        $(".img-number").removeClass("questionMark");
        $(".img-number").removeClass("singleDigit");
        $(".img-number").removeClass("doubleDigit");
        $(".img-number").removeClass("tripleDigit");
        $(".img-number").removeClass("megaDigit");
        if (newNumber == "") {
            var total_price = base_price;
            $(".shirtCost").attr("data-cost",total_price);
            $(".bonus-price").html("?");
            $(".img-number").html("?");
            $(".total-price").html("What You Pay");
            $(".img-number").html("?");
            // set font class
            $(".img-number").addClass("questionMark");
        }
        else {
            var total_price = base_price + parseInt(newNumber);
            $(".shirtCost").attr("data-cost",total_price);
            $(".bonus-price").html("$" + newNumber);
            $(".img-number").html(newNumber);
            $(".total-price").html("$" + total_price);
            // set font class
            if (newNumber < 10) {
                $(".img-number").addClass("singleDigit");
            }
            else if (newNumber < 100) {
                $(".img-number").addClass("doubleDigit");
            }
            else if (newNumber < 1000) {
                $(".img-number").addClass("tripleDigit");
            }
            else {
                $(".img-number").addClass("megaDigit");
            }
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
        $(".color-button").removeClass("selected-color").removeClass("selected");
        $(this).addClass("selected-color").addClass("selected");

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
    $(".printsize-button").click(function(e) {
        e.preventDefault();
        $(".printsize-button").removeClass("selected-printsize").removeClass("selected");
        $(this).addClass("selected-printsize").addClass("selected");
    });
    $(".size-button").click(function(e) {
        e.preventDefault();
        $(".size-button").removeClass("selected-size").removeClass("selected");
        $(this).addClass("selected-size").addClass("selected");
    });
    $(".bootysize-button").click(function(e) {
        e.preventDefault();
        $(".bootysize-button").removeClass("selected-bootysize").removeClass("selected");
        $(this).addClass("selected-bootysize").addClass("selected");
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

    $(".tshirt-button").click(function(e) {
        e.preventDefault();
        window.location.replace("/the_capitalist_tshirt/");
//        shirtPage();
//        window.scrollTo(0, 300);
    });
    $(".print-button").click(function(e) {
        e.preventDefault();
        window.location.replace("/the_capitalist_print/");
//        printPage();

//        window.scrollTo(0, 300);
    });
    $(".booty-button").click(function(e) {
        e.preventDefault();
        window.location.replace("/the_capitalist_booty/");
//        bootyPage();
//        window.scrollTo(0, 300);
    });

    $(".small-print-button").click(function(e) {
        setBasePrice(5);
    });
    $(".medium-print-button").click(function(e) {
        setBasePrice(20);
    });
    $(".large-print-button").click(function(e) {
        setBasePrice(100);
    });


    $(".why-link").click(function(e) {
        e.preventDefault();
        $(".why-text").show();
    });

});