window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.vehicles = {
  render() {
    const { $, esc, money, badge, setEmpty } = TransitOpsUI;
    const rows = TransitOpsData.get().vehicles;
    $('#vehicleRows').innerHTML = rows.map(v =>
      `<tr><td>${esc(v.registration)}</td><td>${esc(v.name)}</td><td>${esc(v.type)}</td>` +
      `<td>${esc(v.capacity)} kg</td><td>${Number(v.odometer).toLocaleString()} km</td>` +
      `<td>${money(v.cost)}</td><td>${badge(v.status)}</td>` +
      `<td><div class="table-actions">` +
      `<button class="secondary-btn" data-vehicle-edit="${v.id}">Edit</button>` +
      `<button class="danger-btn" data-vehicle-delete="${v.id}">Delete</button>` +
      `</div></td></tr>`
    ).join('');
    setEmpty('#vehicleRows', '#vehicleEmpty', rows.length > 0);
  },

  reset() {
    const { $ } = TransitOpsUI;
    $('#vehicleForm').reset();
    $('#vehicleId').value = '';
    $('#vehicleFormTitle').textContent = 'Register Vehicle';
    $('#vehicleCancel').hidden = true;
  },

  init() {
    const { $, showNotice } = TransitOpsUI;
    this.render();

    $('#vehicleForm').addEventListener('submit', e => {
      e.preventDefault();
      const data = TransitOpsData.get();
      const record = {
        id: $('#vehicleId').value || TransitOpsUtils.createId(),
        registration: TransitOpsVehicles.normalizeRegistration($('#registration').value),
        name: $('#vehicleName').value.trim(),
        type: $('#vehicleType').value.trim(),
        capacity: Number($('#capacity').value),
        odometer: Number($('#odometer').value),
        cost: Number($('#acquisitionCost').value),
        status: $('#vehicleState').value
      };

      if (data.vehicles.some(v => v.registration === record.registration && v.id !== record.id)) {
        return showNotice('#vehicleNotice', 'Registration number must be unique.', true);
      }

      const old = data.vehicles.find(v => v.id === record.id);
      if (old?.status === 'On Trip') {
        return showNotice('#vehicleNotice', 'An On Trip vehicle cannot be edited.', true);
      }

      if (old) Object.assign(old, record);
      else data.vehicles.push(record);

      TransitOpsData.save(data);
      this.reset();
      this.render();
      showNotice('#vehicleNotice', 'Vehicle saved successfully.');
    });

    $('#vehicleCancel').addEventListener('click', () => this.reset());

    document.addEventListener('click', e => {
      const editId = e.target.dataset.vehicleEdit;
      const deleteId = e.target.dataset.vehicleDelete;

      if (editId) {
        const v = TransitOpsData.get().vehicles.find(x => x.id === editId);
        if (!v) return;
        if (v.status === 'On Trip') {
          return showNotice('#vehicleNotice', 'Complete or cancel the trip before editing this vehicle.', true);
        }
        $('#vehicleId').value = v.id;
        $('#registration').value = v.registration;
        $('#vehicleName').value = v.name;
        $('#vehicleType').value = v.type;
        $('#capacity').value = v.capacity;
        $('#odometer').value = v.odometer;
        $('#acquisitionCost').value = v.cost;
        $('#vehicleState').value = v.status;
        $('#vehicleFormTitle').textContent = 'Edit Vehicle';
        $('#vehicleCancel').hidden = false;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }

      if (deleteId) {
        const data = TransitOpsData.get();
        const v = data.vehicles.find(x => x.id === deleteId);
        const hasActiveTrip = data.trips.some(t => t.vehicleId === deleteId && t.status === 'Dispatched');
        const hasOpenMaintenance = data.maintenance.some(m => m.vehicleId === deleteId && m.status === 'Open');
        if (hasActiveTrip || hasOpenMaintenance) {
          return showNotice('#vehicleNotice', 'This vehicle has an active trip or maintenance log and cannot be deleted.', true);
        }
        if (!confirm(`Delete ${v?.registration}?`)) return;
        data.vehicles = data.vehicles.filter(x => x.id !== deleteId);
        TransitOpsData.save(data);
        this.render();
      }
    });
  }
};
