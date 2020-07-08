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
    except (TypeError, ValueError):
        response.status = 400
        response.content_type = "application/json"
        return {
            "error": "invalid query string. Valid example: ?lat=47.9007&lon=1.9036&duration=60&start=2020-07-02T13:00:00",
            "recieved": request.query_string,
        }

    return main.compute_isochrone_with_data(
        data, lat, lon, start_datetime, max_duration_seconds
    )
