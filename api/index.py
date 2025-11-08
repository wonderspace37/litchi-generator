@app.route("/generate", methods=["POST"])
def generate():
    """Handle JSON input from frontend and return generated CSV."""
    try:
        data = json.loads(request.data.decode("utf-8"))
        init_lat = float(data["init_lat"])
        init_lon = float(data["init_lon"])
        init_bearing = float(data["init_bearing"])

        # --- new user parameters ---
        speed_start = float(data.get("speed_start", 0))  # m/s
        curve_size = float(data.get("curve_size", 0))  # m
        gimbal_pitch = float(data.get("gimbal_pitch", 0))  # °
        poi_altitude = float(data.get("poi_altitude", 1))  # m
        photo_interval = float(data.get("photo_interval", 1))  # s

        waypoints = data.get("waypoints", [])

        # --- normalize waypoints as before ---
        parsed_waypoints = []
        for wp in waypoints:
            if isinstance(wp, dict):
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

        # --- pass new params to export function ---
        results = generate_waypoints(init_lat, init_lon, init_bearing, parsed_waypoints)
        filename = export_to_litchi_csv(
            init_lat,
            init_lon,
            results,
            poi_altitude=poi_altitude,
            speed_start=speed_start,
            curve_size=curve_size,
            gimbal_pitch=gimbal_pitch,
            photo_interval=photo_interval,
        )

        return send_file(filename, as_attachment=True, download_name=filename)

    except Exception as e:
        print(f"❌ Error generating CSV: {e}")
        return {"error": str(e)}, 500
