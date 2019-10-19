#!/usr/bin/python

from json import dumps
from sys import exit, stderr
from requests import session
from argparse import ArgumentParser


def start():
    a = ArgumentParser(description="Scorebot Events Creator")
    a.add_argument(
        "-s",
        "--scorebot",
        dest="scorebot",
        metavar="scorebot",
        required=True,
        type=str,
        help="Scorebot URL",
    )
    a.add_argument(
        "-u",
        "--token",
        dest="token",
        metavar="uuid",
        required=True,
        type=str,
        help="Scorebot Access Token UUID",
    )
    a.add_argument(
        "-g",
        "--game",
        dest="game",
        metavar="game",
        required=True,
        type=int,
        help="The Game ID to Show the Event on",
    )

    a.add_argument(
        "-t",
        "--timeout",
        dest="timeout",
        metavar="timeout",
        required=True,
        type=int,
        help="The Time (in seconds) to Display the Event",
    )

    a.add_argument(
        "-m",
        "--message",
        dest="message",
        metavar="message",
        required=False,
        type=str,
        help="Message to Display",
    )
    a.add_argument(
        "-c",
        "--command",
        dest="command",
        action="store_true",
        required=False,
        help="Message Display as Command",
    )
    a.add_argument(
        "--response",
        dest="response",
        metavar="response",
        required=False,
        type=str,
        help="Message Command Response (implies --command)",
    )

    a.add_argument(
        "--title",
        dest="title",
        metavar="title",
        required=False,
        type=str,
        help="Window Popup Title",
    )
    a.add_argument(
        "--fullscreen",
        dest="fullscreen",
        action="store_true",
        help="Window Popup is Fullscreen",
    )

    a.add_argument(
        "-v",
        "--video",
        dest="video",
        metavar="video",
        required=False,
        type=str,
        help="Youtube Video ID to Use",
    )
    a.add_argument(
        "--start",
        dest="start",
        metavar="start",
        required=False,
        type=int,
        help="The Time (in seconds) to Start the video at",
    )

    a.add_argument(
        "-d",
        "--content",
        dest="content",
        metavar="html",
        required=False,
        type=str,
        help="Window Content to Use. (Empty to use file)",
    )

    a.add_argument(
        "-e",
        "--effect",
        dest="effect",
        metavar="effect",
        required=False,
        type=str,
        help="Effect string to use. (Empty to use file)",
    )

    a.add_argument(
        "-f",
        "--file",
        dest="file",
        metavar="path",
        required=False,
        type=str,
        help="File to Read Window/Effect Content From",
    )
    return check(a.parse_args())


def check(args):
    if (
        args.video is None
        and args.effect is None
        and args.message is None
        and args.content is None
    ):
        print(
            "One of the following values must be provided (content, event, message or video)!",
            file=stderr,
        )
        exit(1)
    if args.content is not None:
        if len(args.content) > 0:
            return (
                {
                    "type": 1,
                    "timeout": args.timeout,
                    "data": {
                        "text": args.content,
                        "title": args.title,
                        "fullscreen": str(args.fullscreen),
                    },
                },
                args.game,
                args.scorebot,
                args.token,
            )
        if args.file is not None:
            try:
                d = open(args.file, "r")
                data = d.read()
                d.close()
            except OSError as err:
                print('Could not read file "%s"! (%s)' % (args.file, err))
                exit(1)
            return (
                {
                    "type": 1,
                    "timeout": args.timeout,
                    "data": {
                        "text": data,
                        "title": args.title,
                        "fullscreen": str(args.fullscreen),
                    },
                },
                args.game,
                args.scorebot,
                args.token,
            )
    if args.message is not None:
        command = "true" if args.command or args.response else ""
        return (
            {
                "type": 0,
                "timeout": args.timeout,
                "data": {
                    "text": args.message,
                    "command": command,
                    "response": args.response,
                },
            },
            args.game,
            args.scorebot,
            args.token,
        )
    if args.video is not None:
        if args.start is not None:
            args.start = str(args.start)
        return (
            {
                "type": 3,
                "timeout": args.timeout,
                "data": {
                    "video": args.video,
                    "title": args.title,
                    "start": args.start,
                    "fullscreen": str(args.fullscreen),
                },
            },
            args.game,
            args.scorebot,
            args.token,
        )
    if args.effect is not None:
        if len(args.effect) > 0:
            return (
                {"type": 2, "timeout": args.timeout, "data": {"html": args.effect}},
                args.game,
                args.scorebot,
                args.token,
            )
        if args.file is not None:
            try:
                d = open(args.file, "r")
                data = d.read()
                d.close()
            except OSError as err:
                print('Could not read file "%s"! (%s)' % (args.file, err))
                exit(1)
            return (
                {
                    "type": 2,
                    "timeout": args.timeout,
                    "data": {"html": data},
                    "fullscreen": str(args.fullscreen),
                },
                args.game,
                args.scorebot,
                args.token,
            )
    print("No correct option selected!", file=stderr)
    exit(1)


if __name__ == "__main__":
    d, g, s, t = start()

    r = session()
    r.headers["SBE-AUTH"] = t

    try:
        o = r.post("%s/api/event/%d/" % (s, g), data=dumps(d), timeout=5)
    except OSError as err:
        print("Failed to send Event data! (%s)" % str(err), file=stderr)
        exit(1)

    if o.status_code != 201:
        print(
            "Error occured from Scorebot event parsing! (code: %d) %s"
            % (o.status_code, o.content.decode("UTF-8"))
        )
        exit(1)

    print("Done!")
    exit(0)
