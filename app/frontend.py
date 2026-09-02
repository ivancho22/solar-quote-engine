
import sys
import os
import urllib.parse
from datetime import datetime
import requests
# Asegurar path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from fpdf import FPDF
from app.core.calculator import calculate_solar_quote
from app.schemas.quote import QuoteRequest
# Configuración inicial
st.set_page_config(
    page_title="Cotizador SOLARTECH",
    page_icon="☀️",
    layout="wide"
)
# Configuración de Supabase
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase_client = None
# Generador de PDF integrado
class PDFQuote(FPDF):
    def header(self):
        # 1. Fondo azul oscuro continuo
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 38, 'F')
        
        # 2. Rutas del logo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, "logo.png"),
            os.path.join(os.path.dirname(base_dir), "logo.png"),
            "app/logo.png",
            "logo.png"
        ]
        logo_path = next((p for p in possible_paths if os.path.exists(p)), None)
        if logo_path:
            # Estampar directamente el logo PNG transparente
            try:
                self.image(logo_path, x=10, y=7, w=46)
            except Exception:
                pass
            
            # Textos institucionales
            self.set_xy(58, 7)
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(255, 255, 255)
            self.cell(142, 6, "PROPUESTA TECNICA - SISTEMA SOLAR SOLARTECH", ln=True, align="R")
            
            self.set_x(58)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(56, 189, 248)
            self.cell(142, 5, "Dimensionamiento Preliminar y Estimacion Economica", ln=True, align="R")
            
            self.set_x(58)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(203, 213, 225)
            self.cell(142, 5, "NIT: 901798729 | Cel / WhatsApp: 310 247 6744", ln=True, align="R")
        else:
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(255, 255, 255)
            self.cell(0, 7, "PROPUESTA TECNICA - SISTEMA SOLAR SOLARTECH", ln=True, align="C")
            
            self.set_font("Helvetica", "", 9)
            self.set_text_color(56, 189, 248)
            self.cell(0, 5, "Dimensionamiento Preliminar y Estimacion Economica", ln=True, align="C")
            
            self.set_font("Helvetica", "", 8)
            self.set_text_color(203, 213, 225)
            self.cell(0, 5, "NIT: 901798729 | Cel / WhatsApp: 310 247 6744", ln=True, align="C")
            
        self.ln(16)
    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "SOLARTECH - Soluciones en Tecnologia y Energias Alternativas. Documento preliminar.", align="C")
def sanitize_pdf_text(text: str) -> str:
    replacements = {
        "•": "-", "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "ñ": "n", "Ñ": "N",
        "“": '"', "”": '"', "’": "'", "–": "-", "—": "-"
    }
    for k, v in replacements.items():
        text = str(text).replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')
def make_pdf(client_data: dict, quote_data: dict) -> bytes:
    pdf = PDFQuote()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    # 1. Cliente
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, sanitize_pdf_text("1. INFORMACION DEL CLIENTE Y UBICACION"), ln=True)
    pdf.set_line_width(0.4)
    pdf.set_draw_color(56, 189, 248)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(100, 6, sanitize_pdf_text(f"Cliente: {client_data.get('full_name', 'N/A')}"), ln=False)
    pdf.cell(90, 6, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(100, 6, sanitize_pdf_text(f"Telefono: {client_data.get('phone', 'N/A')}"), ln=False)
    pdf.cell(90, 6, sanitize_pdf_text(f"Ciudad: {client_data.get('city', 'N/A')}"), ln=True)
    if client_data.get('email'):
        pdf.cell(100, 6, sanitize_pdf_text(f"Email: {client_data.get('email')}"), ln=True)
    pdf.cell(100, 6, sanitize_pdf_text(f"Consumo promedio evaluado: {client_data.get('monthly_kwh', 0):.1f} kWh/mes"), ln=True)
    pdf.ln(5)
    # 2. Equipamiento
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, sanitize_pdf_text("2. DIMENSIONAMIENTO Y EQUIPAMIENTO RECOMENDADO"), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, sanitize_pdf_text(f"- Potencia Solar Total: {quote_data['recommended_kwp']} kWp"), ln=True)
    pdf.cell(0, 6, sanitize_pdf_text(f"- Cantidad de Paneles: {quote_data['solar_panels_count']} paneles Tier-1 de 550W"), ln=True)
    pdf.cell(0, 6, sanitize_pdf_text(f"- Gabinete Integrado: {quote_data['cabinet']['model_name']}"), ln=True)
    pdf.cell(0, 6, sanitize_pdf_text(f"    * Inversor Integrado: {quote_data['cabinet']['inverter_power_kw']} kW"), ln=True)
    pdf.cell(0, 6, sanitize_pdf_text(f"    * Bateria Litio LiFePO4: {quote_data['cabinet']['battery_capacity_kwh']} kWh"), ln=True)
    pdf.cell(0, 6, sanitize_pdf_text(f"    * Dimensiones Gabinete: {quote_data['cabinet']['dimensions_cm']}"), ln=True)
    pdf.cell(0, 6, sanitize_pdf_text(f"- Generacion Mensual Estimada: ~{quote_data['estimated_monthly_generation_kwh']} kWh/mes"), ln=True)
    pdf.ln(5)
    # 3. Costos
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, sanitize_pdf_text("3. ESTIMACION FINANCIERA Y RETORNO"), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_fill_color(240, 249, 255)
    pdf.rect(10, pdf.get_y(), 190, 24, 'F')
    pdf.set_xy(14, pdf.get_y() + 2)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(0, 6, sanitize_pdf_text(f"Rango de Inversion Llave en Mano: ${quote_data['total_cost_min_cop']:,.0f} - ${quote_data['total_cost_max_cop']:,.0f} COP"), ln=True)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, sanitize_pdf_text(f"Ahorro mensual proyectado en factura: ~${quote_data['estimated_monthly_savings_cop']:,.0f} COP/mes"), ln=True)
    pdf.set_x(14)
    pdf.cell(0, 6, sanitize_pdf_text(f"Tiempo estimado de Retorno de Inversion (ROI): ~{quote_data['estimated_roi_years']} anos"), ln=True)
    out = pdf.output(dest='S')
    return out.encode('latin-1') if isinstance(out, str) else bytes(out)
