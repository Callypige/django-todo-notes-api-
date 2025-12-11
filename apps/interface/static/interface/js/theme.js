// Simple theme toggle (light/dark)
const html = document.documentElement;
const themeBtn = document.querySelector('.theme-btn');
const lightMode = document.querySelector('.light-mode');
const darkMode = document.querySelector('.dark-mode');

// Load saved theme (default: light)
let currentTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', currentTheme);
updateDisplay();

// Toggle on click
themeBtn.addEventListener('click', () => {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateDisplay();
});

function updateDisplay() {
    if (currentTheme === 'dark') {
        lightMode.style.display = 'none';
        darkMode.style.display = 'inline';
    } else {
        lightMode.style.display = 'inline';
        darkMode.style.display = 'none';
    }
}
