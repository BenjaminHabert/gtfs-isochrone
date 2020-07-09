import click

from gtfs_isochrone import prepare as _prepare, main


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
    from server import app

    bottle.run(app=app, reloader=True, host="localhost", port=9090)


cli.add_command(prepare)
cli.add_command(demo)
cli.add_command(server)


if __name__ == "__main__":
    cli()
