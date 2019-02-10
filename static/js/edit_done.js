$(function() {
    $('#edit_done').click(function() {

        $.ajax({
            url: '/update_profile',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                //console.log(response);
                window.location.href = "profile"
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});