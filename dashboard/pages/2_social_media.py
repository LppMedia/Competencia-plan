"""
Page 2 — Social Media Analytics
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
    load_all_images_b64, posts_by_user, engagement_rate,
    detect_cta, detect_location, get_post_b64,
)

st.set_page_config(page_title="Social Media · Lpp Media", page_icon="📊", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
  html,[class*="css"]{font-family:'Inter',sans-serif;}
  .section-title{font-size:20px;font-weight:700;color:#f0f0f0;margin:28px 0 14px;}
  .stat-card{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:16px;text-align:center;}
</style>""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
profiles_raw = load_raw_instagram_profiles()
posts_raw    = load_raw_instagram_posts()
img_cache    = load_all_images_b64()
pbu          = posts_by_user(posts_raw)

profiles = [{
    **p,
    "_er":  engagement_rate(p, pbu),
    "_cta": detect_cta(p.get("externalUrl", ""), p.get("biography", "")),
    "_loc": detect_location(p),
} for p in profiles_raw]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filtros")
    min_follow = st.slider("Mínimo seguidores", 0, 500_000, 500, step=500)
    loc_filter = st.multiselect("Mercado", ["Miami FL", "Colombia", "Venezuela", "Internacional"],
                                default=["Miami FL", "Colombia", "Venezuela", "Internacional"])

filtered = [p for p in profiles if p.get("followersCount", 0) >= min_follow and p["_loc"] in loc_filter]
sorted_p  = sorted(filtered, key=lambda x: x.get("followersCount", 0), reverse=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#001a10,#0e0e0e);padding:32px 28px;
     border-radius:16px;border:1px solid #2a2a2a;margin-bottom:24px;">
  <h1 style="font-size:32px;font-weight:900;color:#f0f0f0;margin:0 0 8px;">📊 Social Media Analytics</h1>
  <p style="color:#888;font-size:14px;margin:0;">Métricas de engagement, alcance y distribución por mercado</p>
</div>""", unsafe_allow_html=True)

# ── Summary Metrics ────────────────────────────────────────────────────────────
total_f   = sum(p.get("followersCount", 0) for p in filtered)
total_pts = sum(len(pbu.get(p.get("username", ""), [])) for p in filtered)
avg_er    = round(sum(p["_er"] for p in filtered) / max(len(filtered), 1), 2)
top_er    = max((p["_er"] for p in filtered), default=0)
by_loc    = {}
for p in filtered:
    by_loc[p["_loc"]] = by_loc.get(p["_loc"], 0) + 1

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📌 Influencers Filtrados", len(filtered))
c2.metric("❤️ Seguidores Combinados", f"{total_f:,}")
c3.metric("📸 Posts Totales", total_pts)
c4.metric("📈 Eng. Rate Promedio", f"{avg_er}%")
c5.metric("🔥 Eng. Rate Máximo", f"{top_er}%")

