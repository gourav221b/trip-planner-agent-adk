"""Domain-specific tools used by the personal assistant agents."""

from __future__ import annotations

import datetime as _dt
import logging
import textwrap
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import TypedDict
from typing import cast

import requests

_LOGGER = logging.getLogger(__name__)

_GEOCODE_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"
_WEATHER_ENDPOINT = "https://api.open-meteo.com/v1/forecast"
_NEWS_RSS_ENDPOINT = "https://news.google.com/rss/search"


class WeatherSummary(TypedDict, total=False):
  location: str
  latitude: float
  longitude: float
  current_conditions: Dict[str, Any]
  daily_forecast: List[Dict[str, Any]]
  source: str


class SafetyHeadline(TypedDict, total=False):
  title: str
  link: str
  published: str
  snippet: str


class SafetyBrief(TypedDict, total=False):
  location: str
  headlines: List[SafetyHeadline]
  source: str


def _resolve_location(location: str) -> Tuple[float, float, str]:
  """Resolve a free-form location string into coordinates."""
  response = requests.get(
      _GEOCODE_ENDPOINT,
      params={
          "name": location,
          "count": 1,
          "language": "en",
          "format": "json",
      },
      timeout=10,
  )
  response.raise_for_status()
  payload = response.json()
  results = payload.get("results") or []
  if not results:
    raise ValueError(f"Unable to geocode location '{location}'.")

  top_hit = results[0]
  resolved_name = ", ".join(
      part
      for part in (
          top_hit.get("name"),
          top_hit.get("admin1"),
          top_hit.get("country"),
      )
      if part
  )
  lat = cast(float, top_hit["latitude"])
  lon = cast(float, top_hit["longitude"])
  return lat, lon, resolved_name


def fetch_weather_summary(
    location: str, *, days: int = 5, include_hourly: bool = False
) -> WeatherSummary:
  """Fetch a short-term weather outlook for a destination.

  Args:
    location: Free-form location to resolve (city, landmark, etc.).
    days: Number of daily entries to include (1-7 supported by Open-Meteo).
    include_hourly: Whether to include hourly data for the next 24 hours.

  Returns:
    Structured weather summary suitable for LLM consumption.
  """
  if not location or not location.strip():
    raise ValueError("location is required")

  lat, lon, resolved_name = _resolve_location(location)

  params = {
      "latitude": lat,
      "longitude": lon,
      "timezone": "auto",
      "current_weather": True,
      "daily": [
          "temperature_2m_max",
          "temperature_2m_min",
          "precipitation_probability_max",
          "sunrise",
          "sunset",
          "uv_index_max",
          "wind_speed_10m_max",
          "precipitation_sum",
      ],
  }

  if include_hourly:
    params["hourly"] = [
        "temperature_2m",
        "precipitation_probability",
        "weathercode",
        "relativehumidity_2m",
    ]

  response = requests.get(_WEATHER_ENDPOINT, params=params, timeout=10)
  response.raise_for_status()
  payload = response.json()

  current = payload.get("current_weather", {}) or {}
  daily = payload.get("daily", {}) or {}
  days_available = min(days, len(daily.get("time", [])))

  daily_forecast: List[Dict[str, Any]] = []
  for idx in range(days_available):
    daily_forecast.append(
        {
            "date": daily.get("time", [])[idx],
            "summary": {
                "max_temp_c": daily.get("temperature_2m_max", [None])[idx],
                "min_temp_c": daily.get("temperature_2m_min", [None])[idx],
                "precip_probability": daily.get(
                    "precipitation_probability_max", [None]
                )[idx],
                "precipitation_total_mm": daily.get(
                    "precipitation_sum", [None]
                )[idx],
                "uv_index_max": daily.get("uv_index_max", [None])[idx],
                "wind_speed_max_kmh": daily.get(
                    "wind_speed_10m_max", [None]
                )[idx],
            },
            "sunrise": daily.get("sunrise", [None])[idx],
            "sunset": daily.get("sunset", [None])[idx],
        }
    )

  summary: WeatherSummary = {
      "location": resolved_name,
      "latitude": lat,
      "longitude": lon,
      "current_conditions": {
          "temperature_c": current.get("temperature"),
          "windspeed_kmh": current.get("windspeed"),
          "weather_code": current.get("weathercode"),
          "observation_time": current.get("time"),
      },
      "daily_forecast": daily_forecast,
      "source": "Open-Meteo (https://open-meteo.com)",
  }

  if include_hourly and "hourly" in payload:
    hourly_data = payload["hourly"]
    next_24_hours: List[Dict[str, Any]] = []
    base_times = hourly_data.get("time", [])
    now = _dt.datetime.now(_dt.timezone.utc)
    for idx, time_str in enumerate(base_times):
      timestamp = _dt.datetime.fromisoformat(time_str)
      if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=_dt.timezone.utc)
      else:
        timestamp = timestamp.astimezone(_dt.timezone.utc)
      if timestamp < now:
        continue
      if timestamp > now + _dt.timedelta(hours=24):
        break
      next_24_hours.append(
          {
              "time": time_str,
              "temperature_c": hourly_data.get("temperature_2m", [None])[idx],
              "precip_probability": hourly_data.get(
                  "precipitation_probability", [None]
              )[idx],
              "relative_humidity": hourly_data.get(
                  "relativehumidity_2m", [None]
              )[idx],
              "weather_code": hourly_data.get("weathercode", [None])[idx],
          }
      )
    summary["hourly_outlook"] = next_24_hours  # type: ignore[typeddict-item]

  return summary


def fetch_safety_brief(
    location: str, *, max_items: int = 4, language: str = "en-US"
) -> SafetyBrief:
  """Fetch recent safety-related headlines for a destination.

  Args:
    location: Free-form location string to search against.
    max_items: Maximum number of entries to return.
    language: Google News language/locale code.

  Returns:
    A structured brief with URLs that downstream agents can summarize.
  """
  if not location or not location.strip():
    raise ValueError("location is required")

  query = f"{location} travel warning OR safety advisory OR disruption OR protest"
  params = {
      "q": query,
      "hl": language,
      "gl": language.split("-")[-1],
      "ceid": language.replace("-", ":"),
  }

  response = requests.get(
      _NEWS_RSS_ENDPOINT, params=params, timeout=10, headers={"User-Agent": "trip-assistant/1.0"}
  )
  response.raise_for_status()
  response.encoding = response.apparent_encoding

  headlines: List[SafetyHeadline] = []

  try:
    import xml.etree.ElementTree as ET

    tree = ET.fromstring(response.text)
    for item in tree.findall(".//item")[:max_items]:
      title = (item.findtext("title") or "").strip()
      link = (item.findtext("link") or "").strip()
      pub_date = (item.findtext("pubDate") or "").strip()
      description = (item.findtext("description") or "").strip()
      snippet = textwrap.shorten(
          description.replace("<br>", " ").replace("\n", " "), width=240
      )
      if not title or not link:
        continue
      headlines.append(
          SafetyHeadline(
              title=title,
              link=link,
              published=pub_date,
              snippet=snippet,
          )
      )
  except Exception as exc:  # pylint: disable=broad-except
    _LOGGER.warning("Failed to parse safety brief for %s: %s", location, exc)
    raise

  if not headlines:
    raise ValueError(
        f"Unable to find recent safety headlines for '{location}'."
    )

  return SafetyBrief(
      location=location,
      headlines=headlines,
      source="Google News RSS",
  )


__all__ = [
    "fetch_weather_summary",
    "fetch_safety_brief",
    "WeatherSummary",
    "SafetyBrief",
]
