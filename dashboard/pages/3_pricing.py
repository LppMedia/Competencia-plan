"""
Page 3 — Pricing Intelligence
Lpp Media Analisis | Influence Marketing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from components.data_loader import (
    load_raw_instagram_profiles, load_raw_instagram_posts,
    posts_by_user, engagement_rate, detect_location, pricing_estimate,
)

st.set_page_config(page_title="Pricing · Lpp Media", page_icon="💰", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
  html,[class*="css"]{font-family:'Inter',sans-serif;}
  .section-title{font-size:20px;font-weight:700;color:#f0f0f0;margin:28px 0 14px;}
  .tier-card{border-radius:14px;padding:24px;border:1px solid #2a2a2a;text-align:center;}
</style>""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
profiles_raw = load_raw_instagram_profiles()
posts_raw    = load_raw_instagram_posts()
pbu          = posts_by_user(posts_raw)

def _shows_price(profile: dict, pbu: dict) -> bool:
    """Check if account shows prices publicly."""
    bio   = (profile.get("biography", "") or "").lower()
    posts = pbu.get(profile.get("username", ""), [])
    text  = bio
    for post in posts[:6]:
        text += " " + (post.get("caption", "") or "").lower()
    price_keywords = ["$", "usd", "precio", "price", "tarifa", "rate", "costo",
                      "cost", "paquete", "package", "plan ", "planes"]
    return any(kw in text for kw in price_keywords)

profiles = []
for p in profiles_raw:
    f    = p.get("followersCount", 0)
    tier, price = pricing_estimate(f)
    profiles.append({
        **p,
        "_er":          engagement_rate(p, pbu),
        "_loc":         detect_location(p),
        "_tier":        tier,
        "_price":       price,
        "_shows_price": _shows_price(p, pbu),
    })

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#1a1000,#0e0e0e);padding:32px 28px;
     border-radius:16px;border:1px solid #2a2a2a;margin-bottom:24px;">
  <h1 style="font-size:32px;font-weight:900;color:#f0f0f0;margin:0 0 8px;">💰 Pricing Intelligence</h1>
  <p style="color:#888;font-size:14px;margin:0;">
    Estimados de tarifas por tier y análisis de transparencia de precios en el mercado
  </p>
</div>""", unsafe_allow_html=True)

# ── Tier Reference Table ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Referencia de Tarifas por Tier (USD)</div>', unsafe_allow_html=True)

tier_data = [
    {"Tier": "Micro",     "Seguidores": "< 10K",        "Post Feed": "$50–$300",      "Story": "$20–$100",      "Reel": "$100–$500",      "Campaña (30d)": "$150–$1,000"},
    {"Tier": "Mid-tier",  "Seguidores": "10K–50K",       "Post Feed": "$300–$1,500",   "Story": "$100–$500",     "Reel": "$500–$2,000",    "Campaña (30d)": "$1,000–$5,000"},
    {"Tier": "Macro",     "Seguidores": "50K–200K",      "Post Feed": "$1,500–$8,000", "Story": "$500–$2,500",   "Reel": "$2,000–$10,000", "Campaña (30d)": "$5,000–$25,000"},
    {"Tier": "Mega",      "Seguidores": "200K–1M",       "Post Feed": "$8,000–$50,000","Story": "$2,500–$15,000","Reel": "$10,000–$60,000","Campaña (30d)": "$25,000–$150,000"},
    {"Tier": "Celebrity", "Seguidores": "> 1M",          "Post Feed": "$50,000+",      "Story": "$15,000+",      "Reel": "$60,000+",       "Campaña (30d)": "$150,000+"},
]

df_tier = pd.DataFrame(tier_data)
st.dataframe(
    df_tier.style.apply(lambda x: [
        "background-color:#1a1a1a; color:#f0f0f0" for _ in x
    ], axis=1),
    use_container_width=True, hide_index=True,
)

st.markdown("""
<div style="background:#1a1a1a;border-left:3px solid #f7971e;padding:14px 16px;border-radius:8px;font-size:13px;color:#aaa;margin:12px 0 24px;">
  ⚠️ Tarifas son estimados basados en benchmarks de mercado 2024-2025 para mercados latinoamericanos y Miami.
  Los precios reales varían por nicho, engagement, exclusividad y negociación directa.
</div>""", unsafe_allow_html=True)

# ── Tier Distribution ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Distribución de Tiers en el Mercado</div>', unsafe_allow_html=True)

