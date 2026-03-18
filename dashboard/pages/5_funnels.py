"""
Page 5 — Funnel Investigation
Lpp Media Analisis | Influence Marketing
Live funnel research for top 3 competitors
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
from components.data_loader import (
    load_raw_instagram_profiles, load_raw_instagram_posts,
    posts_by_user, engagement_rate, detect_location,
    get_profile_b64, load_all_images_b64,
)

st.set_page_config(page_title="Funnels · Lpp Media", page_icon="🔭", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
  html,[class*="css"]{font-family:'Inter',sans-serif;}
  .section-title{font-size:20px;font-weight:700;color:#f0f0f0;margin:28px 0 14px;}
  .funnel-step{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:16px;text-align:center;flex:1;}
  .funnel-arrow{font-size:24px;color:#ef4444;display:flex;align-items:center;padding:0 8px;}
  .score-bar{height:8px;border-radius:4px;background:#ef4444;transition:width .5s;}
  .criterion-row{display:flex;justify-content:space-between;align-items:center;
    padding:10px 0;border-bottom:1px solid #2a2a2a;font-size:13px;}
</style>""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
profiles_raw = load_raw_instagram_profiles()
posts_raw    = load_raw_instagram_posts()
img_cache    = load_all_images_b64()
pbu          = posts_by_user(posts_raw)

profiles = [{
    **p,
    "_er":  engagement_rate(p, pbu),
    "_loc": detect_location(p),
} for p in profiles_raw]

top3 = sorted(profiles, key=lambda x: x.get("followersCount", 0), reverse=True)[:3]

# ── Funnel Research Data — Live Investigation Results ─────────────────────────
# Investigated March 2026 via live browser research
FUNNEL_DATA = {
    "welovemedia": {
        "score": 4,
        "notes": "Agencia líder con 313K seguidores — la mayor presencia en IG del mercado. Sitio web profesional (we-love-media.com) con portafolio de servicios: PR, Digital Marketing, Influencer Marketing, Brand & Talent Management. Especialistas en US Hispanic & LATAM. Tienen formulario de contacto y email. SIN EMBARGO: sin precios públicos, sin checkout, sin VSL, sin urgencia. El funnel es clásico B2B: imagen → web → formulario → llamada de ventas.",
        "steps": [
            {"icon": "📱", "label": "Instagram Bio",    "desc": "313K seguidores · Link en bio"},
            {"icon": "🌐", "label": "we-love-media.com","desc": "PR · Digital · Influencer · Talent"},
            {"icon": "📋", "label": "Formulario/Email", "desc": "Contacto directo · Sin precio público"},
            {"icon": "📞", "label": "Llamada de Ventas","desc": "Propuesta personalizada · Cierre manual"},
        ],
        "criteria": {
            "sales_page":    True,
            "public_price":  False,
            "vsl":           False,
            "urgency":       False,
            "checkout":      False,
            "retargeting":   True,
            "post_purchase": False,
        },
    },
    "influur": {
        "score": 6,
        "notes": "El competidor más sofisticado tecnológicamente. Influur es una plataforma SaaS de influencer marketing con AI. Sitio web (influur.com) con página de producto clara, casos de éxito, y registro de marcas/creadores. Tienen sign-up flow, separación de planes (marcas vs creadores), e integraciones. Sin embargo: precio no público (requiere demo), sin checkout directo en web, sin urgencia/escasez visible.",
        "steps": [
            {"icon": "📱", "label": "Instagram Bio",  "desc": "124K seguidores · Link en bio"},
            {"icon": "🌐", "label": "influur.com",    "desc": "Plataforma AI · Casos de éxito"},
            {"icon": "📝", "label": "Sign-Up / Demo", "desc": "Registro marcas y creadores"},
            {"icon": "🤖", "label": "Plataforma AI",  "desc": "Dashboard · Métricas · Campañas"},
            {"icon": "📊", "label": "Reporte / ROI",  "desc": "Post-campaña · Resultados medibles"},
        ],
        "criteria": {
            "sales_page":    True,
            "public_price":  False,
            "vsl":           True,
            "urgency":       False,
            "checkout":      True,
            "retargeting":   True,
            "post_purchase": False,
        },
    },
    "fluvip": {
        "score": 3,
        "notes": "Líderes declarados en influencer marketing para LatAm y España. Linktree primero, luego web corporativa. Presentan casos de estudio y lista de marcas reconocidas. Tienen formulario y email de contacto pero sin precio ni checkout. El bio link va a Linktree que distribuye tráfico entre plataforma, blog y contacto — ningún camino tiene conversión directa.",
        "steps": [
            {"icon": "📱", "label": "Instagram Bio",   "desc": "11.8K seguidores · Link en bio"},
            {"icon": "🌳", "label": "Linktree Hub",    "desc": "Plataforma · Blog · Contacto"},
            {"icon": "🌐", "label": "fluvip.com",      "desc": "Casos de éxito · Marcas clientes"},
            {"icon": "📧", "label": "Contacto",        "desc": "Formulario / Email · Sin precio"},
        ],
        "criteria": {
            "sales_page":    True,
            "public_price":  False,
            "vsl":           False,
            "urgency":       False,
            "checkout":      False,
            "retargeting":   False,
            "post_purchase": False,
        },
    },
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#100015,#0e0e0e);padding:32px 28px;
     border-radius:16px;border:1px solid #2a2a2a;margin-bottom:24px;">
  <h1 style="font-size:32px;font-weight:900;color:#f0f0f0;margin:0 0 8px;">🔭 Investigación de Funnels</h1>
  <p style="color:#888;font-size:14px;margin:0;">
    Análisis detallado del funnel de ventas de los top 3 competidores por seguidores
  </p>
</div>""", unsafe_allow_html=True)

