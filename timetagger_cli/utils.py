import os
import sys
import secrets
import datetime
import subprocess


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


def open_with_os_default(path):
    """Open the given filename with the OS default application."""
    if sys.platform.startswith("darwin"):
        subprocess.call(("open", path))
    elif sys.platform.startswith("win"):
        if " " in path:  # http://stackoverflow.com/a/72796/2271927
            subprocess.call(("start", "", path), shell=True)
        else:
            subprocess.call(("start", path), shell=True)
    elif sys.platform.startswith("linux"):
        # xdg-open is available on all Freedesktop.org compliant distros
        # http://superuser.com/questions/38984/linux-equivalent-command-for-open-command-on-mac-windows
        try:
            subprocess.call(("xdg-open", path))
        except FileNotFoundError:
            subprocess.call((os.getenv("EDITOR", "vi"), path))
    else:
        raise RuntimeError(f"Don't know how to open {path}")


def user_config_dir(appname=None, roaming=False):
    """Get the directory to store app config files."""
    if sys.platform.startswith("win"):
        path1, path2 = os.getenv("LOCALAPPDATA"), os.getenv("APPDATA")
        path = (path2 or path1) if roaming else (path1 or path2)
        path = os.path.normpath(path)
    elif sys.platform.startswith("darwin"):
        path = os.path.expanduser("~/Library/Preferences/")
    else:
        path = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    if not (path and os.path.isdir(path)):
        path = os.path.expanduser("~")
    if appname:
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
    return path


def total_time(records, start, end):
    total = 0
    t_start = start.timestamp()
    t_end = end.timestamp()
    t_now = datetime.datetime.now().timestamp()
    for r in records:
        t1 = r["t1"]
        t2 = r["t2"] if r["t1"] != r["t2"] else t_now
        total += min(t_end, t2) - max(t_start, t1)
    return total


def readable_time(timestamp):
    """Turn a timestamp into a readable string."""
    value = datetime.datetime.fromtimestamp(timestamp)
    return f"{value:%Y-%m-%d %H:%M}"


def readable_duration(nsecs):
    """Turn a duration in seconds into a reabable string."""
    m = round(nsecs / 60)
    # return f"{m // 60:.0f}h{m % 60:.0f}m"
    return f"{m // 60:.0f}:{m % 60:02.0f}"
