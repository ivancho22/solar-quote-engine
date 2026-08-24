import math
from app.schemas.quote import QuoteRequest, QuoteResponse, CabinetDetails, SystemType
from app.core.catalog import SOLAR_CABINETS, CITY_HSP

PANEL_WATT_RATING = 550  # Wp por panel
PERFORMANCE_RATIO = 0.80  # Eficiencia global del sistema

def select_cabinet(required_kwp: float, system_type: SystemType) -> dict:
    for cabinet in SOLAR_CABINETS:
        if cabinet["max_recommended_kwp"] >= required_kwp:
            return cabinet
    return SOLAR_CABINETS[-1]

def calculate_solar_quote(payload: QuoteRequest) -> QuoteResponse:
    # 1. Obtener HSP
    city_key = payload.city.strip().lower()
    hsp = CITY_HSP.get(city_key, CITY_HSP["default"])

    # 2. Consumo diario requerido
    daily_consumption_kwh = payload.monthly_consumption_kwh / 30.0

    # 3. Potencia DC necesaria (kWp)
    required_kwp = round(daily_consumption_kwh / (hsp * PERFORMANCE_RATIO), 2)

    # 4. Número de módulos
    panel_count = math.ceil((required_kwp * 1000) / PANEL_WATT_RATING)
    actual_kwp = round((panel_count * PANEL_WATT_RATING) / 1000.0, 2)

    # 5. Selección de Gabinete
    cabinet_info = select_cabinet(actual_kwp, payload.system_type)
    
    # 6. Generación mensual estimada
    monthly_generation_kwh = round(actual_kwp * hsp * 30 * PERFORMANCE_RATIO, 1)
    
    # 7. Estimación de costos (Estructura paneles + instalación + gabinete)
    cost_per_panel_installed = 1_100_000  # Panel + estructura + cableado DC
    base_installation_cost = 2_500_000
    
    total_cost = cabinet_info["base_cost_cop"] + (panel_count * cost_per_panel_installed) + base_installation_cost
    cost_min = round(total_cost * 0.95, -4)
    cost_max = round(total_cost * 1.05, -4)

    # 8. Estimación de Ahorro y ROI
    usable_monthly_kwh = min(monthly_generation_kwh, payload.monthly_consumption_kwh)
    monthly_savings_cop = round(usable_monthly_kwh * payload.energy_rate_cop, 2)
    annual_savings = monthly_savings_cop * 12
    
    roi_years = round(total_cost / annual_savings, 1) if annual_savings > 0 else 0.0

    return QuoteResponse(
        recommended_kwp=actual_kwp,
        solar_panels_count=panel_count,
        panel_individual_power_w=PANEL_WATT_RATING,
        cabinet=CabinetDetails(
            model_name=cabinet_info["name"],
            inverter_power_kw=cabinet_info["inverter_power_kw"],
            battery_capacity_kwh=cabinet_info["battery_capacity_kwh"],
            dimensions_cm=cabinet_info["dimensions"]
        ),
        estimated_monthly_generation_kwh=monthly_generation_kwh,
        estimated_monthly_savings_cop=monthly_savings_cop,
        total_cost_min_cop=cost_min,
        total_cost_max_cop=cost_max,
        estimated_roi_years=roi_years
    )