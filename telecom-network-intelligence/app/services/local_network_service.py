"""Read live network adapter details for the computer running the app."""

from __future__ import annotations

import logging
import platform
import re
import socket
import subprocess
import threading
import time
from typing import Any

import psutil

logger = logging.getLogger("telecom")
_counter_lock = threading.Lock()
_previous_counters: dict[str, tuple[int, int]] = {}
_previous_sample_time: float | None = None
_wifi_cache: tuple[float, dict[str, str | None] | None] = (0.0, None)
_wifi_cache_lock = threading.Lock()


def _wifi_details() -> dict[str, str | None] | None:
    global _wifi_cache
    if platform.system() != "Windows":
        return None

    now = time.monotonic()
    with _wifi_cache_lock:
        cached_at, cached_details = _wifi_cache
        if now - cached_at < 15:
            return cached_details

        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                check=False,
                capture_output=True,
                text=True,
                timeout=2,
                encoding="utf-8",
                errors="replace",
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            logger.warning("Unable to read Windows Wi-Fi details: %s", exc)
            _wifi_cache = (now, None)
            return None

        if result.returncode != 0 or not result.stdout.strip():
            details = None
        else:
            patterns = {
                "ssid": r"^\s*SSID\s*:\s*(.+?)\s*$",
                "signal_percent": r"^\s*Signal\s*:\s*(\d+%)\s*$",
                "radio_type": r"^\s*Radio type\s*:\s*(.+?)\s*$",
                "channel": r"^\s*Channel\s*:\s*(\d+)\s*$",
                "receive_rate_mbps": r"^\s*Receive rate \(Mbps\)\s*:\s*(.+?)\s*$",
                "transmit_rate_mbps": r"^\s*Transmit rate \(Mbps\)\s*:\s*(.+?)\s*$",
            }
            details = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, result.stdout, re.IGNORECASE | re.MULTILINE)
                details[key] = match.group(1) if match else None
            if not details["ssid"]:
                details = None

        _wifi_cache = (now, details)
        return details


def _internet_probe() -> dict[str, Any]:
    started_at = time.perf_counter()
    try:
        with socket.create_connection(("1.1.1.1", 443), timeout=1.5):
            return {
                "reachable": True,
                "latency_ms": round((time.perf_counter() - started_at) * 1000, 1),
            }
    except OSError as exc:
        return {"reachable": False, "latency_ms": None, "error": str(exc)}


def get_local_network_status() -> dict[str, Any]:
    """Return current local adapter state and traffic rates since the prior poll."""
    global _previous_counters, _previous_sample_time

    addresses = psutil.net_if_addrs()
    interface_stats = psutil.net_if_stats()
    counters = psutil.net_io_counters(pernic=True) or {}
    now = time.monotonic()

    with _counter_lock:
        elapsed = now - _previous_sample_time if _previous_sample_time is not None else 0
        interfaces = []
        current_counters = {}
        for name, stats in interface_stats.items():
            counter = counters.get(name)
            previous = _previous_counters.get(name)
            received = counter.bytes_recv if counter else 0
            sent = counter.bytes_sent if counter else 0
            current_counters[name] = (received, sent)

            receive_rate = 0.0
            transmit_rate = 0.0
            if counter and previous and elapsed > 0:
                receive_rate = max(0, received - previous[0]) / elapsed
                transmit_rate = max(0, sent - previous[1]) / elapsed

            interface_addresses = []
            mac_address = None
            for address in addresses.get(name, []):
                if address.family == socket.AF_INET:
                    interface_addresses.append({"family": "IPv4", "address": address.address})
                elif address.family == socket.AF_INET6:
                    interface_addresses.append({"family": "IPv6", "address": address.address})
                elif getattr(psutil, "AF_LINK", None) == address.family:
                    mac_address = address.address

            interfaces.append(
                {
                    "name": name,
                    "is_up": stats.isup,
                    "speed_mbps": stats.speed or None,
                    "mtu": stats.mtu,
                    "mac_address": mac_address,
                    "addresses": interface_addresses,
                    "received_bytes": received,
                    "sent_bytes": sent,
                    "receive_bytes_per_second": round(receive_rate, 1),
                    "transmit_bytes_per_second": round(transmit_rate, 1),
                }
            )

        _previous_counters = current_counters
        _previous_sample_time = now

    interfaces.sort(key=lambda item: (not item["is_up"], item["name"].casefold()))
    internet = _internet_probe()
    return {
        "sampled_at": time.time(),
        "computer_name": socket.gethostname(),
        "operating_system": platform.platform(),
        "internet": internet,
        "wifi": _wifi_details(),
        "interfaces": interfaces,
        "note": "Adapter traffic rates are measured on the computer running this app; first sample rates start at zero.",
    }
