# Roadmap — TA-unifi_security

Companion app backlog: [unifi_security/docs/ROADMAP.md](https://github.com/RossLopez/unifi_security/blob/main/docs/ROADMAP.md).

## Splunkbase readiness

### Must-fix (AppInspect / Splunk Cloud)
- [x] `inputs.conf`: no input shipped; README documents an example `[udp://5555]` stanza for `local/` (Cloud disallows network inputs in apps).
- [ ] Decide sourcetype naming (`unifi:*` vs vendor-prefixed `ubiquiti:unifi:*`); check for collisions with other UniFi add-ons and SC4S.
- [x] `app.conf`: `[id]` stanza, `check_for_updates = true`, `is_configured` removed. `[triggers]` not needed (only Splunk-native conf files).
- [x] Author: Ross Lopez (`app.conf`, `app.manifest`).
- [x] `app.manifest` (`slim generate-manifest`) with target workloads: search heads + indexers.
- [x] Icons and logos in `static/` (`appIcon` 36/72, `appIconAlt` 36/72, `appLogo` 160x40/320x80); built by `scripts/build_icons.py`, 512px listing icon in `assets/`.
- [x] Support contact: GitHub Issues (README Support section, issue template). Repos must be public before the listing goes live.
- [x] LICENSE (Apache 2.0) and release notes.
- [x] Clean packaging (no `local/`, `local.meta`, hidden files; 644/755 perms; top dir == app id).
- [x] `splunk-appinspect inspect --mode precert --included-tags cloud` clean (AppInspect 4.3.1, 0.1.3). Re-run before every release.

### Ingestion portability
- [ ] Transport-agnostic parsing: RFC3164 + RFC5424, with/without `<PRI>`, ISO8601 timestamps, single header (direct) vs relay double header, SC4S-forwarded events.
- [ ] Do not overwrite `host` when upstream (SC4S/relay) already set it correctly.
- [ ] Accept multiple entry sourcetypes; map or document SC4S UniFi sourcetypes.
- [ ] Device coverage: UDM-SE, UDR, UCG-Ultra/Max, UXG, Cloud Key; U7 and other APs; USG-era firewall logs (`[WAN_LOCAL-default-D]`); zone-based firewall rule logs. Remove dependence on the `DreamMachinePro` token.
- [ ] Build the CEF event catalog from Ubiquiti's published SIEM event list (Network, Protect, Access, OS).
- [ ] Timestamp handling: no-year/no-TZ syslog headers; document `TZ`. CEF `UNIFIutcTime` cannot be used because sourcetype is rewritten after timestamping.
- [ ] Multi-firmware test matrix (UniFi Network 8.x–10.x, UniFi OS 3–5).
- [ ] Document collection options: SC4S (recommended, enterprise/Cloud), rsyslog/syslog-ng -> file -> UF, direct UDP/TCP (single-instance labs).

### CIM accuracy
- [ ] Validate with pytest-splunk-addon / CIM Validator; declare supported CIM version.
- [ ] Network_Sessions `action` (`added`/`removed`) is not a CIM value.
- [ ] `duration` from CEF is a string ("47d 18h") — convert to seconds.
- [ ] WiFi auth: `user` = client MAC is a stretch — document or move to custom eventtype.
- [ ] sudo as Authentication/privileged is debatable (Change / Endpoint?).
- [ ] `bytes` from iptables `LEN` is packet length, not session bytes.
- [ ] Scope `EVAL-dest = host` (applies to every `unifi:syslog` event).
- [ ] Generic field names (`process`, `message`, `command`, `reason`) — prefix or confirm CIM-correct.
- [ ] `process` not extracted for iptables rule-log events (header regex expects `proc[pid]:`).

### Listing / docs
- [ ] README: supported devices/firmware, enabling UniFi SIEM integration, install-location table, sourcetype + CIM tables, troubleshooting (input stanza merge precedence).
- [ ] Sanitized samples + eventgen + pytest-splunk-addon configs.
- [ ] Screenshots; trademark disclaimer; no Ubiquiti logos.

## Release history
- 0.1.5 — Author set to Ross Lopez; added support details and a GitHub bug report template.
- 0.1.4 — Added app icons and logos (`static/`) and `scripts/build_icons.py`.
- 0.1.3 — AppInspect fixes: removed the shipped UDP input (breaking: create your own input), added `[id]` and `app.manifest`, removed `is_configured`, enabled update checks, removed example IPs from comments.
- 0.1.2 — Moved to its own repository; Apache 2.0 LICENSE included in the package; sanitized example values in config comments and samples.
- 0.1.1 — Fixed dynamic-key REPORT extractions (FORMAT cannot prefix `$1`); CEF fields now native `UNIFI*` names; stahtd via `spath()`; iptables via EXTRACT.
- 0.1.0 — Initial build (as TA-unifi).
