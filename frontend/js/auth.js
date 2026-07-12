const form = document.querySelector('#loginForm'), pass = document.querySelector('#password'), toggle = document.querySelector('#togglePassword');

toggle.addEventListener('click', () => { pass.type = pass.type === 'password' ? 'text' : 'password'; toggle.textContent = pass.type === 'password' ? '◉' : '◌' });

form.addEventListener('submit', e => { e.preventDefault(); localStorage.setItem('user', JSON.stringify({ role: document.querySelector('#role').value })); location.href = 'dashboard.html' });
