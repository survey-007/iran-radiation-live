import requests
import datetime

regions = [
    {"name": "Turkey", "lat": 39.0, "lon": 35.0, "distance": 300},
    {"name": "Iraq", "lat": 33.3, "lon": 44.4, "distance": 300},
    {"name": "Georgia", "lat": 41.7, "lon": 44.8, "distance": 150},
]

limit_per_region = 100

def fetch_measurements(lat, lon, dist):
    url = f"https://api.safecast.org/measurements.json?latitude={lat}&longitude={lon}&distance={dist}&limit={limit_per_region}"
    try:
        print(f"📡 Fetching measurements near {lat}, {lon} (distance={dist} km)")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Received {len(data)} records")
        return data
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return []

def build_kml(measurements_by_region):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Safecast Radiation - Combined</name>
  <description>Updated: {now}</description>
'''
    placemarks = ""
    for region_name, measurements in measurements_by_region.items():
        placemarks += f"<Folder><name>{region_name}</name>"
        for m in measurements:
            lat = m.get("latitude")
            lon = m.get("longitude")
            value = m.get("value")
            unit = m.get("unit", "µSv/h")
            captured = m.get("captured_at", "Unknown Time")
            if lat and lon:
                placemarks += f'''
  <Placemark>
    <name>{value} {unit}</name>
    <description>Captured at: {captured}</description>
    <Point>
      <coordinates>{lon},{lat},0</coordinates>
    </Point>
  </Placemark>
'''
        placemarks += "</Folder>"

    footer = "</Document></kml>"
    return header + placemarks + footer

def main():
    measurements_by_region = {}
    for region in regions:
        data = fetch_measurements(region["lat"], region["lon"], region["distance"])
        measurements_by_region[region["name"]] = data

    total_points = sum(len(v) for v in measurements_by_region.values())
    if total_points == 0:
        print("⚠ No data from any region.")
        return

    kml_content = build_kml(measurements_by_region)
    with open("live_combined.kml", "w", encoding="utf-8") as f:
        f.write(kml_content)

    print(f"✅ File 'live_combined.kml' created with {total_points} points.")

if __name__ == "__main__":
    main()