# Estilos CSS
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
        .logo-box {
            background: #ffffff;
            border-radius: 10px;
            padding: 6px 12px;
            display: flex;
            align-items: center;
            justify-content: center;
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
# --- ENCABEZADO INSTITUCIONAL SOLARTECH ---
header_col1, header_col2 = st.columns([1, 3], gap="medium")
with header_col1:
    logo_path = "app/logo.png" if os.path.exists("app/logo.png") else "logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("### ☀️ SOLAR&TECH")
with header_col2:
    st.markdown("""
        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; padding-top: 5px;">
            <h2 style="margin: 0; color: #38bdf8 !important; font-size: 1.7rem; font-weight: 700;">
                Cotizador Sistema SOLARTECH
            </h2>
            <p style="margin: 3px 0; font-size: 0.95rem; color: #cbd5e1 !important;">
                <b>SOLAR&TECH</b> · Soluciones en Tecnología y Energías Alternativas
            </p>
            <p style="margin: 0; font-size: 0.85rem; color: #94a3b8 !important;">
                📄 <b>NIT:</b> 901798729 &nbsp;|&nbsp; 📲 <b>WhatsApp:</b> +57 310 247 6744
            </p>
        </div>
    """, unsafe_allow_html=True)
st.divider()
# Función para reiniciar formulario
def reset_form():
    st.session_state["f_nombre"] = ""
    st.session_state["f_tel"] = ""
    st.session_state["f_email"] = ""
    st.session_state["f_mes1"] = 350.0
    st.session_state["f_mes2"] = 380.0
    st.session_state["f_mes3"] = 360.0
    st.session_state["f_factura"] = 320000.0
# Inicialización de keys
if "f_nombre" not in st.session_state:
    st.session_state["f_nombre"] = ""
if "f_tel" not in st.session_state:
    st.session_state["f_tel"] = ""
if "f_email" not in st.session_state:
    st.session_state["f_email"] = ""
col1, col2 = st.columns([1, 1], gap="large")
with col1:
    st.subheader("1. Tus Datos de Contacto")
    nombre = st.text_input("Nombre Completo *", placeholder="Ej. Juan Pérez", key="nombre_input")
    telefono = st.text_input("Número de Teléfono / WhatsApp *", placeholder="Ej. 3001234567", key="tel_input")
    email = st.text_input("Correo Electrónico (Opcional)", placeholder="juan@ejemplo.com", key="email_input")
    st.subheader("2. Datos de Consumo")
    input_mode = st.radio(
        "¿Cómo prefieres ingresar tus consumos?",
        ["Promedio últimos 3 consumos de tu factura (kWh)", "Valor promedio de la factura ($ COP)"],
        horizontal=True
    )
    
    tarifa_kwh = st.number_input("Costo por kWh en tu factura por la electrificadora ($ COP)", min_value=300.0, max_value=2000.0, value=850.0, step=10.0)
    if input_mode == "Promedio últimos 3 consumos de tu factura (kWh)":
        c1, c2, c3 = st.columns(3)
        with c1:
            mes1 = st.number_input("FacturaMes 1 (kWh)", min_value=0.0, value=350.0)
        with c2:
            mes2 = st.number_input("Factura Mes 2 (kWh)", min_value=0.0, value=380.0)
        with c3:
            mes3 = st.number_input("Factura Mes 3 (kWh)", min_value=0.0, value=360.0)
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
                # Guardar Lead en Supabase
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
                        
                        # 1. Guarda en Supabase
                        supabase_client.table("solar_leads").insert(lead_record).execute()
                        
                        # 2. Notifica al Webhook de Make al instante
                        webhook_url = "https://hook.eu1.make.com/bkfmuow1cy97yjad97giswd8rq7g7olx"
                        requests.post(webhook_url, json=lead_record)

                    except Exception:
                        pass
                st.success("✅ Cotización generada exitosamente. Desplázate hacia abajo para ver los detalles y descargar la propuesta en PDF.")
                st.divider()                
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
                # Generación PDF
                client_info = {
                    "full_name": nombre,
                    "phone": telefono,
                    "email": email,
                    "city": ciudad,
                    "monthly_kwh": promedio_kwh
                }
                pdf_bytes = make_pdf(client_info, data)
                st.download_button(
                    label="📄 Descargar Propuesta en PDF",
                    data=pdf_bytes,
                    file_name=f"Propuesta_Solar_{nombre.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                # WhatsApp
                numero_whatsapp = "573102476744"
                mensaje_wa = (
                    f"¡Hola! Mi nombre es {nombre}. Acabo de cotizar un sistema solar con SOLARTECH:\n"
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
