import datetime
import json

import geopandas

from .load import load_prepared_data
from . import prepare, travel


def compute_isochrone(gtfs_folder, lat, lon, start_datetime, max_duration_seconds):
    data = load_prepared_data(gtfs_folder)
    return compute_isochrone_with_data(
        data, lat, lon, start_datetime, max_duration_seconds
    )


def compute_isochrone_with_data(
    data, lat, lon, start_datetime, max_duration_seconds, use_bus=True, use_tram=True
):
    end_datetime = start_datetime + datetime.timedelta(seconds=max_duration_seconds)

    data = prepare.prepare_data_for_query(
        data, start_datetime, end_datetime, use_bus, use_tram
    )
    points = travel.compute_arrival_points(data, lat, lon, start_datetime, end_datetime)
    distances = walk_from_points(points, end_datetime)
    geojson = build_isochrone_from_points(distances)
    return geojson


def walk_from_points(points, end_datetime):
    points["duration_seconds"] = (end_datetime - points["arrival_datetime"]).dt.seconds
    points["walking_distance_m"] = (
        points["duration_seconds"] * prepare.WALKING_SPEED_M_S
    )
    distances = points.loc[:, ["lat", "lon", "walking_distance_m"]]
    return distances


def build_isochrone_from_points(distances):
    points = geopandas.GeoDataFrame(
        distances, geometry=geopandas.points_from_xy(distances["lon"], distances["lat"])
    )

    mapping_CRS = "EPSG:3949"
    lonlat_CRS = "EPSG:4326"
    # initial coords: lon, lat
    points = points.set_crs(lonlat_CRS)
    # project to a projection in meters
    # WARNING: the choice of CRS is very important here !
    gdf = points.to_crs(mapping_CRS)
    # expand the points and collapse to a single shape
    gdf = gdf.buffer(gdf["walking_distance_m"])
    shape = gdf.unary_union
    # create a geojson from the shame, keeping the same crs as before
    shape = geopandas.GeoSeries(shape, crs=mapping_CRS)
    # convert back to lon, lat
    shape = shape.to_crs(lonlat_CRS)

    # TEMP: show points of stops (and origin)
    # shape = shape.append(points.geometry)

    # convert back to lon, lat to create the geojson
    geojson = json.loads(shape.to_json())
    return geojson
