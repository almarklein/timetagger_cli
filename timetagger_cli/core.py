import time
import datetime
import webbrowser

import requests

from .utils import generate_uid, readable_time, readable_duration, open_with_os_default
from .config import prepare_config_file, load_config


# %% lower level functions


def request(method, path, body=None):
    """Do an API request."""
    if body is not None:
        assert isinstance(body, (list, dict))

    config = load_config()
    url = config["api_url"].rstrip("/") + "/" + path.lstrip("/")
    token = config["api_token"].strip()
    if not token:
        raise RuntimeError("api_token not set, run 'timetagger setup' first.")

    headers = {"authtoken": token}
    response = requests.request(method.upper(), url, json=body, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"{response.status_code} - { response.text}")


def print_records(records):
    """Pretty-print a list of records."""
    # Sort
    records = sorted(records, key=lambda r: r["t1"])

    # Write header
    print("Started".rjust(17), "Stopped".rjust(17), "Duration".rjust(9), " Description")

    # Write each record
    for r in records:
        started = readable_time(r["t1"])
        if r["t1"] == r["t2"]:
            stopped = "-"
            duration = readable_duration(time.time() - r["t1"])
        else:
            stopped = readable_time(r["t2"])
            duration = readable_duration(r["t2"] - r["t1"])
            if stopped.split(" ")[0] == started.split(" ")[0]:
                stopped = stopped.split(" ", 1)[1]
        description = " " + r.get("ds", "")
        print(started.rjust(17), stopped.rjust(17), duration.rjust(9), description)


def get_running_records():
    now = int(time.time())
    t1 = now - 35 * 60
    t2 = now + 60
    ob = request("GET", f"records?timerange={t1}-{t2}")
    return [r for r in ob["records"] if r["t1"] == r["t2"]]


# %% The commands


def app():
    """Open the TimeTagger app in your default browser."""
    config = load_config()
    parts = config["api_url"].rstrip("/").split("/")
    url = "/".join(parts[:-2]) + "/app/"
    print(f"Opening {url}")
    webbrowser.open(url)


def setup():
    """Edit the API URL and token by opening the config file in your default editor."""
    filename = prepare_config_file()
    print("Config file: " + filename)
    print("Will now (try to) open the config file. Just edit and safe the file.")
    open_with_os_default(filename)


# Alternative to setup() ...
# def init():
#     """ Set the server address and API token.
#     """
#     # Get url
#     print("What API endpoint do you wish to use? Examples:")
#     print("- use the default 'https://timetagger.app/api/v2/' to connect with timetagger.app")
#     print("- use for example 'http://localhost/timetagger/api/v2/' to connect to a local server")
#     print()
#     url = input("Provide URL (or hit enter to use the default): ").strip()
#     if not url:
#         url = "https://timetagger.app/api/v2/"
#     if not url.startswith("")


def start(description):
    """Start timer with the given description. Use '#' to create tags."""
    now = int(time.time())

    # Get running records, to stop them
    running_records = get_running_records()
    for r in running_records:
        if r.get("ds", "") == description:
            print("Timer with this description is already running.")
            print()
            print_records([r])
            return
        r["t2"] = now

    # Create new record
    r = {
        "key": generate_uid(),
        "t1": now,
        "t2": now,
        "mt": time.time(),
        "st": 0,
        "ds": str(description),
    }

    # Push
    records = running_records + [r]
    request("PUT", "records", records)

    # Report
    if not running_records:
        print("Timer started ...")
    else:
        print(f"Timer started ... and stopped {len(running_records)} running records.")

    print()
    print_records(records)


def stop():
    """Stop any running timers."""
    now = int(time.time())

    # Get and stop any running records
    running_records = get_running_records()
    for r in running_records:
        r["t2"] = now

    # Push if necessary, and report
    if not running_records:
        print("No running records.")
    else:
        print("Stopping running records.")
        request("PUT", "records", running_records)
        print()
        print_records(running_records)


def status():
    """Get an overview of today and this week. The exact content may change."""

    now = int(time.time())
    d = datetime.datetime.fromtimestamp(now)

    # Get important dates
    today = datetime.datetime(d.year, d.month, d.day)
    tomorrow = today + datetime.timedelta(1)
    last_monday = today - datetime.timedelta(today.weekday())
    next_monday = last_monday + datetime.timedelta(7)

    # Convert to timestamps
    t_week1 = int(last_monday.timestamp())
    t_week2 = int(next_monday.timestamp())
    t_day1 = int(today.timestamp())
    t_day2 = int(tomorrow.timestamp())

    # Collect records
    ob = request("GET", f"records?timerange={t_week1}-{t_week2}")
    week_records = [
        r for r in ob["records"] if not r.get("ds", "").startswith("HIDDEN")
    ]
    day_records = [
        r
        for r in week_records
        if r["t1"] < t_day2 and (r["t1"] == r["t2"] or r["t2"] > t_day1)
    ]
    running_records = [r for r in week_records if r["t1"] == r["t2"]]

    # Calculate totals
    total_week = 0
    total_day = 0
    for r in week_records:
        t1 = r["t1"]
        t2 = r["t2"] if r["t1"] != r["t2"] else now
        total_week += min(t_week2, t2) - max(t_week1, t1)
    for r in day_records:
        t1 = r["t1"]
        t2 = r["t2"] if r["t1"] != r["t2"] else now
        total_day += min(t_day2, t2) - max(t_day1, t1)

    # Report
    print()
    print(f"Hours clocked this week: {readable_duration(total_week)}")
    print(f"Hours clocked today: {readable_duration(total_day)}")
    if not running_records:
        print("Running: N/A")
    elif len(running_records) == 1:
        r = running_records[0]
        duration = now - running_records[0]["t1"]
        print(f"Running: {readable_duration(duration)} - {r.get('ds')}")
    else:
        print(f"There are {len(running_records)} running timers.")
    print()
    print("Todays records:")
    print_records(day_records)
