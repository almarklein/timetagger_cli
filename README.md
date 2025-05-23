[![CI](https://github.com/almarklein/timetagger_cli/workflows/CI/badge.svg)](https://github.com/almarklein/timetagger_cli/actions)

# timetagger_cli

Track your time from the command-line


## Introduction

This is a command line interface (CLI) that connects to a
[TimeTagger](https://github.com/almarklein/timetagger) server.
This can be the server at https://timetagger.app, or a self-hosted server.

The idea is to provide a quick way to track time for devs who are already using
a terminal.


## Installation

The TimeTagger CLI requires Python 3.9 or higher. Install with your favorite Python package manager, e.g.:
```
$ pipx install timetagger_cli
```
or
```
$ pip install timetagger_cli
```

After installation, you should be able to use the `timetagger`command.

Start by running `timetagger setup` to setup the API's url and authentication token.


## Docs

Run `timetagger` without arguments to get the list of available subcommands:

```
$ timetagger
usage: timetagger [-h] [--version] {setup,app,status,show,start,stop,add,resume} ...

Track your time from the command-line, a CLI for https://timetagger.app.

positional arguments:
  {setup,app,status,show,start,stop,add,resume}
    setup               Edit the API URL and token by opening the config file in your default editor.
    app                 Open the TimeTagger app in your default browser.
    status              Get an overview of today and this week. The exact content may change.
    show                List records of the requested time frame.
    start               Start timer with the given description. Use '#' to create tags.
    stop                Stop any running timers.
    add                 Add already finished task.
    resume              Start a timer with the same description as the selected record.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```


## Example

```
$ timetagger status
Hours clocked this week: 11:42
Hours clocked today: 7:00
Running: 0:01 - #timeapp #oss more cli

Todays records:
          Started           Stopped  Duration  Description
 2021-03-23 09:05             09:42      0:37  #oss #vispy prep
 2021-03-23 09:42             12:12      2:30  #timeapp #oss cli
 2021-03-23 13:06             14:00      0:53  #timeapp #oss cli
 2021-03-23 14:00             14:58      0:58  #oss #vispy #meeting
 2021-03-23 15:24             17:13      1:49  #timeapp #oss cli
 2021-03-23 17:13                 -      0:12  #timeapp #oss more cli
```


## License

MIT


## Developers

Additional developer dependencies:
```
pip install invoke black flake8 pytest
```

* `invoke -l` to see available invoke tasks
* `invoke clean` to remove temporary files
* `invoke format` to autoformat the code (using black)
* `invoke lint` to detect linting errors (using flake8)
* `invoke tests` to run tests (using pytest)
