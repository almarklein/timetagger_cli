"""
The CLI logic.
"""

import sys

import timetagger_cli


# %% Some additional commands defined here


def version():
    """Print version."""
    print(f"timetagger_cli v{timetagger_cli.__version__}")


def help():
    """Show this help message and exit."""
    print(docs)


# %%


def _make_func_dict_and_docs(*args):
    funcs = {}
    description = "usage: timetagger command [arguments]"
    description += "\n\n" + timetagger_cli.__doc__.strip() + "\n\n"

    for func in args:
        if isinstance(func, str):
            description += func + "\n\n"  # header
        else:
            funcs[func.__name__] = func
            funcs[func.__name__.replace("_", "-")] = func
            co = func.__code__
            arg_names = " ".join(x.upper() for x in co.co_varnames[: co.co_argcount])
            description += "    " + func.__name__ + " " + arg_names + "\n"
            doc = "    " + func.__doc__.strip()
            description += doc.replace("    ", "        ") + "\n"

    return funcs, description


funcs, docs = _make_func_dict_and_docs(
    "Available commands:",
    version,
    help,
    timetagger_cli.app,
    timetagger_cli.setup,
    timetagger_cli.status,
    timetagger_cli.start,
    timetagger_cli.stop,
)


def main(argv=None):

    assert sys.version_info.major == 3, "This script needs to run with Python 3."

    # Get CLI args
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        argv = ["help"]
    if argv[0] in ["-h", "--help"]:
        argv = ["help"]

    # Get function to call
    if argv[0] in funcs:
        func = funcs[argv[0]]
    else:
        sys.exit(f"Invalid use of TimeTagger command: {argv}")

    # Call it
    try:
        func(*argv[1:])
    except RuntimeError as err:
        # Inside the functions, RunTimeError is raised in situations
        # that can sufficiently be described with the error message.
        # Other exceptions fall through, and their traceback is
        # printed.
        sys.exit(str(err))


if __name__ == "__main__":  # pragma: no cover
    main()
