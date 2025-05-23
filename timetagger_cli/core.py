import time
import datetime
import webbrowser

import requests

from .utils import (
    generate_uid,
    total_time,
    readable_time,
    readable_duration,
    open_with_os_default,
)
from .config import prepare_config_file, load_config


# %% lower level functions


def request(method, path, body=None):
    """Do an API request."""
    if body is not None:
        assert isinstance(body, (list, dict))

    config = load_config()
    url = config["api_url"].rstrip("/") + "/" + path.lstrip("/")
    token = config["api_token"].strip()
    ssl_verify = config["ssl_verify"]
    if not token:
        raise RuntimeError("api_token not set, run 'timetagger setup' first.")

    headers = {"authtoken": token}
    response = requests.request(
        method.upper(), url, json=body, headers=headers, verify=ssl_verify
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"{response.status_code} - {response.text}")


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


def app(args):
    """Open the TimeTagger app in your default browser."""
    config = load_config()
    parts = config["api_url"].rstrip("/").split("/")
    url = "/".join(parts[:-2]) + "/app/"
    print(f"Opening {url}")
    webbrowser.open(url)


def setup(args=None):
    """Edit the API URL and token by opening the config file in your default editor."""
    filename = prepare_config_file()
    print("Config file: " + filename)
    print("Will now (try to) open the config file. Just edit and save the file.")
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


def start(args):
    """Start timer with the given description. Use '#' to create tags."""
    description = args.description
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


def add(args):
    """Add already finished task."""
    description = args.description

    date = datetime.date.today()
    if args.date:
        date = args.date

    start = datetime.datetime.combine(date, args.start_time)
    end = datetime.datetime.combine(date, args.end_time)

    # Create new record
    r = {
        "key": generate_uid(),
        "t1": int(start.timestamp()),
        "t2": int(end.timestamp()),
        "mt": time.time(),
        "st": 0,
        "ds": str(description),
    }

    # Push
    request("PUT", "records", [r])

    print()
    print_records([r])


def stop(args=None):
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


def resume(args):
    """Start a timer with the same description as the selected record."""
    selected = args.selected

    now = int(time.time())
    d = datetime.datetime.fromtimestamp(now)

    today = datetime.datetime(d.year, d.month, d.day)
    tomorrow = today + datetime.timedelta(days=1)
    last_week = today - datetime.timedelta(days=7)

    t1 = int(last_week.timestamp())
    t2 = int(tomorrow.timestamp())

    # Get records from the last week
    records = request("GET", f"records?timerange={t1}-{t2}")["records"]

    # Remove HIDDEN records
    filtered_records = [r for r in records if "HIDDEN" not in r["ds"]]

    if len(filtered_records) == 0:
        print("No records within the last week.")
        return

    # Sort records by time
    filtered_records.sort(key=lambda r: r["t2"])

    # Get last 10 records
    if len(filtered_records) > 10:
        filtered_records = filtered_records[-10:]

    if selected is None:
        print("Which record would you like to resume? [1]")
        for i in range(len(filtered_records)):
            number_string = f"[{len(filtered_records)-i}]"
            print(f"{number_string.rjust(4)} {filtered_records[i]['ds']}")

        try:
            selected = int(input("> ") or "1")
        except KeyboardInterrupt:
            return
    else:
        try:
            selected = int(selected)
        except ValueError:
            print("Error in index. Try: timetagger resume")
            return

    selected_record = filtered_records[-selected]

    # Get running records, to stop them
    running_records = get_running_records()
    for r in running_records:
        if r.get("ds", "") == selected_record["ds"]:
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
        "ds": selected_record["ds"],
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


def status(args=None):
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
    total_week = total_time(week_records, last_monday, next_monday)
    total_day = total_time(day_records, today, tomorrow)

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


def show(args):
    """List records of the requested time frame."""
    if args.end:
        end = datetime.datetime.combine(args.end, datetime.time.max).replace(
            microsecond=0
        )
    else:
        end = datetime.datetime.now()
    if args.start:
        start = datetime.datetime.combine(args.start, datetime.time.min)
        if not args.end and args.days:
            end = start + datetime.timedelta(days=args.days - 1)
            end = end.replace(hour=23, minute=59, second=59, microsecond=0)
    else:
        days = 0
        if args.days:
            days = args.days - 1
        start = end - datetime.timedelta(days=days)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    # Collect records
    ob = request(
        "GET", f"records?timerange={int(start.timestamp())}-{int(end.timestamp())}"
    )
    records = [r for r in ob["records"] if not r.get("ds", "").startswith("HIDDEN")]
    total = total_time(records, start, end)
    days = (end - start).days + 1
    print(f"Start:       {start}")
    print(f"End:         {end}")
    print(f"Time Period: {days} days")
    print(f"Total Hours: {readable_duration(total)}")
    print()

    print("Records:")
    print_records(records)


def diagnose(args):
    """Load all records and perform diagnostics to detect errors. Use '--fix' to fix errors."""

    def show_record(prefix, r):
        dt1 = datetime.datetime.fromtimestamp(r["t1"])
        dt2 = datetime.datetime.fromtimestamp(r["t2"])
        print(f"{prefix}: {r['key']}, from {dt1} to {dt2}")

    # Get records and sort by t1
    ob = request("GET", f"updates?since=0")
    records = ob["records"]
    records = sorted(records, key=lambda r: r["t1"])

    # Prep
    early_date = datetime.datetime(2000, 1, 1)
    late_date = datetime.datetime.now() + datetime.timedelta(days=1)
    very_late_date = datetime.datetime.now() + datetime.timedelta(days=365 * 2)

    # Investigate records
    suspicious_records = []
    wrong_records = []
    for r in records:
        t1, t2 = r["t1"], r["t2"]
        if t1 < 0 or t2 < 0:
            wrong_records.append(("negative timestamp", r))
        elif t1 > t2:
            wrong_records.append(("t1 larger than t2", r))
        elif datetime.datetime.fromtimestamp(r["t2"]) > very_late_date:
            wrong_records.append(("far future", r))
        elif datetime.datetime.fromtimestamp(r["t1"]) < early_date:
            suspicious_records.append(("early", r))
        elif datetime.datetime.fromtimestamp(r["t2"]) > late_date:
            suspicious_records.append(("future", r))
        elif t2 - t1 > 86400 * 2:
            suspicious_records.append(("duration over two days", r))
        elif t1 == t2 and abs(time.time() - t1) > 86400 * 2:
            ndays = round(abs(time.time() - t1) / 86400)
            suspicious_records.append((f"running for about {ndays} days", r))

    suspicious_records.sort()
    wrong_records.sort()

    print(f"Checked {len(records)} records")

    # Show records
    if wrong_records:
        print("Errored records:")
        for prefix, r in wrong_records:
            show_record(prefix + ":", r)
    if suspicious_records:
        print("Suspicious records:")
        for prefix, r in suspicious_records:
            show_record(prefix + ":", r)

    if not wrong_records and not suspicious_records:
        print("All looks good")

    # Fixing wrong records
    if args.fix:
        for prefix, r in wrong_records:
            if "t1 larger than t2 " in prefix:
                r["t1"], r["t2"] = r["t2"], r["t1"]
                request("PUT", "records", [r])
            else:
                dt = abs(r["t1"] - r["t2"])
                if dt > 86400 * 1.2:
                    dt = 3600
                r["t1"] = int(time.time())
                r["t2"] = r["t1"] + dt
                request("PUT", "records", [r])
            print(f"Updated {r['key']}")
