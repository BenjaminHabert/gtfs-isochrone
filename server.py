import bottle
from bottle import request, response
import datetime

from gtfs_isochrone import main, load


app = application = bottle.Bottle()
data = load.load_prepared_data("data/orleans")


@app.route("/isochrone", method="GET")
def isochrone():
    response.headers["Access-Control-Allow-Origin"] = "*"
    try:
        lat = float(request.query.get("lat"))
        lon = float(request.query.get("lon"))
        max_duration_seconds = int(request.query.get("duration"))
        date_str = request.query.get("start")
        start_datetime = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        convert_string = {"false": False, "true": True}
        use_bus = convert_string[request.query.get("bus")]
        use_tram = convert_string[request.query.get("tram")]
        print(use_bus, use_tram)
    except (TypeError, ValueError, KeyError):
        response.status = 400
        response.content_type = "application/json"
        return {
            "error": (
                "invalid query string. Valid example: GET /isochrone"
                "?duration=2700&lat=47.910244&lon=1.907501&start=2020-07-02T08:00:00&bus=true&tram=true"
            ),
            "recieved": request.query_string,
        }

    return main.compute_isochrone_with_data(
        data, lat, lon, start_datetime, max_duration_seconds, use_bus, use_tram
    )
