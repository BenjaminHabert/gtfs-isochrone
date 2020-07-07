import pandas as pd
import numpy as np

from . import load


EARTH_RADIUS_METERS = 6_371_000
WALKING_SPEED_M_S = 1.4


def prepare_data_in_gtfs_folder(folder):
    # stops
    stops = load.load_raw_stops(folder)
    durations = prepare_stop_walk_duration(stops)

    load.store_stops(stops, folder)
    load.store_durations(durations, folder)

    # trip dates
    calendar_dates = load.load_raw_calendar_dates(folder)
    trips = load.load_raw_trips(folder)
    trips_dates = prepare_trips_dates(trips, calendar_dates)

    load.store_trips_dates(trips_dates, folder)

    # stoptimes


def prepare_trips_dates(trips, calendar_dates):
    return trips.merge(calendar_dates, on="service_id").loc[:, ["trip_id", "date"]]


def prepare_stop_walk_duration(stops):
    stops = stops.copy()
    stops["fake"] = True
    distances = stops.merge(stops, on="fake", suffixes=["_from", "_to"])
    lat1, lat2, lon1, lon2 = map(
        lambda col: np.radians(distances[col]),
        ["stop_lat_from", "stop_lat_to", "stop_lon_from", "stop_lon_to"],
    )

    distances["distance_m"] = (
        2
        * EARTH_RADIUS_METERS
        * np.arcsin(
            np.sqrt(
                np.sin((lat1 - lat2) / 2) ** 2
                + np.cos(lat1) * np.cos(lat2) * (np.sin((lon1 - lon2) / 2) ** 2)
            )
        )
    )

    distances["walk_duration"] = pd.TimedeltaIndex(
        distances["distance_m"] / WALKING_SPEED_M_S, "seconds"
    ).round("S")

    distances = distances.loc[
        distances["stop_id_from"] != distances["stop_id_to"],
        ["stop_id_from", "stop_id_to", "walk_duration"],
    ]
    return distances
