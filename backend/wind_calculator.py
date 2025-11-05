from typing import List, Dict
from decimal import Decimal


class WindCalculator:
    """Wind power generation calculator.

    Uses a simple piecewise power curve with power law wind shear to adjust
    wind speed from 10m to hub height.
    """

    def __init__(self, shear_exponent: float = 0.2):
        self.shear_exponent = shear_exponent

    def adjust_wind_to_height(self, wind_speed_10m: float, hub_height_m: float) -> float:
        if wind_speed_10m is None:
            return 0.0
        if hub_height_m <= 0:
            return max(0.0, float(wind_speed_10m))
        return max(0.0, float(wind_speed_10m) * (hub_height_m / 10.0) ** self.shear_exponent)

    def hourly_power_kw(
        self,
        wind_speed_ms: float,
        cut_in_ms: float,
        rated_ms: float,
        cut_out_ms: float,
        rated_capacity_kw: float,
    ) -> float:
        v = Decimal(str(wind_speed_ms or 0))
        v_in = Decimal(str(cut_in_ms))
        v_r = Decimal(str(rated_ms))
        v_out = Decimal(str(cut_out_ms))
        p_r = Decimal(str(rated_capacity_kw))

        if v < v_in or v > v_out:
            return 0.0
        if v_in <= v <= v_r:
            # cubic between cut-in and rated
            denom = (v_r ** Decimal(3) - v_in ** Decimal(3))
            if denom == 0:
                return float(p_r)
            p = p_r / denom * v ** Decimal(3) - p_r / denom * v_in ** Decimal(3)
            return float(max(Decimal(0), p))
        # rated plateau
        return float(p_r)

    def calculate_hourly_generation(
        self,
        weather_data: List[Dict],
        hub_height_m: float,
        rated_capacity_kw: float,
        cut_in_ms: float,
        rated_ms: float,
        cut_out_ms: float,
        num_turbines: int = 1,
    ) -> List[Dict]:
        results: List[Dict] = []
        n = max(1, int(num_turbines or 1))
        for item in weather_data:
            wind10 = float(item.get('wind_speed', 0) or 0)
            wind_hub = self.adjust_wind_to_height(wind10, hub_height_m)
            power_kw = self.hourly_power_kw(
                wind_hub, cut_in_ms, rated_ms, cut_out_ms, rated_capacity_kw
            ) * n
            results.append({
                'timestamp': item.get('ts'),
                'wind_speed_10m_ms': wind10,
                'wind_speed_hub_ms': round(wind_hub, 3),
                'hourly_generation_kwh': round(float(power_kw), 4),
            })
        return results

    def summarize(self, hourly: List[Dict]) -> Dict:
        total = sum(x['hourly_generation_kwh'] for x in hourly)
        count = len(hourly)
        return {
            'total_generation_kwh': round(total, 4),
            'avg_hourly_generation_kwh': round(total / count, 4) if count else 0.0,
            'data_points': count,
        }


