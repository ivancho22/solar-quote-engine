from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class SystemType(str, Enum):
    ON_GRID = "on_grid"
    HYBRID = "hybrid"
    OFF_GRID = "off_grid"

class QuoteRequest(BaseModel):
    monthly_consumption_kwh: float = Field(..., gt=0, description="Promedio mensual en kWh de los últimos 3 meses")
    system_type: SystemType = Field(..., description="Tipo de sistema deseado")
    city: str = Field(default="Bogotá", description="Ciudad para determinar Horas Sol Pico (HSP)")
    energy_rate_cop: float = Field(default=850.0, gt=0, description="Tarifa actual por kWh en COP")
    backup_percentage: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Porcentaje de respaldo diario (para híbrido/off-grid)")

class CabinetDetails(BaseModel):
    model_name: str
    inverter_power_kw: float
    battery_capacity_kwh: float
    dimensions_cm: str

class QuoteResponse(BaseModel):
    recommended_kwp: float
    solar_panels_count: int
    panel_individual_power_w: int
    cabinet: CabinetDetails
    estimated_monthly_generation_kwh: float
    estimated_monthly_savings_cop: float
    total_cost_min_cop: float
    total_cost_max_cop: float
    estimated_roi_years: float