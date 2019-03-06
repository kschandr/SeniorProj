$(function() {
    $('#workoutDone').click(function() {

        $.ajax({
            url: '/workoutDone',
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