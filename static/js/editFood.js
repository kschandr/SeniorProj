$(function() {
    $('#editFood').click(function() {

        $.ajax({
            url: '/editFood',
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