from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import math
from typing import List
from pydantic import BaseModel
from pv_calculator import PVCalculator

# 加载环境变量
load_dotenv()

app = FastAPI(title="交通能源融合系统平台", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "123456"),  # 修改为正确的密码
    "database": os.getenv("DB_NAME", "energy_platform"),
    "charset": "utf8mb4"
}

def get_db_connection():
    """获取数据库连接"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")

def execute_query(sql: str, params: tuple = ()):
    """执行查询并返回结果"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        conn.close()

def get_table_name_by_province(province: str) -> str:
    """根据省份名称获取对应的天气观测表名"""
    province_table_mapping = {
        "北京": "weather_observation_beijing",
        "上海": "weather_observation_shanghai", 
        "天津": "weather_observation_tianjin",
        "河北": "weather_observation_hebei",
        "山西": "weather_observation_shanxi",
        "内蒙古": "weather_observation_neimenggu",
        "辽宁": "weather_observation_liaoning",
        "吉林": "weather_observation_jilin",
        "黑龙江": "weather_observation_heilongjiang"
    }
    return province_table_mapping.get(province, "weather_observation")

def get_province_id_by_name(province: str) -> int:
    """根据省份名称获取省份ID"""
    sql = "SELECT id FROM province WHERE name = %s"
    result = execute_query(sql, (province,))
    return result[0]['id'] if result else None

def get_province_name_by_id(province_id: int) -> str:
    """根据省份ID获取省份名称"""
    sql = "SELECT name FROM province WHERE id = %s"
    result = execute_query(sql, (province_id,))
    return result[0]['name'] if result else None

# Pydantic模型定义
class PVForecastConfig(BaseModel):
    station_id: int
    installed_capacity_kw: float
    panel_efficiency: float = 0.20
    inverter_efficiency: float = 0.95
    temperature_coefficient: float = -0.004
    degradation_rate: float = 0.005
    tilt_angle: float = 30.0
    azimuth_angle: float = 180.0

class PVForecastRequest(BaseModel):
    station_id: int
    start_date: str
    end_date: str
    installed_capacity_kw: float
    panel_efficiency: float = 0.20
    inverter_efficiency: float = 0.95
    temperature_coefficient: float = -0.004
    degradation_rate: float = 0.005
    tilt_angle: float = 30.0
    azimuth_angle: float = 180.0

# 创建光伏计算器实例
pv_calculator = PVCalculator()

def get_weather_data_by_station_and_time(station_id: int, start_date: str, end_date: str) -> List[dict]:
    """根据站点ID和时间范围获取气象数据"""
    try:
        # 获取站点信息
        station_sql = """
        SELECT s.id, s.name, s.province, s.province_id, p.name as province_name
        FROM station s 
        LEFT JOIN province p ON s.province_id = p.id
        WHERE s.id = %s
        """
        station_result = execute_query(station_sql, (station_id,))
        
        if not station_result:
            raise HTTPException(status_code=404, detail="站点不存在")
        
        station = station_result[0]
        table_name = get_table_name_by_province(station['province'])
        
        # 查询气象数据
        weather_sql = f"""
        SELECT ts, surface_radiation_wm2, temp_c, humidity, pressure_hpa
        FROM {table_name} 
        WHERE province_id = %s 
        AND ts BETWEEN %s AND %s
        ORDER BY ts
        """
        
        weather_data = execute_query(weather_sql, (station['province_id'], start_date, end_date))
        
        return weather_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取气象数据失败: {str(e)}")

# 计算函数现在使用pv_calculator模块

# 静态文件服务 - 将HTML文件作为前端
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    """访问根路径时返回主页面"""
    return FileResponse("交通能源融合系统平台.html")

# API路由
@app.get("/api/stations/nearby")
async def get_nearby_stations(
    lng: float = Query(..., description="经度"),
    lat: float = Query(..., description="纬度"),
    limit: int = Query(5, description="返回站点数量")
):
    """根据经纬度获取附近站点"""
    sql = """
    SELECT id, name, province, lng, lat,
           ((lng-%s)*(lng-%s)+(lat-%s)*(lat-%s)) AS distance_squared
    FROM station 
    ORDER BY distance_squared 
    LIMIT %s
    """
    stations = execute_query(sql, (lng, lng, lat, lat, limit))
    
    # 计算实际距离（公里）
    for station in stations:
        station['distance_km'] = math.sqrt(station['distance_squared']) * 111.32  # 粗略转换
        del station['distance_squared']
    
    return {"stations": stations}

@app.get("/api/stations/search")
async def search_stations(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回数量")
):
    """搜索站点"""
    sql = """
    SELECT id, name, province, lng, lat
    FROM station 
    WHERE name LIKE %s OR province LIKE %s
    ORDER BY 
        CASE 
            WHEN name = %s THEN 1
            WHEN name LIKE %s THEN 2
            ELSE 3
        END
    LIMIT %s
    """
    keyword_pattern = f"%{keyword}%"
    exact_match = keyword
    stations = execute_query(sql, (keyword_pattern, keyword_pattern, exact_match, keyword_pattern, limit))
    return {"stations": stations}

