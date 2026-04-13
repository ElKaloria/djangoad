import random


WIND_DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def get_weather_payload():
    return {
        "temperature": round(random.uniform(-20, 35), 1),
        "humidity": round(random.uniform(20, 95), 1),
        "pressure": round(random.uniform(720, 780), 1),
        "wind_speed": round(random.uniform(0, 20), 1),
        "wind_direction": random.choice(WIND_DIRECTIONS),
    }
