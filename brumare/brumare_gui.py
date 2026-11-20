#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo
# BrUMaRe: Brillouin-zone Utilities for Materials Research - https://github.com/brunohdmacedo/brumare
"""BrUMaRe: aplicativo de computador, com a MESMA interface do site.

Abre a interface web do BrUMaRe (brumare_app/web: as mesmas abas, gráficos interativos,
3D, comparação, diferença de densidade, CASTEP/VASP/SIESTA) numa janela nativa,
sem internet:
  * Windows: motor do Edge (WebView2, já presente no Windows 10 e 11);
  * Linux: Qt WebEngine ou GTK WebKit;  * macOS: WebKit.
Se a janela nativa não estiver disponível, abre a mesma interface no navegador padrão,
servida localmente (nada sai do computador).

    brumare-gui                 (ou: python3 brumare_gui.py)
    brumare-gui --navegador     (força o navegador)
    brumare-gui --sobre         (autor e como citar)

Autor: Bruno Henrique Dourado Macedo · https://brunohdmacedo.tech/brumare/
"""
import argparse
import functools
import http.server
import os
import socket
import sys
import threading
import webbrowser

BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
import brumare  # noqa: E402  (identificação: nome, versão, autor, citação)
from brumare_app import web_dir  # noqa: E402

TITULO = f"{brumare.NOME} {brumare.VERSAO} · bandas, DOS, densidade e defeitos (CASTEP, VASP, SIESTA)"
DADOS = os.path.join(os.path.expanduser("~"), ".brumare")


def icone():
    for p in (os.path.join(BASE, "assets", "brumare-256.png"), os.path.join(web_dir(), "assets", "brumare-512.png")):
        if os.path.isfile(p):
            return p
    return None


class _Silencioso(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript", ".mjs": "text/javascript",
                      ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".svg": "image/svg+xml", ".cff": "text/plain; charset=utf-8",
                      ".bib": "text/plain; charset=utf-8", ".html": "text/html; charset=utf-8"}

    def log_message(self, *a):
        pass


def servidor_local(porta=0):
    """Serve brumare_app/web em 127.0.0.1 (só esta máquina). Devolve (servidor, url)."""
    handler = functools.partial(_Silencioso, directory=web_dir())
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", porta), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/index.html"


def no_navegador(porta=0, motivo="", idioma=None):
    srv, url = servidor_local(porta)
    if idioma:
        url += f"?lang={idioma}"
    print(f" {TITULO}\n Abrindo no navegador: {url}" + (f"\n ({motivo})" if motivo else ""))
    webbrowser.open(url)
    try:                                       # pequena janela para encerrar (útil no .exe sem console)
        import tkinter as tk
        r = tk.Tk(); r.title(f"{brumare.NOME} {brumare.VERSAO}")
        tk.Label(r, text=f"O {brumare.NOME} está aberto no navegador:\n{url}\n\nFeche esta janela para encerrar.", padx=24, pady=18, justify="center").pack()
        tk.Button(r, text="Abrir de novo no navegador", command=lambda: webbrowser.open(url)).pack(pady=(0, 6))
        tk.Button(r, text="Encerrar", command=r.destroy).pack(pady=(0, 16))
        r.mainloop()
    except Exception:
        print(" Pressione Ctrl+C para encerrar.")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
    srv.shutdown()


def tamanho_janela(webview):
    """Janela proporcional à tela: 85 % x 88 %, maximizada em notebooks pequenos (<= 1366 px).
    A interface é responsiva, então funciona de 640 x 480 até monitores 4K."""
    try:
        sc = webview.screens[0]
        sw, sh = int(sc.width), int(sc.height)
    except Exception:
        return 1440, 920, False
    W = max(800, min(int(sw * 0.85), 2560))
    H = max(600, min(int(sh * 0.88), 1600))
    return W, H, sw <= 1366


def janela(debug=False, idioma=None):
    import webview
    webview.settings["ALLOW_DOWNLOADS"] = True                   # exportações: PNG, .dat, CHGCAR, .zip
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True    # site, tutorial online, redes sociais
    os.makedirs(DADOS, exist_ok=True)
    W, H, maxi = tamanho_janela(webview)
    webview.create_window(TITULO, url=os.path.join(web_dir(), "index.html"), width=W, height=H, min_size=(640, 480),
                          maximized=maxi, text_select=True)
    if idioma:                                                   # abre direto no idioma pedido (a escolha fica guardada)
        def _lang(w=webview.windows[0]):
            w.evaluate_js(f"window.BrUMaReI18n && BrUMaReI18n.setLang('{idioma}')")
        webview.windows[0].events.loaded += _lang
    webview.start(http_server=True, private_mode=False, storage_path=os.path.join(DADOS, "webview"), icon=icone(), debug=debug)


def main(argv=None):
    p = argparse.ArgumentParser(prog="brumare-gui", description=f"{TITULO}. A mesma interface do site, sem internet.")
    p.add_argument("--navegador", action="store_true", help="abrir no navegador padrão em vez da janela nativa")
    p.add_argument("--porta", type=int, default=0, help="porta local para o modo navegador (padrão: livre)")
    p.add_argument("--debug", action="store_true", help="ferramentas de desenvolvedor na janela")
    p.add_argument("--sobre", action="store_true", help="autor, links e como citar")
    p.add_argument("--idioma", "--lang", choices=["pt", "en", "es", "fr", "it", "la"], help="idioma da interface: pt, en, es, fr, it ou la (latim)")
    p.add_argument("--versao", "--version", action="version", version=f"{brumare.NOME} {brumare.VERSAO}")
    a = p.parse_args(argv)
    if a.idioma:
        brumare.LANG["v"] = a.idioma
    if a.sobre:
        print(brumare.sobre_texto())
        return
    if a.navegador:
        return no_navegador(a.porta, idioma=a.idioma)
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    try:
        janela(a.debug, a.idioma)
    except Exception as e:                                       # sem pywebview / sem WebView2 / sem Qt/GTK
        no_navegador(a.porta, motivo=f"janela nativa indisponível: {type(e).__name__}: {e}", idioma=a.idioma)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
