"""
The CLI logic.
"""

import sys
import argparse

import dateparser
import timetagger_cli


# %%


def date_from_natural_language(string):
    """convert string to date object"""
    return dateparser.parse(string).date()


def time_from_natural_language(string):
    """convert string to time object"""
    return dateparser.parse(string).time()


def create_command_parser(subparsers, func):
    """helper function to create a argparse subparser"""
    parser = subparsers.add_parser(func.__name__, help=func.__doc__.strip())
    parser.set_defaults(func=func)
    return parser


def setup_parser():
    """setup argument parsing"""
    argparser = argparse.ArgumentParser(
        prog="timetagger",
        description=timetagger_cli.__doc__.strip(),
    )

    argparser.add_argument(
        "--version",
        action="version",
        version=f"timetagger_cli v{timetagger_cli.__version__}",
    )

    subparsers = argparser.add_subparsers()

    create_command_parser(subparsers, timetagger_cli.setup)

    create_command_parser(subparsers, timetagger_cli.app)

    create_command_parser(subparsers, timetagger_cli.status)

    show = create_command_parser(subparsers, timetagger_cli.show)
    show.add_argument(
        "--days", type=int, help="Show records of the last <DAYS> days. Default: 1"
    )
    show.add_argument(
        "--start",
        type=date_from_natural_language,
        help="Start date in ISO-format (YYYY-MM-DD).",
    )
    show.add_argument(
        "--end",
        type=date_from_natural_language,
        help="Start date in ISO-format (YYYY-MM-DD).",
    )

    diagnose = create_command_parser(subparsers, timetagger_cli.diagnose)
    diagnose.add_argument("--fix", action="store_true", help="fix error records")

    start = create_command_parser(subparsers, timetagger_cli.start)
    start.add_argument("description", help="Description. Use '#' to create tags.")

    create_command_parser(subparsers, timetagger_cli.stop)

    add = create_command_parser(subparsers, timetagger_cli.add)
    add.add_argument(
        "--date",
        type=date_from_natural_language,
        help="Date of the entry in ISO-format (YYYY-MM-DD). Default: today.",
    )
    add.add_argument(
        "start_time",
        type=time_from_natural_language,
        help="Start time of the task in ISO-format (hh:mm or  hhmm).",
    )
    add.add_argument(
        "end_time",
        type=time_from_natural_language,
        help="End time of the task in ISO-format (hh:mm or hhmm).",
    )
    add.add_argument("description", help="Description. Use '#' to create tags.")

    resume = create_command_parser(subparsers, timetagger_cli.resume)
    resume.add_argument(
        "selected",
        type=int,
        nargs="?",
        help="Number of the record would you like to resume.",
    )

    return argparser


def main(argv=None):
    assert sys.version_info.major == 3, "This script needs to run with Python 3."

    parser = setup_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        try:
            args.func(args)
        except RuntimeError as err:
            msg = err.args[0] if err.args else "''"
            sys.exit(f"Timetagger runtime error: {msg}")
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
