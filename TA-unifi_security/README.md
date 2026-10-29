# UniFi Security Add-on (TA-unifi_security) v0.2.4

Companion add-on for the **UniFi Security** app (`unifi_security`). Parsing and CIM mapping for UDM Pro / UniFi OS syslog, UniFi APs and switches, and the UniFi SIEM integration (CEF).

## Compatibility

- Splunk Enterprise 9.4, 10.0, 10.2, 10.4 and 10.6 (tested on 9.4.16, 10.0.11, 10.2.8, 10.4.2 and 10.6.1).
- Splunk Cloud Platform: passes AppInspect's Splunk Cloud checks; not yet tested on a Cloud stack.

## Supported devices

Tested with:

| Device | Role | Firmware / software | Sourcetypes |
|---|---|---|---|
| UDM Pro | Gateway and UniFi OS console | UniFi OS 5.1, UniFi Network 10.6, UniFi Protect 7.3 | `ubiquiti:unifi`, `ubiquiti:unifi:cef` |
| U6 Pro, U6 Extender, UAP-AC-Pro-Gen2 | Access points | 6.8.2 | `ubiquiti:unifi:ap` |
| US-8-60W | Switch | 7.5.15 | `ubiquiti:unifi:switch` |
| USW-Flex-2.5G-5 | Switch | 2.1.8 | `ubiquiti:unifi:switch` |

Other UniFi consoles (UDM-SE, UDR, UCG, UXG, Cloud Key) send the same SIEM (CEF) events, so the CEF-based fields, eventtypes and dashboards should work, but their syslog has not been tested. If events from your devices are not parsed, open an issue with a few sanitized samples (see Support).

## Where to install

| Splunk instance | Install the add-on? | Why |
|---|---|---|
| Search heads (incl. search head clusters) | Yes | Search-time field extractions, eventtypes, tags and CIM mapping |
| Heavy forwarder that receives UniFi syslog | Yes | Index-time `host` and sourcetype routing runs on the first full Splunk instance that parses the data |
| Indexers | Yes | Index-time routing when syslog is received directly on an indexer (no heavy forwarder in front) |
| Universal forwarders | No | Universal forwarders don't parse; just set `sourcetype = ubiquiti:unifi` on the input |
| Splunk Cloud Platform | Yes, on the Cloud stack | Plus the heavy forwarder that receives syslog (Cloud does not accept network inputs in apps) |

On a single instance, install it once. The add-on has no setup page and no Python, so nothing else needs configuring.

## Install (single instance)

