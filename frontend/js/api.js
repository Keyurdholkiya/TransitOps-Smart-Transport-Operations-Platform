/* Shared backend client plus the existing local demo-data repository. */
window.TransitOpsApi = {
  getAccessToken() {
    return localStorage.getItem(TransitOpsConfig.accessTokenKey);
  },

  setAccessToken(token) {
    localStorage.setItem(TransitOpsConfig.accessTokenKey, token);
  },

  clearSession() {
    localStorage.removeItem(TransitOpsConfig.accessTokenKey);
    localStorage.removeItem('user');
  },

  async request(path, options = {}) {
    const { skipAuth = false, ...fetchOptions } = options;
    const headers = new Headers(fetchOptions.headers || {});
    const token = this.getAccessToken();

    headers.set('Accept', 'application/json');
    if (fetchOptions.body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }
    if (token && !skipAuth) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(`${TransitOpsConfig.apiBaseUrl}${path}`, {
      ...fetchOptions,
      headers
    });
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      const detail = payload?.detail;
      const message = typeof detail === 'string'
        ? detail
        : detail?.message || `Request failed (${response.status})`;
      const error = new Error(message);
      error.status = response.status;
      error.payload = payload;
      throw error;
    }

    return payload;
  },

  login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      skipAuth: true,
      body: JSON.stringify({ email, password })
    });
  },

  getMyProfile() {
    return this.request('/auth/me');
  },

  read(key, fallback = []) {
    try { return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback)); }
    catch { return fallback; }
  },

  write(key, value) { localStorage.setItem(key, JSON.stringify(value)); },
  remove(key) { localStorage.removeItem(key); }
};
