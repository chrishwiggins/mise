#!/usr/bin/env python3
"""
================================================================================
WEATHER PREDICTION / POSTDICTION TOOL
================================================================================

This script retrieves weather data for a given US zip code, either:
  - PREDICTION (future): Fetches forecast data from the National Weather Service
  - POSTDICTION (past): Fetches historical data from Open-Meteo's archive API

The user provides two inputs interactively:
  1. A US zip code (e.g., "02139")
  2. An integer offset in days:
       - Positive integers = future forecast (prediction)
       - Negative integers = past weather (postdiction)
       - Zero is not allowed

API Sources:
  - Geocoding: US Census Bureau Geocoder (converts zip -> lat/lon)
  - Future weather: National Weather Service (NWS) API (free, no key required)
  - Historical weather: Open-Meteo Archive API (free, no key required)

Limitations:
  - Only works for US zip codes (Census geocoder is US-only)
  - NWS forecasts typically only go ~7 days into the future
  - Open-Meteo historical data may not include very recent dates

================================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

import sys                      # For sys.exit() to terminate with error codes
import urllib.request           # For making HTTP requests (no external deps!)
import urllib.parse             # For URL encoding (not currently used but available)
import json                     # For parsing JSON responses from APIs
from datetime import datetime, timedelta  # For date arithmetic


# =============================================================================
# GEOCODING FUNCTION
# =============================================================================

def get_coordinates(zip_code: str) -> tuple[float, float, str]:
    """
    Convert a US zip code to geographic coordinates (latitude/longitude).

    Uses the US Census Bureau's free geocoding API. This is a reliable,
    no-authentication-required service for US addresses.

    Args:
        zip_code: A US zip code as a string (e.g., "90210", "02139")

    Returns:
        A tuple of (latitude, longitude, matched_address)
        - latitude: float, degrees north (positive in US)
        - longitude: float, degrees west (negative in US)
        - matched_address: str, the full address the geocoder matched

    Raises:
        ValueError: If the zip code cannot be geocoded (invalid or not found)
        URLError: If the network request fails

    API Documentation:
        https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
    """

    # Build the Census geocoder URL
    # - "onelineaddress" endpoint accepts freeform address text
    # - "benchmark=Public_AR_Current" uses the current public dataset
    # - "format=json" returns JSON instead of default HTML
    url = (
        f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        f"?address={zip_code}"
        f"&benchmark=Public_AR_Current"
        f"&format=json"
    )

    # Make the HTTP request with a 10-second timeout
    # Using a context manager ensures the connection is properly closed
    with urllib.request.urlopen(url, timeout=10) as response:
        # Read the response body and decode from bytes to string
        raw_data = response.read().decode()
        # Parse the JSON string into a Python dictionary
        data = json.loads(raw_data)

    # Navigate the response structure to find address matches
    # Structure: {"result": {"addressMatches": [...]}}
    # If no matches, the list will be empty
    matches = data.get("result", {}).get("addressMatches", [])

    if not matches:
        # No matches found - the zip code is invalid or not in the database
        raise ValueError(f"Could not geocode zip code: {zip_code}")

    # Take the first (best) match
    # Each match has "coordinates" with "x" (longitude) and "y" (latitude)
    # Note: x=longitude, y=latitude (standard GIS convention)
    coords = matches[0]["coordinates"]
    address = matches[0].get("matchedAddress", zip_code)

    # Return as (lat, lon, address) - note we swap x/y to lat/lon order
    return coords["y"], coords["x"], address


# =============================================================================
# FUTURE WEATHER FORECAST (PREDICTION)
# =============================================================================

def get_forecast(lat: float, lon: float) -> dict:
    """
    Get weather forecast from the National Weather Service (NWS) API.

    The NWS API is free and requires no authentication, but it does require
    a User-Agent header (they block requests without one).

    The NWS API uses a two-step process:
      1. First, query /points/{lat},{lon} to get metadata about that location,
         including which forecast office covers it and the forecast URL
      2. Then, fetch the actual forecast from the returned URL

    This two-step process exists because NWS organizes forecasts by regional
    forecast offices, not by raw coordinates.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        dict: The full forecast JSON response containing:
            - properties.periods: List of forecast periods (day/night segments)
            - Each period has: name, temperature, windSpeed, detailedForecast, etc.

    Raises:
        URLError: If network requests fail
        KeyError: If the API response structure is unexpected

    API Documentation:
        https://www.weather.gov/documentation/services-web-api
    """

    # -------------------------------------------------------------------------
    # STEP 1: Get the forecast grid endpoint for this location
    # -------------------------------------------------------------------------

    # The /points endpoint returns metadata about a location
    points_url = f"https://api.weather.gov/points/{lat},{lon}"

    # NWS requires a User-Agent header - they'll return 403 without it
    # The format should be "(application, contact)" per their docs
    req = urllib.request.Request(
        points_url,
        headers={"User-Agent": "weather-cli/1.0"}
    )

    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())

    # Extract the forecast URL from the response
    # Structure: {"properties": {"forecast": "https://api.weather.gov/gridpoints/..."}}
    forecast_url = data["properties"]["forecast"]

    # -------------------------------------------------------------------------
    # STEP 2: Fetch the actual forecast
    # -------------------------------------------------------------------------

    req = urllib.request.Request(
        forecast_url,
        headers={"User-Agent": "weather-cli/1.0"}
    )

    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())


# =============================================================================
# HISTORICAL WEATHER DATA (POSTDICTION)
# =============================================================================

def get_historical(lat: float, lon: float, target_date: datetime) -> dict:
    """
    Get historical weather data from Open-Meteo's archive API.

    Open-Meteo is a free, open-source weather API that provides both
    forecasts and historical data. The archive API specifically serves
    historical weather observations.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        target_date: The historical date to retrieve weather for

    Returns:
        dict: Historical weather data containing:
            - daily.temperature_2m_max: High temperature (list with one element)
            - daily.temperature_2m_min: Low temperature
            - daily.precipitation_sum: Total precipitation
            - daily.weathercode: WMO weather code (see weather_code_to_description)

    Raises:
        URLError: If the network request fails

    API Documentation:
        https://open-meteo.com/en/docs/historical-weather-api

    Notes:
        - "2m" in variable names means "2 meters above ground" (standard height)
        - Weather codes follow WMO (World Meteorological Organization) standard
        - Data may not be available for very recent dates (1-2 day lag)
    """

    # Format the date as YYYY-MM-DD (ISO 8601 format, required by API)
    date_str = target_date.strftime("%Y-%m-%d")

    # Build the API URL with all our parameters
    # We request both start_date and end_date as the same day for single-day data
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"                  # Location
        f"&start_date={date_str}&end_date={date_str}"      # Date range (single day)
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"  # Variables
        f"&temperature_unit=fahrenheit"                    # Use Fahrenheit (default is Celsius)
        f"&precipitation_unit=inch"                        # Use inches (default is mm)
        f"&timezone=auto"                                  # Auto-detect timezone from coordinates
    )

    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode())


# =============================================================================
# WMO WEATHER CODE TRANSLATION
# =============================================================================

def weather_code_to_description(code: int) -> str:
    """
    Convert a WMO (World Meteorological Organization) weather code to a
    human-readable description.

    WMO weather codes are an international standard for representing weather
    conditions as integers. Open-Meteo uses these codes in their API.

    The codes are organized in ranges:
        0-9:    Clear/cloudy conditions
        40-49:  Fog
        50-59:  Drizzle
        60-69:  Rain
        70-79:  Snow
        80-89:  Showers
        90-99:  Thunderstorms

    Args:
        code: WMO weather code (integer 0-99)

    Returns:
        str: Human-readable weather description

    Reference:
        https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/
        (WMO Code Table 4677)
    """

    # Lookup table for common WMO weather codes
    # Not all codes 0-99 are defined; we handle unknown codes gracefully
    codes = {
        # Clear and cloudy
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",

        # Fog (40s)
        45: "Fog",
        48: "Depositing rime fog",  # Fog that deposits ice crystals

        # Drizzle (50s) - light precipitation with small droplets
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",

        # Rain (60s)
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",

        # Snow (70s)
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",

        # Showers (80s) - brief, intense precipitation
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",

        # Thunderstorms (90s)
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    # Return the description if found, otherwise indicate unknown code
    return codes.get(code, f"Unknown ({code})")


# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():
    """
    Main entry point for the weather tool.

    Prompts the user for:
        1. A US zip code
        2. A days offset (positive=future, negative=past)

    Then fetches and displays the appropriate weather data.
    """

    # -------------------------------------------------------------------------
    # INPUT: Get zip code from user
    # -------------------------------------------------------------------------

    zip_code = input("Zip code: ").strip()  # .strip() removes leading/trailing whitespace

    if not zip_code:
        print("Error: zip code required")
        sys.exit(1)  # Exit with error code 1

    # -------------------------------------------------------------------------
    # INPUT: Get days offset from user
    # -------------------------------------------------------------------------

    offset_str = input("Days offset (+ for prediction, - for postdiction): ").strip()

    # Attempt to parse the input as an integer
    try:
        days_offset = int(offset_str)
    except ValueError:
        # int() failed - the input wasn't a valid integer
        print(f"Error: days offset must be an integer, got '{offset_str}'")
        sys.exit(1)

    # Zero offset doesn't make sense (that's just "now")
    if days_offset == 0:
        print("Error: days offset cannot be 0")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # GEOCODING: Convert zip code to coordinates
    # -------------------------------------------------------------------------

    print(f"Looking up zip code {zip_code}...")

    # This may raise ValueError if the zip code is invalid
    lat, lon, address = get_coordinates(zip_code)

    print(f"Location: {address}")
    print(f"Coordinates: {lat:.4f}, {lon:.4f}\n")  # .4f = 4 decimal places

    # -------------------------------------------------------------------------
    # Calculate the target date
    # -------------------------------------------------------------------------

    # datetime.now() = current date/time
    # timedelta(days=N) = a duration of N days
    # Adding them gives us the target date
    target_date = datetime.now() + timedelta(days=days_offset)

    # -------------------------------------------------------------------------
    # BRANCH: Prediction (future) vs Postdiction (past)
    # -------------------------------------------------------------------------

    if days_offset > 0:
        # =================================================================
        # PREDICTION: Fetch future forecast from NWS
        # =================================================================

        print(f"=== PREDICTION: {days_offset} day(s) ahead ===")
        print(f"Target date: {target_date.strftime('%A, %B %d, %Y')}\n")
        # strftime format: %A=weekday, %B=month name, %d=day, %Y=4-digit year

        # Fetch the forecast data
        forecast = get_forecast(lat, lon)

        # Extract the forecast periods (each period is a day or night segment)
        periods = forecast["properties"]["periods"]

        # Find periods that match our target date
        # Period startTime is ISO format: "2024-01-15T06:00:00-05:00"
        # We extract just the date part (first 10 characters)
        target_str = target_date.strftime("%Y-%m-%d")

        found = False  # Track whether we found any matching periods

        for period in periods:
            # Extract date from ISO timestamp
            period_date = period["startTime"][:10]  # "2024-01-15T..." -> "2024-01-15"

            if period_date == target_str:
                found = True

                # Print this period's forecast
                print(f"{period['name']}:")  # e.g., "Tuesday" or "Tuesday Night"
                print(f"  Temperature: {period['temperature']}{period['temperatureUnit']}")
                print(f"  Wind: {period['windSpeed']} {period['windDirection']}")
                print(f"  Forecast: {period['detailedForecast']}")
                print()

        # Handle case where requested date is beyond forecast range
        if not found:
            print(f"No forecast available for {days_offset} days ahead.")
            print("NWS typically provides forecasts up to 7 days out.")
            print("\nAvailable forecasts:")
            # Show the first few available periods as a helpful reference
            for period in periods[:4]:
                print(f"  - {period['name']}: {period['shortForecast']}")

    else:
        # =================================================================
        # POSTDICTION: Fetch historical data from Open-Meteo
        # =================================================================

        # abs() converts negative to positive for display
        print(f"=== POSTDICTION: {abs(days_offset)} day(s) ago ===")
        print(f"Target date: {target_date.strftime('%A, %B %d, %Y')}\n")

        # Fetch historical weather data
        historical = get_historical(lat, lon, target_date)

        # Extract the daily data
        # Structure: {"daily": {"time": [...], "temperature_2m_max": [...], ...}}
        daily = historical.get("daily", {})

        # Check if we actually got data
        if not daily.get("time"):
            print("No historical data available for this date.")
            sys.exit(1)

        # Extract values - they're lists, we want the first (only) element
        # since we only requested one day
        temp_max = daily["temperature_2m_max"][0]      # High temperature
        temp_min = daily["temperature_2m_min"][0]      # Low temperature
        precip = daily["precipitation_sum"][0]          # Total precipitation
        weather_code = daily["weathercode"][0]          # WMO condition code

        # Display the historical weather
        print(f"High: {temp_max:.1f}F")                  # .1f = 1 decimal place
        print(f"Low: {temp_min:.1f}F")
        print(f"Precipitation: {precip:.2f} inches")     # .2f = 2 decimal places
        print(f"Conditions: {weather_code_to_description(weather_code)}")


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

# This is the standard Python idiom for "run main() only if this file is
# executed directly, not if it's imported as a module"
if __name__ == "__main__":
    main()
