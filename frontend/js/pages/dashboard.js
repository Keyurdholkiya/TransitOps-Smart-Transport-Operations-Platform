window.TransitOpsPages = window.TransitOpsPages || {};
//dashboard
window.TransitOpsPages.dashboard = {
  init() {
    const { $, esc, badge } = TransitOpsUI;
    const data = TransitOpsData.get();
    const vs = TransitOpsData.vehiclesById(data);
    const ds = TransitOpsData.driversById(data);

    const activeVehicles = data.vehicles.filter(v => v.status !== 'Retired').length;
    const available = data.vehicles.filter(v => v.status === 'Available').length;
    const inShop = data.vehicles.filter(v => v.status === 'In Shop').length;
    const activeTrips = data.trips.filter(t => t.status === 'Dispatched').length;
    const pending = data.trips.filter(t => t.status === 'Draft').length;
    const driversOnTrip = data.drivers.filter(d => d.status === 'On Trip').length;
    const utilization = activeVehicles
      ? Math.round((data.vehicles.filter(v => v.status === 'On Trip').length / activeVehicles) * 100)
      : 0;

    $('#kpiActive').textContent = activeVehicles;
    $('#kpiAvailable').textContent = available;
    $('#kpiShop').textContent = inShop;
    $('#kpiActiveTrips').textContent = activeTrips;
    $('#kpiPendingTrips').textContent = pending;
    $('#kpiDrivers').textContent = driversOnTrip;
    $('#kpiUtilization').textContent = `${utilization}%`;

    const today = new Date();
    const inThirtyDays = new Date(today);
    inThirtyDays.setDate(today.getDate() + 30);
    const dueLicenses = data.drivers.filter(d => {
      const expiry = new Date(`${d.licenseExpiry}T00:00:00`);
      return d.status === 'Suspended' || expiry < inThirtyDays;
    });
    const readyPairs = Math.min(available, data.drivers.filter(TransitOpsDrivers.isAssignable).length);

    $('#readyResources').textContent = `${readyPairs} ready pair${readyPairs === 1 ? '' : 's'}`;
    $('#licenseWatch').textContent = `${dueLicenses.length} license alert${dueLicenses.length === 1 ? '' : 's'}`;
    $('#nextAction').textContent = readyPairs
      ? 'Ready to create a safe trip'
      : available ? 'Add a compliant driver' : 'Add an available vehicle';

    const trips = data.trips.slice().reverse().slice(0, 6);
    $('#recentTrips').innerHTML = trips.map(t =>
      `<tr><td>${esc(t.code)}</td><td>${esc(t.source)} → ${esc(t.destination)}</td>` +
      `<td>${esc(vs[t.vehicleId]?.name || '—')}</td><td>${esc(ds[t.driverId]?.name || '—')}</td>` +
      `<td>${badge(t.status)}</td></tr>`
    ).join('');
    $('#recentTripsEmpty').style.display = trips.length ? 'none' : '';

    const statuses = ['Available', 'On Trip', 'In Shop', 'Retired'];
    const barColors = { Available: '#25c55a', 'On Trip': '#55a6ed', 'In Shop': '#f2b520', Retired: '#f05151' };
    $('#vehicleStatus').innerHTML = statuses.map(s => {
      const n = data.vehicles.filter(v => v.status === s).length;
      const p = data.vehicles.length ? Math.round(n / data.vehicles.length * 100) : 0;
      return `<div class="progress-row"><span>${s}</span><div class="bar">` +
        `<i style="width:${p}%;--bar:${barColors[s]}"></i></div><b>${n}</b></div>`;
    }).join('');
  }
};
