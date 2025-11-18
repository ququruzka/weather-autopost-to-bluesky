import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv, dotenv_values
import re
import zoneinfo # Import zoneinfo

load_dotenv()

# BSKY Config
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")
BLUESKY_API_HOST = "https://bsky.social"

# OpenWeatherMap Config
OWM_API_KEY = os.getenv("OWM_API_KEY")
CITY_ID = os.getenv("CITY_ID")
COUNTRY_CODE = os.getenv("COUNTRY_CODE")

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?id={CITY_ID}&appid={OWM_API_KEY}&units=metric"
    print(f"Requesting URL: {url}")
    resp = requests.get(url)
    data = resp.json()
    if data.get("cod") != 200:
        print("Weather API error:", data)
        return None
    desc = data["weather"][0]["description"].capitalize()
    temp = data["main"]["temp"]
    CITY = data["name"]
    humidity = data["main"]["humidity"]

    try:
        # Get the current timezone from the environment variable (e.g., 'Europe/Kyiv')
        local_tz_name = os.getenv('TZ', 'UTC')
        local_tz = zoneinfo.ZoneInfo(local_tz_name)
    except zoneinfo.ZoneInfoNotFoundError:
        local_tz = timezone.utc # Fallback to UTC if TZ env var is missing or invalid

    now_local = datetime.now(local_tz)
    time_str = now_local.strftime('%Y-%m-%d %H:%M')

    return f"Weather in {CITY} now: {desc}, Temp: {temp}°C, Humidity: {humidity}%. at {datetime.now().strftime('%Y-%m-%d %H:%M')} | #autoweatherpost #openweathermap"

def create_session(handle, app_password):
    url = f"{BLUESKY_API_HOST}/xrpc/com.atproto.server.createSession"
    resp = requests.post(url, json={"identifier": handle, "password": app_password})
    resp.raise_for_status()
    return resp.json()

def utf8_byte_pos(text, start_char_idx, end_char_idx):
    # Calculate UTF-8 byte positions from character indices
    start_byte = len(text[:start_char_idx].encode('utf-8'))
    end_byte = len(text[:end_char_idx].encode('utf-8'))
    return start_byte, end_byte

def post_to_bluesky(session, text):
    url = f"{BLUESKY_API_HOST}/xrpc/com.atproto.repo.createRecord"
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    static_tags = ["autoweatherpost", "openweathermap"]
    facets = []

    for tag in static_tags:
        tag_with_hash = "#" + tag
        start_char = text.find(tag_with_hash)






        if start_char == -1:
            continue
        end_char = start_char + len(tag_with_hash)
        start_byte, end_byte = utf8_byte_pos(text, start_char, end_char)
        facets.append({
            "index": {
                "byteStart": start_byte,
                "byteEnd": end_byte
            },
            "features": [{
                "$type": "app.bsky.richtext.facet#tag",
                "tag": tag
            }]
        })

    post_record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now_iso,
        "facets": facets
    }

    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    payload = {
        "repo": session["did"],
        "collection": "app.bsky.feed.post",
        "record": post_record,
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    weather_report = get_weather()
    if weather_report:
        try:
            session = create_session(BLUESKY_HANDLE, BLUESKY_APP_PASSWORD)
            response = post_to_bluesky(session, weather_report)
            print("Posted successfully to Bluesky. URI:", response.get("uri"))
        except Exception as e:
            print("Failed to post to Bluesky:", e)
    else:
        print("Failed to get weather data.")
