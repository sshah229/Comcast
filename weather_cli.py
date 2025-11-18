#!/usr/bin/env python3
"""
OpenWeather CLI - Activity 1

Features
- Search current weather for a city (OpenWeather Current Weather API)
- Add a city to favourites (max 3, in-memory only)
- List favourite cities with current weather
- Update favourites: remove a city, then optionally add another (respecting max 3)

Setup
- Requires environment variable OPENWEATHER_API_KEY to be set with your API key.
- Units: metric (Celsius).
"""
from __future__ import annotations

import os
import sys
import time
from typing import Dict, List

import requests

API_BASE = "https://api.openweathermap.org/data/2.5/weather"
UNITS = "metric"
TIMEOUT_SECONDS = 12


def load_env_from_file(filename: str = ".env", override: bool = False) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.isabs(filename):
        candidates = [filename]
    else:
        candidates = [
            os.path.join(os.getcwd(), filename),
            os.path.join(script_dir, filename),
        ]
    path = next((p for p in candidates if os.path.exists(p)), None)
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                if len(v) >= 2 and ((v[0] == v[-1]) and v[0] in ("'", '"')):
                    v = v[1:-1]
                if override or k not in os.environ:
                    os.environ[k] = v
    except Exception:
        return


class WeatherClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def fetch_weather(self, city: str) -> Dict:
        params = {
            "q": city,
            "appid": self.api_key,
            "units": UNITS,
        }
        try:
            resp = requests.get(API_BASE, params=params, timeout=TIMEOUT_SECONDS)
        except requests.RequestException as e:
            raise RuntimeError(f"Network error: {e}") from e

        if resp.status_code == 404:
            raise ValueError(f"City not found: {city}")
        if not resp.ok:
            try:
                payload = resp.json()
                msg = payload.get("message", "Unknown error")
            except Exception:
                msg = resp.text
            raise RuntimeError(f"API error ({resp.status_code}): {msg}")
        return resp.json()


def get_api_key() -> str:
    api_key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is not set. Get a key at https://openweathermap.org/api and set it in your environment."
        )
    return api_key


def format_weather(data: Dict) -> str:
    name = data.get("name", "?")
    sys_info = data.get("sys", {})
    country = sys_info.get("country", "")

    main = data.get("main", {})
    temp = main.get("temp")
    feels = main.get("feels_like")
    humidity = main.get("humidity")

    wind = data.get("wind", {})
    wind_speed = wind.get("speed")

    weather = (data.get("weather") or [{}])[0]
    desc = weather.get("description", "?")

    dt = data.get("dt")
    tz = data.get("timezone", 0)
    local_ts = (dt + tz) if isinstance(dt, int) else None
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(local_ts)) if local_ts else "?"

    parts = [
        f"City: {name}{', ' + country if country else ''}",
        f"Weather: {temp}°C (feels {feels}°C), {desc}",
        f"Humidity: {humidity}%",
        f"Wind: {wind_speed} m/s",
        f"Updated (local): {local_time}",
    ]
    return "\n".join(parts)


class Favourites:
    def __init__(self, capacity: int = 3) -> None:
        self.capacity = capacity
        self._items: List[str] = []

    def list(self) -> List[str]:
        return list(self._items)

    def add(self, city: str) -> None:
        city_norm = city.strip()
        if not city_norm:
            raise ValueError("City name cannot be empty")
        if city_norm in self._items:
            raise ValueError(f"Already in favourites: {city_norm}")
        if len(self._items) >= self.capacity:
            raise ValueError(f"Favourites is full (max {self.capacity}). Remove one first.")
        self._items.append(city_norm)

    def remove(self, city: str) -> None:
        city_norm = city.strip()
        try:
            self._items.remove(city_norm)
        except ValueError as e:
            raise ValueError(f"Not in favourites: {city_norm}") from e


def prompt(prompt_text: str) -> str:
    try:
        return input(prompt_text)
    except EOFError:
        return ""


def search_flow(client: WeatherClient) -> None:
    city = prompt("Enter city name: ").strip()
    if not city:
        print("No city entered.")
        return
    try:
        data = client.fetch_weather(city)
        print("\n" + format_weather(data) + "\n")
    except Exception as e:
        print(f"Error: {e}")


def add_flow(client: WeatherClient, fav: Favourites) -> None:
    city = prompt("City to add to favourites: ").strip()
    if not city:
        print("No city entered.")
        return
    try:
        client.fetch_weather(city)  # validate city exists
        fav.add(city)
        print(f"Added to favourites: {city}")
    except Exception as e:
        print(f"Error: {e}")


def list_flow(client: WeatherClient, fav: Favourites) -> None:
    items = fav.list()
    if not items:
        print("No favourites yet.")
        return
    print(f"\nFavourites ({len(items)}/{fav.capacity}):\n")
    for i, city in enumerate(items, start=1):
        try:
            data = client.fetch_weather(city)
            print(f"[{i}] {city}")
            print(format_weather(data))
            print("-")
        except Exception as e:
            print(f"[{i}] {city} -> Error: {e}")
    print("")


def update_flow(client: WeatherClient, fav: Favourites) -> None:
    items = fav.list()
    if not items:
        print("No favourites to update. Add some first.")
        return
    print("Current favourites:")
    for i, city in enumerate(items, start=1):
        print(f" {i}. {city}")
    sel = prompt("Enter exact city name to remove (or blank to cancel): ").strip()
    if not sel:
        print("Cancelled.")
        return
    try:
        fav.remove(sel)
        print(f"Removed: {sel}")
    except Exception as e:
        print(f"Error: {e}")
        return

    if len(fav.list()) < fav.capacity:
        add_more = prompt("Add a new city now? (y/N): ").strip().lower()
        if add_more == "y":
            add_flow(client, fav)


def menu() -> None:
    load_env_from_file()
    try:
        api_key = get_api_key()
    except RuntimeError as e:
        print(e)
        sys.exit(1)

    client = WeatherClient(api_key)
    fav = Favourites(capacity=3)

    while True:
        print("""
OpenWeather CLI
1. Search weather for a city
2. Add a city to favourites
3. List favourite cities (with current weather)
4. Update favourites (remove and optionally add)
0. Exit
""")
        choice = prompt("Choose an option: ").strip()
        if choice == "1":
            search_flow(client)
        elif choice == "2":
            add_flow(client, fav)
        elif choice == "3":
            list_flow(client, fav)
        elif choice == "4":
            update_flow(client, fav)
        elif choice == "0":
            print("Goodbye!")
            return
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    menu()