@app.get("/api/weather/by-station/{station_id}")
async def get_weather_by_station(station_id: int):
    """根据站点ID获取天气数据"""
    try:
        # 1. 获取站点信息（包含province_id）
        station_sql = """
        SELECT s.id, s.name, s.province, s.lng, s.lat, s.province_id, p.name as province_name
        FROM station s 
        LEFT JOIN province p ON s.province_id = p.id
        WHERE s.id = %s
        """
        station_result = execute_query(station_sql, (station_id,))
        
        if not station_result:
            raise HTTPException(status_code=404, detail="站点不存在")
        
        station = station_result[0]
        
        if not station['province_id']:
            raise HTTPException(status_code=404, detail="站点未关联省份")
        
        # 2. 获取对应省份的天气表名
        table_name = get_table_name_by_province(station['province'])
        
        # 3. 获取该省份的天气数据
        weather_sql = f"""
        SELECT * FROM {table_name} 
        WHERE province_id = %s
        ORDER BY ts DESC 
        LIMIT 100
        """
        weather_data = execute_query(weather_sql, (station['province_id'],))
        
        return {
            "station": {
                "id": station['id'],
                "name": station['name'],
                "province": station['province'],
                "province_id": station['province_id'],
                "province_name": station['province_name'],
                "lng": station['lng'],
                "lat": station['lat']
            },
            "weather_data": weather_data,
            "data_source": f"{station['province_name']}省天气数据",
            "table_name": table_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取天气数据失败: {str(e)}")

@app.get("/api/weather/by-province/{province}")
async def get_weather_by_province(province: str):
    """根据省份获取天气数据"""
    try:
        table_name = get_table_name_by_province(province)
        
        # 获取该省份的天气数据
        weather_sql = f"""
        SELECT * FROM {table_name} 
        WHERE station_id = (
            SELECT station_id FROM {table_name} LIMIT 1
        )
        ORDER BY ts DESC 
        LIMIT 100
        """
        weather_data = execute_query(weather_sql)
        
        return {
            "province": province,
            "weather_data": weather_data,
            "data_source": f"{province}省天气数据"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取天气数据失败: {str(e)}")

# 光伏发电预测API
@app.post("/api/pv-forecast/config")
async def create_pv_config(config: PVForecastConfig):
    """创建光伏发电预测配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查站点是否存在
        station_check = execute_query("SELECT id FROM station WHERE id = %s", (config.station_id,))
        if not station_check:
            raise HTTPException(status_code=404, detail="站点不存在")
        
        # 插入或更新配置
        sql = """
        INSERT INTO pv_forecast_config 
        (station_id, installed_capacity_kw, panel_efficiency, inverter_efficiency, 
         temperature_coefficient, degradation_rate, tilt_angle, azimuth_angle)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        installed_capacity_kw = VALUES(installed_capacity_kw),
        panel_efficiency = VALUES(panel_efficiency),
        inverter_efficiency = VALUES(inverter_efficiency),
        temperature_coefficient = VALUES(temperature_coefficient),
        degradation_rate = VALUES(degradation_rate),
        tilt_angle = VALUES(tilt_angle),
        azimuth_angle = VALUES(azimuth_angle),
        updated_at = CURRENT_TIMESTAMP
        """
        
        cursor.execute(sql, (
            config.station_id, config.installed_capacity_kw, config.panel_efficiency,
            config.inverter_efficiency, config.temperature_coefficient, config.degradation_rate,
            config.tilt_angle, config.azimuth_angle
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "光伏发电配置保存成功", "station_id": config.station_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")

@app.get("/api/pv-forecast/config/{station_id}")
async def get_pv_config(station_id: int):
    """获取光伏发电预测配置"""
    try:
        sql = """
        SELECT * FROM pv_forecast_config WHERE station_id = %s
        """
        result = execute_query(sql, (station_id,))
        
        if not result:
            raise HTTPException(status_code=404, detail="未找到光伏发电配置")
        
        return {"config": result[0]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@app.post("/api/pv-forecast/calculate")
async def calculate_pv_forecast(request: PVForecastRequest):
    """计算光伏发电预测"""
    try:
        # 获取气象数据
        weather_data = get_weather_data_by_station_and_time(
            request.station_id, request.start_date, request.end_date
        )
        
        if not weather_data:
            raise HTTPException(status_code=404, detail="未找到指定时间范围内的气象数据")
        
        # 使用pv_calculator计算发电量
        params = {
            'panel_efficiency': request.panel_efficiency,
            'inverter_efficiency': request.inverter_efficiency,
            'temperature_coefficient': request.temperature_coefficient,
            'degradation_rate': request.degradation_rate
        }
        
        forecast_results = pv_calculator.calculate_hourly_generation(
            weather_data=weather_data,
            installed_capacity=request.installed_capacity_kw,
            params=params
        )
        
        # 格式化时间戳
        for result in forecast_results:
            if isinstance(result['timestamp'], datetime):
                result['timestamp'] = result['timestamp'].isoformat()
            else:
                result['timestamp'] = str(result['timestamp'])
        
        # 计算统计信息
        stats = pv_calculator.calculate_statistics(forecast_results)
        total_generation = stats['total_generation_kwh']
        avg_daily_generation = stats['average_daily_generation_kwh']
        capacity_factor = pv_calculator.calculate_capacity_factor(
            total_generation, request.installed_capacity_kw, len(weather_data)
        )
        
        return {
            "station_id": request.station_id,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "installed_capacity_kw": request.installed_capacity_kw,
            "total_generation_kwh": round(total_generation, 4),
            "average_daily_generation_kwh": round(avg_daily_generation, 4),
            "capacity_factor": round(capacity_factor, 4),
            "forecast_results": forecast_results,
            "data_points": len(weather_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算预测失败: {str(e)}")

@app.get("/api/pv-forecast/yearly/{station_id}")
async def get_yearly_pv_forecast(
    station_id: int,
    years: int = Query(5, description="预测年数"),
    installed_capacity_kw: float = Query(1000, description="装机容量(kW)"),
    degradation_rate: float = Query(0.005, description="年衰减率")
):
    """获取多年光伏发电预测"""
    try:
        # 获取站点信息
        station_sql = """
        SELECT s.id, s.name, s.province, s.province_id, p.name as province_name
        FROM station s 
        LEFT JOIN province p ON s.province_id = p.id
        WHERE s.id = %s
        """
        station_result = execute_query(station_sql, (station_id,))
        
        if not station_result:
            raise HTTPException(status_code=404, detail="站点不存在")
        
        station = station_result[0]
        table_name = get_table_name_by_province(station['province'])
        
        # 获取历史气象数据（用于计算基准发电量）
        current_year = datetime.now().year
        weather_sql = f"""
        SELECT surface_radiation_wm2, temp_c
        FROM {table_name} 
        WHERE province_id = %s 
        AND YEAR(ts) = %s
        AND surface_radiation_wm2 IS NOT NULL
        AND temp_c IS NOT NULL
        """
        
        weather_data = execute_query(weather_sql, (station['province_id'], current_year))
        
        if not weather_data:
            raise HTTPException(status_code=404, detail="未找到气象数据")
        
        # 使用pv_calculator计算基准年发电量
        base_year_generation = 0
        for weather in weather_data:
            # 确保数据类型转换，处理 decimal.Decimal 类型
            solar_radiation = float(weather.get('surface_radiation_wm2', 0) or 0)
            temperature = float(weather.get('temp_c', 25) or 25)
            
            hourly_generation = pv_calculator.calculate_pv_generation(
                solar_radiation=solar_radiation,
                temperature=temperature,
                installed_capacity=installed_capacity_kw,
                degradation_factor=1.0
            )
            base_year_generation += hourly_generation
        
        # 使用pv_calculator计算多年预测
        yearly_forecasts = pv_calculator.calculate_yearly_forecast(
            base_year_generation=base_year_generation,
            years=years,
            installed_capacity=installed_capacity_kw,
            degradation_rate=degradation_rate
        )
        
        return {
            "station_id": station_id,
            "station_name": station['name'],
            "province": station['province'],
            "installed_capacity_kw": installed_capacity_kw,
            "degradation_rate": degradation_rate,
            "base_year_generation_kwh": round(base_year_generation, 2),
            "yearly_forecasts": yearly_forecasts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算多年预测失败: {str(e)}")

@app.get("/api/system/status")
async def get_system_status():
    """获取系统状态"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        conn.close()
        
        # 获取数据统计
        station_count = execute_query("SELECT COUNT(*) as count FROM station")[0]['count']
        
        # 统计所有地区表的数据总量
        province_tables = [
            "weather_observation_beijing", "weather_observation_shanghai", "weather_observation_tianjin",
            "weather_observation_hebei", "weather_observation_shanxi", "weather_observation_neimenggu",
            "weather_observation_liaoning", "weather_observation_jilin", "weather_observation_heilongjiang",
            "weather_observation_anhui", "weather_observation_shandong", "weather_observation_jiangxi",
            "weather_observation_zhejiang", "weather_observation_fujian", "weather_observation_henan"
        ]
        
        total_obs_count = 0
        for table in province_tables:
            try:
                count_result = execute_query(f"SELECT COUNT(*) as count FROM {table}")
                total_obs_count += count_result[0]['count']
            except:
                # 如果表不存在，跳过
                continue
        
        return {
            "status": "healthy",
            "database": "connected",
            "stations": station_count,
            "observations": total_obs_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    import signal
    import sys
    
    # 忽略 Ctrl+C 信号，防止服务器被意外停止
    def signal_handler(sig, frame):
        print("\n服务器正在运行中，无法通过 Ctrl+C 停止")
        print("如需停止服务器，请关闭终端窗口或使用任务管理器")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
