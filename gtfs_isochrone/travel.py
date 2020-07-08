# import datetime

import pandas as pd
import numpy as np

from . import prepare


def compute_arrival_points(data, lat, lon, start_datetime, end_datetime):
    """
    returns: df with columns ["lat", "lon", "arrival_datetime"]
    """
    stops = data.stops
    stoptimes = data.stoptimes.sort_values(by=["trip_id", "datetime"])

    # Initially reached stops from origin
    reached_stops = walk_from_origin(start_datetime, lat, lon, stops)
    reached_stops = reached_stops.loc[
        reached_stops["arrival_datetime"] < end_datetime,
        ["stop_id", "arrival_datetime"],
    ]

    # find reachable stoptimes
    reachable_stoptimes = stoptimes.merge(reached_stops, on="stop_id", how="left")
    reachable_stoptimes["reachable"] = np.nan
    reachable_stoptimes.loc[
        reachable_stoptimes["datetime"] > reachable_stoptimes["arrival_datetime"],
        "reachable",
    ] = True
    reachable_stoptimes["reachable"] = reachable_stoptimes.groupby("trip_id")[
        "reachable"
    ].fillna(method="ffill")

    valids = reachable_stoptimes["reachable"].notnull()
    reachable_stoptimes = reachable_stoptimes.loc[valids]

    reachable_stoptimes["arrival_datetime"] = reachable_stoptimes.loc[
        :, ["arrival_datetime", "datetime"]
    ].min(axis=1)

    reached_stops = (
        reached_stops.append(
            reachable_stoptimes.loc[:, ["stop_id", "arrival_datetime"]]
        )
        .sort_values(by="arrival_datetime")
        .drop_duplicates(subset=["stop_id"], keep="first")
    )

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
