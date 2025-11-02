from flask import Flask, request, send_file, render_template
from waypoint_logic import generate_waypoints, export_to_litchi_csv
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = json.loads(request.data.decode("utf-8"))
    init_lat = float(data["init_lat"])
    init_lon = float(data["init_lon"])
    init_bearing = float(data["init_bearing"])
    poi_altitude = float(data.get("poi_altitude", 1))
    waypoints = [
        {
            "horizontal": float(wp["horizontal"]),
            "vertical": float(wp["vertical"]),
            "bearing": float(wp["bearing"]),
            "hold_time": float(wp["hold_time"]),
        }
        for wp in data["waypoints"]
    ]

    results = generate_waypoints(init_lat, init_lon, init_bearing, waypoints)
    filename = export_to_litchi_csv(init_lat, init_lon, results, poi_altitude)
    return send_file(filename, as_attachment=True, download_name=filename)


# Vercel looks for this entry point
app.run()
