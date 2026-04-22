"""
tests/test_adaptador.py
Testes unitários para adaptador_playerctl.py (mock de subprocess).
"""
from __future__ import annotations

import pathlib
import sys
from unittest.mock import MagicMock, patch, call

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from adaptador_playerctl import AdaptadorPlayerctl  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_run(stdout: str = "", returncode: int = 0):
    m = MagicMock()
    m.stdout = stdout
    m.returncode = returncode
    return m


@pytest.fixture()
def adaptador():
    return AdaptadorPlayerctl()


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------

class TestGetStatus:
    def test_playing(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run("Playing\n")):
            assert adaptador.get_status() == "Playing"

    def test_paused(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run("Paused\n")):
            assert adaptador.get_status() == "Paused"

    def test_sem_player_returncode_nonzero(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run("", returncode=1)):
            assert adaptador.get_status() == ""

    def test_playerctl_ausente(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", side_effect=FileNotFoundError):
            assert adaptador.get_status() == ""

    def test_timeout(self, adaptador):
        import subprocess
        with patch("adaptador_playerctl.subprocess.run", side_effect=subprocess.TimeoutExpired("playerctl", 2)):
            assert adaptador.get_status() == ""


# ---------------------------------------------------------------------------
# get_titulo
# ---------------------------------------------------------------------------

class TestGetTitulo:
    def test_retorna_titulo(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run("Bohemian Rhapsody\n")):
            assert adaptador.get_titulo() == "Bohemian Rhapsody"

    def test_titulo_vazio_sem_player(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run("", returncode=1)):
            assert adaptador.get_titulo() == ""

    def test_playerctl_ausente(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", side_effect=FileNotFoundError):
            assert adaptador.get_titulo() == ""

    def test_comando_correto(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run("titulo")) as mock:
            adaptador.get_titulo()
        cmd = mock.call_args[0][0]
        assert cmd == ["playerctl", "metadata", "--format", "{{title}}"]


# ---------------------------------------------------------------------------
# Comandos de controle
# ---------------------------------------------------------------------------

class TestControles:
    def test_play_pause_chama_playerctl(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run()) as mock:
            adaptador.play_pause()
        cmd = mock.call_args[0][0]
        assert "play-pause" in cmd

    def test_proximo_chama_next(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run()) as mock:
            adaptador.proximo()
        cmd = mock.call_args[0][0]
        assert "next" in cmd

    def test_anterior_chama_previous(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run()) as mock:
            adaptador.anterior()
        cmd = mock.call_args[0][0]
        assert "previous" in cmd

    def test_avancar_posicao(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run()) as mock:
            adaptador.avancar(10)
        cmd = mock.call_args[0][0]
        assert "position" in cmd
        assert "10+" in cmd

    def test_retroceder_posicao(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", return_value=_mock_run()) as mock:
            adaptador.retroceder(5)
        cmd = mock.call_args[0][0]
        assert "position" in cmd
        assert "5-" in cmd

    def test_controle_sem_player_nao_explode(self, adaptador):
        with patch("adaptador_playerctl.subprocess.run", side_effect=FileNotFoundError):
            adaptador.play_pause()   # não deve levantar exceção
            adaptador.proximo()
            adaptador.anterior()
