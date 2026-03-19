"""
Image downloader for Lpp Media Analisis dashboard.
Downloads profile pics and post thumbnails from scraped JSON data.
"""

import json
import os
import re
import requests
from pathlib import Path

def safe_fn(name):
    return re.sub(r"[^\w\-_]", "_", str(name))

def download(url, dest, timeout=15):
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            Path(dest).write_bytes(r.content)
            return True
    except Exception as e:
        print(f"  WARN: {dest} — {e}")
    return False

def main():
    os.makedirs("data/images/profiles", exist_ok=True)
    os.makedirs("data/images/posts", exist_ok=True)

    # --- Profile pictures ---
    profiles_path = "data/raw/instagram_profiles.json"
    if os.path.exists(profiles_path):
        profiles = json.load(open(profiles_path, encoding="utf-8"))
        print(f"Downloading {len(profiles)} profile pictures...")
        ok = 0
        for p in profiles:
            u = p.get("username", "")
            url = p.get("profilePicUrlHD") or p.get("profilePicUrl", "")
            if url and u:
                dest = f"data/images/profiles/{safe_fn(u)}.jpg"
                if not os.path.exists(dest):
                    if download(url, dest):
                        ok += 1
                else:
                    ok += 1
        print(f"  -> {ok}/{len(profiles)} profile images ready")
    else:
        print(f"WARN: {profiles_path} not found. Run run_collection.py first.")

    # --- Post thumbnails ---
    posts_path = "data/raw/instagram_posts.json"
    if os.path.exists(posts_path):
        posts = json.load(open(posts_path, encoding="utf-8"))
        print(f"Downloading post thumbnails for {len(posts)} posts...")
        ok = 0
        for post in posts:
            u  = post.get("ownerUsername", "")
            sc = post.get("shortCode", "")
            url = post.get("displayUrl", "")
            if url and u and sc:
                dest = f"data/images/posts/{safe_fn(u)}_{safe_fn(sc)}.jpg"
                if not os.path.exists(dest):
                    if download(url, dest):
                        ok += 1
                else:
                    ok += 1
        print(f"  -> {ok}/{len(posts)} post images ready")
    else:
        print(f"WARN: {posts_path} not found. Run run_collection.py first.")

if __name__ == "__main__":
    main()
