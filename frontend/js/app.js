/* Application bootstrap — loads the correct page module based on data-page. */
(function boot() {
  if (!TransitOpsUI.setupHeader()) return;

  TransitOpsUI.setupSearch();
  TransitOpsData.ensureReferenceData();

  const page = document.body.dataset.page;
  const pages = window.TransitOpsPages || {};
  const handlers = {
    dashboard: () => pages.dashboard?.init(),
    vehicles: () => pages.vehicles?.init(),
    drivers: () => pages.drivers?.init(),
    trips: () => pages.trips?.init(),
    maintenance: () => pages.maintenance?.init(),
    fuel: () => pages.fuel?.init(),
    analytics: () => pages.analytics?.init(),
    settings: () => pages.settings?.init()
  };

  handlers[page]?.();
})();
