#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版气象数据导入工具 - 不依赖pandas
"""

import os
import csv
import mysql.connector
from datetime import datetime
import chardet

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'energy_platform',
    'charset': 'utf8mb4'
}

# 文件映射
FILE_MAPPING = {
    "北京.csv": {"province": "北京", "station": "北京", "table": "weather_observation_beijing"},
    "上海.csv": {"province": "上海", "station": "上海", "table": "weather_observation_shanghai"},
    "天津.csv": {"province": "天津", "station": "天津", "table": "weather_observation_tianjin"},
    "河北.csv": {"province": "河北", "station": "河北", "table": "weather_observation_hebei"},
    "山西.csv": {"province": "山西", "station": "山西", "table": "weather_observation_shanxi"},
    "内蒙古.csv": {"province": "内蒙古", "station": "内蒙古", "table": "weather_observation_neimenggu"},
    "辽宁.csv": {"province": "辽宁", "station": "辽宁", "table": "weather_observation_liaoning"},
    "吉林.csv": {"province": "吉林", "station": "吉林", "table": "weather_observation_jilin"},
    "黑龙江.csv": {"province": "黑龙江", "station": "黑龙江", "table": "weather_observation_heilongjiang"},
}

def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def create_station_if_not_exists(conn, station_name, province, lng=116.4, lat=39.9):
    """创建站点（如果不存在）"""
    cursor = conn.cursor()
    
    # 检查站点是否存在
    cursor.execute("SELECT id FROM station WHERE name = %s", (station_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # 创建新站点
    cursor.execute("""
        INSERT INTO station (name, lng, lat, province) 
        VALUES (%s, %s, %s, %s)
    """, (station_name, lng, lat, province))
    
    station_id = cursor.lastrowid
    conn.commit()
    print(f"   ✅ 创建站点: {station_name} (ID: {station_id})")
    return station_id

def clean_numeric_value(value):
    """清理数值数据"""
    if value == '' or value is None:
        return None
    
    try:
        str_value = str(value).strip()
        if str_value == '' or str_value.lower() in ['nan', 'null', 'none']:
            return None
        return float(str_value)
    except (ValueError, TypeError):
        return None

def import_csv_file(csv_file, province, station, table_name):
    """导入单个CSV文件"""
    print(f"🔄 正在导入: {csv_file}")
    print(f"   省份: {province}")
    print(f"   站点: {station}")
    print(f"   目标表: {table_name}")
    
    # 检测编码
    encoding = detect_encoding(csv_file)
    print(f"   编码: {encoding}")
    
    # 获取数据库连接
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        # 检查省份是否存在
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM province WHERE name = %s", (province,))
        province_result = cursor.fetchone()
        if not province_result:
            print(f"   ❌ 省份 {province} 不存在，请先创建省份数据")
            return False
        
        # 读取CSV文件
        with open(csv_file, 'r', encoding=encoding, errors='ignore') as f:
            lines = f.readlines()
            
            # 找到真正的数据开始行（包含"日期,时间"的行）
            data_start_line = 0
            for i, line in enumerate(lines):
                if '日期' in line and '时间' in line:
                    data_start_line = i
                    break
            
            if data_start_line == 0:
                print("   ❌ 未找到数据开始行")
                return False
            
            print(f"   列标题在第 {data_start_line + 1} 行")
            print(f"   数据从第 {data_start_line + 2} 行开始")
            
            # 从数据开始行创建CSV读取器（跳过列标题行）
            reader = csv.DictReader(lines[data_start_line:])
            
            # 获取列名
            headers = reader.fieldnames
            print(f"   列名: {headers}")
            
            # 调试：显示前几行数据
            print("   前3行数据示例:")
            for i, row in enumerate(reader):
                if i >= 3:
                    break
                print(f"     行{i+1}: {dict(row)}")
            
            # 重新创建reader，因为上面已经消费了一些行
            reader = csv.DictReader(lines[data_start_line:])
            
            # 准备插入语句
            cursor = conn.cursor()
            insert_count = 0
            skip_count = 0
            
            print(f"   开始处理数据行...")
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # 解析时间
                    date_str = row.get('日期', '')
                    time_str = row.get('时间', '')
                    
                    if not date_str or not time_str:
                        continue
                    
                    # 尝试解析时间格式
                    try:
                        if '/' in date_str:
                            date_parts = date_str.split('/')
                            if len(date_parts) == 3:
                                year, month, day = date_parts
                                date_obj = datetime(int(year), int(month), int(day))
                            else:
                                continue
                        else:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        
                        # 处理时间
                        if ':' in time_str:
                            time_parts = time_str.split(':')
                            if len(time_parts) >= 2:
                                hour, minute = int(time_parts[0]), int(time_parts[1])
                                second = int(time_parts[2]) if len(time_parts) > 2 else 0
                                ts = datetime.combine(date_obj.date(), datetime.min.time().replace(hour=hour, minute=minute, second=second))
                            else:
                                ts = date_obj
                        else:
                            ts = date_obj
                    except:
                        continue
                    
                    # 提取所有13列数据（根据实际CSV列名）
                    temp_c = clean_numeric_value(row.get('气温℃'))
                    humidity = clean_numeric_value(row.get('湿度%'))
                    pressure_hpa = clean_numeric_value(row.get('气压hPa'))
                    precip_mm = clean_numeric_value(row.get('降水量mm/h'))
                    meridional_wind_ms = clean_numeric_value(row.get('经向风m/s'))
                    zonal_wind_ms = clean_numeric_value(row.get('纬向风m/s'))
                    wind_speed_ms = clean_numeric_value(row.get('地面风速m/s'))
                    wind_dir_deg = clean_numeric_value(row.get('风向°'))
                    surface_radiation_wm2 = clean_numeric_value(row.get('地表水平辐射W/m^2'))
                    normal_direct_radiation_wm2 = clean_numeric_value(row.get('法向直接辐射W/m^2'))
                    scattered_radiation_wm2 = clean_numeric_value(row.get('散射辐射W/m^2'))
                    
                    # 获取省份ID
                    cursor.execute("SELECT id FROM province WHERE name = %s", (province,))
                    province_result = cursor.fetchone()
                    if not province_result:
                        print(f"   ❌ 省份 {province} 不存在")
                        continue
                    province_id = province_result[0]
                    
                    # 插入数据到对应的地区表（包含所有13列字段）
                    cursor.execute(f"""
                        INSERT INTO {table_name} 
                        (province_id, ts, temp_c, humidity, pressure_hpa, precip_mm, 
                         meridional_wind_ms, zonal_wind_ms, wind_speed_ms, wind_dir_deg, 
                         surface_radiation_wm2, normal_direct_radiation_wm2, scattered_radiation_wm2)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (province_id, ts, temp_c, humidity, pressure_hpa, precip_mm, 
                          meridional_wind_ms, zonal_wind_ms, wind_speed_ms, wind_dir_deg,
                          surface_radiation_wm2, normal_direct_radiation_wm2, scattered_radiation_wm2))
                    
                    insert_count += 1
                    
                    if insert_count % 5000 == 0:
                        print(f"   📊 已导入 {insert_count} 条记录...")
                        conn.commit()
                        
                except Exception as e:
                    skip_count += 1
                    if skip_count <= 5:  # 只显示前5个错误
                        print(f"   ⚠️  跳过第{row_num}行: {e}")
                    elif skip_count == 6:
                        print(f"   ⚠️  还有更多错误行被跳过...")
                    continue
            
            conn.commit()
            print(f"   ✅ 成功导入 {insert_count} 条记录")
            print(f"   ⚠️  跳过 {skip_count} 条无效记录")
            return True
            
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        return False
    finally:
        conn.close()

