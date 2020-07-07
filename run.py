import click

from gtfs_isochrone import prepare as _prepare


@click.group()
def cli():
    pass


@click.command()
@click.argument("gtfs_folder")
def prepare(gtfs_folder):
    _prepare.prepare_data_in_gtfs_folder(gtfs_folder)


cli.add_command(prepare)


if __name__ == "__main__":
    cli()
