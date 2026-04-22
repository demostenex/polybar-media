"""
adaptador_playerctl.py
Responsabilidade única: comunicação com players MPRIS via playerctl.
"""
from __future__ import annotations

import subprocess
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Protocolo — permite substituição por mock nos testes
# ---------------------------------------------------------------------------

@runtime_checkable
class AdaptadorMidiaProtocol(Protocol):
    def get_status(self) -> str: ...
    def get_titulo(self) -> str: ...
    def play_pause(self) -> None: ...
    def proximo(self) -> None: ...
    def anterior(self) -> None: ...
    def avancar(self, segundos: int = 5) -> None: ...
    def retroceder(self, segundos: int = 5) -> None: ...


# ---------------------------------------------------------------------------
# Implementação real (playerctl)
# ---------------------------------------------------------------------------

class AdaptadorPlayerctl:
    """Implementação via playerctl (suporta MPRIS: Firefox, Brave, etc.)."""

    def _run(self, *args: str) -> str:
        try:
            resultado = subprocess.run(
                ["playerctl", *args],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if resultado.returncode != 0:
                return ""
            return resultado.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return ""

    def _run_cmd(self, *args: str) -> None:
        """Executa comando playerctl sem capturar saída."""
        try:
            subprocess.run(
                ["playerctl", *args],
                capture_output=True,
                timeout=2,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

    def get_status(self) -> str:
        """Retorna 'Playing', 'Paused' ou '' se nenhum player ativo."""
        return self._run("status")

    def get_titulo(self) -> str:
        """Retorna o título da mídia atual ou '' se indisponível."""
        return self._run("metadata", "--format", "{{title}}")

    def play_pause(self) -> None:
        self._run_cmd("play-pause")

    def proximo(self) -> None:
        self._run_cmd("next")

    def anterior(self) -> None:
        self._run_cmd("previous")

    def avancar(self, segundos: int = 5) -> None:
        self._run_cmd("position", f"{segundos}+")

    def retroceder(self, segundos: int = 5) -> None:
        self._run_cmd("position", f"{segundos}-")
