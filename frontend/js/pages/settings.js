window.TransitOpsPages = window.TransitOpsPages || {};

window.TransitOpsPages.settings = {
  init() {
    const { $, showNotice } = TransitOpsUI;
    const settings = TransitOpsData.get().settings || {};

    $('#organizationName').value = settings.organizationName || '';
    $('#timezone').value = settings.timezone || 'Asia/Kolkata';
    $('#language').value = settings.language || 'English';

    $('#settingsForm').addEventListener('submit', e => {
      e.preventDefault();
      const data = TransitOpsData.get();
      data.settings = {
        organizationName: $('#organizationName').value.trim(),
        timezone: $('#timezone').value,
        language: $('#language').value
      };
      TransitOpsData.save(data);
      showNotice('#settingsNotice', 'Settings saved.');
    });
  }
};
