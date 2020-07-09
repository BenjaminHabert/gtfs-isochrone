import pandas as pd
import numpy as np

from . import load


EARTH_RADIUS_METERS = 6_371_000
WALKING_SPEED_M_S = 1.1


def prepare_data_for_query(data, start_datetime, end_datetime, use_bus, use_tram):

    # data = load.copy_data(data)
    stops = data.stops.copy()
    durations = data.durations.copy()
    trips_dates = data.trips_dates.copy()
    stoptimes = data.stoptimes.copy()

    # only trips on that day
    trips_dates = trips_dates.loc[trips_dates["date"].dt.date == start_datetime.date()]
    valid_routes = []
    if use_bus:
        valid_routes.append(3)
    if use_tram:
        valid_routes.append(0)
    trips_dates = trips_dates.loc[trips_dates["route_type"].isin(valid_routes)]

    # only stoptimes with that trips
    stoptimes = stoptimes.merge(trips_dates, on="trip_id", how="inner")
    # add datetime and filter relevent stoptimes
    stoptimes["datetime"] = stoptimes["date"] + stoptimes["arrival_time"]
    stoptimes = stoptimes.loc[
        (stoptimes["datetime"] > start_datetime)
        & (stoptimes["datetime"] < end_datetime),
        ["trip_id", "stop_id", "datetime"],
    ]

    # only valid stops
    stops = stops.loc[stops["stop_id"].isin(stoptimes["stop_id"].unique())]

    # only valid durations
    durations = durations.loc[
        (durations["walk_duration"] < (end_datetime - start_datetime))
        & durations["stop_id_from"].isin(stops["stop_id"])
        & durations["stop_id_to"].isin(stops["stop_id"])
    ]

    new_data = load.Data(
        stops=stops, durations=durations, trips_dates=trips_dates, stoptimes=stoptimes
    )

    return new_data


def prepare_data_in_gtfs_folder(folder):
    # stops
    stops = load.load_raw_stops(folder)
    durations = prepare_stop_walk_duration(stops)

    load.store_stops(stops, folder)
    load.store_durations(durations, folder)

    # trip dates with route type
    calendar_dates = load.load_raw_calendar_dates(folder)
    trips = load.load_raw_trips(folder)
    routes = load.load_raw_routes(folder)
    trips_dates = prepare_trips_dates(trips, calendar_dates, routes)

    load.store_trips_dates(trips_dates, folder)

    # stoptimes
    stoptimes = load.load_raw_stoptimes(folder)
    load.store_stoptimes(stoptimes, folder)


def prepare_trips_dates(trips, calendar_dates, routes):
    return (
        trips.merge(calendar_dates, on="service_id")
        .merge(routes, on="route_id")
        .loc[:, ["trip_id", "route_type", "date"]]
    )


def prepare_stop_walk_duration(stops):
    stops = stops.copy()
    stops["fake"] = True
    distances = stops.merge(stops, on="fake", suffixes=["_from", "_to"])
    lat1, lat2, lon1, lon2 = map(
        lambda col: distances[col],
        ["stop_lat_from", "stop_lat_to", "stop_lon_from", "stop_lon_to"],
    )

    distances["walk_duration"] = walk_duration(lat1, lat2, lon1, lon2)

    distances = distances.loc[
        distances["stop_id_from"] != distances["stop_id_to"],
        ["stop_id_from", "stop_id_to", "walk_duration"],
    ]
    return distances


def distance_meters(lat1, lat2, lon1, lon2):
    """coords in degrees"""
    lat1, lat2, lon1, lon2 = [np.radians(col) for col in [lat1, lat2, lon1, lon2]]

    # https://en.wikipedia.org/wiki/Haversine_formula
    distances_meters = (
        2
        * EARTH_RADIUS_METERS
        * np.arcsin(
            np.sqrt(
                np.sin((lat1 - lat2) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2) * (np.sin((lon1 - lon2) / 2) ** 2)
            )
        )
    )
    return distances_meters


def walk_duration(lat1, lat2, lon1, lon2):
    distances_meters = distance_meters(lat1, lat2, lon1, lon2)
    walk_duration_seconds = pd.TimedeltaIndex(
        distances_meters / WALKING_SPEED_M_S, "seconds"
    ).round("S")
    return walk_duration_seconds


def arrival_datetime(start_datetime, lat1, lat2, lon1, lon2):
    walk_duration_seconds = walk_duration(lat1, lat2, lon1, lon2)
    return walk_duration_seconds + start_datetime
