#!/usr/bin/env python3
"""
inibidor_lock.py
Daemon que inibe o bloqueio de tela quando um player de mídia está em foco E reproduzindo.

Requer que o xidlehook seja iniciado com --socket /tmp/xidlehook.sock no i3/config.
"""
from __future__ import annotations

import json
import signal
import subprocess
import sys
import time

SOCKET_XIDLEHOOK = "/tmp/xidlehook.sock"
POLL_INTERVAL = 10  # segundos

MEDIA_CLASSES = frozenset({
    "mpv",
    "vlc",
    "firefox",
    "firefoxdeveloperedition",
    "brave-browser",
    "chromium",
    "totem",
    "celluloid",
    "smplayer",
    "dragon",
    "kodi",
})

_inibindo = False


def _find_focused(node: dict) -> dict | None:
    if node.get("focused"):
        return node
    for child in node.get("nodes", []) + node.get("floating_nodes", []):
        result = _find_focused(child)
        if result:
            return result
    return None


def get_focused_class() -> str:
    try:
        result = subprocess.run(
            ["i3-msg", "-t", "get_tree"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode != 0:
            return ""
        focused = _find_focused(json.loads(result.stdout))
        if not focused:
            return ""
        props = focused.get("window_properties") or {}
        return (props.get("class") or "").lower()
    except Exception:
        return ""


def get_playerctl_status() -> str:
    try:
        result = subprocess.run(
            ["playerctl", "status"],
            capture_output=True, text=True, timeout=2,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def xidlehook_control(action: str) -> None:
    try:
        subprocess.run(
            ["xidlehook-client", "--socket", SOCKET_XIDLEHOOK,
             "control", "--action", action],
            capture_output=True, timeout=2,
        )
    except Exception:
        pass


def should_inhibit() -> bool:
    cls = get_focused_class()
    if not any(media in cls for media in MEDIA_CLASSES):
        return False
    return get_playerctl_status() == "Playing"


def main() -> None:
    global _inibindo

    def handle_exit(*_: object) -> None:
        if _inibindo:
            xidlehook_control("Enable")
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    while True:
        inibir = should_inhibit()
        if inibir and not _inibindo:
            xidlehook_control("Disable")
            _inibindo = True
        elif not inibir and _inibindo:
            xidlehook_control("Enable")
            _inibindo = False
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
