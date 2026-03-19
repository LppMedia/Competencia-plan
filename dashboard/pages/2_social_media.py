"""
Page 2 - Social Media Analytics + Video Intelligence
Lpp Media Analisis | Influence Marketing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from components.data_loader import (
    load_raw_instagram_profiles, load_raw_instagram_posts,
    posts_by_user, engagement_rate,
    detect_cta, detect_location,
    classify_video_intent, extract_script_structure,
    get_post_img_b64,
)

st.set_page_config(page_title="Social Media · Lpp Media", page_icon="📊", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
  html,[class*="css"]{font-family:'Inter',sans-serif;}
  .section-title{font-size:20px;font-weight:700;color:#f0f0f0;margin:28px 0 14px;}
</style>""", unsafe_allow_html=True)

profiles_raw = load_raw_instagram_profiles()
posts_raw    = load_raw_instagram_posts()
pbu          = posts_by_user(posts_raw)

profiles = [{
    **p,
    "_er":  engagement_rate(p, pbu),
    "_cta": detect_cta(p.get("externalUrl",""), p.get("biography","")),
    "_loc": detect_location(p),
} for p in profiles_raw]

with st.sidebar:
    st.markdown("## Filtros")
    min_follow = st.slider("Minimo seguidores", 0, 500_000, 500, step=500)
    loc_filter = st.multiselect(
        "Mercado", ["Miami FL","Colombia","Venezuela","Internacional"],
        default=["Miami FL","Colombia","Venezuela","Internacional"]
    )

filtered = [p for p in profiles if p.get("followersCount",0) >= min_follow and p["_loc"] in loc_filter]
sorted_p  = sorted(filtered, key=lambda x: x.get("followersCount",0), reverse=True)

st.markdown("""
<div style="background:linear-gradient(90deg,#001a10,#0e0e0e);padding:32px 28px;
     border-radius:16px;border:1px solid #2a2a2a;margin-bottom:24px;">
  <h1 style="font-size:32px;font-weight:900;color:#f0f0f0;margin:0 0 8px;">📊 Social Media Analytics</h1>
  <p style="color:#888;font-size:14px;margin:0;">
    Metricas de engagement + Video Intelligence: scripts y estructura replicable para superar a la competencia
  </p>
</div>""", unsafe_allow_html=True)

total_f   = sum(p.get("followersCount",0) for p in filtered)
total_pts = sum(len(pbu.get(p.get("username",""),[])) for p in filtered)
avg_er    = round(sum(p["_er"] for p in filtered)/max(len(filtered),1), 2)
top_er    = max((p["_er"] for p in filtered), default=0)
by_loc    = {}
for p in filtered:
    by_loc[p["_loc"]] = by_loc.get(p["_loc"],0)+1

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Agencias Filtradas", len(filtered))
c2.metric("Seguidores Combinados", f"{total_f:,}")
c3.metric("Posts Totales", total_pts)
c4.metric("Eng. Rate Promedio", f"{avg_er}%")
c5.metric("Eng. Rate Maximo", f"{top_er}%")

