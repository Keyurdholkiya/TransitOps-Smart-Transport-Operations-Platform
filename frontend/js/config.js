/* Shared browser-only configuration for the frontend demo. */
window.TransitOpsConfig = Object.freeze({
  storageKey: 'transitOpsDataV2',
  accessTokenKey: 'transitOpsAccessToken',
  apiBaseUrl: window.TRANSITOPS_API_URL || 'http://127.0.0.1:8000/api/v1',
  roles: ['Fleet Manager', 'Driver / Dispatcher', 'Safety Officer', 'Financial Analyst'],
  vehicleStatuses: ['Available', 'On Trip', 'In Shop', 'Retired'],
  driverStatuses: ['Available', 'On Trip', 'Off Duty', 'Suspended']
});
