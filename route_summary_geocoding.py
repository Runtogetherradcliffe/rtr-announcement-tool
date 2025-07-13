import requests
import polyline
import os

LOCATIONIQ_API_KEY = os.getenv("LOCATIONIQ_API_KEY")
GEOCODE_FIELDS_PRIORITY = ["neighbourhood", "suburb", "city_district", "city", "town", "village"]

def locationiq_reverse_geocode(lat, lon):
    try:
        response = requests.get(url, timeout=5)
        url = f"https://us1.locationiq.com/v1/reverse?key={LOCATIONIQ_API_KEY}&lat={lat}&lon={lon}&format=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})
        display_name = data.get("display_name", "")
        for field in GEOCODE_FIELDS_PRIORITY:
            if field in address:
                return address[field]
        if "," in display_name:
            return display_name.split(",")[0]
        return None
    except Exception as e:
        print(f"LocationIQ reverse geocode failed: {e}")
        return None

def get_features_along_route(coords, distance_threshold=0.0015):
    features = set()
    for lat, lon in coords:
        query = (
            f"[out:json][timeout:25];"
            f"(node[\"leisure\"=\"park\"](around:{int(distance_threshold * 100000)}, {lat}, {lon});"
            f"way[\"leisure\"=\"park\"](around:{int(distance_threshold * 100000)}, {lat}, {lon});"
            f"relation[\"leisure\"=\"park\"](around:{int(distance_threshold * 100000)}, {lat}, {lon}););"
            "out center;"
        )
        try:
        response = requests.get(url, timeout=5)
            response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
            response.raise_for_status()
            data = response.json()
            elements = data.get("elements", [])
            for el in elements:
                name = el.get("tags", {}).get("name")
                if name:
                    features.add(name)
        except Exception as e:
            print(f"Overpass API error: {e}")
            continue
    return list(features)

def summarize_routes(route_data_list):
    summaries = []
    for data in route_data_list:
        polyline_str = data.get("map", {}).get("polyline")
        if not polyline_str:
            continue
        try:
        response = requests.get(url, timeout=5)
            coords = polyline.decode(polyline_str)
            elev_gain = round(data.get("elevation_gain", 0))
            distance_km = round(data.get("distance", 0) / 1000, 1)
            features = get_features_along_route(coords)
            title = data.get("name", "Route")
            url = f"https://www.strava.com/routes/{data.get('id')}"
            feature_str = ", ".join(features[:6])  # limit to first 6
            summary = f"{title}: {url}\n  {distance_km} km with {elev_gain}m of elevation – gently undulating 🌿\n  🏞️ This route passes {feature_str}."
            summaries.append(summary)
        except Exception as e:
            print(f"Error summarizing route: {e}")
            continue
    return summaries