tier_counts = {}
for p in profiles:
    t = p["_tier"]
    tier_counts[t] = tier_counts.get(t, 0) + 1

tier_order = ["Micro", "Mid-tier", "Macro", "Mega", "Celebrity"]
tier_colors = ["#888", "#ff9f9f", "#ef4444", "#c0392b", "#7f0000"]

df_tc = pd.DataFrame([
    {"Tier": t, "Cantidad": tier_counts.get(t, 0)}
    for t in tier_order if t in tier_counts
])

if not df_tc.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            df_tc, x="Tier", y="Cantidad",
            color="Tier",
            color_discrete_sequence=tier_colors,
            text="Cantidad",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=320, paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
            font_color="#f0f0f0", showlegend=False,
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
            margin=dict(t=10,b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        for t, c in tier_counts.items():
            pct = round(c / len(profiles) * 100)
            _, price = pricing_estimate({"Micro":5000,"Mid-tier":25000,"Macro":100000,"Mega":500000,"Celebrity":2000000}.get(t,1000))
            st.markdown(f"""
            <div style="background:#1a1a1a;border-radius:10px;padding:12px 16px;margin-bottom:8px;
                 display:flex;align-items:center;justify-content:space-between;">
              <div>
                <span style="font-weight:700;color:#f0f0f0;">{t}</span>
                <span style="color:#888;font-size:12px;margin-left:8px;">{c} influencers ({pct}%)</span>
              </div>
              <span style="color:#ef4444;font-size:13px;font-weight:600;">{price}</span>
            </div>""", unsafe_allow_html=True)

# ── Price Transparency Gap ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔓 Transparencia de Precios — Gap de Mercado</div>', unsafe_allow_html=True)

shows   = sum(1 for p in profiles if p["_shows_price"])
hides   = len(profiles) - shows
pct_hid = round(hides / max(len(profiles), 1) * 100)

col_a, col_b, col_c = st.columns(3)
col_a.metric("✅ Muestran precio", shows)
col_b.metric("❌ Ocultan precio", hides)
col_c.metric("📊 % Sin precio público", f"{pct_hid}%")

df_trans = pd.DataFrame([
    {"Estado": "Muestra Precio", "Cantidad": shows},
    {"Estado": "Oculta Precio",  "Cantidad": hides},
])
fig_trans = px.pie(
    df_trans, names="Estado", values="Cantidad",
    color_discrete_sequence=["#25d366", "#ef4444"],
    hole=0.6,
)
fig_trans.update_layout(paper_bgcolor="#0e0e0e", font_color="#f0f0f0", height=280, margin=dict(t=10,b=10))
st.plotly_chart(fig_trans, use_container_width=True)

st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a0000,#0e0e0e);border:1px solid #ef4444;
     border-radius:14px;padding:24px;margin-top:8px;">
  <div style="font-size:24px;margin-bottom:10px;">💡</div>
  <div style="font-size:16px;font-weight:700;color:#f0f0f0;margin-bottom:8px;">
    Oportunidad: {pct_hid}% del mercado no muestra precios
  </div>
  <div style="font-size:13px;color:#aaa;line-height:1.7;">
    La mayoría de agencias e influencers en Miami · Colombia · Venezuela <b>no publican sus tarifas</b>,
    lo que genera fricción en el proceso de compra. <b>Lpp Media Influence</b> puede diferenciarse
    significativamente siendo transparente con su pricing, ofreciendo paquetes claros en su sitio web
    y materiales de ventas — reduciendo el tiempo de cierre y aumentando la confianza del cliente.
  </div>
</div>""", unsafe_allow_html=True)

# ── Per-Profile Pricing Table ─────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Estimado por Influencer</div>', unsafe_allow_html=True)

df_profiles = pd.DataFrame([{
    "Handle": f"@{p.get('username','')}",
    "Nombre": p.get("fullName", ""),
    "Seguidores": p.get("followersCount", 0),
    "Tier": p["_tier"],
    "Precio Estimado/Post": p["_price"],
    "Mercado": p["_loc"],
    "Muestra Precio": "✅ Sí" if p["_shows_price"] else "❌ No",
    "Engagement %": p["_er"],
} for p in sorted(profiles, key=lambda x: x.get("followersCount",0), reverse=True)])

st.dataframe(df_profiles, use_container_width=True, hide_index=True)