col_l, col_r = st.columns(2)
with col_l:
    st.markdown('<div class="section-title">Top 15 por Seguidores</div>', unsafe_allow_html=True)
    top15 = sorted_p[:15]
    if top15:
        df = pd.DataFrame([{
            "handle": f"@{p.get('username','')}",
            "followers": p.get("followersCount",0),
            "loc": p["_loc"],
        } for p in top15])
        fig = px.bar(df, x="followers", y="handle", orientation="h", color="loc",
            color_discrete_map={"Miami FL":"#ef4444","Colombia":"#ff9f9f","Venezuela":"#ffcfcf","Internacional":"#888"},
            text="followers")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(height=420, paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
            font_color="#f0f0f0", showlegend=True,
            xaxis=dict(showgrid=False), yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h",y=-0.15,font=dict(size=11)),
            margin=dict(l=10,r=80,t=10,b=40))
        st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.markdown('<div class="section-title">Top 15 por Engagement Rate</div>', unsafe_allow_html=True)
    top15_er = sorted(filtered, key=lambda x: x["_er"], reverse=True)[:15]
    if top15_er:
        df_er = pd.DataFrame([{
            "handle": f"@{p.get('username','')}",
            "er": p["_er"],
            "loc": p["_loc"],
        } for p in top15_er])
        fig_er = px.bar(df_er, x="er", y="handle", orientation="h", color="loc",
            color_discrete_map={"Miami FL":"#ef4444","Colombia":"#ff9f9f","Venezuela":"#ffcfcf","Internacional":"#888"},
            text="er")
        fig_er.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_er.update_layout(height=420, paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
            font_color="#f0f0f0", showlegend=False,
            xaxis=dict(showgrid=False, title="Engagement %"),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10,r=60,t=10,b=10))
        st.plotly_chart(fig_er, use_container_width=True)

