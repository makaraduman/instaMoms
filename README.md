# 📸 Enhanced Instagram Scraper

This project combines **Playwright** and **Instaloader** to scrape Instagram post metadata for academic research and data analysis. It simulates human login through a browser using Playwright, then reuses the authenticated session to power Instaloader — enabling large-scale, reliable scraping.

---

## ⚙️ Features

- ✅ One-command scraping via `main.py`
- ✅ Login to Instagram using Playwright (real browser automation)
- ✅ Convert browser cookies into a valid Instaloader session
- ✅ Scrape post and profile metadata into JSON + CSV
- ✅ Timestamped filenames for all outputs
- ✅ Modular architecture (each step can run independently)
- ✅ Headless or interactive login support
- ✅ Clean and extendable Python code

---

## Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/insta-scraper.git
cd insta-scraper

2. Create a Virtual Environment
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt
python -m playwright install

Usage
1. Run the Script
python main.py

2. Login
Enter your Instagram username:
Enter your Instagram password:

This will:

1. Remove old cookies
2. Log in using Playwright
3. Convert cookies into an Instaloader session
4. Scrape all target accounts defined in scraper.py
5. Save results in academic_data_enhanced/ and summary CSVs

Output Structure
| File Name Format                     | Description                          |
| ------------------------------------ | ------------------------------------ |
| `username_complete_<timestamp>.json` | Full profile and post metadata       |
| `username_posts_<timestamp>.csv`     | Tabular version of scraped posts     |
| `FINAL_SUMMARY_<timestamp>.csv`      | Summary: post counts, success status |

Notes & Tips
- Run during off-peak hours (2–6 AM) for fewer rate limits

- Some location lookups may fail (harmless, logged as warnings)

- Set max_posts=None to scrape all posts

- Update target accounts in src/scraper.py under TARGET_ACCOUNTS


Project Structure
instaMoms/
├── main.py                     #  Master script — run this!
├── requirements.txt            #  Python dependencies
├── README.md
└── src/
    ├── ig_playwright_login.py  #  Logs in to Instagram via browser
    ├── convert_cookies.py      #  Converts cookies to Instaloader session
    └── scraper.py              #  Scrapes profiles using Instaloader

FAQ
❓ What if I get "Please wait a few minutes..." errors?
That means Instagram has rate-limited your account or IP. Wait at least 30 minutes or switch accounts.

❓ Can I use proxies?
Yes, both Playwright and Instaloader support proxies. Contact me if you need help setting it up.

❓ Can I scrape images or videos?
This version is metadata-only for ethical and legal safety. You can enable media download in Instaloader() options if needed.

License
For educational and research purposes only.
Respect Instagram’s Terms of Use and all applicable laws.

Credits
Built by Karaduman
Powered by Instaloader and Playwright

