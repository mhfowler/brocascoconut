
$( document ).ready(function() {

    // get stripeKey from page
    var stripePublishableKey = $(".stripeKey").data("stripeKey");

    var handler = StripeCheckout.configure({
        key: stripePublishableKey,
        image: '/square-image.png',
        token: function (token) {
            // Use the token to create the charge with a server-side script.
            // You can access the token ID with `token.id`
        }
    });

    $(".purchaseButton").click( function (e) {
        e.preventDefault();
        // Open Checkout with further options
        handler.open({
            name: 'Demo Site',
            description: '2 widgets ($20.00)',
            amount: 2000
        });
    });

});