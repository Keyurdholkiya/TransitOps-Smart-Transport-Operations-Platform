/* Vehicle Registry rules used by the management workflow. */
window.TransitOpsVehicles = {
  canDispatch(vehicle) { return vehicle?.status === 'Available'; },
  normalizeRegistration(value) { return String(value || '').trim().toUpperCase(); },
  hasValidCapacity(value) { return Number(value) > 0; }
};
