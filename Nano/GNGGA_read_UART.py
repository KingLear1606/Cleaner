import serial

def nmea_to_decimal(coord, direction):
    """将 NMEA 坐标格式（ddmm.mmmm）转换为十进制度"""
    if not coord:
        return None
    try:
        if direction in ['N', 'S']:
            degrees = int(coord[:2])
            minutes = float(coord[2:])
        else:
            degrees = int(coord[:3])
            minutes = float(coord[3:])
        decimal = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    except ValueError:
        return None


def parse_nmea(sentence, gps_data):
    """通用解析函数，自动提取经纬度与高度"""
    parts = sentence.split(',')

    # 提取经纬度信息（GNRMC 或 GNGGA 通用字段）
    if len(parts) > 6:
        # RMC 格式：$--RMC, time, status, lat, N/S, lon, E/W, ...
        # GGA 格式：$--GGA, time, lat, N/S, lon, E/W, fix, sats, hdop, alt, ...
        lat_idx = 2 if sentence.startswith('$GNGGA') else 3
        lon_idx = 4 if sentence.startswith('$GNGGA') else 5
        ns_idx  = 3 if sentence.startswith('$GNGGA') else 4
        ew_idx  = 5 if sentence.startswith('$GNGGA') else 6

        latitude = nmea_to_decimal(parts[lat_idx], parts[ns_idx])
        longitude = nmea_to_decimal(parts[lon_idx], parts[ew_idx])
        if latitude: gps_data['latitude'] = latitude
        if longitude: gps_data['longitude'] = longitude

    # 提取高度信息（仅 GGA 有效）
    if sentence.startswith('$GNGGA') and len(parts) > 9:
        try:
            altitude = float(parts[9]) if parts[9] else None
            gps_data['altitude'] = altitude
        except ValueError:
            pass

    return gps_data


def main():
    gps_data = {'latitude': None, 'longitude': None, 'altitude': None}

    port = 'COM10'
    baudrate = 115200
    ser = serial.Serial(port, baudrate, timeout=1)
    print(f"正在监听 {port} ({baudrate} bps)...\n")

    try:
        while True:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if not line.startswith('$'):
                continue
            gps_data = parse_nmea(line, gps_data)

            # 实时打印字典内容
            print(
                f"\r纬度: {gps_data['latitude']:.8f}  "
                f"经度: {gps_data['longitude']:.8f}  "
                f"高度: {gps_data['altitude']} m",
                end=''
            )
    except KeyboardInterrupt:
        print("\n停止接收。")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
