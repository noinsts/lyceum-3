function resetToDefault() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const defaultSheet = ss.getSheetByName('closed__');
  const modifySheet = ss.getSheetByName('templateDemo');
  const values = defaultSheet.getDataRange().getValues();
  modifySheet.getRange(1, 1, values.length, values[0].length).setValues(values);
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Admin Panel')
    .addItem('🔁 Reset to Default', 'resetToDefault')
    .addToUi();
}