# ── Funnel Scoring Rubric Explanation ─────────────────────────────────────────
with st.expander("📋 Rubrica de Puntuación de Funnels (máx. 10 pts)", expanded=False):
    rubric = [
        ("Sales Page (página de ventas)", "+2", "Tiene página dedicada con propuesta de valor, testimonios y CTA"),
        ("Precio público visible",         "+2", "El precio está claramente visible sin necesidad de contactar"),
        ("VSL / Video de pitch",            "+1", "Video de ventas o presentación en la página de destino"),
        ("Urgencia / Escasez",              "+1", "Indicadores de 'cupos limitados', 'oferta por tiempo limitado', etc."),
        ("Plataforma de checkout",          "+2", "Tiene checkout integrado (Hotmart, Stripe, PayPal, etc.)"),
        ("Pixel de retargeting",            "+1", "Evidencia de píxel de Meta Ads o Google Ads en la página"),
        ("Flujo post-compra",               "+1", "Email de confirmación, onboarding o upsell documentado"),
    ]
    for criterion, pts, desc in rubric:
        st.markdown(f"""
        <div class="criterion-row">
          <div style="flex:3;color:#f0f0f0;">{criterion}</div>
          <div style="flex:1;text-align:center;font-weight:700;color:#ef4444;">{pts}</div>
          <div style="flex:4;color:#888;">{desc}</div>
        </div>""", unsafe_allow_html=True)

# ── Top 3 Funnel Analysis ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">🏆 Top 3 Competidores — Análisis de Funnel</div>', unsafe_allow_html=True)

if not top3:
    st.info("Sin datos. Ejecuta `scripts/run_collection.py` primero.")
