# media-polybar

Módulo de controle de mídia para o [Polybar](https://github.com/polybar/polybar), exibindo
título e status da mídia em reprodução nos navegadores (Zen/Firefox, Brave/Chromium) via MPRIS.

## Dependências

- [`playerctl`](https://github.com/altdesktop/playerctl) — controle MPRIS
  - Arch: `sudo pacman -S playerctl`
  - Ubuntu/Debian: `sudo apt install playerctl`
- Python 3.10+
- Nerd Font com Material Design Icons

## Instalação

```bash
cp media_polybar.py adaptador_playerctl.py carrossel.py \
   ~/.config/polybar/scripts/
```

## Configuração no Polybar

Copie o conteúdo de `polybar-module.ini` para o seu `config.ini` e adicione
`midia` na linha `modules-left`, `modules-center` ou `modules-right`.

## Comportamento

- Exibe ícone + título da mídia em reprodução
- Títulos com mais de 30 caracteres rolam como carrossel (1 char/2s)
- Ao trocar de mídia, pausa 6 segundos antes de começar a rolar
- Clique esquerdo: play/pause
- Clique direito: próxima mídia
- Clique do meio: mídia anterior
- Scroll para cima/baixo: avança/retrocede 5 segundos

## Testes

```bash
python -m pytest tests/ -v
```
