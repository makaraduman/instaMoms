# scraper.py

import instaloader
import pandas as pd
import json
import time
import os
import sys
from datetime import datetime
import logging
import random
from instaloader.exceptions import *
from instaloader import RateController  # ✅ Needed for custom rate control

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ✅ Custom Rate Controller with Random Delay
class RandomRateController(RateController):
    def __init__(self, context):
        super().__init__(context)

    def wait_before_query(self, query_type):
        delay = random.uniform(8, 15)
        logger.info(f"⏳ Waiting {delay:.2f} seconds before query: {query_type.name}")
        return delay

# ✅ Scraper Class
class EnhancedInstagramScraper:
    def __init__(self, username=None, password=None, session_file=None):
        self.L = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_pictures=False,
            download_geotags=False,
            save_metadata=False,
            compress_json=False,
            sleep=True,
            max_connection_attempts=5,
            request_timeout=30,
        )
        self.L.context.rate_controller = RandomRateController(self.L.context)
        self.username = username
        self.password = password
        self.session_file = session_file
        self.login_successful = False

        if session_file and os.path.exists(session_file):
            try:
                self.L.load_session_from_file(username, session_file)
                logger.info(f"✅ Loaded session from {session_file}")
                self.login_successful = True
                return
            except Exception as e:
                logger.warning(f"Could not load session: {str(e)}")

        if username and password:
            self.login_successful = self._safe_login(username, password, session_file)
        else:
            logger.warning("No credentials provided - running without login")

    def _safe_login(self, username, password, session_file=None):
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self.L.login(username, password)
                logger.info(f"✅ Successfully logged in as {username}")
                if session_file:
                    self.L.save_session_to_file(session_file)
                    logger.info(f"✅ Session saved to {session_file}")
                return True
            except Exception as e:
                logger.error(f"❌ Login failed (attempt {attempt+1}): {str(e)}")
                if "checkpoint" in str(e).lower():
                    logger.error("Instagram checkpoint required - try manual login first")
                if attempt < max_attempts - 1:
                    time.sleep(60)
        logger.info("Continuing without login")
        return False

    def scrape_account(self, target_username, output_dir="scraped_data", max_posts=None):
        os.makedirs(output_dir, exist_ok=True)
        try:
            profile = instaloader.Profile.from_username(self.L.context, target_username)

            profile_info = {
                'username': profile.username,
                'full_name': profile.full_name,
                'biography': profile.biography,
                'followers': profile.followers,
                'followees': profile.followees,
                'total_posts': profile.mediacount,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private,
                'external_url': profile.external_url,
                'scraped_at': datetime.now().isoformat()
            }

            posts_to_scrape = min(max_posts, profile.mediacount) if max_posts else profile.mediacount
            logger.info(f"🎯 Scraping {posts_to_scrape} posts from @{target_username}")

            posts_data = []
            scraped_count = 0

            for post in profile.get_posts():
                if max_posts and scraped_count >= max_posts:
                    break
                try:
                    time.sleep(random.uniform(3, 5)) # Random delay to avoid rate limits
                    post_data = {
                        'username': target_username,
                        'shortcode': post.shortcode,
                        'url': f"https://www.instagram.com/p/{post.shortcode}/",
                        'date': post.date.isoformat(),
                        'timestamp': post.date.timestamp(),
                        'caption': post.caption,
                        'likes': post.likes,
                        'comments_count': post.comments,
                        'is_video': post.is_video,
                        'media_type': 'Video' if post.is_video else 'Image',
                        'media_count': post.mediacount,
                        'hashtags': list(post.caption_hashtags) if post.caption_hashtags else [],
                        'mentions': list(post.caption_mentions) if post.caption_mentions else [],
                        'hashtag_count': len(post.caption_hashtags) if post.caption_hashtags else 0,
                        'mention_count': len(post.caption_mentions) if post.caption_mentions else 0,
                        'caption_length': len(post.caption) if post.caption else 0,
                        'location_name': None, # 'location_name': post.location.name if post.location else None,
                        'tagged_users': list(post.tagged_users), #'tagged_users': [user.username for user in post.tagged_users],
                        'tagged_count': len(post.tagged_users), #'tagged_count': len(post.tagged_users),
                        'engagement_score': post.likes + post.comments,
                        'video_view_count': post.video_view_count if post.is_video else None,
                    }
                    posts_data.append(post_data)
                    scraped_count += 1

                    if scraped_count % 25 == 0:
                        logger.info(f"[✓] Scraped {scraped_count}/{posts_to_scrape} posts...")

                    if scraped_count % 100 == 0:
                        logger.info("Taking a 1-minute break...")
                        time.sleep(60)  # Take a longer break every 100 posts

                except Exception as e:
                    logger.error(f"[✗] Error scraping post: {str(e)}")
                    time.sleep(30)
                    continue

            self._save_account_data(posts_data, profile_info, target_username, output_dir)
            logger.info(f"✅ Successfully scraped {scraped_count} posts from @{target_username}")
            return posts_data, profile_info

        except Exception as e:
            logger.error(f"❌ Failed to scrape {target_username}: {str(e)}")
            return None, None

    def _save_account_data(self, posts_data, profile_info, username, output_dir):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_filename = f"{output_dir}/{username}_complete_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'profile_info': profile_info,
                'posts': posts_data,
                'summary': {
                    'total_posts_scraped': len(posts_data),
                    'scraping_method': 'enhanced_instaloader',
                    'scraped_at': timestamp
                }
            }, f, indent=2, ensure_ascii=False)

        csv_filename = f"{output_dir}/{username}_posts_{timestamp}.csv"
        if posts_data:
            df = pd.DataFrame(posts_data)
            df.to_csv(csv_filename, index=False, encoding='utf-8')

        logger.info(f"💾 Data saved:")
        logger.info(f"   📄 JSON: {json_filename}")
        logger.info(f"   📊 CSV: {csv_filename}")

