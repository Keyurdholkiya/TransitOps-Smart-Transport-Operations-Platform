/* Shared UI helpers used across all pages. */
window.TransitOpsUI = {
  $: selector => document.querySelector(selector),

  esc(value) {
    return String(value ?? '').replace(/[&<>'"]/g, char => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[char]));
  },

  money(value) {
    return `₹${Number(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
  },

  dateText(value) {
    if (!value) return '—';
    return new Date(`${value}T00:00:00`).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  },

  statusClass(value) {
    const map = {
      Available: 'green', 'On Trip': 'blue', 'In Shop': 'yellow', Retired: 'red',
      'Off Duty': 'gray', Suspended: 'red', Draft: 'gray', Dispatched: 'blue',
      Completed: 'green', Cancelled: 'red', Open: 'yellow', Closed: 'green'
    };
    return map[value] || 'gray';
  },

  badge(value) {
    return `<span class="badge ${this.statusClass(value)}">${this.esc(value)}</span>`;
  },

  showNotice(selector, message, error = false) {
    const el = this.$(selector);
    if (!el) return;
    el.textContent = message;
    el.className = `notice${error ? ' error' : ''}`;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 5000);
  },

  setEmpty(tableId, emptyId, active) {
    const table = this.$(tableId)?.closest('table');
    const empty = this.$(emptyId);
    if (table) table.style.display = active ? '' : 'none';
    if (empty) empty.style.display = active ? 'none' : '';
  },

  currentUser() {
    try { return JSON.parse(localStorage.getItem('user') || '{}'); }
    catch { return {}; }
  },

  setupHeader() {
    const user = this.currentUser();
    const role = user.role || 'Guest';
    if (!user.role) {
      location.href = 'index.html';
      return false;
    }
    document.querySelectorAll('#currentRole').forEach(el => {
      const initials = role.split(/\s|\//).map(x => x[0]).join('').slice(0, 2) || 'T';
      el.innerHTML = `Role: ${this.esc(role)} <span class="avatar">${this.esc(initials)}</span>`;
    });
    return true;
  },

  setupSearch() {
    document.querySelectorAll('[data-search]').forEach(input => {
      input.addEventListener('input', () => {
        const query = input.value.toLowerCase();
        document.querySelectorAll('tbody tr').forEach(row => {
          row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
        });
      });
    });
  },

  fillVehicleSelect(selector, availableOnly = false) {
    const data = TransitOpsData.get();
    const list = data.vehicles.filter(v =>
      availableOnly ? v.status === 'Available' : v.status !== 'Retired'
    );
    const el = this.$(selector);
    if (!el) return;
    el.innerHTML = list.length
      ? `<option value="">Select vehicle</option>${list.map(v =>
          `<option value="${v.id}">${this.esc(v.registration)} · ${this.esc(v.name)}</option>`
        ).join('')}`
      : '<option value="">Add a vehicle first</option>';
  }
};
