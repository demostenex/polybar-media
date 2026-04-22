"""
tests/test_carrossel.py
Testes unitários para carrossel.py (mock de filesystem via tmp_path).
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from carrossel import GerenciadorCarrossel  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def caminho(tmp_path):
    return tmp_path / "carrossel.json"


@pytest.fixture()
def carrossel(caminho):
    return GerenciadorCarrossel(caminho=caminho)


# ---------------------------------------------------------------------------
# Título curto (≤ largura) — sem rolagem
# ---------------------------------------------------------------------------

class TestTituloCurto:
    def test_retorna_titulo_completo(self, carrossel):
        assert carrossel.proximo_frame("Ola", largura=30) == "Ola"

    def test_titulo_exato_largura_nao_rola(self, carrossel):
        titulo = "A" * 30
        assert carrossel.proximo_frame(titulo, largura=30) == titulo

    def test_chamadas_repetidas_sem_mudanca(self, carrossel):
        for _ in range(10):
            frame = carrossel.proximo_frame("Curto", largura=30)
            assert frame == "Curto"


# ---------------------------------------------------------------------------
# Título longo — pausa antes de rolar
# ---------------------------------------------------------------------------

class TestTituloLongo:
    TITULO = "Bohemian Rhapsody - Queen (Official Video Remastered)"  # 53 chars

    def test_primeira_chamada_retorna_inicio(self, carrossel):
        frame = carrossel.proximo_frame(self.TITULO, largura=30, pausa=3)
        assert frame == self.TITULO[:30]

    def test_durante_pausa_nao_avanca(self, carrossel):
        frames = [carrossel.proximo_frame(self.TITULO, largura=30, pausa=3) for _ in range(3)]
        # Todos os frames da pausa devem ser iguais (início do título)
        assert all(f == self.TITULO[:30] for f in frames)

    def test_apos_pausa_comeca_a_rolar(self, carrossel):
        # Consome os 3 ciclos de pausa (reset conta como 1, mais 2 decrementos)
        for _ in range(3):
            carrossel.proximo_frame(self.TITULO, largura=30, pausa=3)
        # Primeiro frame rolante (offset=0) e segundo (offset=1)
        carrossel.proximo_frame(self.TITULO, largura=30, pausa=3)  # offset=0
        frame = carrossel.proximo_frame(self.TITULO, largura=30, pausa=3)  # offset=1
        assert frame == self.TITULO[1:31]

    def test_rolagem_avanca_um_por_chamada(self, carrossel):
        # Consome pausa
        for _ in range(3):
            carrossel.proximo_frame(self.TITULO, largura=30, pausa=3)
        # Primeiro frame rolante está em offset=0, segundo em offset=1
        carrossel.proximo_frame(self.TITULO, largura=30, pausa=3)  # offset=0
        frame1 = carrossel.proximo_frame(self.TITULO, largura=30, pausa=3)  # offset=1
        frame2 = carrossel.proximo_frame(self.TITULO, largura=30, pausa=3)  # offset=2
        assert frame1 == self.TITULO[1:31]
        assert frame2 == self.TITULO[2:32]


# ---------------------------------------------------------------------------
# Troca de título — reset de estado
# ---------------------------------------------------------------------------

class TestTrocaDeTitulo:
    def test_novo_titulo_reseta_offset(self, carrossel):
        titulo_a = "A" * 50
        titulo_b = "B" * 50
        # Avança alguns frames com titulo_a
        for _ in range(5):
            carrossel.proximo_frame(titulo_a, largura=30, pausa=0)
        # Troca para titulo_b — deve resetar
        frame = carrossel.proximo_frame(titulo_b, largura=30, pausa=0)
        assert frame == titulo_b[:30]

    def test_novo_titulo_reinicia_pausa(self, carrossel, caminho):
        titulo = "X" * 50
        # Esgota a pausa
        for _ in range(4):
            carrossel.proximo_frame(titulo, largura=30, pausa=3)
        # Troca de título → pausa reinicia
        novo = "Y" * 50
        for _ in range(3):
            frame = carrossel.proximo_frame(novo, largura=30, pausa=3)
        assert frame == novo[:30]


# ---------------------------------------------------------------------------
# Wrap circular
# ---------------------------------------------------------------------------

class TestWrapCircular:
    def test_wrap_apos_fim_do_titulo(self, carrossel):
        # titulo > largura para ativar rolagem
        # texto_circular = "ABCDE   " (len=8)
        # offset=5 → wrap: "   " + "A" = "   A"
        titulo = "ABCDE"  # 5 chars > largura=4
        largura = 4
        pausa = 0
        frames = [carrossel.proximo_frame(titulo, largura=largura, pausa=pausa) for _ in range(10)]
        # frames[6] corresponde ao offset=5 (com wrap circular)
        assert frames[6] == "   A"

    def test_frame_nunca_maior_que_largura(self, carrossel):
        titulo = "Titulo bem longo para testar o limite de caracteres do carrossel"
        for _ in range(20):
            frame = carrossel.proximo_frame(titulo, largura=30, pausa=0)
            assert len(frame) <= 30


# ---------------------------------------------------------------------------
# Estado persistido
# ---------------------------------------------------------------------------

class TestEstadoPersistido:
    def test_estado_salvo_em_arquivo(self, carrossel, caminho):
        carrossel.proximo_frame("Titulo", largura=30, pausa=3)
        assert caminho.exists()
        dados = json.loads(caminho.read_text())
        assert dados["titulo"] == "Titulo"

    def test_estado_carregado_entre_instancias(self, caminho):
        c1 = GerenciadorCarrossel(caminho=caminho)
        titulo = "T" * 50
        # Esgota pausa com primeira instância
        for _ in range(4):
            c1.proximo_frame(titulo, largura=30, pausa=3)
        # Segunda instância deve continuar do offset salvo
        c2 = GerenciadorCarrossel(caminho=caminho)
        frame = c2.proximo_frame(titulo, largura=30, pausa=3)
        assert frame == titulo[1:31]

    def test_arquivo_corrompido_reseta_estado(self, caminho, carrossel):
        caminho.write_text("{ invalido json")
        frame = carrossel.proximo_frame("Titulo Novo", largura=30, pausa=3)
        assert frame == "Titulo Novo"
