#!/usr/bin/python
# Generates a JSON game structure from a CSV file.
# iDigitalFlame
#
#  generate.py <csv> [outfile]

from json import dumps
from datetime import datetime
from collections import namedtuple
from sys import argv, stderr, exit

Team = namedtuple("Team", ["Name", "DNS", "Network"])
Record = namedtuple("Record", ["ID", "Name", "Value", "Ports", "Start", "End"])

TEAMS = (
    Team(Name="ALPHA", DNS="10.100.101.60", Network="10.100.101.0/24"),
    Team(Name="GAMMA", DNS="10.100.103.60", Network="10.100.103.0/24"),
    Team(Name="DELTA", DNS="10.100.104.60", Network="10.100.104.0/24"),
    Team(Name="EPSILON", DNS="10.100.105.60", Network="10.100.105.0/24"),
)


def read(file):
    try:
        f = open(file, "r")
        a = f.read().split("\n")
        f.close()
    except OSError as err:
        print("Cannot read file: %s" % str(err), file=stderr)
        exit(1)
    c = None
    r = list()
    for x in range(0, len(a)):
        if x == 0 or len(a[x]) == 0:
            continue
        d = a[x].replace("\r", "").split(",")
        if len(d) == 0 or d[5] != "0":
            continue
        s = datetime.fromisoformat(d[6].replace("Z", ""))
        e = datetime.fromisoformat(d[7].replace("Z", ""))
        if s.hour != 0 and s.minute != 0:
            continue
        try:
            if c is None or c.ID != int(d[0]):
                if c is not None:
                    r.append(c)
                c = Record(
                    ID=int(d[0]),
                    Name=d[1].replace(" ", "-").replace("(", "").replace(")", ""),
                    Value=int(d[4]),
                    Ports=[],
                    Start=s,
                    End=e,
                )
            c.Ports.append(int(d[3]))
            if c.Value != int(d[4]):
                c.Value = int(d[4])
        except ValueError as err:
            print("Could not parse value: %s" % str(err), file=stderr)
            exit(1)
    if c is not None:
        r.append(c)
    return r


def compile(hosts):
    i = list()
    for t in TEAMS:
        d = list()
        for h in hosts:
            s = list()
            for p in h.Ports:
                s.append({"port": str(p), "value": 100, "protocol": "tcp"})
            d.append(
                {
                    "value": h.Value,
                    "hostname": "%s.%s.net" % (h.Name.lower(), t.Name.lower()),
                    "services": s,
                }
            )
        i.append(
            {
                "dns": t.DNS,
                "nets": t.Network,
                "name": t.Name.title(),
                "email": "%s@%s.net" % (t.Name.lower(), t.Name.lower()),
                "hosts": d,
            }
        )
    return i


if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage: %s <csv> [output]" % argv[0], file=stderr)
        exit(1)
    o = dumps(
        {
            "game_name": "Generated Game on %s"
            % datetime.now().strftime("%m/%d/%y %H:%M"),
            "blueteams": compile(read(argv[1])),
        },
        indent=4,
    )
    if len(argv) == 3:
        try:
            f = open(argv[2], "w")
            f.write(o)
            f.close()
        except OSError as err:
            print('Cannot save output to "%s": %s' % (argv[2], str(err)), file=stderr)
            exit(1)
    else:
        print(o)
