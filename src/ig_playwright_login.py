# ig_playwright_login.py

import asyncio
from playwright.async_api import async_playwright
import json
import sys

async def login_and_save_cookies(username, password, cookie_file="playwright_ig_cookies.json"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.instagram.com/accounts/login/")
        await page.wait_for_timeout(2000)

        await page.fill("input[name='username']", username)
        await page.fill("input[name='password']", password)
        await page.click("button[type='submit']")

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(5000)

        cookies = await context.cookies()
        with open(cookie_file, "w") as f:
            json.dump(cookies, f)

        print(f"✅ Cookies saved to {cookie_file}")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ig_playwright_login.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]

    asyncio.run(login_and_save_cookies(username, password))