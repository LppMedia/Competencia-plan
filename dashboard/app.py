"""
app.py — Hero Overview Page
Lpp Media Analisis | Influence Marketing | Miami · Colombia · Venezuela
Client: Lpp Media Influence
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from components.data_loader import (
    load_raw_instagram_profiles,
    load_raw_instagram_posts,
    load_all_images_b64,
    posts_by_user,
    engagement_rate,
    detect_cta,
    detect_location,
    pricing_estimate,
    get_profile_b64,
    get_post_b64,
)

st.set_page_config(
    page_title="Lpp Media Analisis · Influence Marketing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stMetric { background: #1a1a1a; border-radius: 12px; padding: 16px; }
  .pill {
    display:inline-block; padding:4px 14px; border-radius:20px;
    font-size:13px; font-weight:600; margin:4px;
  }
  .card {
    background:#1a1a1a; border-radius:14px; padding:20px;
    border:1px solid #2a2a2a; transition:border .2s;
  }
  .card:hover { border-color:#ef4444; }
  .nav-card {
    background:#1a1a1a; border:1px solid #2a2a2a; border-radius:14px;
    padding:20px 16px; text-align:center; cursor:pointer;
    transition:all .2s;
  }
  .nav-card:hover { border-color:#ef4444; background:#2a1a1a; }
  .opp-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border:1px solid #ef4444; border-radius:14px; padding:22px;
  }
  .section-title {
    font-size:22px; font-weight:700; color:#f0f0f0;
    margin:32px 0 16px; letter-spacing:-.3px;
  }
  .badge {
    display:inline-block; padding:3px 10px; border-radius:8px;
    font-size:11px; font-weight:700; text-transform:uppercase;
  }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
profiles_raw = load_raw_instagram_profiles()
posts_raw    = load_raw_instagram_posts()
img_cache    = load_all_images_b64()
pbu          = posts_by_user(posts_raw)

# Enrich profiles
profiles = []
for p in profiles_raw:
    u   = p.get("username", "")
    f   = p.get("followersCount", 0)
    bio = p.get("biography", "")
    url = p.get("externalUrl", "")
    er  = engagement_rate(p, pbu)
    cta = detect_cta(url, bio)
    loc = detect_location(p)
    tier, price = pricing_estimate(f)
    profiles.append({**p, "_er": er, "_cta": cta, "_loc": loc, "_tier": tier, "_price": price})

profiles_sorted = sorted(profiles, key=lambda x: x.get("followersCount", 0), reverse=True)

# ── Hero Banner ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a0000 0%,#0e0e0e 40%,#0a0a1a 100%);
     border-radius:20px; padding:48px 40px 36px; margin-bottom:8px;
     border:1px solid #2a2a2a;">
  <div style="font-size:11px;letter-spacing:3px;color:#ef4444;font-weight:700;text-transform:uppercase;margin-bottom:12px;">
    LPP MEDIA INFLUENCE · COMPETITIVE INTELLIGENCE
  </div>
  <h1 style="font-size:42px;font-weight:900;color:#f0f0f0;margin:0 0 12px;line-height:1.1;">
    Influence Marketing<br>
    <span style="color:#ef4444;">Miami · Colombia · Venezuela</span>
  </h1>
  <p style="color:#888;font-size:16px;margin:0 0 24px;max-width:600px;">
    Análisis competitivo en tiempo real de los principales influencers y agencias
    de marketing de influencia en los 3 mercados clave.
  </p>
  <div>
    <span class="pill" style="background:#ef4444;color:#fff;">📍 3 Mercados</span>
    <span class="pill" style="background:#1a1a1a;color:#ef4444;border:1px solid #ef4444;">👥 Influencers & Agencias</span>
    <span class="pill" style="background:#1a1a1a;color:#aaa;border:1px solid #333;">🌎 Miami · CO · VE</span>
    <span class="pill" style="background:#1a1a1a;color:#aaa;border:1px solid #333;">🔬 Instagram Data</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
total_followers  = sum(p.get("followersCount", 0) for p in profiles)
total_posts_data = len(posts_raw)
analyzed_posts   = len([p for p in profiles if pbu.get(p.get("username", ""))])
avg_er           = round(sum(p["_er"] for p in profiles) / max(len(profiles), 1), 2)
pct_wa           = round(sum(1 for p in profiles if p["_cta"] == "WhatsApp") / max(len(profiles), 1) * 100)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("👥 Influencers", len(profiles))
c2.metric("📍 Mercados", "3")
c3.metric("❤️ Seguidores Totales", f"{total_followers:,}")
c4.metric("📸 Posts Analizados", total_posts_data)
c5.metric("📈 Eng. Rate Prom.", f"{avg_er}%")
c6.metric("💬 Usan WhatsApp", f"{pct_wa}%")

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Followers Ranking ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🏆 Ranking por Seguidores</div>', unsafe_allow_html=True)

if profiles_sorted:
    top20 = profiles_sorted[:20]
    df_rank = pd.DataFrame([{
        "handle": f"@{p.get('username','')}",
        "followers": p.get("followersCount", 0),
        "location": p["_loc"],
        "cta": p["_cta"],
    } for p in top20])

    colors = ["#FFD700", "#C0C0C0", "#CD7F32"] + ["#ef4444"] * 17
    fig_rank = go.Figure(go.Bar(
        x=df_rank["followers"],
        y=df_rank["handle"],
        orientation="h",
        marker_color=colors[:len(df_rank)],
        text=[f"{v:,}" for v in df_rank["followers"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Seguidores: %{x:,}<extra></extra>",
    ))
    fig_rank.update_layout(
        height=520, paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
        font_color="#f0f0f0", xaxis=dict(showgrid=False, color="#555"),
        yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
        margin=dict(l=10, r=80, t=10, b=10),
    )
    st.plotly_chart(fig_rank, use_container_width=True)
else:
    st.info("Sin datos. Ejecuta `scripts/run_collection.py` para poblar los datos.")

# ── CTA Distribution + Engagement Scatter ────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.markdown('<div class="section-title">📲 Distribución de CTAs</div>', unsafe_allow_html=True)
    if profiles:
        cta_counts = {}
        for p in profiles:
            cta_counts[p["_cta"]] = cta_counts.get(p["_cta"], 0) + 1
        df_cta = pd.DataFrame(list(cta_counts.items()), columns=["cta", "count"])
        fig_cta = px.pie(
            df_cta, names="cta", values="count",
            color_discrete_sequence=["#ef4444", "#ff6b6b", "#ff9f9f", "#ffcfcf", "#c0392b", "#7f0000"],
            hole=0.55,
        )
        fig_cta.update_layout(
            paper_bgcolor="#0e0e0e", font_color="#f0f0f0",
            showlegend=True, legend=dict(orientation="v", font=dict(size=12)),
            margin=dict(t=10, b=10),
        )
        top_cta = max(cta_counts, key=cta_counts.get)
        pct_top  = round(cta_counts[top_cta] / len(profiles) * 100)
        st.plotly_chart(fig_cta, use_container_width=True)
        st.markdown(f"""
        <div style="background:#1a1a1a;border-left:3px solid #ef4444;padding:14px 16px;border-radius:8px;font-size:14px;">
          💡 <b>{pct_top}%</b> de los competidores usan <b>{top_cta}</b> como CTA principal.
          Oportunidad: implementar un funnel más estructurado.
        </div>""", unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="section-title">🎯 Engagement vs. Alcance</div>', unsafe_allow_html=True)
    if profiles:
        df_scatter = pd.DataFrame([{
            "handle": f"@{p.get('username','')}",
            "followers": p.get("followersCount", 0),
            "engagement": p["_er"],
            "cta": p["_cta"],
            "location": p["_loc"],
        } for p in profiles if p.get("followersCount", 0) > 0])

        fig_sc = px.scatter(
            df_scatter, x="followers", y="engagement",
            color="location", hover_name="handle",
            hover_data={"cta": True, "followers": ":,", "engagement": True},
            color_discrete_map={
                "Miami FL": "#ef4444", "Colombia": "#ff9f9f",
                "Venezuela": "#ffcfcf", "Internacional": "#888",
            },
        )
        # Reference lines
        fig_sc.add_hline(y=1, line_dash="dot", line_color="#555", annotation_text="1% ref")
        fig_sc.add_hline(y=3, line_dash="dot", line_color="#ef4444", annotation_text="3% strong")
        fig_sc.update_layout(
            paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
            font_color="#f0f0f0", height=380,
            xaxis=dict(title="Seguidores", color="#888", showgrid=False),
            yaxis=dict(title="Engagement %", color="#888", showgrid=True, gridcolor="#2a2a2a"),
            legend=dict(font=dict(size=11)),
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_sc, use_container_width=True)

# ── Top 5 Coaches Strip ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">⭐ Top 5 Influencers / Agencias</div>', unsafe_allow_html=True)

CTA_COLORS = {
    "WhatsApp": "#25d366", "Linktree": "#43e97b", "Calendly": "#5f6fff",
    "Formulario": "#f7971e", "Sales Page": "#ef4444", "CRM / Proposal": "#8e44ad",
    "Email": "#3498db", "Orgánico": "#888",
}

if profiles_sorted:
    cols5 = st.columns(5)
    for i, (col, p) in enumerate(zip(cols5, profiles_sorted[:5])):
        u       = p.get("username", "")
        name    = p.get("fullName", u)
        follows = p.get("followersCount", 0)
        er      = p["_er"]
        cta     = p["_cta"]
        loc     = p["_loc"]
        bio_url = p.get("externalUrl", "")
        pic_b64  = get_profile_b64(u, img_cache)
        pic_url  = p.get("profilePicUrl", "") or ""
        medal    = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
        cta_col  = CTA_COLORS.get(cta, "#888")

        # Best post thumbnail
        user_posts = pbu.get(u, [])
        best_post  = max(user_posts, key=lambda x: x.get("likesCount", 0)) if user_posts else None
        post_b64   = None
        post_url   = ""
        if best_post:
            post_b64 = get_post_b64(u, best_post.get("shortCode", ""), img_cache)
            post_url = best_post.get("displayUrl", "") or ""

        av_colors = ["#ef4444","#e74c3c","#c0392b","#8e44ad","#2980b9","#16a085","#d35400"]
        av_col    = av_colors[sum(ord(c) for c in u) % len(av_colors)]
        initials  = "".join(w[0].upper() for w in (name or u).split()[:2]) or u[:2].upper()
        fallback_av = f'<div style="width:72px;height:72px;border-radius:50%;background:{av_col};display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:#fff;">{initials}</div>'

        with col:
            if pic_b64:
                pic_html = f'<img src="data:image/jpeg;base64,{pic_b64}" style="width:72px;height:72px;border-radius:50%;object-fit:cover;border:2px solid #ef4444;">'
            elif pic_url:
                pic_html = f'<img src="{pic_url}" style="width:72px;height:72px;border-radius:50%;object-fit:cover;border:2px solid #ef4444;" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\';">{fallback_av.replace("flex;", "flex;display:none;")}'
            else:
                pic_html = fallback_av

            if post_b64:
                post_html = f'<img src="data:image/jpeg;base64,{post_b64}" style="width:100%;height:90px;object-fit:cover;border-radius:8px;margin-top:10px;">'
            elif post_url:
                best_likes = best_post.get("likesCount", 0) if best_post else 0
                post_html  = f'<div style="position:relative;margin-top:10px;"><img src="{post_url}" style="width:100%;height:90px;object-fit:cover;border-radius:8px;" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\';"><div style="display:none;background:linear-gradient(135deg,#1a1a2e,#16213e);height:90px;border-radius:8px;flex-direction:column;align-items:center;justify-content:center;margin-top:10px;"><div style="font-size:12px;font-weight:700;color:#ef4444;">❤️ {best_likes:,}</div><div style="font-size:10px;color:#888;">mejor post</div></div></div>'
            else:
                post_html = ""

            st.markdown(f"""
            <div class="card" style="text-align:center;padding:16px 12px;">
              <div style="font-size:20px;margin-bottom:8px;">{medal}</div>
              {pic_html}
              <div style="font-size:13px;font-weight:700;color:#f0f0f0;margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{name}">{name[:18]}</div>
              <div style="font-size:11px;color:#888;">@{u}</div>
              <div style="font-size:12px;color:#aaa;margin-top:6px;">{follows:,} seguidores</div>
              <div style="font-size:12px;color:#ef4444;">{er}% eng.</div>
              <div style="margin-top:8px;">
                <span class="badge" style="background:{cta_col}22;color:{cta_col};border:1px solid {cta_col}44;">{cta}</span>
              </div>
              <div style="font-size:10px;color:#666;margin-top:4px;">📍 {loc}</div>
              {post_html}
            </div>""", unsafe_allow_html=True)

# ── Section Navigation Cards ───────────────────────────────────────────────────
st.markdown('<div class="section-title">📂 Secciones del Dashboard</div>', unsafe_allow_html=True)

nav_cols = st.columns(5)
nav_items = [
    ("👤", "Perfiles",       "Fichas completas de cada influencer con bio, métricas y posts"),
    ("📊", "Social Media",   "Ranking, engagement, distribución por mercado y top posts"),
    ("💰", "Pricing",        "Estimados de tarifas por tier, gaps de precio y benchmarks"),
    ("🛠️", "Servicios",      "Servicios ofrecidos, brechas de mercado y oportunidades"),
    ("🔭", "Funnels",        "Investigación de funnels de los top 3 competidores"),
]
for col, (icon, label, desc) in zip(nav_cols, nav_items):
    with col:
        st.markdown(f"""
        <div class="nav-card">
          <div style="font-size:32px;margin-bottom:10px;">{icon}</div>
          <div style="font-size:15px;font-weight:700;color:#f0f0f0;">{label}</div>
          <div style="font-size:11px;color:#666;margin-top:6px;">{desc}</div>
        </div>""", unsafe_allow_html=True)

# ── 3 Opportunities Panel ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">🚀 Oportunidades para Lpp Media Influence</div>', unsafe_allow_html=True)

opps = [
    {
        "icon": "💵",
        "title": "Transparencia de Precios",
        "desc": "La mayoría de competidores <b>no publican tarifas</b>. Lpp Media puede diferenciarse con un pricing claro y paquetes definidos para captar clientes que buscan certeza antes de contactar.",
        "tag": "Quick Win",
        "color": "#f7971e",
    },
    {
        "icon": "🔁",
        "title": "Funnel Estructurado Multi-Paso",
        "desc": "Solo 1 de los top 3 tiene un funnel completo con sales page + checkout. <b>Implementar un funnel de 3 pasos</b> (IG → landing → CTA directo) generaría conversiones 3-5× superiores.",
        "tag": "Alto Impacto",
        "color": "#ef4444",
    },
    {
        "icon": "📍",
        "title": "Cobertura Multi-Mercado Unificada",
        "desc": "Ningún competidor activo <b>cubre los 3 mercados</b> (Miami + Colombia + Venezuela) con una propuesta unificada. Lpp Media tiene la ventaja de operar como puente cultural y comercial.",
        "tag": "Ventaja Única",
        "color": "#25d366",
    },
]

opp_cols = st.columns(3)
for col, opp in zip(opp_cols, opps):
    with col:
        st.markdown(f"""
        <div class="opp-card">
          <div style="font-size:36px;margin-bottom:12px;">{opp['icon']}</div>
          <span class="badge" style="background:{opp['color']}22;color:{opp['color']};border:1px solid {opp['color']}55;margin-bottom:10px;">
            {opp['tag']}
          </span>
          <div style="font-size:16px;font-weight:700;color:#f0f0f0;margin:10px 0 8px;">{opp['title']}</div>
          <div style="font-size:13px;color:#aaa;line-height:1.6;">{opp['desc']}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#444;font-size:12px;padding:20px;">
  Lpp Media Analisis · Powered by Instagram Data + Apify · 2025
</div>""", unsafe_allow_html=True)
