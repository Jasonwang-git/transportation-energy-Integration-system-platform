CREATE DATABASE IF NOT EXISTS energy_platform DEFAULT CHARSET utf8mb4;
USE energy_platform;

-- 省份表
CREATE TABLE IF NOT EXISTS province (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(64) NOT NULL UNIQUE COMMENT '省份名称',
  code VARCHAR(10) NOT NULL UNIQUE COMMENT '省份代码',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='省份信息表';

-- 站点表
CREATE TABLE IF NOT EXISTS station (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(128) NOT NULL COMMENT '站点名称',
  province VARCHAR(64) NOT NULL COMMENT '省份名称',
  province_id BIGINT NOT NULL COMMENT '省份ID',
  lng DECIMAL(10,6) NOT NULL COMMENT '经度',
  lat DECIMAL(10,6) NOT NULL COMMENT '纬度',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_station_name_province (name, province),
  INDEX idx_station_province (province),
  INDEX idx_station_province_id (province_id),
  INDEX idx_station_location (lng, lat),
  CONSTRAINT fk_station_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='站点信息表';

-- 为每个省份创建独立的天气观测表（支持13列完整数据）
-- 北京天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_beijing (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 1 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_beijing_ts (ts),
  CONSTRAINT fk_weather_beijing_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='北京天气观测数据表';

-- 上海天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_shanghai (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 2 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_shanghai_ts (ts),
  CONSTRAINT fk_weather_shanghai_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='上海天气观测数据表';

-- 天津天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_tianjin (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 3 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_tianjin_ts (ts),
  CONSTRAINT fk_weather_tianjin_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='天津天气观测数据表';

-- 河北天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_hebei (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 4 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_hebei_ts (ts),
  CONSTRAINT fk_weather_hebei_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='河北天气观测数据表';

-- 山西天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_shanxi (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 5 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_shanxi_ts (ts),
  CONSTRAINT fk_weather_shanxi_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='山西天气观测数据表';

-- 内蒙古天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_neimenggu (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 6 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_neimenggu_ts (ts),
  CONSTRAINT fk_weather_neimenggu_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='内蒙古天气观测数据表';

-- 辽宁天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_liaoning (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 7 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_liaoning_ts (ts),
  CONSTRAINT fk_weather_liaoning_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='辽宁天气观测数据表';

-- 吉林天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_jilin (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 8 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_jilin_ts (ts),
  CONSTRAINT fk_weather_jilin_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='吉林天气观测数据表';

-- 黑龙江天气观测表
CREATE TABLE IF NOT EXISTS weather_observation_heilongjiang (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  province_id BIGINT NOT NULL DEFAULT 9 COMMENT '省份ID',
  ts DATETIME NOT NULL COMMENT '观测时间',
  temp_c DECIMAL(5,2) NULL COMMENT '气温℃',
  humidity DECIMAL(5,2) NULL COMMENT '湿度%',
  pressure_hpa DECIMAL(8,2) NULL COMMENT '气压hPa',
  precip_mm DECIMAL(6,2) NULL COMMENT '降水量mm/h',
  meridional_wind_ms DECIMAL(6,2) NULL COMMENT '经向风m/s',
  zonal_wind_ms DECIMAL(6,2) NULL COMMENT '纬向风m/s',
  wind_speed_ms DECIMAL(6,2) NULL COMMENT '地面风速m/s',
  wind_dir_deg DECIMAL(6,2) NULL COMMENT '风向°',
  surface_radiation_wm2 DECIMAL(8,2) NULL COMMENT '地表水平辐射W/m^2',
  normal_direct_radiation_wm2 DECIMAL(8,2) NULL COMMENT '法向直接辐射W/m^2',
  scattered_radiation_wm2 DECIMAL(8,2) NULL COMMENT '散射辐射W/m^2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_weather_heilongjiang_ts (ts),
  CONSTRAINT fk_weather_heilongjiang_province FOREIGN KEY (province_id) REFERENCES province(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='黑龙江天气观测数据表';



-- 插入省份数据（只包含9个省市）
INSERT IGNORE INTO province (name, code) VALUES
('北京', 'BJ'),
('上海', 'SH'),
('天津', 'TJ'),
('河北', 'HE'),
('山西', 'SX'),
('内蒙古', 'NM'),
('辽宁', 'LN'),
('吉林', 'JL'),
('黑龙江', 'HL');

-- 插入示例站点数据（只包含9个省市）
INSERT IGNORE INTO station (name, province, province_id, lng, lat) VALUES
('北京南站', '北京', 1, 116.3974, 39.9093),
('北京西站', '北京', 1, 116.3207, 39.8963),
('上海虹桥站', '上海', 2, 121.4737, 31.2304),
('上海南站', '上海', 2, 121.4285, 31.1556),
('天津站', '天津', 3, 117.2008, 39.1439),
('石家庄站', '河北', 4, 114.5025, 38.0455),
('太原南站', '山西', 5, 112.5492, 37.8570),
('呼和浩特东站', '内蒙古', 6, 111.6708, 40.8183),
('沈阳站', '辽宁', 7, 123.4315, 41.8057),
('长春西站', '吉林', 8, 125.3245, 43.8868),
('哈尔滨西站', '黑龙江', 9, 126.5349, 45.7732);

-- 光伏发电预测配置表
CREATE TABLE IF NOT EXISTS pv_forecast_config (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  station_id BIGINT NOT NULL COMMENT '站点ID',
  installed_capacity_kw DECIMAL(10,2) NOT NULL COMMENT '装机容量(kW)',
  panel_efficiency DECIMAL(5,4) DEFAULT 0.20 COMMENT '光伏板效率',
  inverter_efficiency DECIMAL(5,4) DEFAULT 0.95 COMMENT '逆变器效率',
  temperature_coefficient DECIMAL(6,4) DEFAULT -0.004 COMMENT '温度系数',
  degradation_rate DECIMAL(6,4) DEFAULT 0.005 COMMENT '年衰减率',
  tilt_angle DECIMAL(5,2) DEFAULT 30.0 COMMENT '倾斜角度',
  azimuth_angle DECIMAL(5,2) DEFAULT 180.0 COMMENT '方位角',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_pv_config_station FOREIGN KEY (station_id) REFERENCES station(id) ON DELETE CASCADE,
  INDEX idx_pv_config_station (station_id)
) ENGINE=InnoDB COMMENT='光伏发电预测配置表';

-- 光伏发电预测结果表
CREATE TABLE IF NOT EXISTS pv_forecast_result (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  station_id BIGINT NOT NULL COMMENT '站点ID',
  forecast_time DATETIME NOT NULL COMMENT '预测时间',
  hourly_generation_kwh DECIMAL(10,4) NOT NULL COMMENT '小时发电量(kWh)',
  daily_generation_kwh DECIMAL(10,4) NULL COMMENT '日发电量(kWh)',
  monthly_generation_kwh DECIMAL(10,4) NULL COMMENT '月发电量(kWh)',
  yearly_generation_kwh DECIMAL(10,4) NULL COMMENT '年发电量(kWh)',
  solar_radiation_wm2 DECIMAL(8,2) NULL COMMENT '太阳辐射(W/m²)',
  temperature_c DECIMAL(5,2) NULL COMMENT '温度(℃)',
  efficiency_factor DECIMAL(6,4) NULL COMMENT '效率因子',
  degradation_factor DECIMAL(6,4) NULL COMMENT '衰减因子',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_pv_result_station_time (station_id, forecast_time),
  INDEX idx_pv_result_time (forecast_time),
  CONSTRAINT fk_pv_result_station FOREIGN KEY (station_id) REFERENCES station(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='光伏发电预测结果表';

-- 光伏发电年度预测表
CREATE TABLE IF NOT EXISTS pv_yearly_forecast (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  station_id BIGINT NOT NULL COMMENT '站点ID',
  forecast_year INT NOT NULL COMMENT '预测年份',
  total_generation_kwh DECIMAL(12,4) NOT NULL COMMENT '年总发电量(kWh)',
  peak_generation_month INT NULL COMMENT '发电量最高月份',
  peak_generation_kwh DECIMAL(10,4) NULL COMMENT '最高月发电量(kWh)',
  average_daily_generation_kwh DECIMAL(10,4) NULL COMMENT '平均日发电量(kWh)',
  capacity_factor DECIMAL(6,4) NULL COMMENT '容量因子',
  degradation_factor DECIMAL(6,4) NULL COMMENT '衰减因子',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_pv_yearly_station_year (station_id, forecast_year),
  INDEX idx_pv_yearly_station (station_id),
  INDEX idx_pv_yearly_year (forecast_year),
  CONSTRAINT fk_pv_yearly_station FOREIGN KEY (station_id) REFERENCES station(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='光伏发电年度预测表';