def find_csv_files(directory="data"):
    """在data目录查找CSV文件"""
    csv_files = []
    
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return []
    
    try:
        for file in os.listdir(directory):
            if file.endswith('.csv') and file in FILE_MAPPING:
                csv_files.append(os.path.join(directory, file))
        return sorted(csv_files)
    except Exception as e:
        print(f"❌ 读取目录失败: {e}")
        return []

def main():
    print("=" * 60)
    print("🌤️  简化版气象数据导入工具")
    print("=" * 60)
    
    # 查找CSV文件
    csv_files = find_csv_files()
    
    if not csv_files:
        print("❌ 在data目录中未找到支持的CSV文件")
        return
    
    print(f"📄 找到 {len(csv_files)} 个CSV文件:")
    for file in csv_files:
        filename = os.path.basename(file)
        print(f"   - {filename}")
    
    print("\n" + "=" * 60)
    print("开始导入数据...")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        mapping = FILE_MAPPING[filename]
        province = mapping["province"]
        station = mapping["station"]
        table_name = mapping["table"]
        
        print(f"\n{'='*20} {filename} {'='*20}")
        
        if import_csv_file(csv_file, province, station, table_name):
            success_count += 1
        else:
            error_count += 1
    
    print("\n" + "=" * 60)
    print("🎉 导入完成!")
    print(f"✅ 成功导入: {success_count} 个文件")
    print(f"❌ 失败: {error_count} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