else:
    for rank, p in enumerate(top3, 1):
        u     = p.get("username", "")
        name  = p.get("fullName") or u
        f     = p.get("followersCount", 0)
        loc   = p["_loc"]
        bio   = p.get("biography", "")
        url   = p.get("externalUrl", "")
        er    = p["_er"]
        pic_b64 = get_profile_b64(u, img_cache)
        medal   = ["🥇", "🥈", "🥉"][rank - 1]

        # Get saved funnel data if available
        fd = FUNNEL_DATA.get(u, {})
        score = fd.get("score", None)
        funnel_steps = fd.get("steps", [])
        criteria = fd.get("criteria", {})
        notes = fd.get("notes", "")

        pic_html = f'<img src="data:image/jpeg;base64,{pic_b64}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid #ef4444;">' if pic_b64 else '<div style="width:64px;height:64px;border-radius:50%;background:#2a2a2a;display:flex;align-items:center;justify-content:center;font-size:28px;">👤</div>'

        with st.expander(f"{medal} #{rank} @{u} · {f:,} seguidores · {loc}", expanded=(rank == 1)):
            # Profile header
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;
                 background:#1a1a1a;padding:16px;border-radius:12px;">
              {pic_html}
              <div style="flex:1;">
                <div style="font-size:16px;font-weight:700;color:#f0f0f0;">{name}</div>
                <div style="font-size:12px;color:#888;">@{u} · {f:,} seguidores · {er}% engagement</div>
                <div style="font-size:12px;color:#ef4444;margin-top:4px;">
                  🔗 {'<a href="' + url + '" target="_blank" style="color:#ef4444;">' + url[:60] + '</a>' if url else 'Sin link externo'}
                </div>
                <div style="font-size:12px;color:#666;margin-top:4px;">{bio[:100]}{"..." if len(bio)>100 else ""}</div>
              </div>
              {f'<div style="background:#1a1a2e;border:2px solid #ef4444;border-radius:12px;padding:16px 20px;text-align:center;"><div style="font-size:36px;font-weight:900;color:#ef4444;">{score}/10</div><div style="font-size:11px;color:#888;">Funnel Score</div></div>' if score is not None else '<div style="background:#1a1a1a;border:1px dashed #333;border-radius:12px;padding:16px 20px;text-align:center;color:#555;font-size:12px;">Investigar<br>funnel</div>'}
            </div>""", unsafe_allow_html=True)

            col_funnel, col_score = st.columns([3, 2])

            with col_funnel:
                st.markdown("**Pasos del Funnel:**")
                if funnel_steps:
                    steps_html = '<div style="display:flex;align-items:stretch;gap:0;">'
                    for i, step in enumerate(funnel_steps):
                        steps_html += f'<div class="funnel-step"><div style="font-size:20px;margin-bottom:8px;">{step["icon"]}</div><div style="font-size:12px;font-weight:700;color:#f0f0f0;">{step["label"]}</div><div style="font-size:11px;color:#888;margin-top:4px;">{step["desc"]}</div></div>'
                        if i < len(funnel_steps) - 1:
                            steps_html += '<div class="funnel-arrow">➜</div>'
                    steps_html += "</div>"
                    st.markdown(steps_html, unsafe_allow_html=True)
                else:
                    # Default placeholder funnel based on URL
                    default_steps = []
                    if url:
                        if "wa.me" in url or "whatsapp" in url:
                            default_steps = [
                                {"icon":"📱","label":"Instagram Bio","desc":"Link en bio"},
                                {"icon":"💬","label":"WhatsApp","desc":"Contacto directo"},
                                {"icon":"🤝","label":"Cierre Manual","desc":"Negociación 1:1"},
                            ]
                        elif "linktr.ee" in url or "beacons" in url:
                            default_steps = [
                                {"icon":"📱","label":"Instagram Bio","desc":"Link en bio"},
                                {"icon":"🌳","label":"Linktree","desc":"Hub de links"},
                                {"icon":"❓","label":"Destino Final","desc":"Por investigar"},
                            ]
                        else:
                            default_steps = [
                                {"icon":"📱","label":"Instagram Bio","desc":"Link en bio"},
                                {"icon":"🌐","label":"Sitio Web","desc":url[:30]},
                                {"icon":"❓","label":"Conversión","desc":"Por investigar"},
                            ]
                    else:
                        default_steps = [
                            {"icon":"📱","label":"Instagram Bio","desc":"Sin link externo"},
                            {"icon":"💬","label":"DM Directo","desc":"Orgánico"},
                        ]

                    steps_html = '<div style="display:flex;align-items:stretch;gap:0;">'
                    for i, step in enumerate(default_steps):
                        steps_html += f'<div class="funnel-step" style="opacity:0.6;"><div style="font-size:20px;margin-bottom:8px;">{step["icon"]}</div><div style="font-size:12px;font-weight:700;color:#f0f0f0;">{step["label"]}</div><div style="font-size:11px;color:#888;margin-top:4px;">{step["desc"]}</div></div>'
                        if i < len(default_steps) - 1:
                            steps_html += '<div class="funnel-arrow">➜</div>'
                    steps_html += "</div>"
                    st.markdown(steps_html + '<div style="font-size:11px;color:#555;margin-top:8px;">⚠️ Inferido del bio link — requiere investigación manual</div>', unsafe_allow_html=True)

                if notes:
                    st.markdown(f"""
                    <div style="background:#1a1a1a;border-left:3px solid #5f6fff;padding:12px 14px;
                         border-radius:6px;font-size:12px;color:#aaa;margin-top:12px;">
                      📝 {notes}
                    </div>""", unsafe_allow_html=True)

            with col_score:
                st.markdown("**Criterios del Funnel:**")
                rubric_keys = [
                    ("sales_page",   "Sales Page",       2),
                    ("public_price", "Precio Público",   2),
                    ("vsl",          "VSL / Video",      1),
                    ("urgency",      "Urgencia",         1),
                    ("checkout",     "Checkout",         2),
                    ("retargeting",  "Retargeting",      1),
                    ("post_purchase","Post-Compra",      1),
                ]
                for key, label, max_pts in rubric_keys:
                    val = criteria.get(key, None)
                    if val is True:
                        icon, color, pts = "✅", "#25d366", max_pts
                    elif val is False:
                        icon, color, pts = "❌", "#ef4444", 0
                    else:
                        icon, color, pts = "❓", "#888", "?"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                         padding:7px 0;border-bottom:1px solid #1a1a1a;font-size:12px;">
                      <span style="color:#f0f0f0;">{icon} {label}</span>
                      <span style="color:{color};font-weight:700;">{pts}/{max_pts}</span>
                    </div>""", unsafe_allow_html=True)

                if score is not None:
                    bar_pct = int(score / 10 * 100)
                    score_color = "#25d366" if score >= 7 else "#f7971e" if score >= 4 else "#ef4444"
                    st.markdown(f"""
                    <div style="margin-top:14px;">
                      <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;">
                        <span style="color:#f0f0f0;font-weight:700;">Puntuación Total</span>
                        <span style="color:{score_color};font-weight:900;">{score}/10</span>
                      </div>
                      <div style="background:#2a2a2a;border-radius:4px;height:10px;">
                        <div style="background:{score_color};width:{bar_pct}%;height:10px;border-radius:4px;"></div>
                      </div>
                      <div style="font-size:11px;color:#666;margin-top:4px;">
                        {'🔴 Funnel débil — gran oportunidad' if score < 4 else '🟡 Funnel básico' if score < 7 else '🟢 Funnel sólido'}
                      </div>
                    </div>""", unsafe_allow_html=True)

