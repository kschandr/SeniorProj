$(function() {
    $('#btnSignIn').click(function() {

        $.ajax({
            url: '/signIn',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                //console.log(response);
                window.location.href = "home"
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});