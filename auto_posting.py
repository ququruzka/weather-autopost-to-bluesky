import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# print(os.getenv("OWM_API_KEY"))
# print(os.getenv("CITY_ID"))
# print(os.getenv("COUNTRY_CODE"))
# print(os.getenv("BLUESKY_HANDLE"))
# print(os.getenv("BLUESKY_APP_PASSWORD"))

# # BSKY Config
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")        # Replace with your Bluesky handle
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")      # Replace with your Bluesky app password
BLUESKY_API_HOST = "https://bsky.social"

# # OpenWeatherMap Config
OWM_API_KEY = os.getenv("OWM_API_KEY")
CITY_ID = os.getenv("CITY_ID")
COUNTRY_CODE = os.getenv("COUNTRY_CODE") # Replace with your country code (UA for Ukraine, UK for United Kingdom, abo shos inshe)


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
    return f"Weather in {CITY} today: {desc}, Temp: {temp}°C, Humidity: {humidity}%. at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | #AutoWeatherPost #openweathermap"


def create_session(handle, app_password):
    url = f"{BLUESKY_API_HOST}/xrpc/com.atproto.server.createSession"
    resp = requests.post(url, json={"identifier": handle, "password": app_password})
    resp.raise_for_status()
    return resp.json()

def post_to_bluesky(session, text):
    url = f"{BLUESKY_API_HOST}/xrpc/com.atproto.repo.createRecord"
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    post_record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now_iso,
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
