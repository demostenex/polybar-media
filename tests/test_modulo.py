"""
tests/test_modulo.py
Testes unitários para media_polybar.py (mock de adaptador e carrossel).
"""
from __future__ import annotations

import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from media_polybar import (  # noqa: E402
    _formatar_module,
    modo_module,
    modo_play_pause,
    modo_proximo,
    modo_anterior,
    modo_avancar,
    modo_retroceder,
    ICONE_PLAYING,
    ICONE_PAUSED,
    ICONE_SEM_MIDIA,
    COR_VERDE,
    COR_CINZA,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_adaptador(status="Playing", titulo="Titulo"):
    a = MagicMock()
    a.get_status.return_value = status
    a.get_titulo.return_value = titulo
    return a


def _make_carrossel(frame="Titulo"):
    c = MagicMock()
    c.proximo_frame.return_value = frame
    return c


# ---------------------------------------------------------------------------
# _formatar_module
# ---------------------------------------------------------------------------

class TestFormatarModule:
    def test_playing_contem_icone_e_cor_verde(self):
        saida = _formatar_module("Playing", "Musica", _make_carrossel("Musica"))
        assert ICONE_PLAYING in saida
        assert COR_VERDE in saida

    def test_paused_contem_icone_e_cor_cinza(self):
        saida = _formatar_module("Paused", "Musica", _make_carrossel("Musica"))
        assert ICONE_PAUSED in saida

    def test_stopped_contem_icone_e_cor_cinza(self):
        saida = _formatar_module("Stopped", "Musica", _make_carrossel("Musica"))
        assert ICONE_PAUSED in saida
        assert COR_CINZA in saida

    def test_sem_midia_contem_icone_sem_midia(self):
        saida = _formatar_module("", "", _make_carrossel())
        assert ICONE_SEM_MIDIA in saida

    def test_playing_contem_frame_do_carrossel(self):
        saida = _formatar_module("Playing", "Qualquer", _make_carrossel("Frame Esperado"))
        assert "Frame Esperado" in saida

    def test_saida_tem_espaco_final(self):
        for status in ("Playing", "Paused", ""):
            saida = _formatar_module(status, "T", _make_carrossel("T"))
            assert saida.rstrip("\n").endswith(" ")

    def test_carrossel_nao_chamado_sem_midia(self):
        carrossel = _make_carrossel()
        _formatar_module("", "", carrossel)
        carrossel.proximo_frame.assert_not_called()


# ---------------------------------------------------------------------------
# modo_module
# ---------------------------------------------------------------------------

class TestModoModule:
    def test_saida_playing(self, capsys):
        adaptador = _make_adaptador("Playing", "Musica X")
        carrossel = _make_carrossel("Musica X")
        modo_module(adaptador, carrossel)
        out = capsys.readouterr().out
        assert ICONE_PLAYING in out
        assert COR_VERDE in out

    def test_saida_paused(self, capsys):
        adaptador = _make_adaptador("Paused", "Musica X")
        carrossel = _make_carrossel("Musica X")
        modo_module(adaptador, carrossel)
        out = capsys.readouterr().out
        assert ICONE_PAUSED in out

    def test_saida_sem_midia(self, capsys):
        adaptador = _make_adaptador("", "")
        carrossel = _make_carrossel()
        modo_module(adaptador, carrossel)
        out = capsys.readouterr().out
        assert ICONE_SEM_MIDIA in out

    def test_status_vazio_nao_chama_get_titulo(self):
        adaptador = _make_adaptador("", "")
        carrossel = _make_carrossel()
        modo_module(adaptador, carrossel)
        adaptador.get_titulo.assert_not_called()

    def test_erro_nao_explode(self, capsys):
        adaptador = MagicMock()
        adaptador.get_status.side_effect = Exception("erro inesperado")
        carrossel = _make_carrossel()
        modo_module(adaptador, carrossel)
        out = capsys.readouterr().out
        assert ICONE_SEM_MIDIA in out

    def test_saida_tem_newline_final(self, capsys):
        adaptador = _make_adaptador("Playing", "Musica")
        carrossel = _make_carrossel("Musica")
        modo_module(adaptador, carrossel)
        out = capsys.readouterr().out
        assert out.endswith("\n")


# ---------------------------------------------------------------------------
# Modos de controle
# ---------------------------------------------------------------------------

class TestModosControle:
    def test_play_pause_chama_adaptador(self):
        a = _make_adaptador()
        modo_play_pause(a)
        a.play_pause.assert_called_once()

    def test_proximo_chama_adaptador(self):
        a = _make_adaptador()
        modo_proximo(a)
        a.proximo.assert_called_once()

    def test_anterior_chama_adaptador(self):
        a = _make_adaptador()
        modo_anterior(a)
        a.anterior.assert_called_once()

    def test_avancar_chama_com_segundos(self):
        a = _make_adaptador()
        modo_avancar(a, 10)
        a.avancar.assert_called_once_with(10)

    def test_retroceder_chama_com_segundos(self):
        a = _make_adaptador()
        modo_retroceder(a, 7)
        a.retroceder.assert_called_once_with(7)
