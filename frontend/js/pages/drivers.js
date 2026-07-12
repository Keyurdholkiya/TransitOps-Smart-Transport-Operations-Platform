window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.drivers = {
  render() {
    const { $, esc, dateText, badge, setEmpty } = TransitOpsUI;
    const rows = TransitOpsData.get().drivers;
    $('#driverRows').innerHTML = rows.map(d =>
      `<tr><td>${esc(d.name)}</td><td>${esc(d.license)}</td><td>${esc(d.category)}</td>` +
      `<td>${dateText(d.licenseExpiry)}</td><td>${esc(d.contact)}</td>` +
      `<td>${esc(d.safety)}%</td><td>${badge(d.status)}</td>` +
      `<td><div class="table-actions">` +
      `<button class="secondary-btn" data-driver-edit="${d.id}">Edit</button>` +
      `<button class="danger-btn" data-driver-delete="${d.id}">Delete</button>` +
      `</div></td></tr>`
    ).join('');
    setEmpty('#driverRows', '#driverEmpty', rows.length > 0);
  },

  reset() {
    const { $ } = TransitOpsUI;
    $('#driverForm').reset();
    $('#driverId').value = '';
    $('#driverFormTitle').textContent = 'Add Driver';
    $('#driverCancel').hidden = true;
  },

  init() {
    const { $, showNotice } = TransitOpsUI;
    this.render();

    $('#driverForm').addEventListener('submit', e => {
      e.preventDefault();
      const data = TransitOpsData.get();
      const record = {
        id: $('#driverId').value || TransitOpsUtils.createId(),
        name: $('#driverName').value.trim(),
        license: $('#licenseNumber').value.trim().toUpperCase(),
        category: $('#licenseCategory').value.trim(),
        licenseExpiry: $('#licenseExpiry').value,
        contact: $('#driverContact').value.trim(),
        safety: Number($('#safetyScore').value),
        status: $('#driverState').value
      };

      if (data.drivers.some(d => d.license === record.license && d.id !== record.id)) {
        return showNotice('#driverNotice', 'License number must be unique.', true);
      }

      const old = data.drivers.find(d => d.id === record.id);
      if (old?.status === 'On Trip') {
        return showNotice('#driverNotice', 'An On Trip driver cannot be edited.', true);
      }

      if (old) Object.assign(old, record);
      else data.drivers.push(record);

      TransitOpsData.save(data);
      this.reset();
      this.render();
      showNotice('#driverNotice', 'Driver saved successfully.');
    });

    $('#driverCancel').addEventListener('click', () => this.reset());

    document.addEventListener('click', e => {
      const editId = e.target.dataset.driverEdit;
      const deleteId = e.target.dataset.driverDelete;

      if (editId) {
        const d = TransitOpsData.get().drivers.find(x => x.id === editId);
        if (d.status === 'On Trip') {
          return showNotice('#driverNotice', 'Complete or cancel the trip before editing this driver.', true);
        }
        $('#driverId').value = d.id;
        $('#driverName').value = d.name;
        $('#licenseNumber').value = d.license;
        $('#licenseCategory').value = d.category;
        $('#licenseExpiry').value = d.licenseExpiry;
        $('#driverContact').value = d.contact;
        $('#safetyScore').value = d.safety;
        $('#driverState').value = d.status;
        $('#driverFormTitle').textContent = 'Edit Driver';
        $('#driverCancel').hidden = false;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }

      if (deleteId) {
        const data = TransitOpsData.get();
        if (data.trips.some(t => t.driverId === deleteId && t.status === 'Dispatched')) {
          return showNotice('#driverNotice', 'This driver has an active trip and cannot be deleted.', true);
        }
        if (!confirm('Delete this driver?')) return;
        data.drivers = data.drivers.filter(x => x.id !== deleteId);
        TransitOpsData.save(data);
        this.render();
      }
    });
  }
};
