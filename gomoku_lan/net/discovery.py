from __future__ import annotations

import json
import socket
import struct
import threading
from dataclasses import dataclass
from typing import Callable

from ..util import now_ms


DISCOVERY_PORT = 37020
DISCOVERY_MULTICAST_GROUP = "239.255.37.20"


@dataclass(frozen=True)
class Beacon:
    peer_id: str
    nickname: str
    tcp_port: int
    ts_ms: int


class UdpDiscovery:
    def __init__(
        self,
        get_local_ip: Callable[[], str],
        beacon_factory: Callable[[], Beacon],
        on_beacon: Callable[[str, Beacon], None],
    ) -> None:
        self._get_local_ip = get_local_ip
        self._beacon_factory = beacon_factory
        self._on_beacon = on_beacon

        self._stop = threading.Event()
        self._rx_thread: threading.Thread | None = None
        self._tx_thread: threading.Thread | None = None
        self._sock: socket.socket | None = None

    def start(self) -> None:
        if self._sock is not None:
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        except OSError:
            pass
        sock.bind(("", DISCOVERY_PORT))
        try:
            mreq = struct.pack("=4s4s", socket.inet_aton(DISCOVERY_MULTICAST_GROUP), socket.inet_aton("0.0.0.0"))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except OSError:
            pass
        sock.settimeout(0.5)
        self._sock = sock

        self._rx_thread = threading.Thread(target=self._rx_loop, name="udp-discovery-rx", daemon=True)
        self._tx_thread = threading.Thread(target=self._tx_loop, name="udp-discovery-tx", daemon=True)
        self._rx_thread.start()
        self._tx_thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
        self._sock = None

    def _tx_loop(self) -> None:
        assert self._sock is not None
        while not self._stop.is_set():
            beacon = self._beacon_factory()
            local_ip = self._get_local_ip()
            payload = json.dumps(
                {
                    "type": "beacon",
                    "peer_id": beacon.peer_id,
                    "nickname": beacon.nickname,
                    "tcp_port": beacon.tcp_port,
                    "ts_ms": now_ms(),
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            for ip in _probe_targets(local_ip):
                try:
                    self._sock.sendto(payload, (ip, DISCOVERY_PORT))
                except OSError:
                    pass
            self._stop.wait(1.2)

    def _rx_loop(self) -> None:
        assert self._sock is not None
        while not self._stop.is_set():
            try:
                data, addr = self._sock.recvfrom(64 * 1024)
            except socket.timeout:
                continue
            except OSError:
                return
            try:
                msg = json.loads(data.decode("utf-8"))
            except Exception:
                continue
            if not isinstance(msg, dict) or msg.get("type") != "beacon":
                continue

            ip = addr[0]
            try:
                beacon = Beacon(
                    peer_id=str(msg.get("peer_id", "")),
                    nickname=str(msg.get("nickname", "")),
                    tcp_port=int(msg.get("tcp_port", 0)),
                    ts_ms=int(msg.get("ts_ms", 0)),
                )
            except Exception:
                continue
            if not beacon.peer_id or beacon.tcp_port <= 0 or beacon.tcp_port > 65535:
                continue
            self._on_beacon(ip, beacon)


def _probe_targets(local_ip: str) -> list[str]:
    targets: list[str] = ["255.255.255.255", DISCOVERY_MULTICAST_GROUP, "127.0.0.1"]
    parts = local_ip.split(".")
    if len(parts) == 4 and all(p.isdigit() for p in parts):
        a, b, c, d = [int(p) for p in parts]
        if all(0 <= x <= 255 for x in (a, b, c, d)):
            if not local_ip.startswith("127."):
                targets.append(local_ip)
                targets.append(f"{a}.{b}.{c}.255")
                targets.append(f"{a}.{b}.255.255")
            if a == 10:
                targets.append("10.255.255.255")
            elif a == 172 and 16 <= b <= 31:
                targets.append("172.31.255.255")
            elif a == 192 and b == 168:
                targets.append("192.168.255.255")
    seen: set[str] = set()
    deduped: list[str] = []
    for ip in targets:
        if ip in seen:
            continue
        seen.add(ip)
        deduped.append(ip)
    return deduped
