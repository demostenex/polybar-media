#!/usr/bin/env python3
"""
media_polybar.py
Entry point do módulo de mídia para o Polybar.
"""
from __future__ import annotations

import argparse
import sys

from adaptador_playerctl import AdaptadorPlayerctl, AdaptadorMidiaProtocol
from carrossel import GerenciadorCarrossel

# ---------------------------------------------------------------------------
# Ícones e cores (Nerd Font / Material Design Icons)
# ---------------------------------------------------------------------------

ICONE_PLAYING  = "\U000f040a"  # 󰐊  verde
ICONE_PAUSED   = "\U000f03e4"  # 󰏤  cinza
ICONE_SEM_MIDIA = "\U000f04c4" # 󰓄  cinza

COR_VERDE = "#00cc44"
COR_CINZA = "#888888"

LARGURA_CARROSSEL = 30
PAUSA_CARROSSEL   = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _formatar_module(status: str, titulo: str, carrossel: GerenciadorCarrossel) -> str:
    """Formata a linha de saída para o Polybar."""
    if status == "Playing":
        icone, cor = ICONE_PLAYING, COR_VERDE
    elif status in ("Paused", "Stopped"):
        icone, cor = ICONE_PAUSED, COR_CINZA
    else:
        return f"%{{F{COR_CINZA}}}{ICONE_SEM_MIDIA}%{{F-}} "

    frame = carrossel.proximo_frame(titulo, LARGURA_CARROSSEL, PAUSA_CARROSSEL)
    return f"%{{F{cor}}}{icone}%{{F-}} {frame} "


# ---------------------------------------------------------------------------
# Modos
# ---------------------------------------------------------------------------

def modo_module(adaptador: AdaptadorMidiaProtocol, carrossel: GerenciadorCarrossel) -> None:
    """Saída de uma linha para o Polybar. Nunca falha visivelmente."""
    try:
        status = adaptador.get_status()
        titulo = adaptador.get_titulo() if status else ""
        print(_formatar_module(status, titulo, carrossel))
    except Exception:  # noqa: BLE001
        print(f"%{{F{COR_CINZA}}}{ICONE_SEM_MIDIA}%{{F-}} ")


def modo_play_pause(adaptador: AdaptadorMidiaProtocol) -> None:
    adaptador.play_pause()


def modo_proximo(adaptador: AdaptadorMidiaProtocol) -> None:
    adaptador.proximo()


def modo_anterior(adaptador: AdaptadorMidiaProtocol) -> None:
    adaptador.anterior()


def modo_avancar(adaptador: AdaptadorMidiaProtocol, segundos: int = 5) -> None:
    adaptador.avancar(segundos)


def modo_retroceder(adaptador: AdaptadorMidiaProtocol, segundos: int = 5) -> None:
    adaptador.retroceder(segundos)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

MODOS = ["module", "play-pause", "next", "previous", "forward", "backward"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Módulo de mídia para Polybar")
    parser.add_argument(
        "--mode",
        choices=MODOS,
        default="module",
        help="Modo de operação",
    )
    parser.add_argument(
        "--segundos",
        type=int,
        default=5,
        help="Segundos para avançar/retroceder (padrão: 5)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    adaptador = AdaptadorPlayerctl()
    carrossel = GerenciadorCarrossel()

    mapa = {
        "module":     lambda: modo_module(adaptador, carrossel),
        "play-pause": lambda: modo_play_pause(adaptador),
        "next":       lambda: modo_proximo(adaptador),
        "previous":   lambda: modo_anterior(adaptador),
        "forward":    lambda: modo_avancar(adaptador, args.segundos),
        "backward":   lambda: modo_retroceder(adaptador, args.segundos),
    }

    mapa[args.mode]()


if __name__ == "__main__":
    main()
