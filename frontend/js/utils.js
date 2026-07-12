/* Small helpers available to screen scripts without a build step. */
window.TransitOpsUtils = {
  formatCurrency(value) { return `₹${Number(value || 0).toLocaleString('en-IN')}`; },
  today() { return new Date().toISOString().slice(0, 10); },
  isFutureDate(date) { return Boolean(date) && date >= this.today(); },
  createId() { return `${Date.now()}-${Math.random().toString(16).slice(2)}`; }
};
