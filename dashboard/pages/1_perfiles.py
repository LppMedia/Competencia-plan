"""
Page 1 — Perfiles / Profiles
Lpp Media Analisis | Influence Marketing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from components.data_loader import (
    load_raw_instagram_profiles, load_raw_instagram_posts,
    load_all_images_b64, posts_by_user, engagement_rate,
    detect_cta, detect_location, pricing_estimate,
    get_profile_b64, get_post_b64, get_post_img_b64,
)

st.set_page_config(page_title="Perfiles · Lpp Media", page_icon="👤", layout="wide")

CTA_COLORS = {
    "WhatsApp": "#25d366", "Linktree": "#43e97b", "Calendly": "#5f6fff",
    "Formulario": "#f7971e", "Sales Page": "#ef4444", "CRM / Proposal": "#8e44ad",
    "Email": "#3498db", "Orgánico": "#888",
}

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
  html,[class*="css"]{font-family:'Inter',sans-serif;}
  .profile-card{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:16px;padding:20px;
    transition:border .2s;}
  .profile-card:hover{border-color:#ef4444;}
  .badge{display:inline-block;padding:3px 10px;border-radius:8px;font-size:11px;font-weight:700;}
  .section-title{font-size:20px;font-weight:700;color:#f0f0f0;margin:28px 0 14px;}
</style>""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
profiles_raw = load_raw_instagram_profiles()
posts_raw    = load_raw_instagram_posts()
img_cache    = load_all_images_b64()
pbu          = posts_by_user(posts_raw)

profiles = []
for p in profiles_raw:
    u   = p.get("username", "")
    f   = p.get("followersCount", 0)
    bio = p.get("biography", "")
    url = p.get("externalUrl", "")
    profiles.append({
        **p,
        "_er":    engagement_rate(p, pbu),
        "_cta":   detect_cta(url, bio),
        "_loc":   detect_location(p),
        "_tier":  pricing_estimate(f)[0],
        "_price": pricing_estimate(f)[1],
    })

# ── Sidebar Filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filtros")
    search     = st.text_input("Buscar handle o nombre", "")
    min_follow = st.slider("Mínimo seguidores", 0, 500_000, 500, step=500)
    cta_filter = st.multiselect("CTA", list(CTA_COLORS.keys()), default=list(CTA_COLORS.keys()))
    loc_filter = st.multiselect("Mercado", ["Miami FL", "Colombia", "Venezuela", "Internacional"],
                                default=["Miami FL", "Colombia", "Venezuela", "Internacional"])
    sort_by    = st.selectbox("Ordenar por", ["Seguidores ↓", "Engagement % ↓", "Nombre A-Z"])

# ── Filter & Sort ──────────────────────────────────────────────────────────────
filtered = [
    p for p in profiles
    if p.get("followersCount", 0) >= min_follow
    and p["_cta"] in cta_filter
    and p["_loc"] in loc_filter
    and (search.lower() in p.get("username", "").lower()
         or search.lower() in (p.get("fullName", "") or "").lower()
         or not search)
]

if sort_by == "Seguidores ↓":
    filtered.sort(key=lambda x: x.get("followersCount", 0), reverse=True)
elif sort_by == "Engagement % ↓":
    filtered.sort(key=lambda x: x["_er"], reverse=True)
else:
    filtered.sort(key=lambda x: (x.get("fullName") or x.get("username", "")).lower())

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(90deg,#1a0000,#0e0e0e);padding:32px 28px;
     border-radius:16px;border:1px solid #2a2a2a;margin-bottom:24px;">
  <h1 style="font-size:32px;font-weight:900;color:#f0f0f0;margin:0 0 8px;">
    👤 Perfiles — Influence Marketing
  </h1>
  <p style="color:#888;font-size:14px;margin:0;">
    {len(filtered)} influencers / agencias encontrados · Miami FL · Colombia · Venezuela
  </p>
</div>""", unsafe_allow_html=True)

# ── Profile Cards Grid ────────────────────────────────────────────────────────
if not filtered:
    st.info("Sin resultados. Ajusta los filtros o ejecuta `scripts/run_collection.py`.")
