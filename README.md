[![CI](https://github.com/almarklein/timetagger_cli/workflows/CI/badge.svg)](https://github.com/almarklein/timetagger_cli/actions)

# timetagger_cli

Track your time from the command-line


```bash
$ timetagger
usage: timetagger command [arguments]

Track your time from the command-line, a CLI for https://timetagger.app.

Available commands:

    version
        Print version.
    help
        Show this help message and exit.
    app
        Open the TimeTagger app in your default browser.
    setup
        Edit the API URL and token by opening the config file in your default editor.
    status
        Get an overview of today and this week. The exact content may change.
    start DESCRIPTION
        Start timer with the given description. Use '#' to create tags.
    stop
        Stop any running timers.


$ timetagger status

Hours clocked this week: 11:32
Hours clocked today: 6:50
There are 2 running timers.

Todays records:
          Started           Stopped  Duration  Description
 2021-03-23 09:05             09:42      0:37  #oss #vispy prep
 2021-03-23 09:42             12:12      2:30  #timeapp #oss cli
 2021-03-23 13:06             14:00      0:53  #timeapp #oss cli
 2021-03-23 14:00             14:58      0:58  #oss #vispy #meeting
 2021-03-23 15:23             15:23      0:00  HIDDEN #oss #vispy #meeting
 2021-03-23 15:24                 -      1:51  #timeapp #oss cli
 2021-03-23 17:13                 -      0:01  #timeapp #oss more cli
 ```
