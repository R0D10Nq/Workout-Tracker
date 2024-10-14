// Получение данных из JSON
const months = JSON.parse(document.getElementById('months-data').textContent);
const workoutsCounts = JSON.parse(document.getElementById('workouts-counts-data').textContent);

// График количества тренировок в месяц
let ctx1 = document.getElementById('workoutsPerMonthChart').getContext('2d');
let workoutsPerMonthChart = new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: months,
        datasets: [{
            label: 'Количество тренировок',
            data: workoutsCounts,
            backgroundColor: 'rgba(54,162,235,0.45)',
            borderColor: 'rgba(54,162,235,0.85)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Месяц'
                }
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Количество тренировок'
                }
            }
        }
    }
});

// Графики прогресса по упражнениям
for (let i = 1; i <= exerciseCount; i++) {
    const monthsEx = JSON.parse(document.getElementById('months-ex-' + i).textContent);
    const maxWeights = JSON.parse(document.getElementById('max-weights-ex-' + i).textContent);
    const maxReps = JSON.parse(document.getElementById('max-reps-ex-' + i).textContent);

    let ctx = document.getElementById('progressChart_' + i).getContext('2d');
    let progressChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthsEx,
            datasets: [
                {
                    label: 'Максимальный вес (кг)',
                    data: maxWeights,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Максимальные повторения',
                    data: maxReps,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: false,
                    tension: 0.1
                }
            ]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Месяц'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Значение'
                    }
                }
            }
        }
    });
}
