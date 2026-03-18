"""
Page 4 — Servicios / Services Analysis
Lpp Media Analisis | Influence Marketing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import pandas as pd
from collections import Counter
from components.data_loader import (
    load_raw_instagram_profiles, load_raw_instagram_posts,
    posts_by_user, engagement_rate, detect_location, infer_services,
)

st.set_page_config(page_title="Servicios · Lpp Media", page_icon="🛠️", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
  html,[class*="css"]{font-family:'Inter',sans-serif;}
  .section-title{font-size:20px;font-weight:700;color:#f0f0f0;margin:28px 0 14px;}
  .service-tag{display:inline-block;padding:4px 12px;border-radius:20px;font-size:11px;
    font-weight:600;background:#ef444422;color:#ef4444;border:1px solid #ef444444;margin:3px;}
  .profile-row{background:#1a1a1a;border-radius:12px;padding:16px;border:1px solid #2a2a2a;margin-bottom:8px;}
</style>""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
profiles_raw = load_raw_instagram_profiles()
posts_raw    = load_raw_instagram_posts()
pbu          = posts_by_user(posts_raw)

profiles = [{
    **p,
    "_er":       engagement_rate(p, pbu),
    "_loc":      detect_location(p),
    "_services": infer_services(p, pbu.get(p.get("username",""), [])),
} for p in profiles_raw]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#001015,#0e0e0e);padding:32px 28px;
     border-radius:16px;border:1px solid #2a2a2a;margin-bottom:24px;">
  <h1 style="font-size:32px;font-weight:900;color:#f0f0f0;margin:0 0 8px;">🛠️ Análisis de Servicios</h1>
  <p style="color:#888;font-size:14px;margin:0;">
    Categorías de servicios ofrecidos, brechas de mercado y oportunidades estratégicas
  </p>
</div>""", unsafe_allow_html=True)

# ── Service Frequency ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Servicios Más Comunes en el Mercado</div>', unsafe_allow_html=True)

all_services = []
for p in profiles:
    all_services.extend(p["_services"])

service_counts = Counter(all_services)

