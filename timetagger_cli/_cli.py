import os
import sys
import time
import secrets

import requests


DIRNAME = os.path.dirname(os.path.abspath(__file__))


def generate_uid():
    """Generate a unique id in the form of an 8-char string. The value is
    used to uniquely identify the record of one user. Assuming a user
    who has been creating 100 records a day, for 20 years (about 1M records),
    the chance of a collision for a new record is about 1 in 50 milion.
    """
    n = 8
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # with len(chars) 52 => 52**8 => 53459728531456 possibilities
    return "".join([secrets.choice(chars) for i in range(n)])


def start(description):
    """Start timer."""
    now = time.time()
    r = {
        "key": generate_uid(),
        "t1": now,
        "t2": now,
        "mt": now,
        "st": 0,
        "ds": str(description),
    }

    response = requests.put("http://localhost/api/v2/records", json=[r])
    if response.status_code == 200:
        print("Timer is running!")
    else:
        print("Fail:", response.reason)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if argv and argv[0].startswith(DIRNAME):
        argv = argv[1:]
    else:
        argv = argv[:]
    if not argv:
        argv = ["help"]

    if argv[0] == "start":
        start(*argv[1:])
    else:
        print("not implemented!")
