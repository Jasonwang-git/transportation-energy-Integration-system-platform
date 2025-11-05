#!/usr/bin/env python3
"""
光伏发电预测计算模块
"""

import math
from datetime import datetime
from typing import List, Dict


class PVCalculator:
    """光伏发电计算器类"""
    
    def __init__(self):
        self.STC_TEMPERATURE = 25.0
        self.default_params = {
            'panel_efficiency': 0.20,
            'inverter_efficiency': 0.95,
            'temperature_coefficient': -0.004,
            'degradation_rate': 0.005
        }
    
    def calculate_pv_generation(self, 
                              solar_radiation: float, 
                              temperature: float, 
                              installed_capacity: float,
                              panel_efficiency: float = None,
                              inverter_efficiency: float = None,
                              temperature_coefficient: float = None,
                              degradation_factor: float = 1.0) -> float:
        """计算光伏发电量"""
        panel_efficiency = panel_efficiency or self.default_params['panel_efficiency']
        inverter_efficiency = inverter_efficiency or self.default_params['inverter_efficiency']
        temperature_coefficient = temperature_coefficient or self.default_params['temperature_coefficient']
        
        temp_factor = 1 + temperature_coefficient * (temperature - self.STC_TEMPERATURE)
        system_efficiency = panel_efficiency * inverter_efficiency * temp_factor * degradation_factor
        generation = (solar_radiation / 1000) * installed_capacity * system_efficiency
        
        return max(0, generation)
    
    def calculate_degradation_factor(self, years: int, degradation_rate: float = None) -> float:
        """计算设备衰减因子"""
        degradation_rate = degradation_rate or self.default_params['degradation_rate']
        return (1 - degradation_rate) ** years
    
    def calculate_hourly_generation(self, 
                                  weather_data: List[Dict],
                                  installed_capacity: float,
                                  params: Dict = None) -> List[Dict]:
        """计算小时级发电量"""
        params = params or self.default_params
        results = []
        
        for weather in weather_data:
            solar_radiation = float(weather.get('surface_radiation_wm2', 0) or 0)
            temperature = float(weather.get('temp_c', self.STC_TEMPERATURE) or self.STC_TEMPERATURE)
            
            hourly_generation = self.calculate_pv_generation(
                solar_radiation=solar_radiation,
                temperature=temperature,
                installed_capacity=installed_capacity,
                panel_efficiency=params['panel_efficiency'],
                inverter_efficiency=params['inverter_efficiency'],
                temperature_coefficient=params['temperature_coefficient'],
                degradation_factor=1.0
            )
            
            results.append({
                'timestamp': weather.get('ts'),
                'solar_radiation_wm2': solar_radiation,
                'temperature_c': temperature,
                'hourly_generation_kwh': round(hourly_generation, 4),
                'efficiency_factor': round(params['panel_efficiency'] * params['inverter_efficiency'], 4)
            })
        
        return results
    
    def calculate_yearly_forecast(self,
                                 base_year_generation: float,
                                 years: int,
                                 installed_capacity: float,
                                 degradation_rate: float = None) -> List[Dict]:
        """计算多年发电量预测"""
        degradation_rate = degradation_rate or self.default_params['degradation_rate']
        current_year = datetime.now().year
        yearly_forecasts = []
        
        for year in range(1, years + 1):
            degradation_factor = self.calculate_degradation_factor(year, degradation_rate)
            yearly_generation = base_year_generation * degradation_factor
            
            yearly_forecasts.append({
                'year': current_year + year,
                'total_generation_kwh': round(yearly_generation, 2),
                'degradation_factor': round(degradation_factor, 4),
                'average_daily_generation_kwh': round(yearly_generation / 365, 2),
                'capacity_factor': round(yearly_generation / (installed_capacity * 8760), 4)
            })
        
        return yearly_forecasts
    
    def calculate_statistics(self, generation_results: List[Dict]) -> Dict:
        """计算发电量统计信息"""
        if not generation_results:
            return {}
        
        total_generation = sum(item['hourly_generation_kwh'] for item in generation_results)
        data_points = len(generation_results)
        
        return {
            'total_generation_kwh': round(total_generation, 4),
            'average_daily_generation_kwh': round(total_generation / data_points * 24, 4),
            'data_points': data_points,
            'avg_hourly_generation_kwh': round(total_generation / data_points, 4)
        }
    
    def calculate_capacity_factor(self, 
                                total_generation: float, 
                                installed_capacity: float, 
                                hours: int) -> float:
        """计算容量因子"""
        if installed_capacity <= 0 or hours <= 0:
            return 0.0
        
        theoretical_max = installed_capacity * hours
        return total_generation / theoretical_max if theoretical_max > 0 else 0.0