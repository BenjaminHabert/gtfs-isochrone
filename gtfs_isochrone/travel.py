import pandas as pd
import numpy as np

from . import prepare


def compute_arrival_points(data, lat, lon, start_datetime, end_datetime):
    """
    returns: df with columns ["lat", "lon", "arrival_datetime"]
    """
    stops = data.stops
    stoptimes = data.stoptimes.sort_values(by=["trip_id", "datetime"])
    stoptimes_columns = stoptimes.columns
    durations = data.durations

    # Initially reached stops from origin
    reached_stops = walk_from_origin(start_datetime, lat, lon, stops)
    reached_stops = reached_stops.loc[
        reached_stops["arrival_datetime"] < end_datetime,
        ["stop_id", "arrival_datetime"],
    ]

    for num_changement in range(4):
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

        # keep only reachable stoptimes, the rest is used for next iteration
        valids = reachable_stoptimes["reachable"].notnull()
        stoptimes = reachable_stoptimes.loc[~valids, stoptimes_columns]
        reachable_stoptimes = reachable_stoptimes.loc[valids]

        print(len(reachable_stoptimes))
        if len(reachable_stoptimes) == 0:
            print(
                f"Stopping with num_changement: {num_changement} because we run out of stoptimes"
            )
            break

        # arrival time at these reachable stoptimes
        reachable_stoptimes["arrival_datetime"] = reachable_stoptimes.loc[
            :, ["arrival_datetime", "datetime"]
        ].min(axis=1)
        # reachable_stoptimes["arrival_datetime"] = np.min

        # adding the stops to the list
        reached_stops = (
            reached_stops.append(
                reachable_stoptimes.loc[:, ["stop_id", "arrival_datetime"]]
            )
            .sort_values(by="arrival_datetime")
            .drop_duplicates(subset=["stop_id"], keep="first")
        )

        # walking from the stops
        reached_stops, has_not_changed = walk_from_stops(
            reached_stops, durations, end_datetime
        )

        if has_not_changed:
            print(
                f"Stopping with num_changement: {num_changement} and has_not_changed: {has_not_changed}"
            )
            break

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


def walk_from_stops(reached_stops, durations, end_datetime):
    """ return : (new reached_stops, has_not_changed) """
    new = reached_stops.merge(
        durations, how="left", left_on="stop_id", right_on="stop_id_from"
    )
    new["arrival_datetime"] = new["arrival_datetime"] + new["walk_duration"]

    new = (
        new.loc[
            new["arrival_datetime"] < end_datetime, ["stop_id_to", "arrival_datetime"]
        ]
        .rename(columns={"stop_id_to": "stop_id"})
        .append(reached_stops)
        .sort_values(by="arrival_datetime")
        .drop_duplicates(subset="stop_id", keep="first")
    )

    has_not_changed = (len(new) == len(reached_stops)) & new.equals(reached_stops)

    return new, has_not_changed
