import os

import pandas as pd
import numpy as np


def load_prepared_data(gtfs_folder):
    durations_path = os.path.join(gtfs_folder, "durations.p")
    return pd.read_pickle(durations_path)


def store_durations(durations, gtfs_folder):
    durations_path = os.path.join(gtfs_folder, "durations.p")
    durations.to_pickle(durations_path)


def load_raw_stops(gtfs_folder):
    stops_path = os.path.join(gtfs_folder, "stops.txt")

    return pd.read_csv(
        stops_path,
        usecols=["stop_id", "stop_lat", "stop_lon"],
        dtype={"stop_id": "object", "stop_lat": np.float64, "stop_lon": np.float64},
    )
