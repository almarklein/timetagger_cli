"""
The CLI logic.
"""

import argparse
import datetime
import sys

import timetagger_cli


# %% Some additional commands defined here


def version(args):
    """Print version."""
    print(f"timetagger_cli v{timetagger_cli.__version__}")


# %%


def create_command_parser(subparsers, func):
    parser = subparsers.add_parser(func.__name__, help=func.__doc__.strip())
    parser.set_defaults(func=func)
    return parser


def setup_parser():
    """setup argument parsing"""
    argparser = argparse.ArgumentParser(
        prog="timetagger", description=timetagger_cli.__doc__.strip()
    )
    # argparser.add_argument(
    #     "-d", "--debug", action="store_true", help="enable debug output"
    # )

    subparsers = argparser.add_subparsers()
    create_command_parser(subparsers, version)
    create_command_parser(subparsers, timetagger_cli.setup)
    create_command_parser(subparsers, timetagger_cli.app)
    create_command_parser(subparsers, timetagger_cli.status)
    start = create_command_parser(subparsers, timetagger_cli.start)
    start.add_argument("description", help="Description. Use '#' to create tags.")
    create_command_parser(subparsers, timetagger_cli.stop)
    resume = create_command_parser(subparsers, timetagger_cli.resume)
    resume.add_argument(
        "selected",
        type=int,
        nargs="?",
        help="Number of the record would you like to resume.",
    )
    show = create_command_parser(subparsers, timetagger_cli.show)
    show.add_argument(
        "--days", type=int, help="Show records of the last <DAYS> days. Default: 1"
    )
    show.add_argument(
        "--start",
        type=datetime.date.fromisoformat,
        help="Start date in ISO-format (YYYY-MM-DD)",
    )
    show.add_argument(
        "--end",
        type=datetime.date.fromisoformat,
        help="Start date in ISO-format (YYYY-MM-DD)",
    )

    return argparser


def main():
    assert sys.version_info.major == 3, "This script needs to run with Python 3."

    parser = setup_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
