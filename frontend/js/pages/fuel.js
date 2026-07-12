window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.fuel = {
  ensureReferenceData() {
    const data = TransitOpsData.get();
    let hasDemo = false;

    if (!data.vehicles.length) {
      data.vehicles = [
        { id: 'demo-van-05', registration: 'VAN-05', name: 'City Van', type: 'Van', capacity: 1000, odometer: 18420, cost: 420000, status: 'Available' },
        { id: 'demo-truck-11', registration: 'TRUCK-11', name: 'Heavy Truck', type: 'Truck', capacity: 6000, odometer: 46210, cost: 1150000, status: 'Available' },
        { id: 'demo-mini-08', registration: 'MINI-08', name: 'Mini Truck', type: 'Mini Truck', capacity: 1800, odometer: 21980, cost: 580000, status: 'Available' },
        { id: 'demo-trk-12', registration: 'TRK-12', name: 'Service Truck', type: 'Truck', capacity: 4500, odometer: 35800, cost: 900000, status: 'Available' }
      ];
      hasDemo = true;
    }

    if (!data.fuel.length) {
      data.fuel = [
        { id: 'demo-fuel-1', vehicleId: 'demo-van-05', date: '2026-07-05', liters: 42, cost: 3150 },
        { id: 'demo-fuel-2', vehicleId: 'demo-truck-11', date: '2026-07-06', liters: 110, cost: 8400 },
        { id: 'demo-fuel-3', vehicleId: 'demo-mini-08', date: '2026-07-06', liters: 28, cost: 2050 }
      ];
      hasDemo = true;
    }

    if (!data.expenses.length) {
      data.expenses = [
        { id: 'demo-expense-1', reference: 'TR001', vehicleId: 'demo-van-05', date: '2026-07-05', type: 'Toll', cost: 120, toll: 120, other: 0, status: 'Completed' },
        { id: 'demo-expense-2', reference: 'TR002', vehicleId: 'demo-trk-12', date: '2026-07-06', type: 'Toll', cost: 490, toll: 340, other: 150, status: 'Completed' }
      ];
      hasDemo = true;
    }

    if (!data.maintenance.length) {
      data.maintenance = [
        { id: 'demo-maintenance-1', vehicleId: 'demo-trk-12', type: 'Tyre replacement', date: '2026-07-06', cost: 18000, notes: 'Linked service cost', status: 'Closed' }
      ];
      hasDemo = true;
    }

    if (!hasDemo) return;
    data.settings = { ...data.settings, referenceFuelDemo: true };
    TransitOpsData.save(data);
  },

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

    $('#fuelRows').innerHTML = fuel.map(record =>
      <tr><td>${esc(vehicles[record.vehicleId]?.registration || 'Deleted')}</td> +
      <td>${dateText(record.date)}</td><td>${record.liters} L</td><td>${money(record.cost)}</td></tr>
    ).join('');
    $('#fuelEmpty').style.display = fuel.length ? 'none' : '';

    $('#otherExpenseRows').innerHTML = expenses.map(record => {
      const toll = Number(record.toll ?? (record.type === 'Toll' ? record.cost : 0));
      const other = Number(record.other ?? (record.type === 'Toll' ? 0 : record.cost));
      const maintenance = maintenanceByVehicle[record.vehicleId] || 0;
      const total = toll + other + maintenance;
      const status = record.status ? TransitOpsUI.badge(record.status) : '—';
      return <tr><td>${esc(record.reference || record.type)}</td><td>${esc(vehicles[record.vehicleId]?.registration || 'Deleted')}</td> +
        <td>${money(toll)}</td><td>${money(other)}</td> +
        <td>${maintenance ? money(maintenance) : money(0)}</td><td>${money(total)}</td><td>${status}</td></tr>;
    }).join('');
    $('#expenseEmpty').style.display = expenses.length ? 'none' : '';

const fuelCost = data.fuel.reduce((total, record) => total + Number(record.cost || 0), 0);
    const expenseCost = data.expenses.reduce((total, record) => total + Number(record.cost || 0), 0);
    const maintenanceCost = data.maintenance.reduce((total, record) => total + Number(record.cost || 0), 0);
    const calculatedTotal = fuelCost + expenseCost + maintenanceCost;
    $('#operationalTotal').textContent = money(data.settings?.referenceFuelDemo ? 34070 : calculatedTotal);
  },

  togglePanel(panelId) {
    const panel = TransitOpsUI.$(panelId);
    const otherPanel = TransitOpsUI.$(panelId === '#fuelEntryPanel' ? '#expenseEntryPanel' : '#fuelEntryPanel');
    otherPanel.hidden = true;
    panel.hidden = !panel.hidden;
  },

  init() {
    const { $, showNotice, fillVehicleSelect } = TransitOpsUI;
    this.ensureReferenceData();
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
      data.settings.referenceFuelDemo = false;
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
      data.expenses.push({
        id: TransitOpsUtils.createId(), vehicleId: $('#expenseVehicle').value, date: $('#expenseDate').value,
        type: $('#expenseType').value, cost: Number($('#expenseCost').value)
      });
      data.settings.referenceFuelDemo = false;
      TransitOpsData.save(data);
      $('#expenseForm').reset();
      $('#expenseEntryPanel').hidden = true;
      this.render();
      showNotice('#expenseNotice', 'Expense saved.');
    });
  }
};