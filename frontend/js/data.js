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
  },

  ensureReferenceData() {
    const data = this.get();
    let changed = false;

    if (!data.vehicles.length) {
      data.vehicles = [
        { id: 'demo-van-05', registration: 'VAN-05', name: 'City Van', type: 'Van', capacity: 1000, odometer: 18420, cost: 420000, status: 'Available' },
        { id: 'demo-truck-11', registration: 'TRUCK-11', name: 'Heavy Truck', type: 'Truck', capacity: 6000, odometer: 46210, cost: 1150000, status: 'On Trip' },
        { id: 'demo-mini-08', registration: 'MINI-08', name: 'Mini Truck', type: 'Mini Truck', capacity: 1800, odometer: 21980, cost: 580000, status: 'Available' },
        { id: 'demo-trk-12', registration: 'TRK-12', name: 'Service Truck', type: 'Truck', capacity: 4500, odometer: 35800, cost: 900000, status: 'In Shop' }
      ];
      changed = true;
    }

    if (!data.drivers.length) {
      data.drivers = [
        { id: 'demo-driver-1', name: 'Rajesh Kumar', license: 'DL-2024-1001', category: 'HMV', licenseExpiry: '2027-06-15', contact: '+91 9876543210', safety: 92, status: 'On Trip' },
        { id: 'demo-driver-2', name: 'Suresh Patel', license: 'DL-2023-2045', category: 'LMV', licenseExpiry: '2026-08-20', contact: '+91 9123456789', safety: 88, status: 'Available' },
        { id: 'demo-driver-3', name: 'Amit Singh', license: 'DL-2022-3310', category: 'HMV', licenseExpiry: '2026-12-01', contact: '+91 9988776655', safety: 95, status: 'Available' }
      ];
      changed = true;
    }

    if (!data.trips.length) {
      data.trips = [
        { id: 'demo-trip-1', code: 'TRP-0001', source: 'Mumbai Depot', destination: 'Pune Hub', vehicleId: 'demo-van-05', driverId: 'demo-driver-2', cargo: 800, distance: 148, status: 'Completed', createdAt: '2026-07-05T08:00:00Z' },
        { id: 'demo-trip-2', code: 'TRP-0002', source: 'Nashik Yard', destination: 'Mumbai Depot', vehicleId: 'demo-truck-11', driverId: 'demo-driver-1', cargo: 4500, distance: 165, status: 'Completed', createdAt: '2026-07-06T09:00:00Z' },
        { id: 'demo-trip-3', code: 'TRP-0003', source: 'Thane Hub', destination: 'Navi Mumbai', vehicleId: 'demo-mini-08', driverId: 'demo-driver-3', cargo: 1200, distance: 42, status: 'Completed', createdAt: '2026-07-08T10:00:00Z' },
        { id: 'demo-trip-4', code: 'TRP-0004', source: 'Pune Hub', destination: 'Nashik Yard', vehicleId: 'demo-truck-11', driverId: 'demo-driver-1', cargo: 5200, distance: 210, status: 'Dispatched', createdAt: '2026-07-11T07:30:00Z' }
      ];
      changed = true;
    }

    if (!data.fuel.length) {
      data.fuel = [
        { id: 'demo-fuel-1', vehicleId: 'demo-van-05', date: '2026-07-06', liters: 42, cost: 3150 },
        { id: 'demo-fuel-2', vehicleId: 'demo-truck-11', date: '2026-07-07', liters: 110, cost: 8400 },
        { id: 'demo-fuel-3', vehicleId: 'demo-mini-08', date: '2026-07-07', liters: 28, cost: 2050 },
        { id: 'demo-fuel-4', vehicleId: 'demo-van-05', date: '2026-07-08', liters: 38, cost: 2850 },
        { id: 'demo-fuel-5', vehicleId: 'demo-trk-12', date: '2026-07-09', liters: 95, cost: 7225 },
        { id: 'demo-fuel-6', vehicleId: 'demo-truck-11', date: '2026-07-10', liters: 105, cost: 7980 },
        { id: 'demo-fuel-7', vehicleId: 'demo-mini-08', date: '2026-07-11', liters: 32, cost: 2340 },
        { id: 'demo-fuel-8', vehicleId: 'demo-van-05', date: '2026-07-12', liters: 40, cost: 3000 }
      ];
      changed = true;
    }

    if (!data.expenses.length) {
      data.expenses = [
        { id: 'demo-expense-1', reference: 'TR001', vehicleId: 'demo-van-05', date: '2026-07-06', type: 'Toll', cost: 320, toll: 320, other: 0, status: 'Completed' },
        { id: 'demo-expense-2', reference: 'TR002', vehicleId: 'demo-trk-12', date: '2026-07-07', type: 'Toll', cost: 490, toll: 340, other: 150, status: 'Completed' },
        { id: 'demo-expense-3', reference: 'TR003', vehicleId: 'demo-truck-11', date: '2026-07-09', type: 'Parking', cost: 180, toll: 0, other: 180, status: 'Completed' },
        { id: 'demo-expense-4', reference: 'TR004', vehicleId: 'demo-mini-08', date: '2026-07-10', type: 'Permit', cost: 750, toll: 0, other: 750, status: 'Completed' },
        { id: 'demo-expense-5', reference: 'TR005', vehicleId: 'demo-van-05', date: '2026-07-11', type: 'Toll', cost: 210, toll: 210, other: 0, status: 'Completed' }
      ];
      changed = true;
    }

    if (!data.maintenance.length) {
      data.maintenance = [
        { id: 'demo-maintenance-1', vehicleId: 'demo-trk-12', type: 'Tyre replacement', date: '2026-07-07', cost: 18000, notes: 'Linked service cost', status: 'Closed' },
        { id: 'demo-maintenance-2', vehicleId: 'demo-truck-11', type: 'Oil change', date: '2026-07-09', cost: 4500, notes: 'Scheduled service', status: 'Closed' }
      ];
      changed = true;
    }

    if (!data.settings.organizationName) {
      data.settings = {
        ...data.settings,
        organizationName: 'TransitOps Fleet Services',
        timezone: 'Asia/Kolkata',
        language: 'English'
      };
      changed = true;
    }

    if (changed) this.save(data);
    return data;
  }
};
