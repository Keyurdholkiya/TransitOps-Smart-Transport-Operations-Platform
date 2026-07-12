window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.maintenance = {
  render() {
    const { $, esc, dateText, money, badge, setEmpty } = TransitOpsUI;
    const data = TransitOpsData.get();
    const vs = TransitOpsData.vehiclesById(data);
    const rows = data.maintenance.slice().reverse();

    $('#maintenanceRows').innerHTML = rows.map(m =>
      `<tr><td>${esc(vs[m.vehicleId]?.registration || 'Deleted')}</td><td>${esc(m.type)}</td>` +
      `<td>${dateText(m.date)}</td><td>${money(m.cost)}</td><td>${badge(m.status)}</td>` +
      `<td>${m.status === 'Open'
        ? `<button class="small-btn" data-maintenance-close="${m.id}">Close log</button>`
        : '—'}</td></tr>`
    ).join('');
    setEmpty('#maintenanceRows', '#maintenanceEmpty', rows.length > 0);
  },

  init() {
    const { $, showNotice, fillVehicleSelect } = TransitOpsUI;
    fillVehicleSelect('#maintenanceVehicle', true);
    this.render();

    $('#maintenanceForm').addEventListener('submit', e => {
      e.preventDefault();
      const data = TransitOpsData.get();
      const vehicle = data.vehicles.find(v => v.id === $('#maintenanceVehicle').value);
      if (!vehicle || vehicle.status !== 'Available') {
        return showNotice('#maintenanceNotice', 'Select an Available vehicle.', true);
      }

      data.maintenance.push({
        id: TransitOpsUtils.createId(),
        vehicleId: vehicle.id,
        type: $('#maintenanceType').value.trim(),
        date: $('#maintenanceDate').value,
        cost: Number($('#maintenanceCost').value),
        notes: $('#maintenanceNotes').value.trim(),
        status: 'Open'
      });
      vehicle.status = 'In Shop';

      TransitOpsData.save(data);
      $('#maintenanceForm').reset();
      fillVehicleSelect('#maintenanceVehicle', true);
      this.render();
      showNotice('#maintenanceNotice', 'Maintenance log opened. Vehicle is now In Shop.');
    });

    document.addEventListener('click', e => {
      const maintenanceId = e.target.dataset.maintenanceClose;
      if (!maintenanceId) return;

      const data = TransitOpsData.get();
      const log = data.maintenance.find(x => x.id === maintenanceId);
      const vehicle = data.vehicles.find(x => x.id === log?.vehicleId);
      if (!log) return;

      log.status = 'Closed';
      if (vehicle?.status === 'In Shop') vehicle.status = 'Available';

      TransitOpsData.save(data);
      fillVehicleSelect('#maintenanceVehicle', true);
      this.render();
    });
  }
};
