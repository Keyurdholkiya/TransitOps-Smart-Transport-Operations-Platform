window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.fuel = {
  render() {
    const { $, esc, dateText, money, setEmpty } = TransitOpsUI;
    const data = TransitOpsData.get();
    const vs = TransitOpsData.vehiclesById(data);
    const records = [
      ...data.fuel.map(x => ({ ...x, kind: 'Fuel' })),
      ...data.expenses.map(x => ({ ...x, kind: x.type }))
    ].sort((a, b) => b.date.localeCompare(a.date));

    $('#expenseRows').innerHTML = records.map(x =>
      `<tr><td>${esc(x.kind)}</td><td>${esc(vs[x.vehicleId]?.registration || 'Deleted')}</td>` +
      `<td>${dateText(x.date)}</td><td>${x.liters ? `${x.liters} L` : '—'}</td>` +
      `<td>${money(x.cost)}</td>` +
      `<td><button class="danger-btn" data-cost-delete="${x.kind === 'Fuel' ? 'fuel' : 'expense'}:${x.id}">Delete</button></td></tr>`
    ).join('');
    setEmpty('#expenseRows', '#expenseEmpty', records.length > 0);
  },

  init() {
    const { $, showNotice, fillVehicleSelect } = TransitOpsUI;
    fillVehicleSelect('#fuelVehicle');
    fillVehicleSelect('#expenseVehicle');
    this.render();

    $('#fuelForm').addEventListener('submit', e => {
      e.preventDefault();
      const data = TransitOpsData.get();
      if (!$('#fuelVehicle').value) {
        return showNotice('#fuelNotice', 'Select a vehicle first.', true);
      }
      data.fuel.push({
        id: TransitOpsUtils.createId(),
        vehicleId: $('#fuelVehicle').value,
        date: $('#fuelDate').value,
        liters: Number($('#fuelLiters').value),
        cost: Number($('#fuelCost').value)
      });
      TransitOpsData.save(data);
      $('#fuelForm').reset();
      this.render();
      showNotice('#fuelNotice', 'Fuel log saved.');
    });

    $('#expenseForm').addEventListener('submit', e => {
      e.preventDefault();
      const data = TransitOpsData.get();
      if (!$('#expenseVehicle').value) {
        return showNotice('#expenseNotice', 'Select a vehicle first.', true);
      }
      data.expenses.push({
        id: TransitOpsUtils.createId(),
        vehicleId: $('#expenseVehicle').value,
        date: $('#expenseDate').value,
        type: $('#expenseType').value,
        cost: Number($('#expenseCost').value)
      });
      TransitOpsData.save(data);
      $('#expenseForm').reset();
      this.render();
      showNotice('#expenseNotice', 'Expense saved.');
    });

    document.addEventListener('click', e => {
      const ref = e.target.dataset.costDelete;
      if (!ref) return;
      const [type, recordId] = ref.split(':');
      const data = TransitOpsData.get();
      const key = type === 'fuel' ? 'fuel' : 'expenses';
      data[key] = data[key].filter(x => x.id !== recordId);
      TransitOpsData.save(data);
      this.render();
    });
  }
};
