const form = document.querySelector('#loginForm');
const pass = document.querySelector('#password');
const toggle = document.querySelector('#togglePassword');

toggle.addEventListener('click', () => {
  pass.type = pass.type === 'password' ? 'text' : 'password';
  toggle.textContent = pass.type === 'password' ? '◉' : '◌';
});

form.addEventListener('submit', e => {
  e.preventDefault();
  const role = document.querySelector('#role').value;
  localStorage.setItem('user', JSON.stringify({ role }));
  location.href = 'dashboard.html';
});
