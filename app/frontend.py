import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import urllib.parse
from app.core.calculator import calculate_solar_quote
from app.core.pdf_generator import generate_quote_pdf
from app.schemas.quote import QuoteRequest

# Configuración de Supabase (Usa st.secrets en Streamlit Cloud o variables de entorno)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase_client = None

st.set_page_config(
    # --- ENCABEZADO INSTITUCIONAL SOLARTECH ---
        header_col1, header_col2 = st.columns([1, 2], gap="medium")

        with header_col1:
            # Buscar el logo en app/logo.png o logo.png
            logo_path = "app/logo.png" if os.path.exists("app/logo.png") else "logo.png"
            if os.path.exists(logo_path):
                st.image(logo_path, use_container_width=True)
            else:
                st.markdown("### ☀️ SOLAR&TECH")

        with header_col2:
            st.markdown("""
                <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
                    <h2 style="margin: 0; color: #38bdf8 !important;">Cotizador Solar All-in-One</h2>
                    <p style="margin: 2px 0; font-size: 0.95rem; color: #cbd5e1 !important;">
                        <b>SOLAR&TECH</b> · Soluciones en Tecnología y Energías Alternativas
                    </p>
                    <p style="margin: 0; font-size: 0.85rem; color: #94a3b8 !important;">
                        📄 <b>NIT:</b> 901798729 &nbsp;|&nbsp; 📲 <b>WhatsApp:</b> +57 310 247 6744
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
)

st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            color: #ffffff !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
            color: #ffffff !important;
        }
        div[data-testid="stWidgetLabel"] label,
        div[data-testid="stWidgetLabel"] p,
        div[role="radiogroup"] label div p {
            color: #ffffff !important;
            font-weight: 500 !important;
        }
        .solution-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            height: 100%;
        }
        .solution-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #38bdf8 !important;
            margin-top: 10px;
        }
        .solution-desc {
            font-size: 0.85rem;
            color: #e2e8f0 !important;
            line-height: 1.4;
        }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 6px;
            background-color: #0284c7;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("☀️ Cotizador Sistema SOLARTECH")
st.caption("Calcula el dimensionamiento y costo de tu sistema solar compacto en gabinete todo en uno.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Tus Datos de Contacto")
    nombre = st.text_input("Nombre Completo *", placeholder="Ej. Juan Pérez")
    telefono = st.text_input("Número de Teléfono / WhatsApp *", placeholder="Ej. 3001234567")
    email = st.text_input("Correo Electrónico (Opcional)", placeholder="juan@ejemplo.com")

    st.subheader("2. Datos de Consumo")
    input_mode = st.radio(
        "¿Cómo prefieres ingresar tus consumos?",
        ["Promedio últimos 3 consumos (kWh)", "Valor promedio de la factura ($ COP)"],
        horizontal=True
    )
    
    tarifa_kwh = st.number_input("Costo aproximado por kWh ($ COP)", min_value=300.0, max_value=2000.0, value=850.0, step=10.0)

    if input_mode == "Promedio últimos 3 consumos (kWh)":
        c1, c2, c3 = st.columns(3)
        with c1:
            mes1 = st.number_input("Mes 1 (kWh)", min_value=0.0, value=350.0)
        with c2:
            mes2 = st.number_input("Mes 2 (kWh)", min_value=0.0, value=380.0)
        with c3:
            mes3 = st.number_input("Mes 3 (kWh)", min_value=0.0, value=360.0)
        promedio_kwh = (mes1 + mes2 + mes3) / 3.0
    else:
        valor_factura = st.number_input("Valor promedio factura ($ COP)", min_value=50000.0, value=320000.0, step=10000.0)
        promedio_kwh = valor_factura / tarifa_kwh

    st.info(f"⚡ Consumo promedio calculado: **{promedio_kwh:.1f} kWh/mes**")

    st.subheader("3. Configuración del Sistema")
    ciudad = st.selectbox(
        "Ciudad / Región",
        ["Bogota", "Medellin", "Cali", "Barranquilla", "Bucaramanga", "Cartagena"]
    )
    
    tipo_sistema = st.selectbox(
        "Tipo de Solución",
        [
            ("hybrid", "Híbrido con Baterías (Respaldo en cortes + Ahorro)"),
            ("on_grid", "Conectado a Red (Solo Ahorro en Factura)"),
            ("off_grid", "Aislado 100% Baterías (Fincas / Sin red)")
        ],
        format_func=lambda x: x[1]
    )[0]

    btn_calcular = st.button("🚀 Calcular y Generar Propuesta", type="primary", use_container_width=True)

with col2:
    if btn_calcular:
        if not nombre.strip() or not telefono.strip():
            st.warning("⚠️ Por favor ingresa tu **Nombre** y **Teléfono** para generar la cotización.")
        else:
            try:
                req = QuoteRequest(
                    monthly_consumption_kwh=promedio_kwh,
                    system_type=tipo_sistema,
                    city=ciudad,
                    energy_rate_cop=tarifa_kwh,
                    backup_percentage=0.5
                )
                data = calculate_solar_quote(req).model_dump()

                # Guardar Lead en Supabase si está configurado
                if supabase_client:
                    try:
                        lead_record = {
                            "full_name": nombre.strip(),
                            "phone": telefono.strip(),
                            "email": email.strip() if email else None,
                            "city": ciudad,
                            "system_type": tipo_sistema,
                            "monthly_kwh": round(promedio_kwh, 2),
                            "recommended_kwp": data['recommended_kwp'],
                            "panels_count": data['solar_panels_count'],
                            "cabinet_model": data['cabinet']['model_name'],
                            "min_cost": data['total_cost_min_cop'],
                            "max_cost": data['total_cost_max_cop']
                        }
                        supabase_client.table("solar_leads").insert(lead_record).execute()
                    except Exception as db_err:
                        st.caption(f"(Nota técnica: lead no guardado en base de datos: {db_err})")

                st.subheader(f"📊 Propuesta para {nombre}")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Potencia Solar", f"{data['recommended_kwp']} kWp")
                m2.metric("Paneles (550W)", f"{data['solar_panels_count']} Unidades")
                m3.metric("Ahorro Estimado", f"${data['estimated_monthly_savings_cop']:,.0f}/mes")

                st.divider()

                st.markdown(f"### 📦 Gabinete: **{data['cabinet']['model_name']}**")
                st.write(f"- **Inversor Integrado:** {data['cabinet']['inverter_power_kw']} kW")
                st.write(f"- **Almacenamiento Litio:** {data['cabinet']['battery_capacity_kwh']} kWh")
                st.write(f"- **Dimensiones:** {data['cabinet']['dimensions_cm']}")

                st.divider()

                st.markdown("### 💰 Inversión Estimada (Llave en Mano)")
                st.success(f"**Rango de Inversión:** ${data['total_cost_min_cop']:,.0f} - ${data['total_cost_max_cop']:,.0f} COP")
                st.info(f"⏳ **Retorno de Inversión (ROI):** ~{data['estimated_roi_years']} años")

                st.divider()

                # 1. Botón de Descarga de PDF
                client_info = {
                    "full_name": nombre,
                    "phone": telefono,
                    "email": email,
                    "city": ciudad,
                    "monthly_kwh": promedio_kwh
                }
                pdf_bytes = generate_quote_pdf(client_info, data)

                st.download_button(
                    label="📄 Descargar Propuesta en PDF",
                    data=pdf_bytes,
                    file_name=f"Propuesta_Solar_{nombre.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                # 2. Botón WhatsApp
                numero_whatsapp = "573001234567" # Reemplaza por tu número
                mensaje_wa = (
                    f"¡Hola! Mi nombre es {nombre}. Acabo de cotizar un sistema solar:\n"
                    f"📍 Ciudad: {ciudad}\n"
                    f"⚡ Consumo: {promedio_kwh:.1f} kWh/mes\n"
                    f"📦 Gabinete: {data['cabinet']['model_name']} ({data['recommended_kwp']} kWp)\n"
                    f"💰 Inversión estimada: ${data['total_cost_min_cop']:,.0f} - ${data['total_cost_max_cop']:,.0f} COP\n\n"
                    f"Quiero agendar una visita técnica."
                )
                url_whatsapp = f"https://wa.me/{numero_whatsapp}?text={urllib.parse.quote(mensaje_wa)}"

                st.link_button(
                    "📲 Enviar Cotización por WhatsApp",
                    url_whatsapp,
                    type="primary",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"Error al procesar la cotización: {e}")
    else:
        st.write("👈 Completa tus datos a la izquierda y presiona **Calcular y Generar Propuesta**.")

# Sección Informativa Inferior
st.divider()
st.subheader("💡 ¿Qué tipo de sistema solar necesitas?")
card_col1, card_col2, card_col3 = st.columns(3, gap="medium")

with card_col1:
    st.markdown("""
        <div class="solution-card">
            <span class="badge">Más Popular</span>
            <div style="font-size: 2.5rem;">🔋⚡</div>
            <div class="solution-title">Sistema Híbrido</div>
            <div class="solution-desc">
                Reduce tu factura y almacena energía en baterías de litio para respaldo automático ante cortes de luz.
            </div>
        </div>
    """, unsafe_allow_html=True)

with card_col2:
    st.markdown("""
        <div class="solution-card">
            <span class="badge">Mayor Ahorro</span>
            <div style="font-size: 2.5rem;">☀️📉</div>
            <div class="solution-title">Conectado a Red (On-Grid)</div>
            <div class="solution-desc">
                Reduce hasta un 90% el valor de la factura trabajando en sincronía directa con la red.
            </div>
        </div>
    """, unsafe_allow_html=True)

with card_col3:
    st.markdown("""
        <div class="solution-card">
            <span class="badge">100% Autónomo</span>
            <div style="font-size: 2.5rem;">🏡🔋</div>
            <div class="solution-title">Aislado (Off-Grid)</div>
            <div class="solution-desc">
                Para fincas o zonas rurales sin red. 100% de la energía proviene de paneles y baterías.
            </div>
        </div>
    """, unsafe_allow_html=True)