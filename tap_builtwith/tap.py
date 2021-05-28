"""builtwith tap."""
# -*- coding: utf-8 -*-
import logging
from argparse import Namespace

import pkg_resources
from singer import get_logger, utils
from singer.catalog import Catalog

from tap_builtwith.builtwith import Builtwith
from tap_builtwith.discover import discover
from tap_builtwith.sync import sync

VERSION: str = pkg_resources.get_distribution('tap-builtwith').version
LOGGER: logging.RootLogger = get_logger()
REQUIRED_CONFIG_KEYS: tuple = (
    'api_key',
    'start_date',
)


@utils.handle_top_exception(LOGGER)
def main() -> None:
    """Run tap."""
    # Parse command line arguments
    args: Namespace = utils.parse_args(REQUIRED_CONFIG_KEYS)

    LOGGER.info(f'>>> Running tap-builtwith v{VERSION}')

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog: Catalog = discover()
        catalog.dump()
        return

    # Otherwise run in sync mode
    if args.catalog:
        # Load command line catalog
        catalog = args.catalog
    else:
        # Loadt the  catalog
        catalog = discover()

    # Initialize Builtwith client
    builtwith: Builtwith = Builtwith(
        args.config['api_key'],
        args.config['technologies'],
    )

    sync(builtwith, args.state, catalog, args.config['start_date'])


if __name__ == '__main__':
    main()
