"""
carrossel.py
Responsabilidade única: gerenciar o estado de rolagem de texto para o módulo Polybar.
Estado persistido em $XDG_RUNTIME_DIR para não poluir o diretório do projeto.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def _caminho_estado() -> Path:
    base = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
    return Path(base) / "polybar-media-carrossel.json"


def _carregar_estado(caminho: Path) -> dict:
    try:
        dados = json.loads(caminho.read_text())
        if isinstance(dados, dict):
            return dados
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return {"titulo": "", "offset": 0, "ciclos_pausa": 0}


def _salvar_estado(caminho: Path, estado: dict) -> None:
    try:
        caminho.write_text(json.dumps(estado))
    except OSError:
        pass


class GerenciadorCarrossel:
    """
    Gerencia a janela deslizante de texto para o Polybar.

    A cada chamada de `proximo_frame`, avança o offset em 1 caractere
    (ou pausa se o título acabou de mudar).
    """

    def __init__(self, caminho: Path | None = None) -> None:
        self._caminho = caminho or _caminho_estado()

    def proximo_frame(
        self,
        titulo: str,
        largura: int = 30,
        pausa: int = 3,
    ) -> str:
        """
        Retorna a fatia do título a exibir no Polybar.

        - Se o título mudou: reseta offset e inicia pausa.
        - Durante a pausa: exibe os primeiros `largura` chars sem mover.
        - Se o título cabe na janela: exibe completo sem rolar.
        - Caso contrário: avança o offset e retorna a janela circular.
        """
        estado = _carregar_estado(self._caminho)
        titulo_limpo = titulo.strip()

        # Título trocou → resetar (este frame já conta como 1 ciclo de pausa)
        if titulo_limpo != estado.get("titulo", ""):
            estado = {"titulo": titulo_limpo, "offset": 0, "ciclos_pausa": max(0, pausa - 1)}
            _salvar_estado(self._caminho, estado)
            return titulo_limpo[:largura]

        # Título cabe inteiro → sem rolagem
        if len(titulo_limpo) <= largura:
            return titulo_limpo

        # Ainda na pausa inicial
        if estado.get("ciclos_pausa", 0) > 0:
            estado["ciclos_pausa"] -= 1
            _salvar_estado(self._caminho, estado)
            return titulo_limpo[:largura]

        # Rolar: texto circular com espaço separador entre fim e início
        separador = "   "
        texto_circular = titulo_limpo + separador
        comprimento = len(texto_circular)
        offset = estado.get("offset", 0) % comprimento

        # Extrai janela (com wrap)
        if offset + largura <= comprimento:
            frame = texto_circular[offset: offset + largura]
        else:
            sobra = (offset + largura) - comprimento
            frame = texto_circular[offset:] + texto_circular[:sobra]

        estado["offset"] = (offset + 1) % comprimento
        _salvar_estado(self._caminho, estado)
        return frame
