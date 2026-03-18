"""
Apify scraping runner for Lpp Media Analisis
Niche: Influence Marketing | Locations: Miami FL, Colombia, Venezuela
"""

import json
import os
from apify_client import ApifyClient

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
client = ApifyClient(APIFY_TOKEN)

HASHTAGS = [
    "influencermarketingmiami",
    "influencermiami",
    "miamiblogger",
    "influencercolombia",
    "influencerscolombia",
    "marketingdigitalcolombia",
    "influencervenezuela",
    "influencersvenezuela",
    "marketingdigitalvenezuela",
    "agenciainfluencer",
    "marketingdeinfluencia",
    "influencermarketing",
    "creadordecontenido",
    "contenidodigital",
]

DIRECT_URLS_SEARCH = [
    "https://www.instagram.com/explore/tags/influencermarketingmiami/",
    "https://www.instagram.com/explore/tags/influencerscolombia/",
    "https://www.instagram.com/explore/tags/influencersvenezuela/",
]


def run_hashtag_scraper():
    print("Running hashtag scraper...")
    run_input = {
        "hashtags": HASHTAGS,
        "resultsLimit": 200,
        "proxy": {"useApifyProxy": True},
    }
    run = client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"  → {len(items)} posts found")

    # Extract unique usernames
    handles = list({p.get("ownerUsername") for p in items if p.get("ownerUsername")})
    print(f"  → {len(handles)} unique handles")
    return handles


def run_profile_scraper(handles):
    print(f"Running profile scraper for {len(handles)} handles...")
    urls = [f"https://www.instagram.com/{h}/" for h in handles]
    run_input = {
        "directUrls": urls,
        "resultsType": "details",
        "resultsLimit": 1,
        "proxy": {"useApifyProxy": True},
    }
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    profiles = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    # Filter: keep accounts with 500+ followers
    filtered = [p for p in profiles if p.get("followersCount", 0) >= 500]
    print(f"  → {len(filtered)} profiles after filtering (<500 followers removed)")

    with open("data/raw/instagram_profiles.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print("  → Saved to data/raw/instagram_profiles.json")
    return filtered


def run_post_scraper(handles):
    print(f"Running post scraper for {len(handles)} handles...")
    urls = [f"https://www.instagram.com/{h}/" for h in handles]
    run_input = {
        "directUrls": urls,
        "resultsType": "posts",
        "resultsLimit": 12,
        "proxy": {"useApifyProxy": True},
    }
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    posts = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    with open("data/raw/instagram_posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"  → {len(posts)} posts saved to data/raw/instagram_posts.json")


if __name__ == "__main__":
    if not APIFY_TOKEN:
        print("ERROR: Set APIFY_API_TOKEN environment variable")
        exit(1)

    handles = run_hashtag_scraper()
    profiles = run_profile_scraper(handles)
    final_handles = [p.get("username") for p in profiles if p.get("username")]
    run_post_scraper(final_handles)
    print("\nCollection complete!")
