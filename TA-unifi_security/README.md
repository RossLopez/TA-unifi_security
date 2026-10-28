# UniFi Security Add-on (TA-unifi_security) v0.2.1

Companion add-on for the **UniFi Security** app (`unifi_security`). Parsing and CIM mapping for UDM Pro / UniFi OS syslog, UniFi APs and switches, and the UniFi SIEM integration (CEF).

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

   Point the UniFi syslog / SIEM integration at that port. If another app already defines the same stanza (e.g. `[udp://5555]`), remove it there: Splunk merges same-named input stanzas across apps, and the app that sorts first in ASCII order wins conflicting settings.
4. Verify: `index=unifi earliest=-15m | stats count by sourcetype host`

On a distributed deployment, install the TA on the receiving HF/indexers *and* the search heads, and create the input on the instance that receives syslog. Splunk Cloud does not allow network inputs in apps; receive UniFi syslog on a heavy forwarder with sourcetype `ubiquiti:unifi` (SC4S support is on the roadmap).

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

## Support

Developer supported, best effort. Report parsing problems and request device or event coverage at https://github.com/RossLopez/TA-unifi_security/issues. Replace real IP addresses, MAC addresses, hostnames, usernames and SSIDs in any log samples you post.

Not supported by Splunk or Ubiquiti.

## Release notes

- **0.2.1** — Splunk Web icons and logos fill the whole square; Splunk 10 showed its blue icon background through the transparent rounded corners.
- **0.2.0** — **Breaking:** sourcetypes renamed to Splunk's vendor:product convention: `ubiquiti:unifi` (entry and UniFi OS / gateway), `ubiquiti:unifi:cef`, `ubiquiti:unifi:ap`, `ubiquiti:unifi:switch`. See Upgrading from 0.1.x.
- **0.1.5** — Author set to Ross Lopez; added support details.
- **0.1.4** — Added app icons and logos (`static/`).
- **0.1.3** — **Breaking:** the add-on no longer ships a `[udp://5555]` input (not allowed in Splunk Cloud); create your own input with sourcetype `unifi:syslog` (see Install). Added `[id]` stanza and `app.manifest`; update checks enabled; example IPs removed from config comments.
- **0.1.2** — Apache 2.0 LICENSE included in the package; sanitized example values in config comments.
- **0.1.1** — Fixed CEF extension, stahtd and iptables field extraction (dynamic-key `FORMAT` does not support a literal prefix, which produced a single `unifi_$1` field). CEF extension fields now use native key names (`UNIFI*`).
- **0.1.0** — Initial build.
