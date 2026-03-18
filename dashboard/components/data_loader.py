"""
data_loader.py — Single source of truth for all dashboard pages.
Lpp Media Analisis | Influence Marketing | Miami · Colombia · Venezuela
"""

import json
import base64
import os
import re
from pathlib import Path
from collections import defaultdict
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root

# ──────────────────────────────────────────────
# Raw JSON loaders
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_raw_instagram_profiles() -> list[dict]:
    path = BASE_DIR / "data" / "raw" / "instagram_profiles.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=3600)
def load_raw_instagram_posts() -> list[dict]:
    path = BASE_DIR / "data" / "raw" / "instagram_posts.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────
# Image helpers
# ──────────────────────────────────────────────

def safe_fn(name: str) -> str:
    return re.sub(r"[^\w\-_]", "_", str(name))


@st.cache_data(ttl=3600)
def load_all_images_b64() -> dict[str, str]:
    """Returns {relative_path: base64_string} for all downloaded images."""
    cache: dict[str, str] = {}
    for folder in ["profiles", "posts"]:
        img_dir = BASE_DIR / "data" / "images" / folder
        if img_dir.exists():
            for img_path in img_dir.glob("*.jpg"):
                key = f"data/images/{folder}/{img_path.name}"
                with open(img_path, "rb") as f:
                    cache[key] = base64.b64encode(f.read()).decode()
    return cache


def get_profile_b64(username: str, cache: dict) -> str | None:
    key = f"data/images/profiles/{safe_fn(username)}.jpg"
    return cache.get(key)


def get_post_b64(username: str, shortcode: str, cache: dict) -> str | None:
    key = f"data/images/posts/{safe_fn(username)}_{safe_fn(shortcode)}.jpg"
    return cache.get(key)


# ──────────────────────────────────────────────
# Derived metrics
# ──────────────────────────────────────────────

def posts_by_user(posts: list[dict]) -> dict[str, list[dict]]:
    """Group posts by ownerUsername."""
    grouped = defaultdict(list)
    for p in posts:
        u = p.get("ownerUsername", "")
        if u:
            grouped[u].append(p)
    return dict(grouped)


def engagement_rate(profile: dict, pbu: dict[str, list[dict]]) -> float:
    """Engagement rate = avg (likes + comments) / followers * 100"""
    uname     = profile.get("username", "")
    followers = profile.get("followersCount", 0)
    user_posts = pbu.get(uname, [])
    if not followers or not user_posts:
        return 0.0
    total = sum(p.get("likesCount", 0) + p.get("commentsCount", 0) for p in user_posts)
    return round(total / len(user_posts) / followers * 100, 2)


def detect_cta(url: str, bio: str) -> str:
    """Detect primary CTA type from external URL and bio text."""
    url_l = (url or "").lower()
    bio_l = (bio or "").lower()

    if any(x in url_l for x in ["wa.me", "wa.link", "whatsapp"]):
        return "WhatsApp"
    if any(x in url_l for x in ["calendly.com", "cal.com"]):
        return "Calendly"
    if any(x in url_l for x in ["linktr.ee", "link.bio", "linkbio", "beacons.ai", "linkin.bio"]):
        return "Linktree"
    if any(x in url_l for x in ["typeform", "forms.gle", "google.com/forms"]):
        return "Formulario"
    if any(x in url_l for x in ["hotmart", "gumroad", "stan.store", "kajabi", "teachable", "canva.site"]):
        return "Sales Page"
    if any(x in url_l for x in ["hubspot", "pipedrive", "notion.site"]):
        return "CRM / Proposal"
    # Phone number in bio (Miami 305, Colombia 57x, Venezuela 58x, Spain 34)
    if any(x in bio_l for x in ["305", "+1", "+57", "+58", "0414", "0412", "0416", "321", "786"]):
        return "WhatsApp"
    if "@" in bio_l and ".com" in bio_l:
        return "Email"
    return "Orgánico"


def detect_location(profile: dict) -> str:
    """Infer location from biography text or username."""
    bio  = (profile.get("biography", "") or "").lower()
    user = (profile.get("username", "") or "").lower()
    ext  = (profile.get("externalUrl", "") or "").lower()
    combined = bio + " " + user + " " + ext

    if any(x in combined for x in ["miami", "florida", "fl ", "305", "786", "usa", "united states", "mia —", "mia —"]):
        return "Miami FL"
    if any(x in combined for x in ["colombia", "bogotá", "bogota", "medellín", "medellin", "cali", "barranquilla", ".co/"]):
        return "Colombia"
    if any(x in combined for x in ["venezuela", "caracas", "maracaibo", "valencia", "vzla", "ve "]):
        return "Venezuela"
    if any(x in combined for x in ["latam", "latin", "latinoamérica", "latinoamerica", "españa", "spain", "perú", "peru", "mexico", "méxico"]):
        return "Internacional"
    return "Internacional"


def pricing_estimate(followers: int) -> tuple[str, str]:
    """Return (tier_label, price_range_USD) based on follower count (agency IG presence)."""
    if followers < 5_000:
        return "Micro", "$500 – $2K / campaña"
    if followers < 15_000:
        return "Mid-tier", "$2K – $10K / campaña"
    if followers < 50_000:
        return "Macro", "$10K – $50K / campaña"
    if followers < 200_000:
        return "Mega", "$50K – $200K / campaña"
    return "Enterprise", "$200K+ / campaña"


def infer_services(profile: dict, user_posts: list[dict]) -> list[str]:
    """Infer service categories from bio and captions (agency-focused)."""
    text = (profile.get("biography", "") or "").lower()
    for p in user_posts[:6]:
        text += " " + (p.get("caption", "") or "").lower()

    services = []
    if any(x in text for x in ["influencer marketing", "influencer mkt", "marketing de influencer", "influencers"]):
        services.append("Influencer Marketing")
    if any(x in text for x in ["talent management", "talent mgmt", "representacion", "representación", "managers creators", "talent"]):
        services.append("Talent Management")
    if any(x in text for x in ["campaign", "campaña", "strategy", "estrategia"]):
        services.append("Campaign Strategy")
    if any(x in text for x in ["brand deal", "brand collab", "partnership", "patrocinado", "sponsored", "brand partner"]):
        services.append("Brand Partnerships")
    if any(x in text for x in ["ugc", "user generated", "contenido ugc", "content creator", "creación de contenido"]):
        services.append("UGC Content")
    if any(x in text for x in ["pr ", "public relations", "relaciones públicas", "relaciones publicas", "comunicacion", "comunicación"]):
        services.append("PR / Comunicación")
    if any(x in text for x in ["paid media", "paid ads", "meta ads", "google ads", "paid social", "performance"]):
        services.append("Paid Media")
    if any(x in text for x in ["branding", "brand identity", "identidad de marca"]):
        services.append("Branding")
    if any(x in text for x in ["social media", "redes sociales", "social"]):
        services.append("Social Media")
    if any(x in text for x in ["photo", "foto", "video", "reel", "filming", "produccion", "producción", "content production"]):
        services.append("Content Production")
    if any(x in text for x in ["consulting", "consultoria", "consultoría", "asesor", "coaching"]):
        services.append("Consulting")
    if not services:
        services.append("Marketing Digital")
    return services