else:
    for i in range(0, len(filtered), 3):
        row = filtered[i:i+3]
        cols = st.columns(3)
        for col, p in zip(cols, row):
            u    = p.get("username", "")
            name = p.get("fullName") or u
            f    = p.get("followersCount", 0)
            fol  = p.get("followingCount", 0)
            bio  = p.get("biography", "")
            url  = p.get("externalUrl", "")
            er   = p["_er"]
            cta  = p["_cta"]
            loc  = p["_loc"]
            tier = p["_tier"]
            price= p["_price"]
            cta_col = CTA_COLORS.get(cta, "#888")
            pic_b64   = get_profile_b64(u, img_cache)
            pic_url   = p.get("profilePicUrl", "") or ""
            user_posts = pbu.get(u, [])
            top3_posts = sorted(user_posts, key=lambda x: x.get("likesCount", 0), reverse=True)[:3]

            initials  = "".join(w[0].upper() for w in (name or u).split()[:2]) or u[:2].upper()
            av_colors = ["#ef4444","#e74c3c","#c0392b","#8e44ad","#2980b9","#16a085","#d35400"]
            av_col    = av_colors[sum(ord(c) for c in u) % len(av_colors)]
            fallback_av = f'<div style="width:80px;height:80px;border-radius:50%;background:{av_col};display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700;color:#fff;flex-shrink:0;">{initials}</div>'

            if pic_b64:
                pic_html = f'<img src="data:image/jpeg;base64,{pic_b64}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #ef4444;flex-shrink:0;">'
            elif pic_url:
                pic_html = f'<img src="{pic_url}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #ef4444;flex-shrink:0;" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\';">{fallback_av.replace("flex-shrink:0;", "flex-shrink:0;display:none;")}'
            else:
                pic_html = fallback_av

            posts_html = ""
            for post in top3_posts:
                sc_code    = post.get("shortCode", "")
                pb64       = get_post_img_b64(u, sc_code)
                post_url   = post.get("displayUrl", "") or ""
                likes      = post.get("likesCount", 0)
                comments   = post.get("commentsCount", 0)
                ig_post_url = f"https://www.instagram.com/p/{sc_code}/" if sc_code else ""
                link_open  = f'<a href="{ig_post_url}" target="_blank" style="display:block;position:relative;">' if ig_post_url else '<div style="position:relative;">'
                link_close = '</a>' if ig_post_url else '</div>'
                if pb64:
                    posts_html += f'{link_open}<img src="data:image/jpeg;base64,{pb64}" style="width:100%;height:80px;object-fit:cover;border-radius:8px;"><div style="position:absolute;bottom:4px;left:4px;font-size:10px;background:#000a;color:#fff;padding:2px 6px;border-radius:4px;">❤️ {likes:,}</div>{link_close}'
                elif post_url:
                    posts_html += f'<div style="position:relative;"><img src="{post_url}" style="width:100%;height:80px;object-fit:cover;border-radius:8px;" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\';"><div style="display:none;background:linear-gradient(135deg,#1a1a2e,#16213e);height:80px;border-radius:8px;flex-direction:column;align-items:center;justify-content:center;"><div style="font-size:11px;font-weight:700;color:#ef4444;">❤️ {likes:,}</div><div style="font-size:10px;color:#888;">💬 {comments:,}</div></div></div>'
                else:
                    posts_html += f'<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);height:80px;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;"><div style="font-size:11px;font-weight:700;color:#ef4444;">❤️ {likes:,}</div><div style="font-size:10px;color:#888;">💬 {comments:,}</div></div>'

            url_display = f'<a href="{url}" target="_blank" style="color:#ef4444;font-size:12px;text-decoration:none;">🔗 {url[:40]}{"..." if len(url)>40 else ""}</a>' if url else '<span style="color:#555;font-size:12px;">Sin link externo</span>'

            with col:
                st.markdown(f"""
                <div class="profile-card">
                  <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">
                    {pic_html}
                    <div style="flex:1;min-width:0;">
                      <div style="font-size:15px;font-weight:700;color:#f0f0f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</div>
                      <div style="font-size:12px;color:#888;">@{u}</div>
                      <div style="font-size:11px;color:#666;margin-top:2px;">📍 {loc} · {tier}</div>
                    </div>
                  </div>
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px;">
                    <div style="background:#111;border-radius:8px;padding:8px;text-align:center;">
                      <div style="font-size:16px;font-weight:700;color:#ef4444;">{f:,}</div>
                      <div style="font-size:10px;color:#666;">Seguidores</div>
                    </div>
                    <div style="background:#111;border-radius:8px;padding:8px;text-align:center;">
                      <div style="font-size:16px;font-weight:700;color:#f0f0f0;">{fol:,}</div>
                      <div style="font-size:10px;color:#666;">Siguiendo</div>
                    </div>
                    <div style="background:#111;border-radius:8px;padding:8px;text-align:center;">
                      <div style="font-size:16px;font-weight:700;color:#43e97b;">{er}%</div>
                      <div style="font-size:10px;color:#666;">Engagement</div>
                    </div>
                  </div>
                  <div style="font-size:12px;color:#aaa;line-height:1.5;margin-bottom:12px;min-height:40px;">
                    {bio[:120]}{"..." if len(bio)>120 else ""}
                  </div>
                  <div style="margin-bottom:12px;">{url_display}</div>
                  <div style="margin-bottom:14px;">
                    <span class="badge" style="background:{cta_col}22;color:{cta_col};border:1px solid {cta_col}44;">{cta}</span>
                    <span class="badge" style="background:#ef444422;color:#ef4444;border:1px solid #ef444444;margin-left:6px;">{price}</span>
                  </div>
                  <div style="font-size:11px;color:#555;margin-bottom:8px;">TOP POSTS</div>
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;">
                    {posts_html}
                  </div>
                </div>""", unsafe_allow_html=True)
