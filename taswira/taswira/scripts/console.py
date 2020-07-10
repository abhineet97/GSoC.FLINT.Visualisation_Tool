"""Taswira's CLI"""
import argparse
import os
import tempfile

import terracotta as tc
from terracotta.server.app import app as tc_app

from ..app import get_app
from . import arg_types, update_config
from .helpers import get_free_port
from .ingestion import ingest


def start_servers(dbpath, port):
    """Load given DB and start a Terracotta and Dash server.

    Args:
        dbpath: Path to a Terracota-generated DB.
        port: Port number for Terracotta server.
    """
    tc.update_settings(DRIVER_PATH=dbpath, DRIVER_PROVIDER='sqlite')
    app = get_app(tc_app)
    app.run_server(port=port, threaded=False, debug='DEBUG' in os.environ)


def console():
    """The command-line interface for Taswira"""
    parser = argparse.ArgumentParser(
        description="Interactive visualization tool for GCBM")
    parser.add_argument(
        "config",
        type=arg_types.indicator_file,
        help="Path to JSON config file",
    )
    parser.add_argument("spatial_results",
                        type=arg_types.spatial_results,
                        help="Path to GCBM spatial output directory")
    parser.add_argument("db_results",
                        type=arg_types.db_results,
                        help="Path to compiled GCBM results database")
    args = parser.parse_args()

    update_config(args.config)

    with tempfile.TemporaryDirectory() as tmpdirname:
        db = ingest(args.spatial_results, args.db_results, tmpdirname)  # pylint: disable=invalid-name
        port = get_free_port()
        start_servers(db, port)