// Получение CSRF токена
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

// Обработка отправки формы для добавления подхода
document.querySelectorAll('.add-set-form').forEach(form => {
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const workoutExerciseId = this.dataset.workoutExerciseId;
        const repetitions = this.querySelector('input[name="repetitions"]').value;
        const weight = this.querySelector('input[name="weight"]').value;

        fetch('/add_set_ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            credentials: 'same-origin', // Добавлено
            body: JSON.stringify({
                'workout_exercise_id': workoutExerciseId,
                'repetitions': repetitions,
                'weight': weight
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.set_info) {
                    const setsList = document.getElementById('sets-list-' + workoutExerciseId);
                    const newListItem = document.createElement('li');
                    newListItem.textContent = data.set_info;
                    setsList.appendChild(newListItem);
                    // Очистка полей ввода
                    this.querySelector('input[name="repetitions"]').value = '';
                    this.querySelector('input[name="weight"]').value = '';
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
    });
});