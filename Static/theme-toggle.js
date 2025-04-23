// Get the toggle switch, body, and label elements
const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const themeLabel = document.getElementById('theme-label');

// Check local storage for the saved theme preference
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
  body.classList.toggle('dark-mode', savedTheme === 'dark');
  themeToggle.checked = savedTheme === 'dark';
  themeLabel.textContent = savedTheme === 'dark' ? 'Dark Mode' : 'Light Mode';
}

// Event listener for the toggle switch
themeToggle.addEventListener('change', () => {
  const isDarkMode = themeToggle.checked;
  body.classList.toggle('dark-mode', isDarkMode);
  localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  themeLabel.textContent = isDarkMode ? 'Dark Mode' : 'Light Mode';
});
