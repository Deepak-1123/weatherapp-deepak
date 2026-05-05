"""
Synent Technologies - Python Development Internship
Task 6: Weather App (API Integration)
Author: Deepak

Setup:
    1. pip install requests
    2. Sign up at https://openweathermap.org/api and grab your free API key
    3. Paste your key below where it says MY_API_KEY
"""

import requests
from datetime import datetime


# paste your api key here
MY_API_KEY = "your_api_key_here"   # replace with placeholder

WEATHER_URL  = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def show_banner():
    print()
    print("*" * 48)
    print("*     DEEPAK'S WEATHER APP                   *")
    print("*     Powered by OpenWeatherMap               *")
    print("*" * 48)
    print()


def pick_unit():
    print("Which temperature unit do you prefer?")
    print("  1. Celsius   (°C)  - default")
    print("  2. Fahrenheit (°F)")

    while True:
        picked = input("\n  Your choice (1/2): ").strip()
        if picked in ("", "1"):
            return "metric"
        elif picked == "2":
            return "imperial"
        else:
            print("  Just enter 1 or 2.")


def sky_emoji(sky):
    # match the weather condition to a fitting emoji
    sky = sky.lower()
    if "clear"  in sky:                          return "☀️"
    elif "cloud" in sky:                         return "☁️"
    elif "rain"  in sky or "drizzle" in sky:     return "🌧️"
    elif "thunderstorm" in sky:                  return "⛈️"
    elif "snow"  in sky:                         return "❄️"
    elif "mist"  in sky or "fog" in sky \
                         or "haze" in sky:       return "🌫️"
    elif "wind"  in sky:                         return "💨"
    else:                                        return "🌡️"


def to_fahrenheit(c):
    return round(c * 9 / 5 + 32, 1)


def wind_direction(deg):
    compass = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return compass[round(deg / 45) % 8]


def get_weather(city_name, unit):
    # call the api and return the raw data or an error message
    query = {
        "q":     city_name,
        "appid": MY_API_KEY,
        "units": unit,
    }

    try:
        resp = requests.get(WEATHER_URL, params=query, timeout=10)

        if resp.status_code == 200:
            return resp.json(), None
        elif resp.status_code == 401:
            return None, "Invalid API key — double check it at openweathermap.org."
        elif resp.status_code == 404:
            return None, f"Could not find '{city_name}'. Check the spelling and try again."
        elif resp.status_code == 429:
            return None, "Too many requests — wait a moment and try again."
        else:
            return None, f"Something went wrong (error {resp.status_code}). Try again."

    except requests.exceptions.ConnectionError:
        return None, "No internet connection. Check your network and retry."
    except requests.exceptions.Timeout:
        return None, "The request timed out. Try again in a moment."
    except requests.exceptions.RequestException as err:
        return None, f"Unexpected error: {err}"


def show_weather(info, unit):
    deg       = "°C" if unit == "metric" else "°F"
    spd       = "m/s" if unit == "metric" else "mph"

    city      = info["name"]
    country   = info["sys"]["country"]
    sky       = info["weather"][0]["description"].capitalize()
    icon      = sky_emoji(sky)

    temp      = info["main"]["temp"]
    feels     = info["main"]["feels_like"]
    low       = info["main"]["temp_min"]
    high      = info["main"]["temp_max"]
    humidity  = info["main"]["humidity"]
    pressure  = info["main"]["pressure"]

    w_speed   = info["wind"]["speed"]
    w_deg     = info["wind"].get("deg", 0)
    w_dir     = wind_direction(w_deg)

    # convert visibility from metres to km
    raw_vis   = info.get("visibility", None)
    vis       = f"{raw_vis // 1000} km" if raw_vis else "N/A"

    sunrise   = datetime.fromtimestamp(info["sys"]["sunrise"]).strftime("%I:%M %p")
    sunset    = datetime.fromtimestamp(info["sys"]["sunset"]).strftime("%I:%M %p")

    # show the alternate unit alongside
    alt       = f"({to_fahrenheit(temp)}°F)" if unit == "metric" else f"({round((temp - 32) * 5 / 9, 1)}°C)"

    now       = datetime.now().strftime("%A, %d %B %Y  %I:%M %p")

    print()
    print("-" * 50)
    print(f"  {city}, {country}")
    print(f"  {now}")
    print("-" * 50)
    print(f"  {icon}  {sky}")
    print()
    print(f"  Temperature  : {temp}{deg}  {alt}")
    print(f"  Feels like   : {feels}{deg}")
    print(f"  Low / High   : {low}{deg} / {high}{deg}")
    print()
    print(f"  Humidity     : {humidity}%")
    print(f"  Pressure     : {pressure} hPa")
    print(f"  Visibility   : {vis}")
    print()
    print(f"  Wind         : {w_speed} {spd}  {w_dir}")
    print()
    print(f"  Sunrise      : {sunrise}")
    print(f"  Sunset       : {sunset}")
    print("-" * 50)
    print()


def get_forecast(city_name, unit):
    query = {
        "q":     city_name,
        "appid": MY_API_KEY,
        "units": unit,
        "cnt":   5,    # next 5 slots, one every 3 hours
    }

    try:
        resp = requests.get(FORECAST_URL, params=query, timeout=10)
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, f"Could not load forecast (error {resp.status_code})."
    except requests.exceptions.RequestException as err:
        return None, f"Forecast fetch failed: {err}"


def show_forecast(info, unit):
    deg = "°C" if unit == "metric" else "°F"
    print("  Upcoming forecast (every 3 hours):\n")

    for slot in info["list"]:
        # reusing 'time' would shadow the built-in so using slot_time instead
        slot_time = datetime.fromtimestamp(slot["dt"]).strftime("%d %b  %I:%M %p")
        temp      = slot["main"]["temp"]
        sky       = slot["weather"][0]["description"].capitalize()
        icon      = sky_emoji(sky)
        print(f"     {slot_time}  ->  {temp}{deg}  {icon} {sky}")

    print()


def main():
    show_banner()

    unit = pick_unit()

    while True:
        print()
        city_name = input("  Enter a city name (or type quit to exit): ").strip()

        if city_name.lower() in ("quit", "exit", "q"):
            print("\n  Take care, Deepak! Stay weather-aware.\n")
            break

        if not city_name:
            print("  Please type a city name first.")
            continue

        print(f"\n  Fetching weather for {city_name}...\n")

        weather_data, err = get_weather(city_name, unit)

        if err:
            print(f"  Oops! {err}\n")
            continue

        show_weather(weather_data, unit)

        want_forecast = input("  Want to see the upcoming forecast? (yes/no): ").strip().lower()
        if want_forecast in ("yes", "y"):
            forecast_data, forecast_err = get_forecast(city_name, unit)
            if forecast_err:
                print(f"  {forecast_err}")
            else:
                show_forecast(forecast_data, unit)


if __name__ == "__main__":
    main()
