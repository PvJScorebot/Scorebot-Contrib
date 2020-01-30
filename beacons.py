#!/usr/bin/python
# Retrieves the active beacons from Scorebot based on the supplied Team Token.
# beacons.py <scorebot> <token>
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

from requests import session
from sys import exit, argv, stderr
from json import loads, JSONDecodeError


if __name__ == "__main__":
    if len(argv) != 3:
        print("%s <scorebot> <token>" % argv[0], file=stderr)
        exit(1)
    s = session()
    s.headers["SBE-AUTH"] = argv[2]
    try:
        r = s.get("%s/api/beacon/active/" % argv[1], timeout=5)
    except OSError as err:
        print("Could not access Scorebot: %s" % str(err), file=stderr)
        exit(1)
    if r.status_code != 200:
        print("Received an invalid status code: %d!" % r.status_code, file=stderr)
        exit(1)
    try:
        o = r.content.decode("UTF-8")
    except UnicodeDecodeError as err:
        print("Could not decode response: %%" % str(err), file=stderr)
        exit(1)
    try:
        d = loads(o)
    except JSONDecodeError as err:
        print("Could not decode JSON output: %s" % str(err), file=stderr)
        exit(1)
    print("Active Beacons\n%s" % ("="*40))
    for b in d:
        if b["finish"] is not None or b["finish"] != "None":
            print("Host:\t%s\nTeam:\t%s\nToken:\t%s\nStart:\t%s\n" % (
                b["host"], b["attacker"], b["token"], b["start"]
            ))
