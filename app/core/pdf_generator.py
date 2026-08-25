from fpdf import FPDF
from datetime import datetime
import os

class PDFQuote(FPDF):
    def header(self):
        # 1. Fondo oscuro elegante en el encabezado
        self.set_fill_color(15, 23, 42) # Slate 900
        self.rect(0, 0, 210, 36, 'F')
        
        # 2. Ruta del Logo (busca app/logo.png o logo.png)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "..", "logo.png")
        
        if not os.path.exists(logo_path):
            logo_path = os.path.join(current_dir, "logo.png")

        if os.path.exists(logo_path):
            # Logo en la izquierda con fondo blanco para que resalte
            self.set_fill_color(255, 255, 255)
            self.rect(10, 5, 48, 26, 'F')
            self.image(logo_path, x=11, y=8, w=46)
            
            # Textos institucionales alineados a la derecha
            self.set_xy(60, 6)
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(255, 255, 255)
            self.cell(140, 6, "PROPUESTA TECNICA - SISTEMA SOLAR SOLARTECH", ln=True, align="R")
            
            self.set_x(60)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(56, 189, 248) # Cyan
            self.cell(140, 5, "Dimensionamiento Preliminar y Estimacion Economica", ln=True, align="R")
            
            self.set_x(60)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(203, 213, 225)
            self.cell(140, 5, "NIT: 901798729 | Cel / WhatsApp: 310 247 6744", ln=True, align="R")
        else:
            # Encabezado centrado si aún no encuentra la imagen
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(255, 255, 255)
            self.cell(0, 7, "PROPUESTA TECNICA - SISTEMA SOLAR SOLARTECH", ln=True, align="C")
            
            self.set_font("Helvetica", "", 9)
            self.set_text_color(56, 189, 248)
            self.cell(0, 5, "Dimensionamiento Preliminar y Estimacion Economica", ln=True, align="C")
            
            self.set_font("Helvetica", "", 8)
            self.set_text_color(203, 213, 225)
            self.cell(0, 5, "NIT: 901798729 | Cel / WhatsApp: 310 247 6744", ln=True, align="C")
            
        self.ln(14)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "SOLARTECH - Soluciones en Tecnologia y Energias Alternativas. Sujeto a visita tecnica en sitio.", align="C")

def sanitize_text(text: str) -> str:
    """Limpia tildes y caracteres especiales incompatibles con la fuente estandar Helvetica."""
    replacements = {
        "•": "-", "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "ñ": "n", "Ñ": "N",
        "“": '"', "”": '"', "’": "'", "–": "-", "—": "-"
    }
    for k, v in replacements.items():
        text = str(text).replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_quote_pdf(client_data: dict, quote_data: dict) -> bytes:
    pdf = PDFQuote()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Datos del Cliente
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, sanitize_text("1. INFORMACION DEL CLIENTE Y UBICACION"), ln=True)
    pdf.set_line_width(0.4)
    pdf.set_draw_color(56, 189, 248)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(100, 6, sanitize_text(f"Cliente: {client_data.get('full_name', 'N/A')}"), ln=False)
    pdf.cell(90, 6, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(100, 6, sanitize_text(f"Telefono: {client_data.get('phone', 'N/A')}"), ln=False)
    pdf.cell(90, 6, sanitize_text(f"Ciudad: {client_data.get('city', 'N/A')}"), ln=True)
    if client_data.get('email'):
        pdf.cell(100, 6, sanitize_text(f"Email: {client_data.get('email')}"), ln=True)
    pdf.cell(100, 6, sanitize_text(f"Consumo promedio evaluado: {client_data.get('monthly_kwh', 0):.1f} kWh/mes"), ln=True)
    pdf.ln(5)

    # 2. Resumen Técnico
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, sanitize_text("2. DIMENSIONAMIENTO Y EQUIPAMIENTO RECOMENDADO"), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, sanitize_text(f"- Potencia Solar Total: {quote_data['recommended_kwp']} kWp"), ln=True)
    pdf.cell(0, 6, sanitize_text(f"- Cantidad de Paneles: {quote_data['solar_panels_count']} paneles Tier-1 de 550W"), ln=True)
    pdf.cell(0, 6, sanitize_text(f"- Gabinete Integrado: {quote_data['cabinet']['model_name']}"), ln=True)
    pdf.cell(0, 6, sanitize_text(f"    * Inversor Integrado: {quote_data['cabinet']['inverter_power_kw']} kW"), ln=True)
    pdf.cell(0, 6, sanitize_text(f"    * Bateria Litio LiFePO4: {quote_data['cabinet']['battery_capacity_kwh']} kWh"), ln=True)
    pdf.cell(0, 6, sanitize_text(f"    * Dimensiones Gabinete: {quote_data['cabinet']['dimensions_cm']}"), ln=True)
    pdf.cell(0, 6, sanitize_text(f"- Generacion Mensual Estimada: ~{quote_data['estimated_monthly_generation_kwh']} kWh/mes"), ln=True)
    pdf.ln(5)

    # 3. Estimación Económica
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, sanitize_text("3. ESTIMACION FINANCIERA Y RETORNO"), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_fill_color(240, 249, 255)
    pdf.rect(10, pdf.get_y(), 190, 24, 'F')
    pdf.set_xy(14, pdf.get_y() + 2)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(0, 6, sanitize_text(f"Rango de Inversion Llave en Mano: ${quote_data['total_cost_min_cop']:,.0f} - ${quote_data['total_cost_max_cop']:,.0f} COP"), ln=True)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, sanitize_text(f"Ahorro mensual proyectado en factura: ~${quote_data['estimated_monthly_savings_cop']:,.0f} COP/mes"), ln=True)
    pdf.set_x(14)
    pdf.cell(0, 6, sanitize_text(f"Tiempo estimado de Retorno de Inversion (ROI): ~{quote_data['estimated_roi_years']} anos"), ln=True)

    output_data = pdf.output(dest='S')
    if isinstance(output_data, str):
        return output_data.encode('latin-1')
    return bytes(output_data)