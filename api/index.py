import sys, os
import json
from flask import Flask, request, send_file, render_template
from waypoint_logic import generate_waypoints, export_to_litchi_csv

# --- Ensure imports work when deployed ---
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# --- Flask app instance ---
app = Flask(__name__, template_folder="templates")

# -------------------------------
# --- ROUTES ---
# -------------------------------


@app.route("/")
def index():
    """Render the main web interface."""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Handle JSON input from frontend and return generated CSV."""
    try:
        data = json.loads(request.data.decode("utf-8"))
        init_lat = float(data["init_lat"])
        init_lon = float(data["init_lon"])
        init_bearing = float(data["init_bearing"])
        poi_altitude = float(data.get("poi_altitude", 1))
        waypoints = data.get("waypoints", [])

        # --- Normalize waypoint structure ---
        parsed_waypoints = []
        for wp in waypoints:
            if isinstance(wp, dict):
                # Handle both lowercase and UI-style keys
                parsed_waypoints.append(
                    {
                        "horizontal": float(
                            wp.get("horizontal") or wp.get("Horizontal (m)") or 0
                        ),
                        "vertical": float(
                            wp.get("vertical") or wp.get("Vertical (m)") or 0
                        ),
                        "bearing": float(
                            wp.get("bearing") or wp.get("Bearing (°)") or 0
                        ),
                        "hold_time": float(
                            wp.get("hold_time") or wp.get("Hold (s)") or 0
                        ),
                    }
                )
            elif isinstance(wp, (list, tuple)) and len(wp) >= 4:
                parsed_waypoints.append(
                    {
                        "horizontal": float(wp[0]),
                        "vertical": float(wp[1]),
                        "bearing": float(wp[2]),
                        "hold_time": float(wp[3]),
                    }
                )

        # --- Generate coordinates and export CSV ---
        results = generate_waypoints(init_lat, init_lon, init_bearing, parsed_waypoints)
        filename = export_to_litchi_csv(init_lat, init_lon, results, poi_altitude)

        return send_file(filename, as_attachment=True, download_name=filename)

    except Exception as e:
        # Log and return JSON error for frontend display
        print(f"❌ Error generating CSV: {e}")
        return {"error": str(e)}, 500


# ✅ Do NOT call app.run()
# ✅ Do NOT define a handler() function
# Vercel automatically uses 'app' as the entry point
