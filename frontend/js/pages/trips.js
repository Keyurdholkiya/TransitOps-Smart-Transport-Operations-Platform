window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.trips = {
  fillOptions() {
    const { $, esc } = TransitOpsUI;
    const data = TransitOpsData.get();
    const vehicles = data.vehicles.filter(v => v.status === 'Available');
    const drivers = data.drivers.filter(TransitOpsDrivers.isAssignable);

    $('#tripVehicle').innerHTML = vehicles.length
      ? `<option value="">Select available vehicle</option>${vehicles.map(v =>
          `<option value="${v.id}">${esc(v.registration)} · ${esc(v.name)} · ${v.capacity} kg</option>`
        ).join('')}`
      : '<option value="">No available vehicles</option>';

    $('#tripDriver').innerHTML = drivers.length
      ? `<option value="">Select compliant driver</option>${drivers.map(d =>
          `<option value="${d.id}">${esc(d.name)} · ${esc(d.license)}</option>`
        ).join('')}`
      : '<option value="">No compliant drivers</option>';

    this.renderValidation();
  },

  setRule(id, state, label) {
    const rule = TransitOpsUI.$(id);
    if (!rule) return;
    rule.className = `rule-check ${state}`;
    rule.querySelector('.rule-icon').textContent = state === 'pass' ? '✓' : state === 'fail' ? '!' : '○';
    rule.querySelector('b').textContent = label;
  },

  renderValidation() {
    const { $ } = TransitOpsUI;
    const data = TransitOpsData.get();
    const vehicle = data.vehicles.find(v => v.id === $('#tripVehicle')?.value);
    const driver = data.drivers.find(d => d.id === $('#tripDriver')?.value);
    const cargo = Number($('#tripCargo')?.value || 0);

    const vehiclePass = vehicle?.status === 'Available';
    const driverPass = driver?.status === 'Available';
    const licensePass = Boolean(driver) && TransitOpsDrivers.isAssignable(driver);

    this.setRule('#vehicleRule', vehicle ? (vehiclePass ? 'pass' : 'fail') : 'waiting',
      vehicle ? (vehiclePass ? 'Pass' : 'Blocked') : 'Waiting');
    this.setRule('#driverRule', driver ? (driverPass ? 'pass' : 'fail') : 'waiting',
      driver ? (driverPass ? 'Pass' : 'Blocked') : 'Waiting');
    this.setRule('#licenseRule', driver ? (licensePass ? 'pass' : 'fail') : 'waiting',
      driver ? (licensePass ? 'Pass' : 'Expired') : 'Waiting');

    const cargoText = $('#cargoRuleText');
    if (!vehicle || !cargo) {
      if (cargoText) cargoText.textContent = 'Enter cargo weight to check capacity.';
      this.setRule('#cargoRule', 'waiting', 'Waiting');
    } else {
      const fits = TransitOpsTrips.cargoFits(cargo, vehicle.capacity);
      if (cargoText) cargoText.textContent = `${cargo} kg cargo / ${vehicle.capacity} kg maximum capacity.`;
      this.setRule('#cargoRule', fits ? 'pass' : 'fail', fits ? 'Pass' : 'Over limit');
    }
  },

  render() {
    const { $, esc, badge, setEmpty } = TransitOpsUI;
    const data = TransitOpsData.get();
    const vs = TransitOpsData.vehiclesById(data);
    const ds = TransitOpsData.driversById(data);
    const rows = data.trips.slice().reverse();

    $('#tripRows').innerHTML = rows.map(t =>
      `<tr><td>${esc(t.code)}</td><td>${esc(t.source)} → ${esc(t.destination)}</td>` +
      `<td>${esc(vs[t.vehicleId]?.registration || 'Deleted')}</td>` +
      `<td>${esc(ds[t.driverId]?.name || 'Deleted')}</td>` +
      `<td>${t.cargo} kg</td><td>${t.distance} km</td><td>${badge(t.status)}</td>` +
      `<td><div class="table-actions">` +
      (t.status === 'Draft'
        ? `<button class="small-btn" data-trip-dispatch="${t.id}">Dispatch</button>` +
          `<button class="danger-btn" data-trip-cancel="${t.id}">Delete</button>`
        : '') +
      (t.status === 'Dispatched'
        ? `<button class="small-btn" data-trip-complete="${t.id}">Complete</button>` +
          `<button class="danger-btn" data-trip-cancel="${t.id}">Cancel</button>`
        : '') +
      `</div></td></tr>`
    ).join('');
    setEmpty('#tripRows', '#tripEmpty', rows.length > 0);
  },

  create(dispatch) {
    const { $, showNotice } = TransitOpsUI;
    const data = TransitOpsData.get();
    const vehicle = data.vehicles.find(v => v.id === $('#tripVehicle').value);
    const driver = data.drivers.find(d => d.id === $('#tripDriver').value);
    const cargo = Number($('#tripCargo').value);

    if (!vehicle || !driver) {
      return showNotice('#tripNotice', 'Select an available vehicle and a compliant driver.', true);
    }
    if (!TransitOpsTrips.cargoFits(cargo, vehicle.capacity)) {
      return showNotice('#tripNotice', `Cargo weight cannot exceed ${vehicle.capacity} kg.`, true);
    }
    if (dispatch && !TransitOpsTrips.canDispatch({ vehicle, driver, cargoKg: cargo })) {
      return showNotice('#tripNotice', 'Selected vehicle or driver is no longer eligible for dispatch.', true);
    }

    const trip = {
      id: TransitOpsUtils.createId(),
      code: `TRP-${String(data.trips.length + 1).padStart(4, '0')}`,
      source: $('#tripSource').value.trim(),
      destination: $('#tripDestination').value.trim(),
      vehicleId: vehicle.id,
      driverId: driver.id,
      cargo,
      distance: Number($('#tripDistance').value),
      status: dispatch ? 'Dispatched' : 'Draft',
      createdAt: new Date().toISOString()
    };

    data.trips.push(trip);
    if (dispatch) {
      vehicle.status = 'On Trip';
      driver.status = 'On Trip';
    }

    TransitOpsData.save(data);
    $('#tripForm').reset();
    this.fillOptions();
    this.render();
    showNotice('#tripNotice', dispatch
      ? 'Trip dispatched. Vehicle and driver are now On Trip.'
      : 'Trip saved as Draft.');
  },

  transition(tripId, action) {
    const data = TransitOpsData.get();
    const trip = data.trips.find(t => t.id === tripId);
    if (!trip) return;

    const vehicle = data.vehicles.find(x => x.id === trip.vehicleId);
    const driver = data.drivers.find(x => x.id === trip.driverId);

    if (action === 'dispatch') {
      if (!TransitOpsTrips.canDispatch({ vehicle, driver, cargoKg: trip.cargo })) {
        return alert('This trip cannot be dispatched because its vehicle or driver is unavailable.');
      }
      trip.status = 'Dispatched';
      vehicle.status = 'On Trip';
      driver.status = 'On Trip';
    } else {
      trip.status = action === 'complete' ? 'Completed' : 'Cancelled';
      if (vehicle?.status === 'On Trip') vehicle.status = 'Available';
      if (driver?.status === 'On Trip') driver.status = 'Available';
    }

    TransitOpsData.save(data);
    this.fillOptions();
    this.render();
  },

  init() {
    const { $ } = TransitOpsUI;
    this.fillOptions();
    this.render();

    ['#tripVehicle', '#tripDriver', '#tripCargo'].forEach(selector => {
      $(selector).addEventListener('input', () => this.renderValidation());
    });

    $('#tripForm').addEventListener('submit', e => {
      e.preventDefault();
      this.create(true);
    });

    $('#saveDraft').addEventListener('click', () => {
      if (!$('#tripForm').reportValidity()) return;
      this.create(false);
    });

    document.addEventListener('click', e => {
      if (e.target.dataset.tripDispatch) this.transition(e.target.dataset.tripDispatch, 'dispatch');
      if (e.target.dataset.tripComplete) this.transition(e.target.dataset.tripComplete, 'complete');
      if (e.target.dataset.tripCancel) {
        const data = TransitOpsData.get();
        const trip = data.trips.find(t => t.id === e.target.dataset.tripCancel);
        if (!trip) return;
        if (trip.status === 'Draft') {
          data.trips = data.trips.filter(t => t.id !== trip.id);
          TransitOpsData.save(data);
          this.render();
        } else if (confirm('Cancel this dispatched trip?')) {
          this.transition(trip.id, 'cancel');
        }
      }
    });
  }
};
