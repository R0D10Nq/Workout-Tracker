function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$(document).ready(function () {
    $('.add-set-form').on('submit', function (e) {
        e.preventDefault();
        let form = $(this);
        let workoutExerciseId = form.data('workout-exercise-id');
        let data = form.serializeArray();
        data.push({name: 'workout_exercise_id', value: workoutExerciseId});
        $.ajax({
            url: "{% url 'add_set_ajax' %}",
            type: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            data: data,
            success: function (response) {
                if (response.set_info) {
                    $('#sets-list-' + workoutExerciseId).append('<li>' + response.set_info + '</li>');
                    form[0].reset();
                }
            },
            error: function (xhr, errmsg, err) {
                alert("Ошибка: " + errmsg);
            }
        });
    });
});