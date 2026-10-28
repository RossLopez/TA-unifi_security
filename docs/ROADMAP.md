# Roadmap — TA-unifi_security

Companion app backlog: [unifi_security/docs/ROADMAP.md](https://github.com/RossLopez/unifi_security/blob/main/docs/ROADMAP.md).

## Splunkbase readiness

### Must-fix (AppInspect / Splunk Cloud)
- [ ] `inputs.conf`: ship the UDP input disabled or as README example only; no hardcoded custom index (Cloud disallows network inputs in apps).
- [ ] Decide sourcetype naming (`unifi:*` vs vendor-prefixed `ubiquiti:unifi:*`); check for collisions with other UniFi add-ons and SC4S.
- [ ] `app.conf`: add `[id]` stanza (name, version), `check_for_updates = true`, `[triggers] reload.* = simple`, publisher name.
- [ ] `app.manifest` (`slim generate-manifest`) with target workloads: search heads + indexers.
- [ ] Icons (`appIcon.png` 36x36, `appIcon_2x.png` 72x72, Alt variants, `appLogo.png`), support contact.
- [x] LICENSE (Apache 2.0) and release notes.
- [ ] Clean packaging (no `local/`, `local.meta`, hidden files; correct perms; top dir == app id).
- [ ] `splunk-appinspect inspect --mode precert --included-tags cloud` clean.

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
- 0.1.2 — Moved to its own repository; Apache 2.0 LICENSE included in the package; sanitized example values in config comments and samples.
- 0.1.1 — Fixed dynamic-key REPORT extractions (FORMAT cannot prefix `$1`); CEF fields now native `UNIFI*` names; stahtd via `spath()`; iptables via EXTRACT.
- 0.1.0 — Initial build (as TA-unifi).
