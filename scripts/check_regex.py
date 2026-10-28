#!/usr/bin/env python3
"""Offline sanity check: apply the TA's index-time routing and search-time
EXTRACT / REPORT regexes to sample events and print what each event yields.

Usage:  python3 scripts/check_regex.py [samples/udp5555_relay_format.log]

Approximation of Splunk behaviour (PCRE vs Python re); it does not evaluate
EVALs, FIELDALIASes or lookups. Always confirm in Splunk.
"""
import configparser, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TA = ROOT / "TA-unifi_security" / "default"

def load(conf):
    cp = configparser.RawConfigParser(strict=False, interpolation=None, delimiters=("=",), comment_prefixes=("#",))
    cp.optionxform = str
    cp.read(TA / conf)
    return cp

def py(rx):  # PCRE named groups -> Python
    return re.compile(rx.replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!"))

props, transforms = load("props.conf"), load("transforms.conf")

def route(raw):
    host, st = None, "unifi:syslog"
    for name in [n.strip() for n in props["unifi:syslog"]["TRANSFORMS-unifi_routing"].split(",")]:
        t = transforms[name]
        m = py(t["REGEX"]).search(raw)
        if not m:
            continue
        val = m.expand(t["FORMAT"].replace("$1", r"\1")).split("::", 1)[1]
        if t["DEST_KEY"] == "MetaData:Host":
            host = val
        else:
            st = val
    return host, st

def fields(raw, st):
    out = {}
    if st not in props:
        return out
    for k, v in props[st].items():
        if k.startswith("EXTRACT-"):
            m = py(v).search(raw)
            if m:
                out.update({a: b for a, b in m.groupdict().items() if b not in (None, "")})
        elif k.startswith("REPORT-"):
            for name in [n.strip() for n in v.split(",")]:
                t = transforms[name]
                fmt = t["FORMAT"]
                if fmt == "$1::$2":
                    for m in py(t["REGEX"]).finditer(raw):
                        out[m.group(1)] = m.group(2)
                else:
                    m = py(t["REGEX"]).search(raw)
                    if m:
                        for pair in fmt.split():
                            f, g = pair.split("::")
                            out[f] = m.group(int(g[1:]))
    return out

sample = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "samples" / "udp5555_relay_format.log")
bad = 0
for i, raw in enumerate(l for l in sample.read_text().splitlines() if l.strip()):
    host, st = route(raw)
    f = fields(raw, st)
    if not host or not f:
        bad += 1
    keys = ", ".join(f"{k}={str(v)[:30]}" for k, v in list(f.items())[:8])
    print(f"[{i:02}] host={host!s:<14} st={st:<13} {len(f):>2} fields  {keys}")
print(f"\n{bad} event(s) with no host or no fields")
sys.exit(1 if bad else 0)
