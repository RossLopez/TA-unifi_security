# UniFi Security Add-on for Splunk (TA-unifi_security)

Splunk add-on for Ubiquiti UniFi security data: sourcetype routing, host correction, field extraction and CIM mapping for UniFi OS / gateway syslog, UniFi AP and switch syslog, and the UniFi SIEM integration (CEF) for UniFi Network, UniFi OS and UniFi Protect.

Install on indexers / heavy forwarders **and** search heads. Dashboards and detections live in the companion app, **UniFi Security** ([`unifi_security`](https://github.com/RossLopez/unifi_security)).

## Repository layout

| Path | Purpose |
|---|---|
| `TA-unifi_security/` | The add-on itself (packaged as-is). See its [README](TA-unifi_security/README.md) for sourcetypes, fields and CIM mappings. |
| `samples/` | Sanitized sample events used for offline regex checks |
| `assets/screenshots/` | Splunkbase listing screenshots, taken on demo data from [`unifi_security/scripts/demo_data.py`](https://github.com/RossLopez/unifi_security/blob/main/scripts/demo_data.py) |
| `scripts/check_regex.py` | Offline check: applies the add-on's routing and EXTRACT/REPORT regexes to `samples/` |
| `scripts/build_icons.py` | Renders `assets/` (SVG sources, 512px Splunkbase listing icon) and the app's `static/` icons and logos (`pip install resvg-py`) |
| `scripts/package.sh` | Builds `dist/TA-unifi_security-<version>.spl` |
| `docs/ROADMAP.md` | Backlog, Splunkbase checklist and release history |

## Build

```bash
python3 scripts/check_regex.py
scripts/package.sh
```

AppInspect (needs Python 3.9–3.12 and `brew install libmagic`):

```bash
python3.12 -m venv .venv && .venv/bin/pip install splunk-appinspect
.venv/bin/splunk-appinspect inspect dist/TA-unifi_security-<version>.spl --mode precert --included-tags cloud
```

## Support

Developer supported, best effort. Report parsing problems and request device or event coverage at https://github.com/RossLopez/TA-unifi_security/issues. Replace real IP addresses, MAC addresses, hostnames, usernames and SSIDs in any log samples you post.

Not supported by Splunk or Ubiquiti.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

*Not affiliated with or endorsed by Ubiquiti Inc. UniFi is a trademark of Ubiquiti Inc.*
