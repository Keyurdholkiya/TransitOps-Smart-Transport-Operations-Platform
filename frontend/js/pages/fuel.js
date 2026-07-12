window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.fuel = {
  render() {
    const { $, esc, dateText, money } = TransitOpsUI;
    const data = TransitOpsData.get();
    const vehicles = TransitOpsData.vehiclesById(data);
    const fuel = data.fuel.slice().sort((a, b) => b.date.localeCompare(a.date));
    const expenses = data.expenses.slice().sort((a, b) => b.date.localeCompare(a.date));
    const maintenanceByVehicle = data.maintenance.reduce((totals, record) => {
      totals[record.vehicleId] = (totals[record.vehicleId] || 0) + Number(record.cost || 0);
      return totals;
    }, {});
    const maintenanceShown = new Set();

    $('#fuelRows').innerHTML = fuel.map(record =>
      `<tr><td>${esc(vehicles[record.vehicleId]?.registration || 'Deleted')}</td>` +
      `<td>${dateText(record.date)}</td><td>${record.liters} L</td><td>${money(record.cost)}</td>` +
      `<td><button class="danger-btn" data-cost-delete="fuel:${record.id}">Delete</button></td></tr>`
    ).join('');
    $('#fuelEmpty').style.display = fuel.length ? 'none' : '';

    const expenseRows = expenses.map(record => {
      const toll = Number(record.toll ?? (record.type === 'Toll' ? record.cost : 0));
      const other = Number(record.other ?? (record.type === 'Toll' ? 0 : record.cost));
      const maintenance = maintenanceShown.has(record.vehicleId)
        ? 0
        : (maintenanceByVehicle[record.vehicleId] || 0);
      maintenanceShown.add(record.vehicleId);
      const total = toll + other + maintenance;
      const status = record.status ? TransitOpsUI.badge(record.status) : '—';
      return `<tr><td>${esc(record.reference || record.type)}</td><td>${esc(vehicles[record.vehicleId]?.registration || 'Deleted')}</td>` +
        `<td>${money(toll)}</td><td>${money(other)}</td>` +
        `<td>${maintenance ? money(maintenance) : money(0)}</td><td>${money(total)}</td><td>${status}</td>` +
        `<td><button class="danger-btn" data-cost-delete="expense:${record.id}">Delete</button></td></tr>`;
    });

    Object.entries(maintenanceByVehicle).forEach(([vehicleId, maintenanceCost]) => {
      if (maintenanceShown.has(vehicleId)) return;
      expenseRows.push(
        `<tr><td>Maintenance</td><td>${esc(vehicles[vehicleId]?.registration || 'Deleted')}</td>` +
        `<td>${money(0)}</td><td>${money(0)}</td>` +
        `<td>${money(maintenanceCost)}</td><td>${money(maintenanceCost)}</td><td>—</td><td>—</td></tr>`
      );
    });

    $('#otherExpenseRows').innerHTML = expenseRows.join('');
    $('#expenseEmpty').style.display = expenseRows.length ? 'none' : '';

    const fuelCost = data.fuel.reduce((total, record) => total + Number(record.cost || 0), 0);
    const expenseCost = data.expenses.reduce((total, record) => total + Number(record.cost || 0), 0);
    const maintenanceCost = data.maintenance.reduce((total, record) => total + Number(record.cost || 0), 0);
    $('#operationalTotal').textContent = money(fuelCost + expenseCost + maintenanceCost);
  },

  togglePanel(panelId) {
    const panel = TransitOpsUI.$(panelId);
    const otherPanel = TransitOpsUI.$(panelId === '#fuelEntryPanel' ? '#expenseEntryPanel' : '#fuelEntryPanel');
    otherPanel.hidden = true;
    panel.hidden = !panel.hidden;
  },

  init() {
    const { $, showNotice, fillVehicleSelect } = TransitOpsUI;
    fillVehicleSelect('#fuelVehicle');
    fillVehicleSelect('#expenseVehicle');
    this.render();

    $('#showFuelForm').addEventListener('click', () => this.togglePanel('#fuelEntryPanel'));
    $('#showExpenseForm').addEventListener('click', () => this.togglePanel('#expenseEntryPanel'));
    document.querySelectorAll('[data-close-entry]').forEach(button => button.addEventListener('click', event => {
      event.currentTarget.closest('.fuel-entry-panel').hidden = true;
    }));

    $('#fuelForm').addEventListener('submit', event => {
      event.preventDefault();
      const data = TransitOpsData.get();
      if (!$('#fuelVehicle').value) return showNotice('#fuelNotice', 'Select a vehicle first.', true);
      data.fuel.push({
        id: TransitOpsUtils.createId(), vehicleId: $('#fuelVehicle').value, date: $('#fuelDate').value,
        liters: Number($('#fuelLiters').value), cost: Number($('#fuelCost').value)
      });
      TransitOpsData.save(data);
      $('#fuelForm').reset();
      $('#fuelEntryPanel').hidden = true;
      this.render();
      showNotice('#fuelNotice', 'Fuel log saved.');
    });

    $('#expenseForm').addEventListener('submit', event => {
      event.preventDefault();
      const data = TransitOpsData.get();
      if (!$('#expenseVehicle').value) return showNotice('#expenseNotice', 'Select a vehicle first.', true);
      const cost = Number($('#expenseCost').value);
      const type = $('#expenseType').value;
      data.expenses.push({
        id: TransitOpsUtils.createId(),
        vehicleId: $('#expenseVehicle').value,
        date: $('#expenseDate').value,
        type,
        cost,
        toll: type === 'Toll' ? cost : 0,
        other: type === 'Toll' ? 0 : cost,
        status: 'Completed'
      });
      TransitOpsData.save(data);
      $('#expenseForm').reset();
      $('#expenseEntryPanel').hidden = true;
      this.render();
      showNotice('#expenseNotice', 'Expense saved.');
    });

    document.addEventListener('click', event => {
      const reference = event.target.dataset.costDelete;
      if (!reference) return;
      const [type, recordId] = reference.split(':');
      if (!confirm('Delete this record?')) return;
      const data = TransitOpsData.get();
      const key = type === 'fuel' ? 'fuel' : 'expenses';
      data[key] = data[key].filter(record => record.id !== recordId);
      TransitOpsData.save(data);
      this.render();
    });
  }
};