if service_counts:
    df_svc = pd.DataFrame(service_counts.most_common(), columns=["Servicio", "Cantidad"])
    total_p = max(len(profiles), 1)
    df_svc["% Mercado"] = (df_svc["Cantidad"] / total_p * 100).round(1)

    col1, col2 = st.columns([3, 2])
    with col1:
        fig = px.bar(
            df_svc, x="Cantidad", y="Servicio", orientation="h",
            text="Cantidad",
            color="Cantidad",
            color_continuous_scale=["#2a2a2a", "#ef4444"],
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=380, paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
            font_color="#f0f0f0", showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10,r=60,t=10,b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Penetración por servicio:**")
        for _, row in df_svc.iterrows():
            bar_pct = int(row["% Mercado"])
            st.markdown(f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;">
                <span style="color:#f0f0f0;">{row['Servicio']}</span>
                <span style="color:#ef4444;font-weight:700;">{row['% Mercado']}%</span>
              </div>
              <div style="background:#2a2a2a;border-radius:4px;height:6px;">
                <div style="background:#ef4444;width:{min(bar_pct,100)}%;height:6px;border-radius:4px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

# ── Market Gap Analysis ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔭 Brechas de Mercado Identificadas</div>', unsafe_allow_html=True)

all_possible_services = [
    "Brand Partnerships", "UGC Content", "Talent Management", "Campaign Strategy",
    "Content Production", "Consulting", "Education / Courses", "Creación de Contenido",
    "Performance Reporting", "Multi-Market Coverage", "Retargeting & Paid Media",
]
offered = set(service_counts.keys())
gaps = [s for s in all_possible_services if s not in offered]

gap_cols = st.columns(min(len(gaps), 3))
gap_descs = {
    "Performance Reporting": "Ningún competidor ofrece reportes formales de performance post-campaña. Diferenciador clave.",
    "Multi-Market Coverage": "Cobertura simultánea Miami+Colombia+Venezuela — vacío total en el mercado actual.",
    "Retargeting & Paid Media": "Pocas agencias combinan influencer marketing con paid ads para retargeting.",
    "Education / Courses": "Mercado de educación sobre influencer marketing para marcas está casi vacío.",
}

for col, gap in zip(gap_cols, gaps[:3]):
    desc = gap_descs.get(gap, f"Servicio {gap} no está ofrecido actualmente por competidores.")
    with col:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#001a10,#0e0e0e);border:1px solid #25d366;
             border-radius:14px;padding:20px;">
          <div style="font-size:28px;margin-bottom:8px;">🆕</div>
          <div style="font-size:15px;font-weight:700;color:#25d366;margin-bottom:8px;">{gap}</div>
          <div style="font-size:12px;color:#aaa;line-height:1.6;">{desc}</div>
        </div>""", unsafe_allow_html=True)

if not gaps:
    st.markdown("""
    <div style="background:#1a1a1a;border-radius:12px;padding:20px;color:#aaa;">
      Todos los servicios principales están cubiertos. El diferenciador clave es ejecución y calidad.
    </div>""", unsafe_allow_html=True)

# ── Per-Profile Service Tags ───────────────────────────────────────────────────
st.markdown('<div class="section-title">👥 Servicios por Influencer / Agencia</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🔍 Filtros")
    svc_filter = st.multiselect(
        "Filtrar por servicio",
        list(service_counts.keys()),
        default=list(service_counts.keys())[:5] if service_counts else [],
    )
    loc_filter = st.multiselect(
        "Mercado",
        ["Miami FL","Colombia","Venezuela","Internacional"],
        default=["Miami FL","Colombia","Venezuela","Internacional"],
    )

filtered = [
    p for p in sorted(profiles, key=lambda x: x.get("followersCount",0), reverse=True)
    if p["_loc"] in loc_filter
    and (not svc_filter or any(s in p["_services"] for s in svc_filter))
]

for p in filtered:
    u     = p.get("username","")
    name  = p.get("fullName") or u
    f     = p.get("followersCount",0)
    loc   = p["_loc"]
    svcs  = p["_services"]
    tags  = "".join(f'<span class="service-tag">{s}</span>' for s in svcs)

    st.markdown(f"""
    <div class="profile-row">
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <div>
          <span style="font-size:15px;font-weight:700;color:#f0f0f0;">@{u}</span>
          <span style="color:#888;font-size:12px;margin-left:8px;">{name}</span>
        </div>
        <div style="font-size:12px;color:#aaa;">📍 {loc} · {f:,} seguidores</div>
      </div>
      <div style="margin-top:10px;">{tags if tags else '<span style="color:#555;font-size:12px;">Sin servicios detectados</span>'}</div>
    </div>""", unsafe_allow_html=True)

# ── Strategic Recommendation Panel ────────────────────────────────────────────
st.markdown('<div class="section-title">🚀 Plan Estratégico 2026 — Lpp Media Influence</div>', unsafe_allow_html=True)

top_svc = service_counts.most_common(1)[0][0] if service_counts else "Marketing Digital"

# ── Header insight card ──
st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a0000,#0a0a1a);border:1px solid #ef4444;
     border-radius:16px;padding:28px;margin-bottom:24px;">
  <div style="font-size:11px;letter-spacing:3px;color:#ef4444;font-weight:700;margin-bottom:10px;">
    ANÁLISIS COMPETITIVO · 20 AGENCIAS · MIAMI · CO · VE
  </div>
  <div style="font-size:22px;font-weight:900;color:#f0f0f0;margin-bottom:8px;line-height:1.3;">
    La competencia comete <span style="color:#ef4444;">7 errores críticos</span> que Lpp Media puede capitalizar hoy.
  </div>
  <div style="font-size:14px;color:#888;line-height:1.6;">
    Basado en análisis de {len(profiles)} agencias con {sum(p.get('followersCount',0) for p in profiles):,} seguidores combinados,
    {len(posts_raw)} posts y funnel research de los 3 competidores más grandes.
  </div>
</div>""", unsafe_allow_html=True)

# ── Section A: 7 Competitor Errors ──
st.markdown("""
<div style="font-size:18px;font-weight:700;color:#f0f0f0;margin:0 0 16px;">
  ❌ Los 7 Errores que Comete tu Competencia
</div>""", unsafe_allow_html=True)

errors = [
    {
        "n": "01", "title": "Funnels sin estructura",
        "stat": "0 de 3 top agencias tienen checkout funcional",
        "detail": "welovemedia (313K), influur (124K) y fluvip (12K) mandan todo al WhatsApp o a un sitio web genérico. No hay sales page, no hay pricing, no hay urgencia. El cliente potencial llega interesado y se pierde en el silencio.",
        "opp": "Lpp Media implementa un funnel de 4 pasos: Post IG → Bio Link → Sales Page con precios → Calendly/WhatsApp con propuesta pre-armada.",
        "color": "#ef4444",
    },
    {
        "n": "02", "title": "Sin precios públicos",
        "stat": "95%+ de agencias ocultan sus tarifas",
        "detail": "Solo 1 de 20 agencias analizadas muestra pricing referencial online. Esto genera fricción de venta enorme: el cliente tiene que solicitar cotización, esperar respuesta, negociar — proceso que dura días y mata el momentum.",
        "opp": "Lpp Media publica 3 paquetes con precios base claros. Los clientes que llegan ya vienen pre-calificados y listos para cerrar.",
        "color": "#ef4444",
    },
    {
        "n": "03", "title": "Cobertura de mercado única",
        "stat": "0 agencias cubren Miami + CO + VE simultáneamente",
        "detail": "Influur se enfoca en LATAM general, welovemedia en Miami, las colombianas en Colombia. Ninguna ofrece un paquete tri-mercado como propuesta de valor central. Las marcas que quieren alcance regional tienen que contratar 2-3 agencias.",
        "opp": "Lpp Media posiciona el servicio 'Tri-Market Pack': una campaña, un equipo, tres mercados. Precio unificado, reporting centralizado.",
        "color": "#f7971e",
    },
    {
        "n": "04", "title": "Sin ROI reportable",
        "stat": "Ningún competidor publica case studies con métricas",
        "detail": "No hay un solo post de welovemedia, influur ni fluvip que muestre resultados reales de campañas (CPM, conversiones, ventas generadas). En 2026, los CFOs B2B exigen ROI medible antes de aprobar presupuestos de influencer marketing.",
        "opp": "Lpp Media construye un 'Results Dashboard' público: mini case studies trimestrales con métricas reales (con permiso del cliente). Esto se convierte en el asset de ventas más poderoso.",
        "color": "#f7971e",
    },
    {
        "n": "05", "title": "Influencer marketing sin paid media",
        "stat": "Solo 10% menciona paid media / retargeting",
        "detail": "Las campañas de influencer quedan 'en el aire' — generan awareness pero no se potencian con anuncios pagados para retargeting. En 2026 los algoritmos de Meta priorizan contenido boosteado, lo que significa que una campaña orgánica llega a solo el 5-8% de la audiencia relevante.",
        "opp": "Lpp Media ofrece el combo 'Influencer + Boost': el contenido del creator se usa como ad creativo en Meta Ads, multiplicando el alcance x10 con el mismo presupuesto creativo.",
        "color": "#5f6fff",
    },
    {
        "n": "06", "title": "Ausencia total en LinkedIn",
        "stat": "0 agencias B2B con presencia activa en LinkedIn",
        "detail": "Todas las agencias analizadas usan Instagram como único canal de captación. Pero sus clientes (CMOs, directores de marketing, fundadores de marcas) viven en LinkedIn. Hay un vacío completo de generación de demanda B2B en la plataforma correcta.",
        "opp": "Lpp Media lanza una estrategia LinkedIn-first: newsletter semanal 'Influencer Marketing Insights', posts de thought leadership y LinkedIn Ads targeting a decision makers en Miami, Bogotá y Caracas.",
        "color": "#0077b5",
    },
    {
        "n": "07", "title": "UGC sin sistema ni entrega",
        "stat": "Solo 15% de agencias menciona UGC explícitamente",
        "detail": "El UGC (User Generated Content) es la tendencia #1 de 2025-2026: las marcas necesitan contenido auténtico en volumen para ads, email y web. Las agencias lo mencionan de pasada, pero ninguna tiene un sistema de producción UGC con entregables, tiempos y formatos estandarizados.",
        "opp": "Lpp Media lanza 'UGC Studio': paquetes de 10/25/50 videos UGC con entrega en 7 días, brief estandarizado y licencia completa para ads. Precio fijo, sin sorpresas.",
        "color": "#25d366",
    },
]

for err in errors:
    st.markdown(f"""
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-left:4px solid {err['color']};
         border-radius:12px;padding:20px;margin-bottom:12px;">
      <div style="display:flex;align-items:flex-start;gap:16px;">
        <div style="font-size:32px;font-weight:900;color:{err['color']};opacity:0.3;line-height:1;min-width:40px;">
          {err['n']}
        </div>
        <div style="flex:1;">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;flex-wrap:wrap;">
            <div style="font-size:16px;font-weight:700;color:#f0f0f0;">{err['title']}</div>
            <div style="font-size:11px;font-weight:600;background:{err['color']}22;color:{err['color']};
                 border:1px solid {err['color']}44;padding:3px 10px;border-radius:20px;">{err['stat']}</div>
          </div>
          <div style="font-size:13px;color:#aaa;line-height:1.6;margin-bottom:10px;">{err['detail']}</div>
          <div style="background:#ffffff06;border-radius:8px;padding:12px;">
            <div style="font-size:11px;font-weight:700;color:{err['color']};margin-bottom:4px;">
              ✅ MOVIDA LPP MEDIA
            </div>
            <div style="font-size:12px;color:#ccc;line-height:1.5;">{err['opp']}</div>
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── Section B: 2026 Trends ──
st.markdown("""
<div style="font-size:18px;font-weight:700;color:#f0f0f0;margin:32px 0 16px;">
  📈 Tendencias 2026 que Lpp Media Debe Liderar
</div>""", unsafe_allow_html=True)

trends = [
    {
        "icon": "🤖", "title": "AI-Powered Influencer Matching",
        "why": "Los clientes B2B ya no aceptan selección de influencers 'a ojo'. Exigen matching basado en datos: audiencia real, afinidad de categoría, historial de engagement autenticado.",
        "action": "Construir un sistema simple de scoring (Excel/Notion + datos de Apify) que muestre a los clientes por qué se eligió cada creator. Diferencia inmediata vs. competidores que 'proponen' sin justificar.",
        "trend_score": "Alto impacto · Bajo costo de implementación",
    },
    {
        "icon": "📊", "title": "Performance-Based Pricing (CPA/CPL)",
        "why": "El mercado está migrando de tarifas planas por post a modelos donde la agencia cobra un base + bonus por resultados. Influur ya ofrece algo similar. Las marcas lo prefieren porque reduce riesgo.",
        "action": "Lpp Media lanza un modelo híbrido: retainer base ($X/mes) + CPA por lead generado vía UTM trackeable. Esto convierte a la agencia en aliada de resultados, no en proveedor de contenido.",
        "trend_score": "Alto impacto · Complejidad media",
    },
    {
        "icon": "🎬", "title": "Short-Form + Creator Amplification",
        "why": "Los Reels de 7-15 segundos con creators obtienen 3-5x más alcance orgánico que posts estáticos. En 2026, Instagram y TikTok priorizan contenido de creator en formato vertical ultra-corto.",
        "action": "Standardizar todas las campañas a incluir mínimo 3 Reels de 7-15 segundos por creator. Ofrecer a clientes un 'Reel Package': brief → creator → posting → boost paid → reporte en 14 días.",
        "trend_score": "Muy alto impacto · Listo para implementar hoy",
    },
    {
        "icon": "🔗", "title": "B2B Influencer Marketing en LinkedIn",
        "why": "CMOs, directores de marketing y VPs de marcas están creando contenido en LinkedIn. Las empresas B2B que venden a otras empresas están descubriendo que los LinkedIn Creators convierten 5x mejor que Instagram para servicios empresariales.",
        "action": "Lpp Media añade LinkedIn Creators a su red. Paquete 'B2B Reach': 2-3 creators LinkedIn en Miami/LATAM para campañas de SaaS, servicios profesionales y marcas de lujo.",
        "trend_score": "Alto impacto · Ventana de oportunidad abierta",
    },
    {
        "icon": "📍", "title": "Nano & Micro Influencers > Mega",
        "why": "Los datos de 2025 confirman: los micro-influencers (10K-50K) tienen 3-5x más engagement rate que los mega (200K+) y cuestan 10x menos. Las marcas están redistribuyendo presupuesto hacia 'ejércitos de micros'.",
        "action": "Construir una red de 50+ micro-influencers certificados en Miami, Bogotá y Caracas. Ofrecer paquetes 'Micro Army': 10 creators × 1 Reel cada uno vs 1 mega creator. Mismo presupuesto, mayor cobertura y autenticidad.",
        "trend_score": "Muy alto impacto · Diferenciador clave",
    },
    {
        "icon": "🔄", "title": "Siempre-Encendido vs. Campañas Puntuales",
        "why": "Las marcas que mantienen presencia constante con creators (1-2 posts/semana) vs. campañas esporádicas generan 4x más awareness acumulado. El modelo de 'campaña de 30 días' está siendo reemplazado por retainers anuales.",
        "action": "Lpp Media ofrece el 'Always-On Plan': retainer mensual que incluye 4-8 posts de creators al mes, reporting quincenal y acceso a red de creators en los 3 mercados. Ingresos recurrentes para la agencia, resultados compuestos para el cliente.",
        "trend_score": "Muy alto impacto · MRR para la agencia",
    },
]

tcols = st.columns(2)
for i, tr in enumerate(trends):
    with tcols[i % 2]:
        st.markdown(f"""
        <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;padding:20px;margin-bottom:14px;height:100%;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
            <div style="font-size:28px;">{tr['icon']}</div>
            <div style="font-size:15px;font-weight:700;color:#f0f0f0;">{tr['title']}</div>
          </div>
          <div style="font-size:12px;color:#888;line-height:1.6;margin-bottom:10px;">{tr['why']}</div>
          <div style="background:#ef444410;border-left:3px solid #ef4444;padding:10px 12px;border-radius:0 8px 8px 0;margin-bottom:10px;">
            <div style="font-size:11px;font-weight:700;color:#ef4444;margin-bottom:4px;">ACCIÓN CONCRETA</div>
            <div style="font-size:12px;color:#ccc;line-height:1.5;">{tr['action']}</div>
          </div>
          <div style="font-size:10px;color:#555;font-style:italic;">{tr['trend_score']}</div>
        </div>""", unsafe_allow_html=True)

# ── Section C: 90-Day Action Plan ──
st.markdown("""
<div style="font-size:18px;font-weight:700;color:#f0f0f0;margin:32px 0 16px;">
  🗓️ Plan de Acción 90 Días — Lpp Media Influence
</div>""", unsafe_allow_html=True)

phases = [
    {
        "phase": "Días 1–30", "label": "FUNDAMENTOS", "color": "#ef4444",
        "items": [
            "Publicar pricing page con 3 paquetes (Starter / Growth / Enterprise)",
            "Lanzar sales page con propuesta tri-mercado Miami+CO+VE",
            "Crear plantilla de 'Campaign Brief' estandarizada para clientes",
            "Instalar pixel de Meta Ads en sitio web para retargeting",
            "Perfilar y certificar 15 micro-influencers en los 3 mercados",
        ],
    },
    {
        "phase": "Días 31–60", "label": "TRACCIÓN", "color": "#f7971e",
        "items": [
            "Lanzar primera campaña 'Influencer + Boost' con un cliente piloto",
            "Publicar primer case study con métricas reales (con aprobación cliente)",
            "Activar perfil de LinkedIn con 2 posts semanales de thought leadership",
            "Lanzar UGC Studio: primeros 3 paquetes UGC vendidos",
            "Implementar sistema de scoring para selección de influencers",
        ],
    },
    {
        "phase": "Días 61–90", "label": "ESCALA", "color": "#25d366",
        "items": [
            "Cerrar primeros 2 clientes en modelo retainer (Always-On Plan)",
            "Red de 30+ micro-influencers activos en los 3 mercados",
            "Presentar deck de resultados Q1 a 5 prospects calificados",
            "Lanzar newsletter LinkedIn 'Influencer Insights LATAM' (500 suscriptores)",
            "Propuesta performance-based para cliente enterprise (CPA model)",
        ],
    },
]

pcols = st.columns(3)
for col, ph in zip(pcols, phases):
    items_html = "".join(f'<div style="display:flex;gap:8px;margin-bottom:8px;"><div style="color:{ph["color"]};flex-shrink:0;font-size:14px;margin-top:1px;">▸</div><div style="font-size:12px;color:#ccc;line-height:1.5;">{it}</div></div>' for it in ph["items"])
    with col:
        st.markdown(f"""
        <div style="background:#1a1a1a;border:1px solid {ph['color']}44;border-top:3px solid {ph['color']};
             border-radius:14px;padding:20px;height:100%;">
          <div style="font-size:11px;letter-spacing:2px;color:{ph['color']};font-weight:700;margin-bottom:4px;">
            {ph['label']}
          </div>
          <div style="font-size:16px;font-weight:700;color:#f0f0f0;margin-bottom:16px;">{ph['phase']}</div>
          {items_html}
        </div>""", unsafe_allow_html=True)

# ── Final KPI targets ──
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="background:linear-gradient(135deg,#0a0a1a,#1a0000);border:1px solid #ef4444;
     border-radius:16px;padding:28px;">
  <div style="font-size:11px;letter-spacing:3px;color:#ef4444;font-weight:700;margin-bottom:16px;">
    TARGETS 2026 — LPP MEDIA INFLUENCE
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;">
    <div style="text-align:center;">
      <div style="font-size:36px;font-weight:900;color:#ef4444;">5–8</div>
      <div style="font-size:12px;color:#888;margin-top:4px;">Clientes retainer activos al mes 6</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:36px;font-weight:900;color:#f7971e;">50+</div>
      <div style="font-size:12px;color:#888;margin-top:4px;">Micro-creators en red certificada</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:36px;font-weight:900;color:#25d366;">3x</div>
      <div style="font-size:12px;color:#888;margin-top:4px;">Más alcance vs. campañas orgánicas puras</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:36px;font-weight:900;color:#5f6fff;">#1</div>
      <div style="font-size:12px;color:#888;margin-top:4px;">Agencia tri-mercado LATAM en 12 meses</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
