$(function() {
    $('#edit_done_alt_workouts').click(function() {

        $.ajax({
            url: '/update_workouts',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                //console.log(response);
                window.location.href = "workout"
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});