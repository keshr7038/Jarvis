import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL   = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(city):
    """Convert city name to coordinates"""
    try:
        response = requests.get(GEOCODING_URL, params={
            "name":     city,
            "count":    1,
            "language": "en",
            "format":   "json"
        })
        data = response.json()

        if "results" not in data or not data["results"]:
            return None, None, None, None

        result  = data["results"][0]
        return (
            result["latitude"],
            result["longitude"],
            result["name"],
            result.get("country", "")
        )
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None, None, None


def get_weather_description(code):
    """Convert weather code to description"""
    codes = {
        0:  "Clear sky",         1: "Mainly clear",
        2:  "Partly cloudy",     3: "Overcast",
        45: "Foggy",             48: "Icy fog",
        51: "Light drizzle",     53: "Moderate drizzle",
        55: "Heavy drizzle",     61: "Slight rain",
        63: "Moderate rain",     65: "Heavy rain",
        71: "Slight snowfall",   73: "Moderate snowfall",
        75: "Heavy snowfall",    80: "Slight showers",
        81: "Moderate showers",  82: "Heavy showers",
        95: "Thunderstorm",      99: "Thunderstorm with hail",
    }
    return codes.get(code, "Unknown conditions")


def get_weather_tip(temp, rain, wind):
    """Smart contextual weather tip"""
    tips = []

    if temp > 38:
        tips.append("It is dangerously hot. Please stay indoors and hydrated, sir.")
    elif temp > 32:
        tips.append("It is very hot today. Stay hydrated and avoid direct sunlight, sir.")
    elif temp > 25:
        tips.append("It is warm and pleasant today, sir.")
    elif temp > 15:
        tips.append("The weather is comfortable today, sir.")
    elif temp > 5:
        tips.append("It is cool. A jacket would be advisable, sir.")
    else:
        tips.append("It is very cold. Please dress warmly, sir.")

    if rain > 5:
        tips.append("Heavy rain expected — carry an umbrella, sir.")
    elif rain > 0:
        tips.append("Light rain possible — you may want an umbrella, sir.")

    if wind > 50:
        tips.append("Very strong winds today — be cautious outdoors, sir.")
    elif wind > 30:
        tips.append("Moderate winds today, sir.")

    return " ".join(tips)


def get_weather(city):
    """Get current weather for any city"""
    try:
        lat, lon, city_name, country = get_coordinates(city)

        if lat is None:
            return f"I could not find {city}, sir. Please check the spelling."

        response = requests.get(WEATHER_URL, params={
            "latitude":         lat,
            "longitude":        lon,
            "current":          [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "precipitation",
                "uv_index"
            ],
            "daily":            [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "weather_code"
            ],
            "timezone":         "auto",
            "wind_speed_unit":  "kmh",
            "temperature_unit": "celsius",
            "forecast_days":    3
        })

        data    = response.json()
        current = data["current"]
        daily   = data.get("daily", {})

        temp        = round(current["temperature_2m"])
        feels_like  = round(current["apparent_temperature"])
        humidity    = current["relative_humidity_2m"]
        wind_speed  = round(current["wind_speed_10m"])
        condition   = get_weather_description(current["weather_code"])
        rain        = current["precipitation"]
        uv          = current.get("uv_index", 0)
        tip         = get_weather_tip(temp, rain, wind_speed)

        # Build report
        report  = f"Current weather in {city_name}, {country}. "
        report += f"{condition}. "
        report += f"Temperature is {temp} degrees Celsius, feels like {feels_like}. "
        report += f"Humidity {humidity} percent. "
        report += f"Wind speed {wind_speed} kilometres per hour. "
        report += f"UV index {uv}. "
        report += tip

        # Add 3-day forecast
        if daily and "temperature_2m_max" in daily:
            report += " Three day forecast: "
            days = ["Tomorrow", "Day after tomorrow", "In 3 days"]
            for i in range(min(3, len(daily["temperature_2m_max"]))):
                max_t = round(daily["temperature_2m_max"][i])
                min_t = round(daily["temperature_2m_min"][i])
                cond  = get_weather_description(daily["weather_code"][i])
                report += f"{days[i]}: {cond}, high of {max_t}, low of {min_t}. "

        return report

    except requests.exceptions.ConnectionError:
        return "Unable to connect to weather service, sir. Please check your internet."
    except Exception as e:
        return f"Weather service error: {str(e)}"


def extract_city(user_input):
    """Extract city name from question"""
    user_lower = user_input.lower()
    patterns   = [
        "weather in ", "weather for ", "weather at ",
        "temperature in ", "temperature at ", "climate in ",
        "how is the weather in ", "what is the weather in ",
        "what's the weather in ", "whats the weather in ",
        "how hot is it in ", "how cold is it in ",
        "forecast for ", "forecast in ",
    ]
    for pattern in patterns:
        if pattern in user_lower:
            city = user_input[user_lower.index(pattern) + len(pattern):]
            city = city.strip().split("?")[0].split(".")[0].strip()
            return city.capitalize()
    return None


def is_weather_query(user_input):
    """Check if asking about weather"""
    keywords = [
        "weather", "temperature", "humid", "raining",
        "sunny", "forecast", "climate", "hot outside",
        "cold outside", "how hot", "how cold",
        "precipitation", "wind speed", "uv index",
        "will it rain", "should i carry umbrella"
    ]
    return any(kw in user_input.lower() for kw in keywords)