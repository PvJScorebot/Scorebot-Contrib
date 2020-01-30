#!/usr/bin/python
# Generates a JSON game structure from a CSV file.
# generate.py <csv> [outfile]
#
# Copyright (C) 2020 iDigitalFlame
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from json import dumps
from datetime import datetime
from collections import namedtuple
from sys import argv, stderr, exit

Team = namedtuple("Team", ["Name", "DNS", "Network"])
Record = namedtuple("Record", ["ID", "Name", "Value", "Ports", "Last"])

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
    r = dict()
    for x in range(0, len(a)):
        if x == 0 or len(a[x]) == 0:
            continue
        d = a[x].replace("\r", "").split(",")
        if len(d) == 0 or d[2] != "0" or d[6] != "0":
            continue
        if len(d[9]) == 0:
            print('Entry "%s" does not have a valid DNS name!' % a[x], file=stderr)
            exit(1)
        try:
            i = int(d[1])
            if i not in r:
                p = d[11].split(".")
                if len(p) > 0:
                    p = p[len(p) - 1]
                c = Record(
                    ID=i,
                    Name=d[9].replace(" ", "-").replace("(", "").replace(")", ""),
                    Value=int(d[5]),
                    Ports=list(),
                    Last=p,
                )
                r[i] = c
            else:
                c = r[i]
            c.Ports.append(int(d[4]))
            if c.Value != int(d[5]):
                c.Value = int(d[5])
        except ValueError as err:
            print("Could not parse value: %s" % str(err), file=stderr)
            exit(1)
    return list(r.values())


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
                    "ip": ".".join(
                        [o if "/" not in o else h.Last for o in t.Network.split(".")]
                    ),
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
