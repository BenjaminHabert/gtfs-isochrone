import os

import pandas as pd
import numpy as np


def load_prepared_data(gtfs_folder):
    files_to_load = [
        "stops.p",
        "durations.p",
        "trips_dates.p",
    ]

    dataframes = map(
        lambda name: pd.read_pickle(os.path.join(gtfs_folder, name)), files_to_load
    )
    return dataframes


def _store(df, folder, name):
    path = os.path.join(folder, name)
    df.to_pickle(path)


def store_durations(durations, gtfs_folder):
    _store(durations, gtfs_folder, "durations.p")


def store_stops(stops, gtfs_folder):
    _store(stops, gtfs_folder, "stops.p")


def store_trips_dates(trips_dates, gtfs_folder):
    _store(trips_dates, gtfs_folder, "trips_dates.p")


def load_raw_stops(gtfs_folder):
    stops_path = os.path.join(gtfs_folder, "stops.txt")

    return pd.read_csv(
        stops_path,
        usecols=["stop_id", "stop_lat", "stop_lon"],
        dtype={"stop_id": "object", "stop_lat": np.float64, "stop_lon": np.float64},
    )


def load_raw_calendar_dates(gtfs_folder):
    path_calendar_dates = os.path.join(gtfs_folder, "calendar_dates.txt")
    return pd.read_csv(
        path_calendar_dates,
        usecols=["service_id", "date"],
        dtype={"service_id": "object", "date": "object"},
        parse_dates=["date"],
    )


def load_raw_trips(gtfs_folder):
    path_trips = os.path.join(gtfs_folder, "trips.txt")
    return pd.read_csv(path_trips, usecols=["service_id", "trip_id"], dtype="object")
