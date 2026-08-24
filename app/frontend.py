import streamlit as st
import requests
from app.core.calculator import calculate_solar_quote
from app.schemas.quote import QuoteRequest


st.set_page_config(
    page_title="Cotizador Solar All-in-One",
    page_icon="☀️",
    layout="wide"
)

# Estilos CSS personalizados: Fondo moderno, tarjetas translúcidas y tipografía limpia
st.markdown("""
    <style>
        /* Fondo general */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            color: #ffffff !important;
        }

        /* Forzar texto blanco en títulos, subtítulos, etiquetas de inputs y radio buttons */
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {
            color: #ffffff !important;
        }

        /* Ajuste específico para etiquetas de campos (inputs, selects, radio) */
        div[data-testid="stWidgetLabel"] label,
        div[data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
        }

        /* Texto de las opciones de los radio buttons */
        div[role="radiogroup"] label div p {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        /* Tarjetas inferiores */
        .solution-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            height: 100%;
            transition: transform 0.2s ease;
        }
        .solution-card:hover {
            transform: translateY(-4px);
            border-color: #38bdf8;
        }
        .solution-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #38bdf8 !important;
            margin-top: 10px;
            margin-bottom: 6px;
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
            margin-bottom: 8px;
        }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/api/v1/quote"

st.title("☀️ Cotizador Solar Instantáneo")
st.caption("Calcula el dimensionamiento y costo de tu sistema solar compacto en gabinete todo en uno.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Datos de Consumo")
    
    input_mode = st.radio(
        "¿Cómo prefieres ingresar tus datos?",
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
        valor_factura = st.number_input("Valor promedio mensual de la factura ($ COP)", min_value=50000.0, value=320000.0, step=10000.0)
        promedio_kwh = valor_factura / tarifa_kwh

    st.info(f"⚡ Consumo promedio calculado: **{promedio_kwh:.1f} kWh/mes**")

    st.subheader("2. Configuración del Sistema")
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

    btn_calcular = st.button("🚀 Calcular Mi Sistema", type="primary", use_container_width=True)

with col2:
    if btn_calcular:
        payload = {
            "monthly_consumption_kwh": promedio_kwh,
            "system_type": tipo_sistema,
            "city": ciudad,
            "energy_rate_cop": tarifa_kwh,
            "backup_percentage": 0.5
        }
        req = QuoteRequest(
            monthly_consumption_kwh=promedio_kwh,
            system_type=tipo_sistema,
            city=ciudad,
            energy_rate_cop=tarifa_kwh,
            backup_percentage=0.5
        )
        data = calculate_solar_quote(req).model_dump()

        try:
            res = requests.post(API_URL, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                
                st.subheader("📊 Resultado del Dimensionamiento")
                
                # Métricas clave
                m1, m2, m3 = st.columns(3)
                m1.metric("Potencia Solar", f"{data['recommended_kwp']} kWp")
                m2.metric("Paneles (550W)", f"{data['solar_panels_count']} Unidades")
                m3.metric("Ahorro Estimado", f"${data['estimated_monthly_savings_cop']:,.0f}/mes")

                st.divider()

                # Gabinete Recomendado
                st.markdown(f"### 📦 Gabinete Recomendado: **{data['cabinet']['model_name']}**")
                st.write(f"- **Inversor Integrado:** {data['cabinet']['inverter_power_kw']} kW")
                st.write(f"- **Almacenamiento Litio:** {data['cabinet']['battery_capacity_kwh']} kWh")
                st.write(f"- **Dimensiones:** {data['cabinet']['dimensions_cm']}")

                st.divider()

                # Costos y ROI
                st.markdown("### 💰 Inversión Estimada (Llave en Mano)")
                st.success(f"**Rango de Inversión:** ${data['total_cost_min_cop']:,.0f} - ${data['total_cost_max_cop']:,.0f} COP")
                st.info(f"⏳ **Retorno de Inversión (ROI) Estimado:** ~{data['estimated_roi_years']} años")

            else:
                st.error("Error al procesar la cotización en el servidor.")
        except Exception as e:
            st.error(f"No se pudo conectar con el backend de FastAPI. Asegúrate de que uvicorn esté corriendo en el puerto 8000. Detalles: {e}")
    else:
        st.write("👈 Ingresa los datos de consumo a la izquierda y presiona **Calcular Mi Sistema** para generar la cotización al instante.")

# --- SECCIÓN INFORMATIVA INFERIOR ---
st.divider()
st.subheader("💡 ¿Qué tipo de sistema solar necesitas?")
st.caption("Conoce las diferencias de forma simple para elegir la mejor opción según tu caso.")

card_col1, card_col2, card_col3 = st.columns(3, gap="medium")

with card_col1:
    st.markdown("""
        <div class="solution-card">
            <span class="badge">Más Popular</span>
            <div style="font-size: 2.5rem;">🔋⚡</div>
            <div class="solution-title">Sistema Híbrido (Todo en Uno)</div>
            <div class="solution-desc">
                Genera energía solar de día, reduce tu factura al mínimo y <b>almacena energía en baterías de litio</b> para mantener tu casa o negocio encendido automáticamente si se va la luz.
            </div>
        </div>
    """, unsafe_allow_html=True)

with card_col2:
    st.markdown("""
        <div class="solution-card">
            <span class="badge">Mayor Ahorro / Menor Inversión</span>
            <div style="font-size: 2.5rem;">☀️📉</div>
            <div class="solution-title">Conectado a Red (On-Grid)</div>
            <div class="solution-desc">
                Ideal si tu objetivo es <b>reducir hasta un 90% el valor de la factura</b> y en tu zona no hay cortes frecuentes. Trabaja en sincronía directa con el operador de red sin requerir baterías.
            </div>
        </div>
    """, unsafe_allow_html=True)

with card_col3:
    st.markdown("""
        <div class="solution-card">
            <span class="badge">100% Autónomo</span>
            <div style="font-size: 2.5rem;">🏡🔋</div>
            <div class="solution-title">Sistema Aislado (Off-Grid)</div>
            <div class="solution-desc">
                Diseñado para <b>fincas, casas de campo o zonas rurales</b> donde no llega la red eléctrica. Toda la energía consumida proviene exclusivamente de los paneles solares y el banco de baterías.
            </div>
        </div>
    """, unsafe_allow_html=True)