st.markdown('<div class="section-title">Distribucion por Mercado</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    df_loc = pd.DataFrame(list(by_loc.items()), columns=["Mercado","Influencers"])
    fig_loc = px.pie(df_loc, names="Mercado", values="Influencers",
        color_discrete_sequence=["#ef4444","#ff9f9f","#ffcfcf","#888"], hole=0.5)
    fig_loc.update_layout(paper_bgcolor="#0e0e0e", font_color="#f0f0f0", margin=dict(t=10,b=10))
    st.plotly_chart(fig_loc, use_container_width=True)
with col2:
    loc_stats = {}
    for p in filtered:
        l = p["_loc"]
        if l not in loc_stats:
            loc_stats[l] = {"followers":[],"er":[]}
        loc_stats[l]["followers"].append(p.get("followersCount",0))
        loc_stats[l]["er"].append(p["_er"])
    rows = []
    for l,v in loc_stats.items():
        rows.append({
            "Mercado": l,
            "Avg Seguidores": round(sum(v["followers"])/len(v["followers"])),
            "Avg Engagement %": round(sum(v["er"])/len(v["er"]),2),
            "Cantidad": len(v["followers"]),
        })
    if rows:
        st.dataframe(pd.DataFrame(rows).sort_values("Avg Seguidores",ascending=False),
                     use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Mapa Engagement vs Seguidores</div>', unsafe_allow_html=True)
if filtered:
    df_sc = pd.DataFrame([{
        "handle": f"@{p.get('username','')}",
        "followers": p.get("followersCount",0),
        "engagement": p["_er"],
        "cta": p["_cta"],
        "loc": p["_loc"],
    } for p in filtered if p.get("followersCount",0)>0])
    fig_sc = px.scatter(df_sc, x="followers", y="engagement", color="loc", size="followers",
        hover_name="handle", hover_data={"cta":True,"followers":":,"},
        color_discrete_map={"Miami FL":"#ef4444","Colombia":"#ff9f9f","Venezuela":"#ffcfcf","Internacional":"#888"},
        size_max=30)
    fig_sc.add_hline(y=1, line_dash="dot", line_color="#555", annotation_text="1% benchmark")
    fig_sc.add_hline(y=3, line_dash="dot", line_color="#ef4444", annotation_text="3% high")
    fig_sc.update_layout(height=400, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font_color="#f0f0f0",
        xaxis=dict(title="Seguidores",color="#888",showgrid=False),
        yaxis=dict(title="Engagement %",color="#888",showgrid=True,gridcolor="#2a2a2a"),
        margin=dict(t=10,b=10))
    st.plotly_chart(fig_sc, use_container_width=True)

# ─── TOP 12 POSTS GRID WITH REAL IMAGES ───────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#1a000a,#0e0e0e);padding:24px 28px;
     border-radius:16px;border:1px solid #2a2a2a;margin:28px 0 16px;">
  <h2 style="font-size:22px;font-weight:900;color:#f0f0f0;margin:0 0 4px;">
    🔥 Top 12 Posts por Likes
  </h2>
  <p style="color:#888;font-size:13px;margin:0;">Click en cualquier imagen para abrir el post original en Instagram</p>
</div>""", unsafe_allow_html=True)

all_posts_enriched = []
for post in posts_raw:
    u      = post.get("ownerUsername","")
    likes  = post.get("likesCount",0)
    cmts   = post.get("commentsCount",0)
    sc     = post.get("shortCode","")
    cap    = (post.get("caption","") or "")
    ptype  = post.get("type","Image")
    views  = post.get("videoViewCount",0) or 0
    ig_url = f"https://www.instagram.com/p/{sc}/"
    intent, intent_col = classify_video_intent(cap, u)
    all_posts_enriched.append({
        "u":u,"likes":likes,"cmts":cmts,"sc":sc,"cap":cap,
        "type":ptype,"views":views,"ig_url":ig_url,
        "intent":intent,"intent_col":intent_col,
    })

top12 = sorted(all_posts_enriched, key=lambda x: x["likes"], reverse=True)[:12]

if top12:
    for i in range(0, 12, 4):
        row_posts = top12[i:i+4]
        cols = st.columns(4)
        for col, post in zip(cols, row_posts):
            type_icon = {"Video":"VIDEO","Sidecar":"CARRUSEL","Image":"FOTO"}.get(post["type"],"POST")
            b64 = get_post_img_b64(post["u"], post["sc"])
            if b64:
                img_block = (
                    f'<a href="{post["ig_url"]}" target="_blank" style="display:block;position:relative;">'
                    f'<img src="data:image/jpeg;base64,{b64}" '
                    f'style="width:100%;height:170px;object-fit:cover;border-radius:12px 12px 0 0;display:block;">'
                    f'<div style="position:absolute;top:8px;right:8px;background:rgba(0,0,0,0.8);color:#fff;'
                    f'font-size:10px;font-weight:700;padding:3px 8px;border-radius:8px;">{type_icon}</div>'
                    f'<div style="position:absolute;bottom:8px;left:8px;background:rgba(0,0,0,0.8);color:#fff;'
                    f'font-size:10px;padding:2px 8px;border-radius:8px;">Likes {post["likes"]:,}</div>'
                    f'</a>'
                )
            else:
                img_block = (
                    f'<a href="{post["ig_url"]}" target="_blank" style="display:block;">'
                    f'<div style="background:#2a2a2a;height:170px;border-radius:12px 12px 0 0;'
                    f'display:flex;align-items:center;justify-content:center;font-size:32px;color:#555;">▶</div></a>'
                )

            cap_short = post["cap"][:90]+"..." if len(post["cap"])>90 else post["cap"]
            views_str = f" · {post['views']:,} views" if post["views"] else ""

            with col:
                st.markdown(f"""
                <div style="background:#1a1a1a;border-radius:12px;overflow:hidden;
                     border:1px solid #2a2a2a;margin-bottom:8px;">
                  {img_block}
                  <div style="padding:10px 12px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                      <span style="font-size:11px;color:#888;">@{post['u']}</span>
                      <span style="font-size:10px;font-weight:700;background:{post['intent_col']}22;
                           color:{post['intent_col']};border:1px solid {post['intent_col']}44;
                           padding:2px 7px;border-radius:8px;">{post['intent']}</span>
                    </div>
                    <div style="font-size:13px;font-weight:700;color:#ef4444;margin-bottom:4px;">
                      {post['likes']:,} likes
                      <span style="color:#888;font-weight:400;font-size:11px;">
                        · {post['cmts']:,} cmts{views_str}
                      </span>
                    </div>
                    <div style="font-size:11px;color:#666;line-height:1.4;">{cap_short}</div>
                    <a href="{post['ig_url']}" target="_blank"
                       style="display:block;margin-top:8px;text-align:center;background:#ef444422;
                              color:#ef4444;border:1px solid #ef444444;border-radius:6px;
                              padding:5px;font-size:11px;font-weight:700;text-decoration:none;">
                      Ver en Instagram →
                    </a>
                  </div>
                </div>""", unsafe_allow_html=True)

# ─── VIDEO INTELLIGENCE ────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#0a001a,#0e0e0e);padding:28px;
     border-radius:16px;border:1px solid #2a2a2a;margin:32px 0 20px;">
  <h2 style="font-size:24px;font-weight:900;color:#f0f0f0;margin:0 0 6px;">
    🎬 Video Intelligence — Scripts y Estructura Replicable
  </h2>
  <p style="color:#888;font-size:13px;margin:0 0 4px;">
    Top 15 posts de la competencia descompuestos por intencion estrategica y estructura de guion.
  </p>
  <p style="color:#555;font-size:12px;margin:0;">
    Cada estructura incluye el "Tip Lpp Media" — como producir una version que supere al original.
  </p>
</div>""", unsafe_allow_html=True)

top_videos = sorted(all_posts_enriched, key=lambda x: x["likes"], reverse=True)[:15]

all_intents_list = sorted(set(p["intent"] for p in top_videos))
intent_filter = st.multiselect("Filtrar por intencion estrategica", all_intents_list, default=all_intents_list, key="vf")

filtered_videos = [p for p in top_videos if p["intent"] in intent_filter]

intent_counts_map = {}
for p in top_videos:
    intent_counts_map[p["intent"]] = intent_counts_map.get(p["intent"],0)+1

seen_intents = set()
legend_html_parts = []
for p in top_videos:
    k = p["intent"]
    if k not in seen_intents:
        seen_intents.add(k)
        c = p["intent_col"]
        cnt = intent_counts_map.get(k,0)
        legend_html_parts.append(
            f'<div style="background:{c}22;color:{c};border:1px solid {c}44;'
            f'padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600;">'
            f'{k} ({cnt})</div>'
        )
st.markdown(
    '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px;">'
    + "".join(legend_html_parts) + '</div>',
    unsafe_allow_html=True
)

beat_map = {
    "Comercial / Ventas": "Replicar el formato + agregar metricas reales de campana (CPM, conversiones, ROI). Un post con resultados verificables de Lpp Media genera 2-3x mas credibilidad que la promesa de un competidor sin datos.",
    "Reclutamiento": "Crear la serie 'Bienvenido al equipo Lpp Media' con un creator de Miami, uno de Colombia y uno de Venezuela — el primer post tri-mercado de reclutamiento en la region. Diferenciador inmediato.",
    "Reach / Viral": "Usar el mismo formato viral + branding sutil de Lpp Media. El humor genera shares → los shares generan nuevos seguidores. Asignar 1 post/semana de puro reach viral en cada mercado.",
    "Educacional": "Producir la misma pieza educativa en espanol e ingles (para la audiencia bilingue de Miami) + agregar datos propios de campanas reales. Thought leadership con datos propios = autoridad imbatible.",
    "Cultura / BTS": "Documentar el making-of de una campana real de Lpp Media. Las mejores agencias venden la experiencia de trabajar con ellas. El contenido autentico de equipo humaniza la marca y genera confianza antes del primer call de ventas.",
    "Contenido General": "Evitar contenido sin intencion clara. Cada post de Lpp Media debe tener un objetivo definido: vender, reclutar, educar o generar reach. El contenido sin proposito diluye la marca y reduce el engagement organico.",
}

for idx, post in enumerate(filtered_videos, 1):
    b64 = get_post_img_b64(post["u"], post["sc"])
    script = extract_script_structure(post["cap"], post["intent"])
    type_label = {"Video":"VIDEO","Sidecar":"CARRUSEL","Image":"IMAGEN"}.get(post["type"],"POST")

    with st.expander(
        f"#{idx}  @{post['u']}  ·  {post['likes']:,} likes  ·  {post['intent']}  ·  {type_label}",
        expanded=(idx <= 3),
    ):
        left_col, right_col = st.columns([1, 2])

        with left_col:
            if b64:
                st.markdown(
                    f'<a href="{post["ig_url"]}" target="_blank" style="display:block;">'
                    f'<img src="data:image/jpeg;base64,{b64}" '
                    f'style="width:100%;border-radius:12px;border:2px solid {post["intent_col"]};'
                    f'max-height:320px;object-fit:cover;display:block;"></a>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<a href="{post["ig_url"]}" target="_blank">'
                    f'<div style="background:#2a2a2a;height:240px;border-radius:12px;'
                    f'display:flex;align-items:center;justify-content:center;font-size:48px;'
                    f'color:#555;border:2px solid {post["intent_col"]};">&#9654;</div></a>',
                    unsafe_allow_html=True,
                )

            views_cell = (
                f'<div style="grid-column:1/-1;margin-top:8px;text-align:center;">'
                f'<div style="font-size:16px;font-weight:700;color:#888;">{post["views"]:,}</div>'
                f'<div style="font-size:10px;color:#666;">Vistas</div></div>'
            ) if post["views"] else ""

            st.markdown(f"""
            <div style="background:#111;border-radius:10px;padding:14px;margin-top:10px;">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;text-align:center;">
                <div>
                  <div style="font-size:20px;font-weight:900;color:#ef4444;">{post['likes']:,}</div>
                  <div style="font-size:10px;color:#666;">Likes</div>
                </div>
                <div>
                  <div style="font-size:20px;font-weight:900;color:#f0f0f0;">{post['cmts']:,}</div>
                  <div style="font-size:10px;color:#666;">Comentarios</div>
                </div>
                {views_cell}
              </div>
              <div style="margin-top:12px;text-align:center;">
                <span style="font-size:11px;font-weight:700;background:{post['intent_col']}22;
                     color:{post['intent_col']};border:1px solid {post['intent_col']}44;
                     padding:4px 14px;border-radius:10px;">{post['intent']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

            st.markdown(
                f'<a href="{post["ig_url"]}" target="_blank" '
                f'style="display:block;margin-top:10px;text-align:center;background:#ef444422;'
                f'color:#ef4444;border:1px solid #ef444444;border-radius:8px;padding:9px;'
                f'font-size:12px;font-weight:700;text-decoration:none;">&#9654; Abrir en Instagram</a>',
                unsafe_allow_html=True,
            )

        with right_col:
            cap_clean = (post["cap"] or "(Sin caption)").replace("<","&lt;").replace(">","&gt;")
            st.markdown(f"""
            <div style="background:#111;border-radius:10px;padding:16px;margin-bottom:14px;">
              <div style="font-size:11px;font-weight:700;color:#888;letter-spacing:2px;margin-bottom:8px;">
                CAPTION ORIGINAL — @{post['u']}
              </div>
              <div style="font-size:13px;color:#ccc;line-height:1.6;white-space:pre-wrap;
                          max-height:130px;overflow-y:auto;">{cap_clean}</div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="font-size:12px;font-weight:700;color:{post['intent_col']};
                 letter-spacing:2px;margin-bottom:10px;">
              ESTRUCTURA REPLICABLE — {post['intent'].upper()}
            </div>""", unsafe_allow_html=True)

            for step in script:
                st.markdown(f"""
                <div style="background:#111;border-left:3px solid {post['intent_col']};
                     border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:8px;">
                  <div style="display:inline-block;font-size:10px;font-weight:800;letter-spacing:2px;
                       color:{post['intent_col']};background:{post['intent_col']}22;
                       padding:2px 8px;border-radius:6px;margin-bottom:6px;">{step['role']}</div>
                  <div style="font-size:12px;color:#f0f0f0;margin-bottom:5px;line-height:1.5;">
                    "{step['text']}"
                  </div>
                  <div style="font-size:11px;color:#555;font-style:italic;">
                    Tip Lpp Media: {step['tip']}
                  </div>
                </div>""", unsafe_allow_html=True)

            beat_text = beat_map.get(post["intent"], "Superar con datos propios y angulo unico de Lpp Media.")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#001a10,#0a0a1a);
                 border:1px solid {post['intent_col']}55;border-radius:10px;padding:14px;margin-top:6px;">
              <div style="font-size:11px;font-weight:700;color:{post['intent_col']};
                   letter-spacing:2px;margin-bottom:6px;">
                COMO LPP MEDIA SUPERA ESTE POST
              </div>
              <div style="font-size:12px;color:#ccc;line-height:1.6;">{beat_text}</div>
            </div>""", unsafe_allow_html=True)

# ─── INTENT DISTRIBUTION ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">Distribucion de Intenciones Estrategicas — Todos los Posts</div>', unsafe_allow_html=True)

all_intents_full = [classify_video_intent(p.get("caption",""), p.get("ownerUsername","")) for p in posts_raw]
intent_counts_full = {}
for intent, col_h in all_intents_full:
    intent_counts_full[intent] = intent_counts_full.get(intent, 0) + 1
color_map = {i:c for i,c in set(all_intents_full)}

df_intent = pd.DataFrame(list(intent_counts_full.items()), columns=["Intencion","Cantidad"])
df_intent = df_intent.sort_values("Cantidad", ascending=False)

col_a, col_b = st.columns([2,3])
with col_a:
    fig_pie = px.pie(df_intent, names="Intencion", values="Cantidad",
        color="Intencion", color_discrete_map=color_map, hole=0.4)
    fig_pie.update_layout(paper_bgcolor="#0e0e0e", font_color="#f0f0f0",
        margin=dict(t=10,b=10), legend=dict(font=dict(size=11)))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    insights = {
        "Comercial / Ventas": "La mayoria posta para vender — pero sin funnel, el CTA muere. Lpp Media con funnel de 4 pasos (Post → Bio Link → Sales Page → WhatsApp) multiplica la conversion del mismo tipo de contenido.",
        "Reclutamiento": "Las agencias usan IG para captar creators. Lpp Media puede diferenciarse con reclutamiento tri-mercado Miami+CO+VE — unico en el espacio regional.",
        "Educacional": "Pocas agencias postean thought leadership. El espacio educativo de influencer marketing esta casi vacio — Lpp Media puede posicionarse como la voz experta de la region.",
        "Reach / Viral": "El contenido viral genera awareness pero no clientes por si solo. Usarlo como top-of-funnel, conectado siempre a una propuesta clara en bio o stories.",
        "Cultura / BTS": "El behind-the-scenes humaniza la agencia. Las marcas contratan personas, no logos. Invertir en cultura genera confianza antes del primer contacto de ventas.",
        "Contenido General": "Posts sin intencion clara tienen engagement bajo. Es el error mas comun de las agencias pequenas. Lpp Media evita esto con un calendario editorial con objetivo definido por post.",
    }

    st.markdown('<div style="background:#1a1a1a;border-radius:12px;padding:20px;border:1px solid #2a2a2a;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;font-weight:700;color:#f0f0f0;margin-bottom:14px;">Lo que dice el mix de contenido sobre la competencia</div>', unsafe_allow_html=True)

    total_posts = len(posts_raw)
    for _, row in df_intent.iterrows():
        intent = row["Intencion"]
        count  = row["Cantidad"]
        pct    = round(count / total_posts * 100, 1)
        col_h  = color_map.get(intent,"#888")
        insight = insights.get(intent,"")
        st.markdown(f"""
        <div style="border-left:3px solid {col_h};padding:10px 12px;margin-bottom:10px;
             background:#111;border-radius:0 8px 8px 0;">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-size:13px;font-weight:700;color:{col_h};">{intent}</span>
            <span style="font-size:12px;color:#888;">{count} posts ({pct}%)</span>
          </div>
          <div style="font-size:11px;color:#aaa;line-height:1.5;">{insight}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
