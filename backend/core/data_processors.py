# Data processors for sensor inputs

def normalize_sensor_data(raw_data):
    """Normalize 8-channel sensor data to 0-100 scale."""
    if len(raw_data) < 8:
        raw_data = list(raw_data) + [6.5, 35, 28, 40, 50, 2.0, 0.3, 28]
    ph, n, p, k, moisture, om, ec, temp = raw_data[:8]
    return [
        max(0, min(100, (7 - abs(ph - 7)) * 50)),  # pH score
        max(0, min(100, n * 2.5)),  # N score
        max(0, min(100, p * 3.3)),  # P score
        max(0, min(100, k * 2.5)),  # K score
        max(0, min(100, moisture * 2)),  # Moisture
        max(0, min(100, om * 20)),  # Organic matter
        max(0, min(100, ec * 50)),  # EC
        max(0, min(100, (30 - abs(temp - 30)) * 5)),  # Temp score
    ]

def extract_npk(sensor_data):
    """Extract NPK values from sensor array."""
    if len(sensor_data) >= 4:
        return sensor_data[1], sensor_data[2], sensor_data[3]
    return 35.0, 28.0, 40.0
