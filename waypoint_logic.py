import csv
import os
import tempfile
from geopy.distance import distance


# -------------------------------
# --- WAYPOINT GENERATION LOGIC ---
# -------------------------------
def export_to_litchi_csv(
    initial_lat,
    initial_lon,
    waypoints,
    poi_altitude=1,
    speed_start=0,
    curve_size=0,
    gimbal_pitch=0,
    photo_interval=1,
):
    ...
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
                    "curvesize(m)": curve_size,  # user value
                    "rotationdir": 0,
                    "gimbalmode": 0,
                    "gimbalpitchangle": gimbal_pitch,  # user value
                    "actiontype1": 0,
                    "actionparam1": int(wp.get("hold_time", 0) * 1000),
                    "altitudemode": 0,
                    "speed(m/s)": speed_start,  # user value
                    "poi_latitude": initial_lat,
                    "poi_longitude": initial_lon,
                    "poi_altitude(m)": poi_altitude,
                    "poi_altitudemode": 0,
                    "photo_timeinterval": photo_interval,  # user value
                    "photo_distinterval": 0,
                }
            )

    print(
        f"✅ Run #{run_count}: Saved '{filename}' (local mode: {not running_on_vercel})"
    )
    return filename
