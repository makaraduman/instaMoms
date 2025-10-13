# convert_cookies.py

import json
import sys
from instaloader import Instaloader, Profile

def convert_cookies(username, cookie_file, session_file):
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)

    cookie_dict = {c['name']: c['value'] for c in cookies if 'instagram.com' in c['domain']}
    required = ['sessionid', 'ds_user_id', 'csrftoken']
    if not all(k in cookie_dict for k in required):
        raise Exception("❌ Missing required cookies.")

    L = Instaloader()
    for key in required:
        L.context._session.cookies.set(key, cookie_dict[key], domain='.instagram.com')

    profile = Profile.from_username(L.context, username)
    L.context.username = profile.username
    L.context.userid = profile.userid
    L.save_session_to_file(session_file)
    print(f"✅ Session saved to: {session_file}")

# Run from CLI
if __name__ == "__main__":
    convert_cookies(sys.argv[1], sys.argv[2], sys.argv[3])