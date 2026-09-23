import os
from typing import Optional
import requests


def geocode_address(address: str) -> str:
    """Converts a street address or location name into geographic latitude and longitude coordinates.

    Args:
        address: Address or location name (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco, CA').

    Returns:
        A string containing the formatted address and latitude/longitude coordinates.
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": api_key}
        res = requests.get(url, params=params, timeout=5).json()

        if res.get("status") != "OK" or not res.get("results"):
            return f"Could not geocode address '{address}'. Status: {res.get('status')}"

        result = res["results"][0]
        formatted_address = result.get("formatted_address")
        location = result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return (
            f"Geocoding Result for '{address}':\n"
            f"- Formatted Address: {formatted_address}\n"
            f"- Latitude: {lat}\n"
            f"- Longitude: {lng}"
        )
    except Exception as e:
        return f"Error executing Geocoding API: {e}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "florist",
    radius_meters: float = 5000.0,
) -> str:
    """Finds nearby places (e.g. florists, plant nurseries, garden centers) using Google Places API (New).

    Args:
        latitude: Latitude coordinate of the search center.
        longitude: Longitude coordinate of the search center.
        place_type: Place type to search for (e.g., 'florist', 'store', 'park').
        radius_meters: Radius in meters around the center point (default 5000.0).

    Returns:
        A string listing nearby places with their names, formatted addresses, and location coordinates.
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
        }
        body = {
            "includedTypes": [place_type],
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                    },
                    "radius": float(radius_meters),
                }
            },
        }

        res = requests.post(url, headers=headers, json=body, timeout=5)
        if res.status_code != 200:
            return f"Error from Places API (New) [HTTP {res.status_code}]: {res.text}"

        data = res.json()
        places = data.get("places", [])
        if not places:
            return f"No nearby '{place_type}' places found within {radius_meters} meters."

        results_list = []
        for p in places[:10]:
            name = p.get("displayName", {}).get("text", "N/A")
            addr = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            lat = loc.get("latitude")
            lng = loc.get("longitude")
            results_list.append(
                f"- Name: {name}\n  Address: {addr}\n  Location: ({lat}, {lng})"
            )

        return f"Nearby '{place_type}' Places Found:\n" + "\n".join(results_list)
    except Exception as e:
        return f"Error executing Places API (New): {e}"
