/* Driver compliance helpers. */
window.TransitOpsDrivers = {
  isAssignable(driver) {
    const today = new Date().toISOString().slice(0, 10);
    return driver?.status === 'Available' && driver.licenseExpiry >= today;
  },
  isSafetyScoreValid(score) { return Number(score) >= 0 && Number(score) <= 100; }
};