# Optional flag to control whether to run a test scrape first
# TEST_MODE = False

# ✅ Main Execution
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide session file path as an argument.")
        print("Usage: python scraper.py session-USERNAME")
        sys.exit(1)

    session_file = sys.argv[1]

    TARGET_ACCOUNTS = [
        "mauroicardi",
        "galatasaray"
    ]

    print("🚀 ENHANCED INSTAGRAM SCRAPER")
    print("Combining instaloader with your Playwright success patterns\n")

    scraper = EnhancedInstagramScraper(
        username=None,
        password=None,
        session_file=session_file
    )

    if not scraper.login_successful:
        print("❌ Login failed. Please check session file or try manual login first.")
        sys.exit(1)

    print(f"🧪 TESTING WITH: @{TARGET_ACCOUNTS[0]}")
    test_posts, test_profile = scraper.scrape_account(
        TARGET_ACCOUNTS[0],
        output_dir="test_enhanced",
        max_posts=50  # Set to None for full scrape
    )

    if test_posts:
        print(f"✅ Test successful! Got {len(test_posts)} posts")
        print(f"\n📊 SCRAPING ALL {len(TARGET_ACCOUNTS)} ACCOUNTS")

        results = {}
        for i, username in enumerate(TARGET_ACCOUNTS, 1):
            print(f"\n--- Account {i}/{len(TARGET_ACCOUNTS)}: @{username} ---")
            posts_data, profile_info = scraper.scrape_account(
                username,
                output_dir="academic_data_enhanced",
                max_posts=None
            )

            if posts_data:
                results[username] = {
                    'posts_count': len(posts_data),
                    'followers': profile_info['followers'],
                    'status': 'success'
                }
                print(f"✅ @{username}: {len(posts_data)} posts scraped")
            else:
                results[username] = {'status': 'failed'}
                print(f"❌ @{username}: Failed")

            if i < len(TARGET_ACCOUNTS):
                wait_time = random.randint(15, 30)
                print(f"⏱️  Waiting {wait_time // 60} minutes...")
                time.sleep(wait_time)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_data = []
        for username, result in results.items():
            summary_data.append({
                'username': username,
                'posts_scraped': result.get('posts_count', 0),
                'status': result.get('status', 'unknown'),
                'followers': result.get('followers', 'N/A')
            })

        summary_df = pd.DataFrame(summary_data)
        summary_filename = f"academic_data_enhanced/FINAL_SUMMARY_{timestamp}.csv"
        summary_df.to_csv(summary_filename, index=False)

        print(f"\n🎉 SCRAPING COMPLETE!")
        print(f"📊 Summary saved: {summary_filename}")
        print(f"✅ Successful: {len([r for r in results.values() if r.get('status') == 'success'])}/{len(TARGET_ACCOUNTS)}")
        print(f"📈 Total posts: {sum([r.get('posts_count', 0) for r in results.values()])}")

    else:
        print("❌ Test failed. Try running during off-peak hours (2–6 AM)")
        print("💡 Your Playwright approach worked, so this should too with patience!")