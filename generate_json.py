import json

TE = (
    ('ALPHA', '10.100.101.0/24'),
    ('GAMMA',  '10.100.103.0/24'),
    ('DELTA',  '10.100.104.0/24'),
    ('EPSILON', '10.100.105.0/24'),
)

d = dict()


def gg(n, o, p):
    global d
    for j in TE:
        if j[0] not in d:
            d[j[0]] = {
                "dns": "",
                "email": "%s@%s.net" % (j[0].lower(), j[0].lower()),
                "hosts": list(),
                "name": j[0].title(),
                "nets": [
                    j[1]
                ]
            }
        h = {
            "hostname": "%s.%s.net" % (n, j[0].lower()),
            "value": 100,
            "services": list()
        }
        for q in p:
            h["services"].append(
                {
                    "port": str(q),
                    "protocol": "tcp",
                    "value": 100
                }
            )
        d[j[0]]["hosts"].append(h)


# Add host definitions here.
gg('freepbx', 18, [80, 22])
gg('samba', 197, [445, 22])
gg('mail', 203, [25, 22])
gg('desktop-12', 42, [445, 3389])
gg('desktop-5', 43, [445, 3389])
gg('ubuntu', 52, [80, 22])
gg('ns', 60, [53, 22])
gg('ook', 76, [445, 22])
gg('win2008-2', 88, [445, 3389])
gg('elk', 99, [9200, 22])

print(json.dumps({
    "game_name": "Game",
    "blueteams": list(d.values()),
}, indent=True))
