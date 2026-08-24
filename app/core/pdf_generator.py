from fpdf import FPDF
from datetime import datetime

class PDFQuote(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 30, 'F')
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "PROPUESTA TECNICA - SISTEMA SOLAR ALL-IN-ONE", ln=True, align="C")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(56, 189, 248)
        self.cell(0, 4, "Dimensionamiento Preliminar y Estimacion Economica", ln=True, align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Documento de estimacion tecnica preliminar. Sujeto a visita tecnica en sitio.", align="C")

def generate_quote_pdf(client_data: dict, quote_data: dict) -> bytes:
    pdf = PDFQuote()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Datos del Cliente
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "1. INFORMACION DEL CLIENTE Y UBICACION", ln=True)
    pdf.set_line_width(0.4)
    pdf.set_draw_color(56, 189, 248)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(100, 6, f"Cliente: {client_data.get('full_name', 'N/A')}", ln=False)
    pdf.cell(90, 6, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(100, 6, f"Telefono: {client_data.get('phone', 'N/A')}", ln=False)
    pdf.cell(90, 6, f"Ciudad: {client_data.get('city', 'N/A')}", ln=True)
    if client_data.get('email'):
        pdf.cell(100, 6, f"Email: {client_data.get('email')}", ln=True)
    pdf.cell(100, 6, f"Consumo promedio evaluado: {client_data.get('monthly_kwh', 0):.1f} kWh/mes", ln=True)
    pdf.ln(6)

    # 2. Resumen Técnico
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "2. DIMENSIONAMIENTO Y EQUIPAMIENTO RECOMENDADO", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, f"- Potencia Solar Total: {quote_data['recommended_kwp']} kWp", ln=True)
    pdf.cell(0, 6, f"- Cantidad de Paneles: {quote_data['solar_panels_count']} paneles Tier-1 de 550W", ln=True)
    pdf.cell(0, 6, f"- Gabinete Integrado: {quote_data['cabinet']['model_name']}", ln=True)
    pdf.cell(0, 6, f"    * Inversor Integrado: {quote_data['cabinet']['inverter_power_kw']} kW", ln=True)
    pdf.cell(0, 6, f"    * Bateria Litio LiFePO4: {quote_data['cabinet']['battery_capacity_kwh']} kWh", ln=True)
    pdf.cell(0, 6, f"    * Dimensiones Gabinete: {quote_data['cabinet']['dimensions_cm']}", ln=True)
    pdf.cell(0, 6, f"- Generacion Mensual Estimada: ~{quote_data['estimated_monthly_generation_kwh']} kWh/mes", ln=True)
    pdf.ln(6)

    # 3. Estimación Económica
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "3. ESTIMACION FINANCIERA Y RETORNO", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_fill_color(240, 249, 255)
    pdf.rect(10, pdf.get_y(), 190, 24, 'F')
    pdf.set_xy(14, pdf.get_y() + 2)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(0, 6, f"Rango de Inversion Llave en Mano: ${quote_data['total_cost_min_cop']:,.0f} - ${quote_data['total_cost_max_cop']:,.0f} COP", ln=True)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, f"Ahorro mensual proyectado en factura: ~${quote_data['estimated_monthly_savings_cop']:,.0f} COP/mes", ln=True)
    pdf.set_x(14)
    pdf.cell(0, 6, f"Tiempo estimado de Retorno de Inversion (ROI): ~{quote_data['estimated_roi_years']} anos", ln=True)

    return bytes(pdf.output())