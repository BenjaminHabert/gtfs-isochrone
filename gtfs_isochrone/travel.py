# import datetime

import pandas as pd

from . import prepare


def compute_arrival_points(data, lat, lon, start_datetime, end_datetime):
    """
    returns: df with columns ["lat", "lon", "arrival_datetimes"]
    """
    stops = data.stops

    # Initially reached stops from origin
    reached_stops = walk_from_origin(start_datetime, lat, lon, stops)
    reached_stops = reached_stops.loc[
        reached_stops["arrival_datetime"] < end_datetime,
        ["stop_id", "arrival_datetime"],
    ]

    # END: add coordinates to reached stops and add origin point
    reached_stops = reached_stops.merge(stops, how="left", on="stop_id").rename(
        columns={"stop_lat": "lat", "stop_lon": "lon"}
    )
    reached_stops = reached_stops.append(
        pd.Series(
            {
                "stop_id": "origin",
                "lat": lat,
                "lon": lon,
                "arrival_datetime": start_datetime,
            },
            name="origin",
        )
    )
    return reached_stops


def walk_from_origin(start_datetime, lat, lon, stops):
    reached_stops = stops.copy()
    reached_stops["arrival_datetime"] = prepare.arrival_datetime(
        start_datetime, lat, stops["stop_lat"], lon, stops["stop_lon"]
    )

    return reached_stops
