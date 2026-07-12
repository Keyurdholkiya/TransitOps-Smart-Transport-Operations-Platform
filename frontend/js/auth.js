const form = document.querySelector('#loginForm');
const pass = document.querySelector('#password');
const toggle = document.querySelector('#togglePassword');
const loginButton = document.querySelector('#loginBtn');

toggle.addEventListener('click', () => {
  pass.type = pass.type === 'password' ? 'text' : 'password';
  toggle.textContent = pass.type === 'password' ? '◉' : '◌';
});

form.addEventListener('submit', async e => {
  e.preventDefault();

  const email = document.querySelector('#email').value.trim();
  const password = pass.value;
  const originalLabel = loginButton.textContent;

  loginButton.disabled = true;
  loginButton.textContent = 'Signing in…';
  TransitOpsApi.clearSession();

  try {
    const token = await TransitOpsApi.login(email, password);
    TransitOpsApi.setAccessToken(token.access_token);

    const profile = await TransitOpsApi.getMyProfile();
    localStorage.setItem('user', JSON.stringify({
      id: profile.id,
      email: profile.email,
      fullName: profile.full_name,
      role: profile.role.display_name,
      roleName: profile.role.name
    }));

    location.href = 'dashboard.html';
  } catch (error) {
    TransitOpsApi.clearSession();
    if (error instanceof TypeError) {
      alert('Cannot reach the TransitOps API. Start the backend on port 8000.');
    } else {
      alert(error.message || 'Sign in failed. Check your credentials.');
    }
    loginButton.disabled = false;
    loginButton.textContent = originalLabel;
  }
});
