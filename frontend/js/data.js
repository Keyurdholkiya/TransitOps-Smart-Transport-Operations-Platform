/* Central data store — swap TransitOpsApi for fetch when backend is ready. */
window.TransitOpsData = {
  empty() {
    return {
      vehicles: [],
      drivers: [],
      trips: [],
      maintenance: [],
      fuel: [],
      expenses: [],
      settings: {}
    };
  },

  get() {
    const stored = TransitOpsApi.read(TransitOpsConfig.storageKey, {});
    return { ...this.empty(), ...stored };
  },

  save(data) {
    TransitOpsApi.write(TransitOpsConfig.storageKey, data);
  },

  vehiclesById(data) {
    return Object.fromEntries(data.vehicles.map(v => [v.id, v]));
  },

  driversById(data) {
    return Object.fromEntries(data.drivers.map(d => [d.id, d]));
  }
};
