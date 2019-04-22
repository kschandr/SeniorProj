$(function() {
    $('#addFood').click(function() {

        $.ajax({
            url: '/addFood',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
                window.location.href = "nutrition"
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});