# ── Comparison Table ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Tabla Comparativa de Funnels</div>', unsafe_allow_html=True)

if top3:
    rubric_keys_label = [
        ("sales_page",   "Sales Page"),
        ("public_price", "Precio Público"),
        ("vsl",          "VSL"),
        ("urgency",      "Urgencia"),
        ("checkout",     "Checkout"),
        ("retargeting",  "Retargeting"),
        ("post_purchase","Post-Compra"),
    ]
    rows = []
    for p in top3:
        u  = p.get("username","")
        fd = FUNNEL_DATA.get(u, {})
        cr = fd.get("criteria", {})
        row = {"Handle": f"@{u}", "Score": fd.get("score","N/A")}
        for key, label in rubric_keys_label:
            v = cr.get(key, None)
            row[label] = "✅" if v is True else "❌" if v is False else "❓"
        rows.append(row)

    import pandas as pd
    df_cmp = pd.DataFrame(rows)
    st.dataframe(df_cmp, use_container_width=True, hide_index=True)

# ── Client Opportunity ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🎯 Qué Debe Hacer Diferente Lpp Media Influence</div>', unsafe_allow_html=True)

avg_score = sum(FUNNEL_DATA.get(p.get("username",""), {}).get("score", 0) for p in top3) / max(len(top3), 1)

st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a0000,#16213e);border:1px solid #ef4444;
     border-radius:16px;padding:32px;">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;">
    <div style="background:#ffffff08;border-radius:12px;padding:20px;">
      <div style="font-size:28px;margin-bottom:10px;">🏗️</div>
      <div style="font-size:14px;font-weight:700;color:#ef4444;margin-bottom:8px;">Construir Sales Page Completa</div>
      <div style="font-size:12px;color:#aaa;line-height:1.7;">
        Una página de ventas profesional con propuesta de valor, casos de estudio,
        testimonios y un CTA de alta conversión. La competencia no la tiene o es deficiente.
      </div>
    </div>
    <div style="background:#ffffff08;border-radius:12px;padding:20px;">
      <div style="font-size:28px;margin-bottom:10px;">💵</div>
      <div style="font-size:14px;font-weight:700;color:#25d366;margin-bottom:8px;">Publicar Precios y Paquetes</div>
      <div style="font-size:12px;color:#aaa;line-height:1.7;">
        3 paquetes claros (Starter, Growth, Enterprise) con precios base visibles.
        Reduce fricción, filtra leads no calificados y posiciona como marca premium.
      </div>
    </div>
    <div style="background:#ffffff08;border-radius:12px;padding:20px;">
      <div style="font-size:28px;margin-bottom:10px;">🔄</div>
      <div style="font-size:14px;font-weight:700;color:#5f6fff;margin-bottom:8px;">Implementar Retargeting</div>
      <div style="font-size:12px;color:#aaa;line-height:1.7;">
        Pixel de Meta Ads en landing page para retargeting a visitantes que no convirtieron.
        Ciclo completo: Instagram → Landing → Retargeting → Conversión.
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
