"""Root python script for Mad-Dash REST API server interface."""

import asyncio
import logging
from urllib.parse import quote_plus

from motor.motor_tornado import MotorClient  # type: ignore
from rest_tools.server import RestHandlerSetup, RestServer, from_environment  # type: ignore

from .config import EXPECTED_CONFIG
from .routes import (CollectionsHistogramsHandler, CollectionsHistogramsNamesHandler,
                     CollectionsNamesHandler, DatabasesNamesHandler, FileNamesHandler,
                     HistogramHandler, MadDashMotorClient, MainHandler)


def start(debug: bool = False) -> RestServer:
    """Start a Mad Dash REST service."""
    config = from_environment(EXPECTED_CONFIG)

    for name in config:
        logging.info(f"{name} = {config[name]}")

    args = RestHandlerSetup({
        'auth': {
            'secret': config['MAD_DASH_AUTH_SECRET'],
            'issuer': config['MAD_DASH_AUTH_ISSUER'],
            'algorithm': config['MAD_DASH_AUTH_ALGORITHM'],
        },
        'debug': debug
    })

    # configure access to MongoDB as a backing store
    mongo_user = quote_plus(config["MAD_DASH_MONGODB_AUTH_USER"])
    mongo_pass = quote_plus(config["MAD_DASH_MONGODB_AUTH_PASS"])
    mongo_host = config["MAD_DASH_MONGODB_HOST"]
    mongo_port = int(config["MAD_DASH_MONGODB_PORT"])
    mongodb_url = f"mongodb://{mongo_host}:{mongo_port}"
    if mongo_user and mongo_pass:
        mongodb_url = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"

    # ensure indexes
    md_mc = MadDashMotorClient(MotorClient(mongodb_url))
    asyncio.get_event_loop().run_until_complete(md_mc.ensure_all_databases_indexes())

    args['motor_client'] = MotorClient(mongodb_url)

    # configure REST routes
    server = RestServer(debug=debug)
    server.add_route(r'/$',
                     MainHandler, args)
    server.add_route(r'/databases/names$',
                     DatabasesNamesHandler, args)  # get database names
    server.add_route(r'/collections/names$',
                     CollectionsNamesHandler, args)  # get collection names
    server.add_route(r'/collections/histograms/names$',
                     CollectionsHistogramsNamesHandler, args)  # get all histogram names in collection
    server.add_route(r'/collections/histograms$',
                     CollectionsHistogramsHandler, args)  # get all histogram objects in collection
    server.add_route(r'/histogram$',
                     HistogramHandler, args)  # get histogram object
    server.add_route(r'/files/names$',
                     FileNamesHandler, args)  # get file names

    server.startup(address=config['MAD_DASH_REST_HOST'], port=int(config['MAD_DASH_REST_PORT']))
    return server


def main() -> None:
    """Configure logging and start a Mad Dash DB service."""
    logging.basicConfig(level=logging.DEBUG)
    start(debug=True)
    loop = asyncio.get_event_loop()
    loop.run_forever()


if __name__ == '__main__':
    main()
