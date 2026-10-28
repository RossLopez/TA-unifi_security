# Sample events

`udp5555_relay_format.log` — one event per format the add-on handles, **sanitized and partly reconstructed** from a real UDM Pro feed (IPs use RFC1918 / RFC5737 documentation ranges, MACs and names are fake). The first header (`<time> 192.168.1.5`) is the relay/receiver header seen in the reference environment; the second header is the device's own.

Gaps to fill before Splunkbase: RFC5424 headers, direct-from-device (single header), SC4S-forwarded events, other gateways (UDM-SE, UDR, UCG, UXG), U7 APs, more CEF event IDs, zone-based firewall rule logs.
