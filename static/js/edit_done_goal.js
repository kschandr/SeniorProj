$(function() {
    $('#edit_done_goal').click(function() {

        $.ajax({
            url: '/update_goals',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                //console.log(response);
                window.location.href = "goals"
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});