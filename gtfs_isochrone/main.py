import datetime
import json

import geopandas

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
    geojson = build_isochrone_from_points(distances)
    return geojson


def compute_arrival_points(data, lat, lon, start_datetime, end_datetime):
    import pandas as pd

    return pd.DataFrame.from_records(
        [
            {"lat": lat, "lon": lon, "arrival_datetime": start_datetime},
            {
                "lat": 47.899932,
                "lon": 1.893925,
                "arrival_datetime": start_datetime + datetime.timedelta(minutes=10),
            },
        ]
    )


def walk_from_points(points, end_datetime):
    points["duration_seconds"] = (end_datetime - points["arrival_datetime"]).dt.seconds
    points["walking_distance_m"] = (
        points["duration_seconds"] * prepare.WALKING_SPEED_M_S
    )
    distances = points.loc[:, ["lat", "lon", "walking_distance_m"]]
    return distances


def build_isochrone_from_points(distances):
    gdf = geopandas.GeoDataFrame(
        distances, geometry=geopandas.points_from_xy(distances["lon"], distances["lat"])
    )

    # initial coords: lon, lat
    gdf = gdf.set_crs("EPSG:4326")
    # project to a projection in meters
    gdf = gdf.to_crs("EPSG:3857")
    # expand the points and collapse to a single shape
    gdf = gdf.buffer(gdf["walking_distance_m"])
    shape = gdf.unary_union
    # create a geojson from the shame, keeping the same crs as before
    shape = geopandas.GeoSeries(shape, crs="EPSG:3857")

    # convert back to lon, lat to create the geojson
    geojson = json.loads(shape.to_crs("EPSG:4326").to_json())
    return geojson