# ── Followers Ranking + Engagement Side by Side ────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.markdown('<div class="section-title">🏆 Top 15 por Seguidores</div>', unsafe_allow_html=True)
    top15 = sorted_p[:15]
    if top15:
        df = pd.DataFrame([{
            "handle": f"@{p.get('username','')}",
            "followers": p.get("followersCount", 0),
            "loc": p["_loc"],
        } for p in top15])
        fig = px.bar(
            df, x="followers", y="handle", orientation="h",
            color="loc",
            color_discrete_map={"Miami FL":"#ef4444","Colombia":"#ff9f9f","Venezuela":"#ffcfcf","Internacional":"#888"},
            text="followers",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(
            height=420, paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
            font_color="#f0f0f0", showlegend=True,
            xaxis=dict(showgrid=False), yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
            margin=dict(l=10, r=80, t=10, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.markdown('<div class="section-title">📈 Top 15 por Engagement Rate</div>', unsafe_allow_html=True)
    top15_er = sorted(filtered, key=lambda x: x["_er"], reverse=True)[:15]
    if top15_er:
        df_er = pd.DataFrame([{
            "handle": f"@{p.get('username','')}",
            "er": p["_er"],
            "loc": p["_loc"],
        } for p in top15_er])
        fig_er = px.bar(
            df_er, x="er", y="handle", orientation="h",
            color="loc",
            color_discrete_map={"Miami FL":"#ef4444","Colombia":"#ff9f9f","Venezuela":"#ffcfcf","Internacional":"#888"},
            text="er",
        )
        fig_er.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_er.update_layout(
            height=420, paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
            font_color="#f0f0f0", showlegend=False,
            xaxis=dict(showgrid=False, title="Engagement %"),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=60, t=10, b=10),
        )
        st.plotly_chart(fig_er, use_container_width=True)

# ── Location Distribution ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">🗺️ Distribución por Mercado</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    df_loc = pd.DataFrame(list(by_loc.items()), columns=["Mercado", "Influencers"])
    fig_loc = px.pie(
        df_loc, names="Mercado", values="Influencers",
        color_discrete_sequence=["#ef4444", "#ff9f9f", "#ffcfcf", "#888"],
        hole=0.5,
    )
    fig_loc.update_layout(paper_bgcolor="#0e0e0e", font_color="#f0f0f0", margin=dict(t=10,b=10))
    st.plotly_chart(fig_loc, use_container_width=True)

with col2:
    # Avg followers per location
    loc_stats = {}
    for p in filtered:
        l = p["_loc"]
        if l not in loc_stats:
            loc_stats[l] = {"followers": [], "er": []}
        loc_stats[l]["followers"].append(p.get("followersCount", 0))
        loc_stats[l]["er"].append(p["_er"])

    rows = []
    for l, v in loc_stats.items():
        rows.append({
            "Mercado": l,
            "Avg Seguidores": round(sum(v["followers"]) / len(v["followers"])),
            "Avg Engagement %": round(sum(v["er"]) / len(v["er"]), 2),
            "Cantidad": len(v["followers"]),
        })
    if rows:
        df_stats = pd.DataFrame(rows).sort_values("Avg Seguidores", ascending=False)
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

# ── Engagement Scatter ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🎯 Mapa de Engagement vs. Seguidores</div>', unsafe_allow_html=True)

if filtered:
    df_sc = pd.DataFrame([{
        "handle": f"@{p.get('username','')}",
        "followers": p.get("followersCount", 0),
        "engagement": p["_er"],
        "cta": p["_cta"],
        "loc": p["_loc"],
    } for p in filtered if p.get("followersCount", 0) > 0])

    fig_sc = px.scatter(
        df_sc, x="followers", y="engagement",
        color="loc", size="followers", hover_name="handle",
        hover_data={"cta": True, "followers": ":,"},
        color_discrete_map={"Miami FL":"#ef4444","Colombia":"#ff9f9f","Venezuela":"#ffcfcf","Internacional":"#888"},
        size_max=30,
    )
    fig_sc.add_hline(y=1, line_dash="dot", line_color="#555", annotation_text="1% benchmark")
    fig_sc.add_hline(y=3, line_dash="dot", line_color="#ef4444", annotation_text="3% high")
    fig_sc.update_layout(
        height=400, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font_color="#f0f0f0",
        xaxis=dict(title="Seguidores", color="#888", showgrid=False),
        yaxis=dict(title="Engagement %", color="#888", showgrid=True, gridcolor="#2a2a2a"),
        margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# ── Top 12 Posts Grid ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔥 Top 12 Posts por Likes</div>', unsafe_allow_html=True)

all_posts_enriched = []
for post in posts_raw:
    u     = post.get("ownerUsername", "")
    likes = post.get("likesCount", 0)
    cmts  = post.get("commentsCount", 0)
    sc    = post.get("shortCode", "")
    cap   = (post.get("caption", "") or "")[:80]
    pb64  = get_post_b64(u, sc, img_cache)
    all_posts_enriched.append({"u": u, "likes": likes, "cmts": cmts, "sc": sc, "cap": cap, "pb64": pb64})

top12 = sorted(all_posts_enriched, key=lambda x: x["likes"], reverse=True)[:12]

if top12:
    for i in range(0, 12, 4):
        row = top12[i:i+4]
        cols = st.columns(4)
        for col, post in zip(cols, row):
            with col:
                img_html = f'<img src="data:image/jpeg;base64,{post["pb64"]}" style="width:100%;height:160px;object-fit:cover;border-radius:10px;">' if post["pb64"] else '<div style="background:#2a2a2a;height:160px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#555;">📷</div>'
                st.markdown(f"""
                <div style="background:#1a1a1a;border-radius:12px;overflow:hidden;border:1px solid #2a2a2a;">
                  {img_html}
                  <div style="padding:10px;">
                    <div style="font-size:11px;color:#888;">@{post['u']}</div>
                    <div style="font-size:13px;font-weight:700;color:#ef4444;">❤️ {post['likes']:,}
                      <span style="color:#888;font-weight:400;font-size:11px;">· 💬 {post['cmts']:,}</span>
                    </div>
                    <div style="font-size:11px;color:#666;margin-top:4px;">{post['cap']}{"..." if len(post["cap"])>=80 else ""}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
else:
    st.info("Sin datos de posts. Ejecuta `scripts/run_collection.py`.")
