/* Dashboard screen contract: KPI values are read from browser storage by app.js. */
window.TransitOpsDashboard = {
  kpis: ['activeVehicles', 'availableVehicles', 'inMaintenance', 'activeTrips', 'pendingTrips', 'driversOnDuty', 'fleetUtilization'],
  vehicleStates: ['Available', 'On Trip', 'In Shop', 'Retired']
};
