import click

from gtfs_isochrone import prepare as _prepare, main, load


@click.group()
def cli():
    pass


@click.command()
@click.argument("gtfs_folder")
def prepare(gtfs_folder):
    _prepare.prepare_data_in_gtfs_folder(gtfs_folder)


@click.command()
def demo():
    import datetime

    gtfs_folder = "data/orleans"
    lat = 47.900792
    lon = 1.903623
    start_datetime = datetime.datetime(2020, 7, 2, 14)
    max_duration_seconds = 3 * 60
    print(
        main.compute_isochrone(
            gtfs_folder, lat, lon, start_datetime, max_duration_seconds
        )
    )


@click.command()
@click.argument("gtfs_folder")
def server(gtfs_folder):
    import bottle
    from bottle import request, response
    import datetime

    app = bottle.Bottle()
    data = load.load_prepared_data(gtfs_folder)

    @app.route("/isochrone", method="GET")
    def isochrone():
        response.headers["Access-Control-Allow-Origin"] = "*"

        try:
            lat = float(request.query.get("lat"))
            lon = float(request.query.get("lon"))
            max_duration_seconds = int(request.query.get("duration"))
            date_str = request.query.get("start")
            start_datetime = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except (TypeError, ValueError):
            response.status = 400
            response.content_type = "application/json"
            return {
                "error": "invalid query string. Valid example: ?lat=47.9007&lon=1.9036&duration=60&start=2020-07-02T13:00:00",
                "recieved": request.query_string,
            }

        return main.compute_isochrone_with_data(
            data, lat, lon, start_datetime, max_duration_seconds
        )

    bottle.run(app=app, reloader=True, host="localhost", port=9090)


cli.add_command(prepare)
cli.add_command(demo)
cli.add_command(server)


if __name__ == "__main__":
    cli()
