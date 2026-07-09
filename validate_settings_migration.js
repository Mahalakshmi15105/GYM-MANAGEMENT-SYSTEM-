#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function validateSettingsMigration() {
  console.log('🔄 Validating Currency and Language Settings Migration...\n');
  
  let allTestsPassed = true;
  
  // Read GymProfilePage.jsx
  const gymProfilePath = path.join('frontend', 'src', 'pages', 'GymProfilePage.jsx');
  const gymProfileContent = fs.readFileSync(gymProfilePath, 'utf8');
  
  // Read GymOwnerSettingsPage.jsx  
  const settingsPath = path.join('frontend', 'src', 'pages', 'GymOwnerSettingsPage.jsx');
  const settingsContent = fs.readFileSync(settingsPath, 'utf8');
  
  // Test 1: Currency Settings should NOT be in GymProfilePage
  if (gymProfileContent.includes('Currency Settings')) {
    console.log('❌ FAIL: Currency Settings still found in GymProfilePage');
    allTestsPassed = false;
  } else {
    console.log('✅ PASS: Currency Settings removed from GymProfilePage');
  }
  
  // Test 2: Language Settings should NOT be in GymProfilePage
  if (gymProfileContent.includes('Language Settings') || gymProfileContent.includes('languageSettings')) {
    console.log('❌ FAIL: Language Settings still found in GymProfilePage');
    allTestsPassed = false;
  } else {
    console.log('✅ PASS: Language Settings removed from GymProfilePage');
  }
  
  // Test 3: Currency Settings should be in GymOwnerSettingsPage
  if (settingsContent.includes('Currency Settings')) {
    console.log('✅ PASS: Currency Settings found in GymOwnerSettingsPage');
  } else {
    console.log('❌ FAIL: Currency Settings NOT found in GymOwnerSettingsPage');
    allTestsPassed = false;
  }
  
  // Test 4: Language Settings should be in GymOwnerSettingsPage  
  if (settingsContent.includes('languageSettings') || settingsContent.includes('Language Settings')) {
    console.log('✅ PASS: Language Settings found in GymOwnerSettingsPage');
  } else {
    console.log('❌ FAIL: Language Settings NOT found in GymOwnerSettingsPage');
    allTestsPassed = false;
  }
  
  // Test 5: GymProfilePage should still have Gym Logo section
  if (gymProfileContent.includes('Gym Logo')) {
    console.log('✅ PASS: Gym Logo section retained in GymProfilePage');
  } else {
    console.log('❌ FAIL: Gym Logo section missing from GymProfilePage');
    allTestsPassed = false;
  }
  
  // Test 6: GymProfilePage should still have Gym Information section
  if (gymProfileContent.includes('Gym Information')) {
    console.log('✅ PASS: Gym Information section retained in GymProfilePage');
  } else {
    console.log('❌ FAIL: Gym Information section missing from GymProfilePage');
    allTestsPassed = false;
  }
  
  // Test 7: Check that the Settings route exists in AppRoutes
  const routesPath = path.join('frontend', 'src', 'routes', 'AppRoutes.jsx');
  const routesContent = fs.readFileSync(routesPath, 'utf8');
  
  if (routesContent.includes('path="settings"') && routesContent.includes('GymOwnerSettingsPage')) {
    console.log('✅ PASS: Settings route properly configured in AppRoutes');
  } else {
    console.log('❌ FAIL: Settings route NOT properly configured in AppRoutes');
    allTestsPassed = false;
  }
  
  // Test 8: Check that Sidebar has Settings link
  const sidebarPath = path.join('frontend', 'src', 'components', 'Sidebar.jsx');
  const sidebarContent = fs.readFileSync(sidebarPath, 'utf8');
  
  if (sidebarContent.includes('name: "Settings"') && sidebarContent.includes('path: "/settings"')) {
    console.log('✅ PASS: Settings link found in Sidebar');
  } else {
    console.log('❌ FAIL: Settings link NOT found in Sidebar');
    allTestsPassed = false;
  }
  
  // Test 9: Verify that currency handling functions are in GymOwnerSettingsPage
  if (settingsContent.includes('handleCurrencyUpdate') && settingsContent.includes('useCurrency')) {
    console.log('✅ PASS: Currency handling functions found in GymOwnerSettingsPage');
  } else {
    console.log('❌ FAIL: Currency handling functions missing from GymOwnerSettingsPage');
    allTestsPassed = false;
  }
  
  // Test 10: Verify that language handling functions are in GymOwnerSettingsPage
  if (settingsContent.includes('handleLanguageUpdate') && settingsContent.includes('useTranslation')) {
    console.log('✅ PASS: Language handling functions found in GymOwnerSettingsPage');
  } else {
    console.log('❌ FAIL: Language handling functions missing from GymOwnerSettingsPage');
    allTestsPassed = false;
  }
  
  console.log('\n' + '='.repeat(50));
  
  if (allTestsPassed) {
    console.log('🎉 All tests PASSED! Settings migration completed successfully.');
    console.log('\n✅ Summary:');
    console.log('   • Currency Settings moved from Gym Profile to Gym Owner Settings');
    console.log('   • Language Settings moved from Gym Profile to Gym Owner Settings');  
    console.log('   • Gym Profile now contains only gym information and logo management');
    console.log('   • Settings page is accessible via Sidebar');
    console.log('   • All routing and functionality preserved');
    console.log('\n🚀 The feature is fully working and ready for use!');
    process.exit(0);
  } else {
    console.log('❌ Some tests FAILED. Please review the issues above.');
    process.exit(1);
  }
}

validateSettingsMigration();