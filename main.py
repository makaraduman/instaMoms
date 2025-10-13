import subprocess
import os
import time

# === 🔧 CONFIGURATION ===
USERNAME = input("Enter your Instagram username: ")
PASSWORD = input("Enter your Instagram password: ")
COOKIE_FILE = "playwright_ig_cookies.json"
SESSION_FILE = f"session-{USERNAME}"

# === Step 0: Clean up any old cookie file ===
if os.path.exists(COOKIE_FILE):
    os.remove(COOKIE_FILE)
    print(f"🧹 Deleted old cookie file: {COOKIE_FILE}")

# Step 1: Log in with Playwright
print("\n🔐 Step 1: Log in using Playwright...")
subprocess.run(["python", "src/ig_playwright_login.py", USERNAME, PASSWORD], check=True)

# === Step 2: Convert Cookies to Session ===
print("\n🔄 Step 2: Convert cookies to session file...")
subprocess.run(["python", "src/convert_cookies.py", USERNAME, COOKIE_FILE, SESSION_FILE], check=True)

# === Step 3: Run Scraper ===
print("\n📥 Step 3: Start scraping with session...")
subprocess.run(["python", "src/scraper.py", SESSION_FILE], check=True)

print("\n✅ Done! Scraping pipeline completed successfully.")
