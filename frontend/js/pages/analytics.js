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

  renderActivityChart(data) {
    const { $, money } = TransitOpsUI;
    const today = new Date();
    const days = Array.from({ length: 7 }, (_, offset) => {
      const date = new Date(today);
      date.setDate(today.getDate() - (6 - offset));
      const key = date.toISOString().slice(0, 10);
      return {
        key,
        label: date.toLocaleDateString('en-IN', { weekday: 'short' }),
        cost: 0
      };
    });
    const dailyCosts = new Map(days.map(day => [day.key, day]));
    [...data.fuel, ...data.maintenance, ...data.expenses].forEach(record => {
      if (dailyCosts.has(record.date)) dailyCosts.get(record.date).cost += Number(record.cost || 0);
    });

    const maxCost = Math.max(...days.map(day => day.cost), 1);
    $('#activityChart').innerHTML = days.map(day => {
      const height = day.cost ? Math.max(12, Math.round(day.cost / maxCost * 100)) : 4;
      return `<div class="chart-column" title="${day.label}: ${money(day.cost)}">` +
        `<span class="chart-value">${day.cost ? money(day.cost) : ''}</span>` +
        `<i style="height:${height}%"></i><b>${day.label}</b></div>`;
    }).join('');
  },

  renderCostlyVehicles(rows) {
    const { $, esc, money } = TransitOpsUI;
    const ranked = rows.slice().sort((a, b) => b.cost - a.cost).slice(0, 4);
    const maxCost = Math.max(...ranked.map(row => row.cost), 1);
    const colors = ['red', 'orange', 'blue', 'yellow'];
    $('#costlyVehicles').innerHTML = ranked.map((row, index) => {
      const percentage = row.cost ? Math.max(8, Math.round(row.cost / maxCost * 100)) : 0;
      return `<div class="costly-row"><div><b>${esc(row.vehicle.registration)}</b>` +
        `<span>${esc(row.vehicle.name)}</span></div><strong>${money(row.cost)}</strong>` +
        `<div class="cost-track"><i class="${colors[index]}" style="width:${percentage}%"></i></div></div>`;
    }).join('');
    $('#reportEmpty').style.display = rows.length ? 'none' : '';
  },

  render() {
    const { $, money } = TransitOpsUI;
    const data = TransitOpsData.get();
    const rows = this.reportData();
    const totalCost = rows.reduce((sum, row) => sum + row.cost, 0);
    const totalFuel = rows.reduce((sum, row) => sum + row.liters, 0);
    const totalDistance = rows.reduce((sum, row) => sum + row.distance, 0);
    const active = rows.filter(row => row.vehicle.status !== 'Retired').length;
    const onTrip = rows.filter(row => row.vehicle.status === 'On Trip').length;
    const averageRoi = rows.length ? rows.reduce((sum, row) => sum + row.roi, 0) / rows.length : 0;

    $('#reportCost').textContent = money(totalCost);
    $('#reportEfficiency').textContent = totalFuel ? `${(totalDistance / totalFuel).toFixed(1)} km/L` : '—';
    $('#reportUtilization').textContent = active ? `${Math.round(onTrip / active * 100)}%` : '0%';
    $('#reportRoi').textContent = rows.length ? `${averageRoi.toFixed(2)}%` : '—';

    this.renderActivityChart(data);
    this.renderCostlyVehicles(rows);
  },

  exportCsv() {
    const rows = this.reportData();
    const header = ['Registration', 'Vehicle', 'Fuel Cost', 'Maintenance Cost', 'Other Expense', 'Operational Cost', 'Fuel Efficiency', 'ROI'];
    const values = rows.map(row => [
      row.vehicle.registration, row.vehicle.name, row.fuelCost, row.maintenanceCost,
      row.otherCost, row.cost, row.liters ? (row.distance / row.liters).toFixed(2) : '', row.roi.toFixed(2)
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
    $('#exportCsv')?.addEventListener('click', () => this.exportCsv());
  }
};