1. Install `TA-unifi_security` (Apps > Manage Apps > Install app from file) and restart Splunk.
2. Create an index for UniFi data (the companion app's `unifi_index` macro defaults to `index=unifi`).
3. Create a syslog input with sourcetype `ubiquiti:unifi` (the add-on does not ship one). For example, in `$SPLUNK_HOME/etc/apps/TA-unifi_security/local/inputs.conf`:

   ```ini
   [udp://5555]
   index = unifi
   sourcetype = ubiquiti:unifi
   connection_host = ip
   ```

   Use a port above 1024 (Splunk normally runs as a non-root user and cannot bind 514). If another app already defines the same stanza (e.g. `[udp://5555]`), remove it there: Splunk merges same-named input stanzas across apps, and the app that sorts first in ASCII order wins conflicting settings.
4. Point UniFi at that port (next section).
5. Verify: `index=unifi earliest=-15m | stats count by sourcetype host`

Splunk Cloud Platform: receive UniFi syslog on a heavy forwarder with the input above and the add-on installed (SC4S support is on the roadmap).

## Send logs from UniFi

Menu names below are from UniFi Network 10.x on UniFi OS 5.x and move between releases.

1. **SIEM events (CEF):** in UniFi Network, open **Integrations** in the left sidebar (older releases: **Settings > Control Plane > Integrations**). Next to **Activity Logging (Syslog)** choose **SIEM Server**, enter the Splunk (or heavy forwarder) IP and the input port, select the event categories you want (at least security detections, admin activity, client and device events) and apply. This produces `ubiquiti:unifi:cef` events: IPS/IDS threats, firewall blocks, WiFi impersonation (rogue AP), client connect/disconnect, admin access, and UniFi OS and UniFi Protect events from the same console. The SIEM option needs UniFi Network 8.5 or later.
2. **Firewall traffic:** open **Settings > CyberSecure > Traffic Logging** and send **Activity Logging (Syslog)** to the same server and port. To log a specific policy, turn on **Syslog Logging** for it under **Settings > Policy Engine**. These arrive as iptables rule logs (`[PREROUTING-DNAT-3] … SRC= DST=`) in `ubiquiti:unifi`.
3. **Gateway, AP and switch syslog** (DHCP, sudo, SSH, hostapd, `stahtd` WiFi auth results, switch link events): with remote logging on, UniFi Network configures adopted devices to send their own syslog directly to the same server. If AP or switch events don't appear, look for a debug or device-log option in the same Activity Logging panel (the name varies by version).

Everything can share one input: the add-on routes events to the right sourcetype by content.

## Sourcetypes

| Sourcetype | Source | Examples |
|---|---|---|
| `ubiquiti:unifi` | UDM Pro / UniFi OS (entry sourcetype) | dnsmasq-dhcp, sudo, sshd, inadyn, iptables rule logs (`[PREROUTING-DNAT-3] … SRC= DST=`) |
| `ubiquiti:unifi:cef` | UniFi SIEM integration (CEF) | Network 200/203/400-404/529/544, UniFi OS 1000, Protect 2159/2161 |
| `ubiquiti:unifi:ap` | UniFi APs (U6 Pro, U6 Extender, AC Pro Gen2 tested) | hostapd, stahtd (JSON), kernel/wlan |
| `ubiquiti:unifi:switch` | UniFi switches (US-8-60W, USW-Flex-2.5G tested) | switch LLDP / DHCP snooping / link |

Index-time transforms set `host` to the originating device (gateway hostname, AP/switch IP or name) instead of the relay. Data indexed before install keeps its original sourcetype and host.

## Upgrading from 0.1.x

0.2.0 renames the sourcetypes (`unifi:syslog` → `ubiquiti:unifi`, `unifi:cef` → `ubiquiti:unifi:cef`, `unifi:ap` → `ubiquiti:unifi:ap`, `unifi:switch` → `ubiquiti:unifi:switch`).

1. Change your input's `sourcetype` to `ubiquiti:unifi`.
2. Optional: to keep fields and eventtypes on data indexed before the upgrade, map the old names at search time in `local/props.conf`:

   ```ini
   [unifi:syslog]
   rename = ubiquiti:unifi
   [unifi:cef]
   rename = ubiquiti:unifi:cef
   [unifi:ap]
   rename = ubiquiti:unifi:ap
   [unifi:switch]
   rename = ubiquiti:unifi:switch
   ```

## Field conventions

- CEF header → `cef_vendor cef_product cef_product_version cef_signature_id cef_name cef_severity`
- CEF extension → keys keep their native names (`UNIFIclientIp`, `UNIFIipsSignature`, `src`, `dst`, `msg` …). Values contain spaces, so the TA uses a lookahead regex instead of KV_MODE.
- AP stahtd JSON → `stahtd_json`, plus `sta_event_type`, `sta_mac`, `sta_vap`, `sta_auth_failures` via `spath()`
- iptables rule logs → `fw_rule fw_descr fw_SRC fw_DST fw_SPT fw_DPT fw_PROTO fw_IN fw_OUT`

## CIM mapping

| Eventtype | Data model | Tags |
|---|---|---|
| `unifi_ips_threat` (CEF 200) | Intrusion_Detection | ids attack |
| `unifi_rogue_ap` (CEF 529) | Intrusion_Detection (ids_type=wireless) | ids attack |
| `unifi_firewall_block` (CEF 203) | Network_Traffic | network communicate |
| `unifi_fw_rule_log` (iptables) | Network_Traffic | network communicate |
| `unifi_admin_access` (CEF 544 / 1000) | Authentication | authentication |
| `unifi_ssh_auth` | Authentication | authentication |
| `unifi_sudo` | Authentication (privileged) | authentication privileged |
| `unifi_wifi_auth_failure` / `_success` (stahtd) | Authentication (app=wifi) | authentication |
| `unifi_client_connect` / `_disconnect` (CEF 400/403, 401/404) | Network_Sessions | network session start/end |
| `unifi_dhcp_lease` (dnsmasq DHCPACK) | Network_Sessions | network session dhcp start |

`lookups/unifi_cef_event_catalog.csv` maps each CEF signature ID to `unifi_event_class` and `cim_datamodel`.

## Notes

- Timestamps are taken from the syslog header (local time, no zone). Set `TZ` in `[ubiquiti:unifi]` if the Splunk server's OS zone differs from the devices'.
- UniFi IPS `action=allowed` means detect-only (IDS mode) or an alert-only signature: the traffic was not dropped.

## Troubleshooting

| Symptom | Check |
|---|---|
| No events at all | The input's port and protocol match UniFi's setting; nothing blocks the port on the Splunk host (`sudo lsof -iUDP:5555`); the input is enabled and Splunk was restarted after creating it. |
| Everything is `ubiquiti:unifi`, nothing in `:cef`, `:ap` or `:switch`, and `host` is the console or relay | Index-time routing did not run: install the add-on on the heavy forwarder or indexer that receives the syslog (not only the search head), make sure the input's `sourcetype` is exactly `ubiquiti:unifi`, and restart. Routing applies to new data only. |
| Events arrive but fields, eventtypes and tags are missing | Install the add-on on the search heads as well. |
| Input settings (index, sourcetype) ignored | Another app defines the same input stanza and wins the merge; remove the duplicate. `$SPLUNK_HOME/bin/splunk btool inputs list udp://5555 --debug` shows which file each setting comes from. |
| Timestamps hours off | UniFi devices log local time without a zone. Set `TZ` in `local/props.conf` under `[ubiquiti:unifi]`, or per device with `[host::<device>]` (some switches, e.g. USW-Flex, log in UTC). |
| No `ubiquiti:unifi:cef` events | SIEM Server is not selected under Integrations (left sidebar), or no event categories are selected. |
| Old searches broke after upgrading from 0.1.x | Sourcetypes were renamed in 0.2.0; see Upgrading from 0.1.x. |

## Support

Developer supported, best effort. Report parsing problems and request device or event coverage at https://github.com/RossLopez/TA-unifi_security/issues. Replace real IP addresses, MAC addresses, hostnames, usernames and SSIDs in any log samples you post.

Not supported by Splunk or Ubiquiti.

## Release notes

- **0.2.4** — README: the SIEM integration is under Integrations in UniFi Network's left sidebar.
- **0.2.3** — README: supported devices, where to install, sending logs from UniFi (SIEM, firewall traffic, device syslog) and troubleshooting.
- **0.2.2** — Documented supported Splunk versions: Enterprise 9.4–10.6, tested on each in Docker.
- **0.2.1** — Splunk Web icons and logos fill the whole square; Splunk 10 showed its blue icon background through the transparent rounded corners.
- **0.2.0** — **Breaking:** sourcetypes renamed to Splunk's vendor:product convention: `ubiquiti:unifi` (entry and UniFi OS / gateway), `ubiquiti:unifi:cef`, `ubiquiti:unifi:ap`, `ubiquiti:unifi:switch`. See Upgrading from 0.1.x.
- **0.1.5** — Author set to Ross Lopez; added support details.
- **0.1.4** — Added app icons and logos (`static/`).
- **0.1.3** — **Breaking:** the add-on no longer ships a `[udp://5555]` input (not allowed in Splunk Cloud); create your own input with sourcetype `unifi:syslog` (see Install). Added `[id]` stanza and `app.manifest`; update checks enabled; example IPs removed from config comments.
- **0.1.2** — Apache 2.0 LICENSE included in the package; sanitized example values in config comments.
- **0.1.1** — Fixed CEF extension, stahtd and iptables field extraction (dynamic-key `FORMAT` does not support a literal prefix, which produced a single `unifi_$1` field). CEF extension fields now use native key names (`UNIFI*`).
- **0.1.0** — Initial build.
