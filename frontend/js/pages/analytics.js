window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.analytics = {
  reportData() {
    const data = TransitOpsData.get();
    return data.vehicles.map(vehicle => {
      const fuel = data.fuel.filter(x => x.vehicleId === vehicle.id);
      const maintenance = data.maintenance.filter(x => x.vehicleId === vehicle.id);
      const expenses = data.expenses.filter(x => x.vehicleId === vehicle.id);
      const trips = data.trips.filter(x => x.vehicleId === vehicle.id && x.status === 'Completed');

      const fuelCost = fuel.reduce((sum, x) => sum + x.cost, 0);
      const maintenanceCost = maintenance.reduce((sum, x) => sum + x.cost, 0);
      const otherCost = expenses.reduce((sum, x) => sum + x.cost, 0);
      const liters = fuel.reduce((sum, x) => sum + x.liters, 0);
      const distance = trips.reduce((sum, x) => sum + x.distance, 0);
      const cost = fuelCost + maintenanceCost + otherCost;
      const roi = vehicle.cost ? -cost / vehicle.cost * 100 : 0;

      return { vehicle, fuelCost, maintenanceCost, otherCost, liters, distance, cost, roi };
    });
  },

  render() {
    const { $, esc, money, setEmpty } = TransitOpsUI;
    const rows = this.reportData();
    const totalCost = rows.reduce((sum, x) => sum + x.cost, 0);
    const totalFuel = rows.reduce((sum, x) => sum + x.liters, 0);
    const totalDistance = rows.reduce((sum, x) => sum + x.distance, 0);
    const totalVehicles = rows.length;
    const onTrip = rows.filter(x => x.vehicle.status === 'On Trip').length;

    $('#reportCost').textContent = money(totalCost);
    $('#reportEfficiency').textContent = totalFuel ? `${(totalDistance / totalFuel).toFixed(2)} km/L` : '—';
    $('#reportUtilization').textContent = totalVehicles ? `${Math.round(onTrip / totalVehicles * 100)}%` : '0%';
    $('#reportDistance').textContent = `${totalDistance} km`;
    $('#reportFuel').textContent = `${totalFuel} L`;
    $('#reportRoi').textContent = rows.length
      ? `${(rows.reduce((sum, x) => sum + x.roi, 0) / rows.length).toFixed(2)}%`
      : '—';

    $('#reportRows').innerHTML = rows.map(x =>
      `<tr><td>${esc(x.vehicle.registration)} · ${esc(x.vehicle.name)}</td>` +
      `<td>${money(x.fuelCost)}</td><td>${money(x.maintenanceCost)}</td>` +
      `<td>${money(x.otherCost)}</td><td>${money(x.cost)}</td>` +
      `<td>${x.liters ? `${(x.distance / x.liters).toFixed(2)} km/L` : '—'}</td>` +
      `<td>${x.roi.toFixed(2)}%</td></tr>`
    ).join('');
    setEmpty('#reportRows', '#reportEmpty', rows.length > 0);
  },

  exportCsv() {
    const rows = this.reportData();
    const header = ['Registration', 'Vehicle', 'Fuel Cost', 'Maintenance Cost',
      'Other Expense', 'Operational Cost', 'Fuel Efficiency', 'ROI'];
    const values = rows.map(x => [
      x.vehicle.registration, x.vehicle.name, x.fuelCost, x.maintenanceCost,
      x.otherCost, x.cost, x.liters ? (x.distance / x.liters).toFixed(2) : '', x.roi.toFixed(2)
    ]);
    const csv = [header, ...values]
      .map(row => row.map(value => `"${String(value).replace(/"/g, '""')}"`).join(','))
      .join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'transitops-report.csv';
    anchor.click();
    URL.revokeObjectURL(url);
  },

  init() {
    const { $ } = TransitOpsUI;
    this.render();
    $('#exportCsv').addEventListener('click', () => this.exportCsv());
  }
};
