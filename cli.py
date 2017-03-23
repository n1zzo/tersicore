#!/usr/bin/env python3
import click
from tersicore import api
from tersicore.mediascanner import scan_media


@click.group()
def cli():
    pass


@cli.command('scan')
def scan():
    scan_media()


@cli.command('rest')
@click.option('--debug', is_flag=True)
def rest(debug):
    api.rest(debug=debug)


if __name__ == '__main__':
    cli()
