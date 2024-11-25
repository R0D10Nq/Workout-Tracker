// Функция для установки темы
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Обновляем состояние чекбокса
    const checkbox = document.getElementById('checkbox');
    if (checkbox) {
        checkbox.checked = theme === 'dark';
    }
}

// Функция для переключения темы
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

// Инициализация темы при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Получаем сохраненную тему или используем светлую по умолчанию
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    // Добавляем обработчик события для переключателя
    const checkbox = document.getElementById('checkbox');
    if (checkbox) {
        checkbox.addEventListener('change', toggleTheme);
    }

    // Добавляем поддержку системной темы
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    prefersDark.addListener((e) => {
        const theme = e.matches ? 'dark' : 'light';
        setTheme(theme);
    });
});
