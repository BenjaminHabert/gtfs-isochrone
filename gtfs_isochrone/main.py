import datetime


# from .load import load_prepared_data
from . import prepare


def compute_isochrone(gtfs_folder, lat, lon, start_datetime, max_duration_seconds):
    # data = load_prepared_data(gtfs_folder)
    data = None
    return compute_isochrone_with_data(
        data, lat, lon, start_datetime, max_duration_seconds
    )


def compute_isochrone_with_data(data, lat, lon, start_datetime, max_duration_seconds):
    end_datetime = start_datetime + datetime.timedelta(seconds=max_duration_seconds)

    # data = prepare.prepare_data_for_query(data, start_datetime, end_datetime)
    points = compute_arrival_points(data, lat, lon, start_datetime, end_datetime)
    distances = walk_from_points(points, end_datetime)
    shape = build_isochrone_from_points(distances)
    geojson = convert_to_geojson(shape)
    return geojson


def compute_arrival_points(data, lat, lon, start_datetime, end_datetime):
    import pandas as pd

    return pd.DataFrame.from_records(
        [{"lat": lat, "lon": lon, "arrival_datetime": start_datetime}]
    )


def walk_from_points(points, end_datetime):
    points["duration_seconds"] = (end_datetime - points["arrival_datetime"]).dt.seconds
    points["walking_distance_m"] = (
        points["duration_seconds"] * prepare.WALKING_SPEED_M_S
    )
    distances = points.loc[:, ["lat", "lon", "walking_distance_m"]]
    return distances


def build_isochrone_from_points(distances):
    return distances


def convert_to_geojson(shape):
    return shape
