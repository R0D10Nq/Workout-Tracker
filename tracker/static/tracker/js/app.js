// tracker/static/tracker/js/app.js

// Инициализация AOS (Animate On Scroll)
AOS.init({
    duration: 800, // Продолжительность анимации
    once: true,    // Анимация запускается только один раз
});

// Функция для получения CSRF токена
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

// Получение CSRF токена
const csrftoken = getCookie('csrftoken');
