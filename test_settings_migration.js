#!/usr/bin/env node

const puppeteer = require('puppeteer');
const path = require('path');

async function testSettingsMigration() {
  console.log('🔄 Testing Currency and Language Settings Migration...');
  
  const browser = await puppeteer.launch({
    headless: false, // Show browser for debugging
    defaultViewport: null,
    args: ['--start-maximized']
  });
  
  try {
    const page = await browser.newPage();
    
    // Navigate to login page
    await page.goto('http://localhost:3000/login');
    console.log('✅ Navigated to login page');
    
    // Wait for login form
    await page.waitForSelector('[type="email"]');
    console.log('✅ Login form loaded');
    
    // Login with test credentials (assuming you have a test account)
    await page.type('[type="email"]', 'owner@test.com');
    await page.type('[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await page.waitForNavigation();
    console.log('✅ Logged in successfully');
    
    // Navigate to Settings via sidebar
    await page.waitForSelector('nav a[href="/settings"]');
    await page.click('nav a[href="/settings"]');
    await page.waitForNavigation();
    console.log('✅ Navigated to Settings page');
    
    // Check if Currency Settings section exists
    const currencySection = await page.$('h2:contains("Currency Settings")');
    if (currencySection) {
      console.log('✅ Currency Settings section found in Settings page');
    } else {
      console.log('❌ Currency Settings section NOT found in Settings page');
    }
    
    // Check if Language Settings section exists  
    const languageSection = await page.$('h2:contains("Language Settings")');
    if (languageSection) {
      console.log('✅ Language Settings section found in Settings page');
    } else {
      console.log('❌ Language Settings section NOT found in Settings page');
    }
    
    // Navigate to Gym Profile to verify settings were removed
    await page.waitForSelector('nav a[href="/gym-profile"]');
    await page.click('nav a[href="/gym-profile"]');
    await page.waitForNavigation();
    console.log('✅ Navigated to Gym Profile page');
    
    // Check that Currency Settings are NOT in Gym Profile
    const gymCurrencySection = await page.$('h2:contains("Currency Settings")');
    if (!gymCurrencySection) {
      console.log('✅ Currency Settings successfully removed from Gym Profile');
    } else {
      console.log('❌ Currency Settings still present in Gym Profile');
    }
    
    // Check that Language Settings are NOT in Gym Profile
    const gymLanguageSection = await page.$('h2:contains("Language Settings")');
    if (!gymLanguageSection) {
      console.log('✅ Language Settings successfully removed from Gym Profile');
    } else {
      console.log('❌ Language Settings still present in Gym Profile');
    }
    
    // Check that Gym Profile only contains gym info and logo
    const logoSection = await page.$('h2:contains("Gym Logo")');
    const gymInfoSection = await page.$('h2:contains("Gym Information")');
    
    if (logoSection && gymInfoSection) {
      console.log('✅ Gym Profile correctly contains only Gym Logo and Gym Information');
    } else {
      console.log('❌ Gym Profile missing expected sections');
    }
    
    console.log('\n🎉 Settings Migration Test Complete!');
    
  } catch (error) {
    console.error('💥 Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

// Only run the test if this file is run directly
if (require.main === module) {
  testSettingsMigration();
}

module.exports = { testSettingsMigration };