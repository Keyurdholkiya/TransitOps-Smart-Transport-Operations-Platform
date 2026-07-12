/* Trip lifecycle and capacity validation definitions. */
window.TransitOpsTrips = {
  lifecycle: ['Draft', 'Dispatched', 'Completed', 'Cancelled'],
  cargoFits(cargoKg, capacityKg) { return Number(cargoKg) > 0 && Number(cargoKg) <= Number(capacityKg); },
  canDispatch({ vehicle, driver, cargoKg }) { return vehicle?.status === 'Available' && driver?.status === 'Available' && this.cargoFits(cargoKg, vehicle.capacity); }
};
