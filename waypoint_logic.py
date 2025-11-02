import csv
import os
import tempfile

def export_to_litchi_csv(initial_lat, initial_lon, waypoints, poi_altitude=1):
    """
    Export generated waypoints to a Litchi-compatible CSV file.
    Uses a persistent counter locally, but disables it on serverless hosts like Vercel.
    """

    # Detect if we're running on Vercel or another serverless environment
    running_on_vercel = "VERCEL" in os.environ or "CI" in os.environ

    if not running_on_vercel:
        # Local mode — keep persistent counter
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
        # Serverless mode — use temporary filename
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        filename = tmp.name
        run_count = "serverless"

    # Exact Litchi CSV headers
    fieldnames = [
        "latitude", "longitude", "altitude(m)", "heading(deg)", "curvesize(m)",
        "rotationdir", "gimbalmode", "gimbalpitchangle",
        "actiontype1", "actionparam1", "altitudemode", "speed(m/s)",
        "poi_latitude", "poi_longitude", "poi_altitude(m)",
        "poi_altitudemode", "photo_timeinterval", "photo_distinterval"
    ]

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for wp in waypoints:
            writer.writerow({
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
                "photo_distinterval": 0
            })

    print(f"✅ Run #{run_count}: Saved '{filename}' (local mode: {not running_on_vercel})")
    return filename
