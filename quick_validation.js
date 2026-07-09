const fs = require('fs');

// Read the files
const gymProfile = fs.readFileSync('frontend/src/pages/GymProfilePage.jsx', 'utf8');
const gymSettings = fs.readFileSync('frontend/src/pages/GymOwnerSettingsPage.jsx', 'utf8');

console.log('=== GYM PROFILE PAGE ===');
console.log('Contains "Currency Settings":', gymProfile.includes('Currency Settings'));
console.log('Contains "Language Settings":', gymProfile.includes('Language Settings'));
console.log('Contains "Gym Logo":', gymProfile.includes('Gym Logo'));
console.log('Contains "Gym Information":', gymProfile.includes('Gym Information'));
console.log('Contains "handleCurrencyUpdate":', gymProfile.includes('handleCurrencyUpdate'));

console.log('\n=== GYM OWNER SETTINGS PAGE ===');
console.log('Contains "Currency Settings":', gymSettings.includes('Currency Settings'));
console.log('Contains "Language Settings":', gymSettings.includes('Language Settings'));
console.log('Contains "handleCurrencyUpdate":', gymSettings.includes('handleCurrencyUpdate'));
console.log('Contains "handleLanguageUpdate":', gymSettings.includes('handleLanguageUpdate'));
console.log('Contains "useCurrency":', gymSettings.includes('useCurrency'));
console.log('Contains "useTranslation":', gymSettings.includes('useTranslation'));

console.log('\n=== FIRST FEW LINES OF SETTINGS PAGE ===');
console.log(gymSettings.substring(0, 500) + '...');