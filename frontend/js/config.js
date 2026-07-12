/* Shared browser-only configuration for the frontend demo. */
window.TransitOpsConfig = Object.freeze({
  storageKey: 'transitOpsDataV2',
  roles: ['Fleet Manager', 'Driver / Dispatcher', 'Safety Officer', 'Financial Analyst'],
  vehicleStatuses: ['Available', 'On Trip', 'In Shop', 'Retired'],
  driverStatuses: ['Available', 'On Trip', 'Off Duty', 'Suspended']
});
