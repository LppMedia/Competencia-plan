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


@st.cache_data(ttl=86400)
def get_post_img_b64(username: str, shortcode: str) -> str | None:
    """Load a single post thumbnail as base64 (cached per shortcode)."""
    path = BASE_DIR / "data" / "images" / "posts" / f"{safe_fn(username)}_{safe_fn(shortcode)}.jpg"
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return None


@st.cache_data(ttl=86400)
def get_profile_img_b64(username: str) -> str | None:
    """Load a single profile picture as base64 (cached per username)."""
    path = BASE_DIR / "data" / "images" / "profiles" / f"{safe_fn(username)}.jpg"
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return None


def profile_avatar_html(username: str, name: str, size: int = 80) -> str:
    """Return <img> with b64 profile pic or coloured initials avatar."""
    b64 = get_profile_img_b64(username)
    initials = "".join(w[0].upper() for w in (name or username).split()[:2]) or username[:2].upper()
    av_colors = ["#ef4444", "#e74c3c", "#c0392b", "#8e44ad", "#2980b9", "#16a085", "#d35400"]
    av_col = av_colors[sum(ord(c) for c in username) % len(av_colors)]
    if b64:
        return (
            f'<img src="data:image/jpeg;base64,{b64}" '
            f'style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;'
            f'border:2px solid #ef4444;flex-shrink:0;">'
        )
    # Try CDN URL directly in browser
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:{av_col};'
        f'display:flex;align-items:center;justify-content:center;font-size:{size//3}px;'
        f'font-weight:700;color:#fff;flex-shrink:0;border:2px solid #ef4444;">{initials}</div>'
    )


def post_img_html(username: str, shortcode: str, height: int = 160,
                  likes: int = 0, post_type: str = "Image") -> str:
    """Return thumbnail <img> html for a post card."""
    b64 = get_post_img_b64(username, shortcode)
    ig_url = f"https://www.instagram.com/p/{shortcode}/"
    type_icon = {"Video": "▶", "Sidecar": "◼◼", "Image": "📷"}.get(post_type, "📷")
    if b64:
        return (
            f'<a href="{ig_url}" target="_blank" style="display:block;position:relative;">'
            f'<img src="data:image/jpeg;base64,{b64}" '
            f'style="width:100%;height:{height}px;object-fit:cover;border-radius:10px 10px 0 0;display:block;">'
            f'<div style="position:absolute;top:6px;right:6px;background:#000c;color:#fff;'
            f'font-size:11px;padding:2px 7px;border-radius:10px;">{type_icon}</div>'
            f'<div style="position:absolute;bottom:6px;left:6px;background:#000c;color:#fff;'
            f'font-size:11px;padding:2px 7px;border-radius:10px;">❤️ {likes:,}</div>'
            f'</a>'
        )
    return (
        f'<a href="{ig_url}" target="_blank" style="display:block;">'
        f'<div style="background:#2a2a2a;height:{height}px;border-radius:10px 10px 0 0;'
        f'display:flex;align-items:center;justify-content:center;color:#555;font-size:28px;">'
        f'{type_icon}</div></a>'
    )


def classify_video_intent(caption: str, username: str) -> tuple[str, str]:
    """Classify the strategic intent of a post from its caption."""
    txt = (caption or "").lower()
    # Influencer Recruitment
    if any(x in txt for x in ["bienvenid", "welcome", "join", "unete", "únete",
                                "nuevo creator", "nueva creator", "nuevo talento",
                                "nueva incorporacion", "team", "familia", "squad"]):
        return "Reclutamiento", "#8e44ad"
    # Sales / Commercial
    if any(x in txt for x in ["campaña", "campaign", "cliente", "client", "marca",
                                "brand", "resultados", "results", "roi", "ventas",
                                "lanzamiento", "launch", "collab", "partnership",
                                "case study", "caso de exito"]):
        return "Comercial / Ventas", "#ef4444"
    # Brand Awareness / Reach
    if any(x in txt for x in ["viral", "trend", "tendencia", "humor", "reto",
                                "challenge", "meme", "funniest", "relatable"]):
        return "Reach / Viral", "#f7971e"
    # Educational / Thought Leadership
    if any(x in txt for x in ["tip", "consejo", "aprende", "learn", "como ",
                                "how to", "guia", "guía", "tutorial", "estrategia",
                                "strategy", "insight", "dato", "fact", "sabias"]):
        return "Educacional", "#25d366"
    # Culture / Behind Scenes
    if any(x in txt for x in ["equipo", "team", "oficina", "office", "detras",
                                "behind", "cultura", "culture", "dia a dia",
                                "journey", "evento", "event", "award", "premio"]):
        return "Cultura / BTS", "#3498db"
    return "Contenido General", "#888"


