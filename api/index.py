import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

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
    waypoints = data["waypoints"]

    results = generate_waypoints(init_lat, init_lon, init_bearing, waypoints)
    filename = export_to_litchi_csv(init_lat, init_lon, results, poi_altitude)
    return send_file(filename, as_attachment=True, download_name=filename)


# ✅ remove this line if it exists:
# app.run()

# ✅ instead, expose the Flask app directly:
def handler(request, response):
    return app(request, response)


# ✅ or simply:
# app = app  # so Vercel detects it as entry point
