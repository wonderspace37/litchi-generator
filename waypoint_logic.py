import csv
import os
import tempfile
from geopy.distance import distance


# -------------------------------
# --- WAYPOINT GENERATION LOGIC ---
# -------------------------------
def generate_waypoints(initial_lat, initial_lon, initial_bearing, waypoints):
    """
    Generate GPS coordinates for waypoints relative to an initial coordinate.
    Waypoint 0 (home) is fixed at 5 m altitude.
    Every waypoint altitude >= 2 m.
    """
    results = []
    current_lat, current_lon, current_alt = initial_lat, initial_lon, 5  # Start 5m high

    # Add the initial waypoint (always 5m)
    results.append(
        {
            "waypoint": 0,
            "latitude": current_lat,
            "longitude": current_lon,
            "altitude": 5,
            "true_bearing": initial_bearing,
            "hold_time": 0,
        }
    )

    for i, wp in enumerate(waypoints, start=1):
        # Convert relative bearing to true bearing
        true_bearing = (initial_bearing + wp["bearing"]) % 360

        # Compute new coordinate using geodesic projection
        new_point = distance(meters=wp["horizontal"]).destination(
            (current_lat, current_lon), true_bearing
        )

        new_lat, new_lon = new_point.latitude, new_point.longitude
        new_alt = max(2, wp["vertical"])  # Ensure at least 2m altitude

        results.append(
            {
                "waypoint": i,
                "latitude": new_lat,
                "longitude": new_lon,
                "altitude": new_alt,
                "true_bearing": true_bearing,
                "hold_time": wp.get("hold_time", 0),
            }
        )

        # Update current position for next waypoint
        current_lat, current_lon, current_alt = new_lat, new_lon, new_alt

    return results


# -------------------------------
# --- LITCHI CSV EXPORT LOGIC ---
# -------------------------------
def export_to_litchi_csv(initial_lat, initial_lon, waypoints, poi_altitude=1):
    """
    Export generated waypoints to a Litchi-compatible CSV file.
    Uses a persistent counter locally, but disables it on serverless hosts like Vercel.
    """

    # Detect if we're running on Vercel or another serverless environment
    running_on_vercel = "VERCEL" in os.environ or "CI" in os.environ

    if not running_on_vercel:
        counter_file = "run_counter.txt"
        if os.path.exists(counter_file):
            with open(counter_file, "r") as f:
                run_count = int(f.read().strip() or 0)
        else:
            run_count = 0
        run_count += 1
        with open(counter_file, "w") as f:
            f.write(str(run_count))
        filename = f"output_{run_count}.csv"
    else:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        filename = tmp.name
        run_count = "serverless"

    # Exact Litchi CSV headers
    fieldnames = [
        "latitude",
        "longitude",
        "altitude(m)",
        "heading(deg)",
        "curvesize(m)",
        "rotationdir",
        "gimbalmode",
        "gimbalpitchangle",
        "actiontype1",
        "actionparam1",
        "altitudemode",
        "speed(m/s)",
        "poi_latitude",
        "poi_longitude",
        "poi_altitude(m)",
        "poi_altitudemode",
        "photo_timeinterval",
        "photo_distinterval",
    ]

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for wp in waypoints:
            writer.writerow(
                {
                    "latitude": wp["latitude"],
                    "longitude": wp["longitude"],
                    "altitude(m)": wp["altitude"],
                    "heading(deg)": wp["true_bearing"],
                    "curvesize(m)": 0,
                    "rotationdir": 0,
                    "gimbalmode": 0,
                    "gimbalpitchangle": 0,
                    "actiontype1": 0,
                    "actionparam1": int(wp.get("hold_time", 0) * 1000),
                    "altitudemode": 0,
                    "speed(m/s)": 0,
                    "poi_latitude": initial_lat,
                    "poi_longitude": initial_lon,
                    "poi_altitude(m)": poi_altitude,
                    "poi_altitudemode": 0,
                    "photo_timeinterval": 1,
                    "photo_distinterval": 0,
                }
            )

    print(
        f"✅ Run #{run_count}: Saved '{filename}' (local mode: {not running_on_vercel})"
    )
    return filename