def extract_script_structure(caption: str, intent: str) -> list[dict]:
    """Generate a replicable script structure from the caption."""
    lines = [l.strip() for l in (caption or "").split("\n") if l.strip()]
    # Build hooks, body, cta from the text
    hook = lines[0][:120] if lines else "(Sin caption)"
    body_lines = lines[1:-1] if len(lines) > 2 else lines[1:] if len(lines) > 1 else []
    last_line = lines[-1] if len(lines) > 1 else ""

    # Detect CTA in last lines
    cta_keywords = ["dm", "link", "bio", "contacto", "whatsapp", "escribenos",
                    "llama", "visita", "click", "swipe", "comenta", "etiqueta",
                    "comparte", "share", "save", "guarda"]
    cta_line = ""
    for line in reversed(lines[-3:]):
        if any(k in line.lower() for k in cta_keywords):
            cta_line = line[:120]
            break

    body_text = " ".join(body_lines)[:200] if body_lines else "(desarrollo del mensaje)"

    templates = {
        "Comercial / Ventas": [
            {"role": "HOOK", "text": hook, "tip": "Abre con el resultado o el problema del cliente"},
            {"role": "PROBLEMA", "text": body_text or "¿Tu marca todavía no está usando influencers?", "tip": "Describe el pain point del cliente ideal"},
            {"role": "SOLUCIÓN", "text": "Campaña ejecutada por [AGENCIA] para [MARCA]", "tip": "Presenta tu servicio como la solución clara"},
            {"role": "PRUEBA SOCIAL", "text": "Resultados: X alcance, Y conversiones, Z ROI", "tip": "Métricas reales generan confianza"},
            {"role": "CTA", "text": cta_line or "DM o link en bio para tu propuesta gratuita", "tip": "Un solo CTA claro, sin ambigüedad"},
        ],
        "Reclutamiento": [
            {"role": "HOOK", "text": hook, "tip": "Anuncia la llegada del nuevo talento con energía"},
            {"role": "PRESENTACIÓN", "text": body_text or "Conoce a [NOMBRE], creator de [NICHO]", "tip": "Humaniza el talento — nombre, nicho, estilo"},
            {"role": "VALOR", "text": "¿Qué hace único a este creator?", "tip": "Destaca su diferenciador para marcas"},
            {"role": "LLAMADO A MARCAS", "text": "¿Quieres colaborar? Somos su agencia.", "tip": "Convierte el post en oportunidad de venta"},
            {"role": "CTA", "text": cta_line or "Contáctanos para gestionar la colaboración", "tip": "CTA directo a marcas interesadas"},
        ],
        "Reach / Viral": [
            {"role": "HOOK", "text": hook, "tip": "Inicia con algo inesperado, gracioso o controversial"},
            {"role": "DESARROLLO", "text": body_text or "(situación relatable del nicho)", "tip": "Conecta con la audiencia en su realidad diaria"},
            {"role": "GIRO", "text": "El giro que nadie esperaba...", "tip": "Sorpresa o remate que genera shares"},
            {"role": "MARCA SUTIL", "text": "[Logo/handle de la agencia] en pantalla", "tip": "Branding no intrusivo — recuerdo sin ruido"},
            {"role": "CTA", "text": cta_line or "Sigue para más contenido como este", "tip": "Construye audiencia, no solo impresiones"},
        ],
        "Educacional": [
            {"role": "HOOK", "text": hook, "tip": "Promesa de aprendizaje en el primer segundo"},
            {"role": "CONTEXTO", "text": body_text or "El problema que resuelve este tip:", "tip": "¿Por qué importa este dato hoy?"},
            {"role": "CONTENIDO", "text": "3 pasos / puntos clave del tema", "tip": "Estructura clara: listas o pasos numerados"},
            {"role": "INSIGHT PROPIO", "text": "Lo que hemos aprendido en [X] campañas:", "tip": "Tu experiencia como diferenciador"},
            {"role": "CTA", "text": cta_line or "Guarda este post para revisarlo después", "tip": "Save = señal de valor para el algoritmo"},
        ],
        "Cultura / BTS": [
            {"role": "HOOK", "text": hook, "tip": "Muestra el momento más auténtico del equipo"},
            {"role": "CONTEXTO", "text": body_text or "Detrás de cámaras de [proyecto/evento]", "tip": "Humaniza la agencia — confianza genera ventas"},
            {"role": "EMOCIÓN", "text": "Lo que este momento significó para el equipo", "tip": "Narrativa emocional > narrativa corporativa"},
            {"role": "CTA", "text": cta_line or "¿Quieres trabajar con nosotros?", "tip": "Convierte la cultura en imán de talento y clientes"},
        ],
    }
    return templates.get(intent, templates["Educacional"])


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
