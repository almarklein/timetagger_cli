import sys
import io
from contextlib import redirect_stdout
from argparse import ArgumentError

import timetagger_cli
from timetagger_cli import __main__
from pytest import raises
from _common import run_tests


def _raise_RuntimeError():
    raise RuntimeError()

def run_main(argv = None):
    capture = io.StringIO()
    with redirect_stdout(capture):
        try:
            __main__.main(argv)
        except SystemExit as exit:
            if exit.code != 0:
                raise
    return capture.getvalue()


def test_cli():

    # Empty args is help
    text = run_main([])
    for x in ["timetagger", "CLI", "version", "setup", "status", "start", "stop"]:
        assert x in text

    # Other common ways to get help
    for arg in ["-h", "--help"]:
        text_help = run_main([arg])
        assert text_help == text

    # No args uses sys.argv
    sys.argv = ["", "--version"]
    text_version = run_main()
    assert timetagger_cli.__version__ in text_version

    # Invalid command
    with raises(BaseException):
        run_main(["notavalidcommand"])

    # Error in command
    timetagger_cli.core.request = lambda method, path, body=None: _raise_RuntimeError()
    with raises(BaseException):  # RunTimeError is turned into SystemExit
        run_main(["status"])

    # Other errors fall through
    with raises(ArgumentError):
        run_main(["help", "help_func_has_no_args"])

    # Run one command through to a function
    response = {"records": []}
    timetagger_cli.core.request = lambda method, path, body=None: response
    run_main(["status"])


if __name__ == "__main__":
    run_tests(globals())
