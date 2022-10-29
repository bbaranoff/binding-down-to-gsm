#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Convert markdown files to ReStructuredText.

Converted files will be placed with the same folder structure into the
specified destination folder
"""

import argparse
import logging
import m2rr
from pathlib import Path
from sys import stdout


def parse_arguments() -> argparse.Namespace:
    """
    Parse CLI arguments.

    :raise      argparse.ArgumentError: Given argument unknown
    :returns:   argparse object
    :rtype:     argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description=("Convert markdown files to ReStructuredText. Place rst "
                     "file to the Sphinx documentation folder."),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # default arguments
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Output logger messages to stderr')
    parser.add_argument('-v',
                        default=0,
                        action='count',
                        dest='verbose',
                        help='Set level of verbosity')

    # specific arguments
    parser.add_argument('--destination',
                        type=str,
                        help='Path to Sphinx sources directory.')
    parser.add_argument('--in_file',
                        type=str,
                        action='append',
                        required=True,
                        help='Markdown files to convert to ReStructuredText')
    parser.add_argument('--dry_run',
                        action="store_true",
                        default=False,
                        help='Only dry run, no file creation')

    parsed_args = parser.parse_args()

    return parsed_args


def main():
    """Invoke all modules and do the work"""
    args = parse_arguments()

    custom_format = '[%(asctime)s] [%(levelname)-8s] [%(filename)-15s @'\
                    ' %(funcName)-15s:%(lineno)4s] %(message)s'

    # configure logging
    logging.basicConfig(level=logging.INFO,
                        format=custom_format,
                        stream=stdout)
    logger = logging.getLogger(__name__)

    if args.verbose:
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"][::-1]
        log_level = log_levels[min(len(log_levels) - 1, max(args.verbose, 0))]
        logger.setLevel(log_level)

    if not (args.verbose > 0 or args.debug is True):
        # '-d' is not specified or default verbose level is set
        logger.disabled = True

    destination_dir = Path(args.destination).resolve()

    here = Path().resolve()
    logger.debug('Current location: {}'.format(here))

    if not destination_dir.exists():
        logger.info('Destination folder does not yet exist')
        destination_dir.mkdir(parents=True, exist_ok=True)
        logger.info('Created destination folder')

    for file in args.in_file:
        infile = Path(file).resolve()
        logger.debug('Processing: {}'.format(infile))
        assert infile.exists

        relative_infile = infile.with_suffix('.rst').relative_to(here)
        outfile = destination_dir / relative_infile
        logger.debug('Outfile path: {}'.format(outfile))

        if outfile.exists():
            outfile.unlink()

        parsed_rst_file_content = m2rr.parse_from_file(infile)

        logger.debug("Saving {} to {}".format(infile, outfile))
        if not args.dry_run:
            if not outfile.parent.exists():
                outfile.parent.mkdir(parents=True, exist_ok=True)

            with open(outfile, 'w', encoding='utf-8') as f:
                f.write(parsed_rst_file_content)
            logger.info("Successfully saved {} to {}".format(infile, outfile))
        else:
            logger.info('Dry run mode, nothing saved to a file')


if __name__ == '__main__':
    main()
