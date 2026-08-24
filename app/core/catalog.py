from typing import List, Dict

SOLAR_CABINETS: List[Dict] = [
    {
        "id": "eco_3k",
        "name": "Gabinete Eco 3K All-in-One",
        "inverter_power_kw": 3.0,
        "battery_capacity_kwh": 5.12,
        "max_recommended_kwp": 3.6,
        "dimensions": "60 x 85 x 25 cm",
        "base_cost_cop": 14_500_000,
    },
    {
        "id": "pro_5k",
        "name": "Gabinete Pro 5K All-in-One",
        "inverter_power_kw": 5.0,
        "battery_capacity_kwh": 5.12,
        "max_recommended_kwp": 6.5,
        "dimensions": "60 x 120 x 25 cm",
        "base_cost_cop": 22_000_000,
    },
    {
        "id": "max_8k",
        "name": "Gabinete Max 8K All-in-One",
        "inverter_power_kw": 8.0,
        "battery_capacity_kwh": 10.24,
        "max_recommended_kwp": 10.5,
        "dimensions": "70 x 150 x 30 cm",
        "base_cost_cop": 35_000_000,
    }
]

# HSP por ciudad base
CITY_HSP: Dict[str, float] = {
    "bogota": 4.2,
    "medellin": 4.3,
    "cali": 4.6,
    "barranquilla": 5.1,
    "bucaramanga": 4.5,
    "cartagena": 5.2,
    "default": 4.3
}