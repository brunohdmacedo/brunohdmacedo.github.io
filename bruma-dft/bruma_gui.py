#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bruma: interface gráfica.

Mesma análise do bruma.py (linha de comando), com janelas: escolha a pasta do
cálculo CASTEP, marque as etapas e clique em Executar. As figuras aparecem na
aba Resultados. A aba Sobre traz o autor, os links e como citar.

    python3 bruma_gui.py          (requer Tkinter; Pillow é opcional, para a foto e as prévias)

Autor: Bruno Henrique Dourado Macedo · https://brunohdmacedo.tech/bruma/
"""
import contextlib
import io
import os
import queue
import re
import subprocess
import sys
import threading
import urllib.request
import webbrowser

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:          # Pillow é opcional
    Image = None

BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
import bruma  # noqa: E402  (o motor de análise)

ASSETS = os.path.join(BASE, "assets")
CACHE = os.path.join(os.path.expanduser("~"), ".bruma")

# cores da identidade visual (as mesmas do site)
C = dict(bg="#0B1211", card="#111B19", line="#1F2D2A", tx="#E8F1EE", mut="#93A8A2", cy="#4FE3C1", am="#F5B544", vi="#8B7CF6", ok="#7ee2a8", err="#ff7b72")


def asset(name):
    p = os.path.join(ASSETS, name)
    return p if os.path.exists(p) else None


# ícones embutidos: o logo aparece mesmo instalado via pip, sem a pasta assets
EMBUTIDOS = {
    "bruma-64.png": (
        "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"
    ),
    "bruma-128.png": (
        "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"
        "AElFTkSuQmCC"
    ),
}


def photo(name):
    """PhotoImage do arquivo em assets/ ou da cópia embutida."""
    p = asset(name)
    if p:
        return tk.PhotoImage(file=p)
    if name in EMBUTIDOS:
        return tk.PhotoImage(data=EMBUTIDOS[name])
    return None


def open_path(path):
    """Abre arquivo ou pasta no programa padrão do sistema."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Bruma", f"Não consegui abrir {path}:\n{e}")


class QueueWriter(io.TextIOBase):
    def __init__(self, q):
        self.q = q

    def write(self, s):
        if s:
            self.q.put(s)
        return len(s)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{bruma.NOME} {bruma.VERSAO}: {bruma.DESCRICAO}")
        self.geometry("1180x800")
        self.minsize(980, 660)
        self.configure(bg=C["bg"])
        self.q = queue.Queue()
        self._photo_ready = None
        self.running = False
        self.images = {}
        self._icon()
        self._style()
        self._header()
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        self.nb = nb
        self.tab_run = ttk.Frame(nb, style="Card.TFrame", padding=14)
        self.tab_res = ttk.Frame(nb, style="Card.TFrame", padding=14)
        self.tab_about = ttk.Frame(nb, style="Card.TFrame", padding=18)
        nb.add(self.tab_run, text="  Análise  ")
        nb.add(self.tab_res, text="  Resultados  ")
        nb.add(self.tab_about, text="  Sobre  ")
        self._build_run()
        self._build_results()
        self._build_about()
        self._footer()
        self.after(100, self._poll)

    # ------------------------------------------------------------------ visual
    def _icon(self):
        try:
            if sys.platform.startswith("win") and asset("bruma.ico"):
                self.iconbitmap(asset("bruma.ico"))
            self._ico = photo("bruma-64.png")
            if self._ico:
                self.iconphoto(True, self._ico)
        except Exception:
            pass

    def _style(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        f = ("Segoe UI", 10) if sys.platform.startswith("win") else ("DejaVu Sans", 10)
        self.font = f
        self.mono = ("Consolas", 9) if sys.platform.startswith("win") else ("DejaVu Sans Mono", 9)
        st.configure(".", background=C["card"], foreground=C["tx"], fieldbackground=C["bg"], bordercolor=C["line"], font=f)
        st.configure("TFrame", background=C["card"])
        st.configure("Card.TFrame", background=C["card"])
        st.configure("Bg.TFrame", background=C["bg"])
        st.configure("TLabel", background=C["card"], foreground=C["tx"])
        st.configure("Mut.TLabel", foreground=C["mut"])
        st.configure("Bg.TLabel", background=C["bg"], foreground=C["tx"])
        st.configure("BgMut.TLabel", background=C["bg"], foreground=C["mut"])
        st.configure("H.TLabel", font=(f[0], 12, "bold"))
        st.configure("Big.TLabel", background=C["bg"], font=(f[0], 20, "bold"))
        st.configure("TLabelframe", background=C["card"], bordercolor=C["line"])
        st.configure("TLabelframe.Label", background=C["card"], foreground=C["cy"], font=(f[0], 10, "bold"))
        st.configure("TNotebook", background=C["bg"], borderwidth=0)
        st.configure("TNotebook.Tab", background=C["bg"], foreground=C["mut"], padding=(14, 7), borderwidth=0)
        st.map("TNotebook.Tab", background=[("selected", C["card"])], foreground=[("selected", C["cy"])])
        st.configure("TButton", background=C["line"], foreground=C["tx"], padding=(12, 6), borderwidth=0)
        st.map("TButton", background=[("active", "#2a3b37")])
        st.configure("Accent.TButton", background=C["cy"], foreground="#04110D", font=(f[0], 10, "bold"))
        st.map("Accent.TButton", background=[("active", "#7AF0D5"), ("disabled", "#3b5550")])
        st.configure("Link.TButton", background=C["bg"], foreground=C["tx"], padding=(10, 5))
        st.map("Link.TButton", foreground=[("active", C["cy"])], background=[("active", C["line"])])
        st.configure("TCheckbutton", background=C["card"], foreground=C["tx"])
        st.map("TCheckbutton", background=[("active", C["card"])], indicatorcolor=[("selected", C["cy"])])
        st.configure("TEntry", fieldbackground=C["bg"], foreground=C["tx"], insertcolor=C["tx"])
        st.configure("TCombobox", fieldbackground=C["bg"], foreground=C["tx"], arrowcolor=C["tx"], background=C["line"])
        st.map("TCombobox", fieldbackground=[("readonly", C["bg"])], foreground=[("readonly", C["tx"])], selectbackground=[("readonly", C["bg"])], selectforeground=[("readonly", C["tx"])])
        self.option_add("*TCombobox*Listbox.background", C["bg"])
        self.option_add("*TCombobox*Listbox.foreground", C["tx"])
        st.configure("Horizontal.TProgressbar", background=C["cy"], troughcolor=C["bg"])

    def _header(self):
        h = ttk.Frame(self, style="Bg.TFrame", padding=(16, 12, 16, 8))
        h.pack(fill="x")
        self._logo = photo("bruma-64.png")
        if self._logo:
            tk.Label(h, image=self._logo, bg=C["bg"]).pack(side="left", padx=(0, 12))
        t = ttk.Frame(h, style="Bg.TFrame")
        t.pack(side="left")
        ttk.Label(t, text=f"{bruma.NOME}", style="Big.TLabel").pack(anchor="w")
        ttk.Label(t, text=f"versão {bruma.VERSAO} · {bruma.DESCRICAO}", style="BgMut.TLabel").pack(anchor="w")
        ttk.Button(h, text="Sobre e como citar", style="Link.TButton", command=lambda: self.nb.select(self.tab_about)).pack(side="right")
        ttk.Button(h, text="Tutorial", style="Link.TButton", command=lambda: webbrowser.open("https://brunohdmacedo.tech/bruma/tutorial.html")).pack(side="right", padx=6)

    def _footer(self):
        f = ttk.Frame(self, style="Bg.TFrame", padding=(16, 0, 16, 10))
        f.pack(fill="x")
        ttk.Label(f, text=f"{bruma.NOME} {bruma.VERSAO} · {bruma.AUTOR} · brunohdmacedo.tech/bruma", style="BgMut.TLabel").pack(side="left")
        self.status = ttk.Label(f, text="Pronto.", style="BgMut.TLabel")
        self.status.pack(side="right")

    # ---------------------------------------------------------------- análise
    def _build_run(self):
        fr = self.tab_run
        fr.columnconfigure(0, weight=0)
        fr.columnconfigure(1, weight=1)
        holder = ttk.Frame(fr)
        holder.grid(row=0, column=0, sticky="nsw", padx=(0, 14))
        cv = tk.Canvas(holder, bg=C["card"], highlightthickness=0, width=470)
        vs = ttk.Scrollbar(holder, orient="vertical", command=cv.yview)
        left = ttk.Frame(cv)
        win = cv.create_window((0, 0), window=left, anchor="nw")
        left.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfigure(win, width=e.width))
        cv.configure(yscrollcommand=vs.set)
        cv.pack(side="left", fill="y", expand=True)
        vs.pack(side="left", fill="y")
        def _wheel(e):
            cv.yview_scroll(int(-e.delta / 120) if e.delta else (-1 if e.num == 4 else 1), "units")
        for w_ in (cv, left):
            w_.bind("<Enter>", lambda e: (cv.bind_all("<MouseWheel>", _wheel), cv.bind_all("<Button-4>", _wheel), cv.bind_all("<Button-5>", _wheel)))
            w_.bind("<Leave>", lambda e: (cv.unbind_all("<MouseWheel>"), cv.unbind_all("<Button-4>"), cv.unbind_all("<Button-5>")))
        right = ttk.Frame(fr)
        right.grid(row=0, column=1, sticky="nsew")
        fr.rowconfigure(0, weight=1)

        self.v = {k: tk.StringVar(value=d) for k, d in dict(
            folder=os.getcwd(), seed="", elements="", sigma="0.05", ymin="-6", ymax="5", fermi="spin", fmt="png", dpi="300",
            ref="", sites="", labels="", field="rho", planes="todos", subtract="", diffsign="puro-defeito", outdir="").items()}
        self.b = {k: tk.BooleanVar(value=d) for k, d in dict(fat=True, defect=True, density=True, vesta=False, chgcar=False,
                                                             gen=False, down=False).items()}

        g = ttk.LabelFrame(left, text="Cálculo", padding=10)
        g.pack(fill="x", pady=(0, 10))
        ttk.Label(g, text="Pasta").grid(row=0, column=0, sticky="w")
        ttk.Entry(g, textvariable=self.v["folder"], width=34).grid(row=1, column=0, sticky="we")
        ttk.Button(g, text="Escolher…", command=self._pick_folder).grid(row=1, column=1, padx=(6, 0))
        ttk.Label(g, text="Seedname (cálculo)").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.cb_seed = ttk.Combobox(g, textvariable=self.v["seed"], width=32)
        self.cb_seed.grid(row=3, column=0, columnspan=2, sticky="we")
        ttk.Button(g, text="Abrir um arquivo .bands/.cell/.den_fmt…", command=self._pick_file).grid(row=4, column=0, columnspan=2, sticky="we", pady=(6, 0))

        o = ttk.LabelFrame(left, text="Opções", padding=10)
        o.pack(fill="x", pady=(0, 10))
        rows = [("Elementos da PDOS (ex.: Mg,H,Fe)", "elements"), ("Átomos individuais (ex.: Fe1,H25)", "sites"),
                ("Rótulos dos pontos k (ex.: G,X,M,G)", "labels")]
        r = 0
        for lab, key in rows:
            ttk.Label(o, text=lab).grid(row=r, column=0, columnspan=4, sticky="w")
            ttk.Entry(o, textvariable=self.v[key]).grid(row=r + 1, column=0, columnspan=4, sticky="we", pady=(0, 6))
            r += 2
        for i, (lab, key) in enumerate([("E mín (eV)", "ymin"), ("E máx (eV)", "ymax"), ("σ (eV)", "sigma"), ("dpi", "dpi")]):
            ttk.Label(o, text=lab).grid(row=r, column=i, sticky="w")
            ttk.Entry(o, textvariable=self.v[key], width=7).grid(row=r + 1, column=i, sticky="w", padx=(0, 6))
        r += 2
        ttk.Label(o, text="Referência de energia").grid(row=r, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Label(o, text="Formato").grid(row=r, column=2, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Combobox(o, textvariable=self.v["fermi"], values=["spin", "mean", "up", "down", "none"], width=10, state="readonly").grid(row=r + 1, column=0, columnspan=2, sticky="w")
        ttk.Combobox(o, textvariable=self.v["fmt"], values=["png", "svg", "pdf", "eps"], width=7, state="readonly").grid(row=r + 1, column=2, columnspan=2, sticky="w")
        o.columnconfigure(0, weight=1)

        s = ttk.LabelFrame(left, text="Etapas", padding=10)
        s.pack(fill="x", pady=(0, 10))
        for lab, key in [("Bandas projetadas (fat bands)", "fat"), ("Defeito, distorção e termodinâmica", "defect"),
                         ("Densidade de carga (se houver .den_fmt/CHGCAR)", "density"), ("Exportar pacote para o VESTA", "vesta"),
                         ("Exportar CHGCAR da grandeza escolhida", "chgcar"), ("Gerar os cálculos de referência (.cell/.param)", "gen"),
                         ("DOS de spin down negativa nos .dat", "down")]:
            ttk.Checkbutton(s, text=lab, variable=self.b[key]).pack(anchor="w")

        d = ttk.LabelFrame(left, text="Densidade e referência pura", padding=10)
        d.pack(fill="x")
        ttk.Label(d, text="Estrutura pura (seed, para defeito e Δρ)").grid(row=0, column=0, columnspan=2, sticky="w")
        self.cb_ref = ttk.Combobox(d, textvariable=self.v["ref"], width=32)
        self.cb_ref.grid(row=1, column=0, columnspan=2, sticky="we")
        ttk.Label(d, text="Grandeza").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(d, text="Planos").grid(row=2, column=1, sticky="w", pady=(6, 0))
        ttk.Combobox(d, textvariable=self.v["field"], values=["rho", "up", "down", "spin", "absm", "zeta", "diff"], width=10, state="readonly").grid(row=3, column=0, sticky="w")
        ttk.Entry(d, textvariable=self.v["planes"], width=18).grid(row=3, column=1, sticky="we")
        ttk.Label(d, text="Sentido de Δρ").grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Combobox(d, textvariable=self.v["diffsign"], values=["puro-defeito", "defeito-puro"], width=16, state="readonly").grid(row=5, column=0, columnspan=2, sticky="w")
        d.columnconfigure(1, weight=1)

        top = ttk.Frame(right)
        top.pack(fill="x")
        self.btn_run = ttk.Button(top, text="▶  Executar análise", style="Accent.TButton", command=self._run)
        self.btn_run.pack(side="left")
        ttk.Button(top, text="Abrir pasta de resultados", command=self._open_out).pack(side="left", padx=8)
        ttk.Button(top, text="Ver comando", command=self._show_cmd).pack(side="left")
        self.pb = ttk.Progressbar(top, mode="indeterminate", length=180)
        self.pb.pack(side="right")
        ttk.Label(right, text="Registro da execução", style="H.TLabel").pack(anchor="w", pady=(12, 4))
        self.log = tk.Text(right, bg=C["bg"], fg=C["tx"], insertbackground=C["tx"], relief="flat", font=self.mono, wrap="word",
                           highlightthickness=1, highlightbackground=C["line"])
        self.log.pack(fill="both", expand=True)
        self.log.tag_configure("err", foreground=C["err"])
        self.log.tag_configure("ok", foreground=C["ok"])
        self.log.tag_configure("hd", foreground=C["cy"])
        self._log(f"{bruma.NOME} {bruma.VERSAO} · {bruma.AUTOR}\nEscolha a pasta do cálculo CASTEP e clique em Executar.\n", "hd")
        self._scan()

    def _log(self, s, tag=None):
        self.log.insert("end", s, tag)
        self.log.see("end")

    def _scan(self):
        folder = self.v["folder"].get()
        seeds, dens = set(), set()
        try:
            for f in os.listdir(folder):
                m = re.match(r"(.+)\.(bands|cell|castep|den_fmt|pdos_bin)$", f)
                if m and not re.search(r"_(up|down)$", m.group(1)):
                    seeds.add(m.group(1))
        except OSError:
            pass
        seeds = sorted(seeds)
        self.cb_seed["values"] = seeds
        self.cb_ref["values"] = [""] + seeds
        if seeds and self.v["seed"].get() not in seeds:
            best = [s for s in seeds if os.path.exists(os.path.join(folder, s + ".bands"))]
            self.v["seed"].set((best or seeds)[0])
        if not self.v["ref"].get():
            pure = [s for s in seeds if re.search(r"pur|pristine|ref|limp|clean", s, re.I)]
            if pure:
                self.v["ref"].set(pure[0])

    def _pick_folder(self):
        d = filedialog.askdirectory(initialdir=self.v["folder"].get() or os.getcwd(), title="Pasta do cálculo CASTEP")
        if d:
            self.v["folder"].set(d)
            self.v["seed"].set("")
            self._scan()

    def _pick_file(self):
        f = filedialog.askopenfilename(title="Arquivo do cálculo", filetypes=[("CASTEP", "*.bands *.cell *.castep *.den_fmt *.pdos_bin"), ("Todos", "*.*")])
        if f:
            self.v["folder"].set(os.path.dirname(f))
            self.v["seed"].set(re.sub(r"\.(bands|cell|castep|den_fmt|pdos_bin)$", "", os.path.basename(f)))
            self._scan()

    def _argv(self):
        v, b = {k: x.get().strip() for k, x in self.v.items()}, {k: x.get() for k, x in self.b.items()}
        if not v["seed"]:
            raise ValueError("Escolha o seedname (o nome do cálculo).")
        a = [v["seed"], "--quiet", "--ymin", v["ymin"], "--ymax", v["ymax"], "-g", v["sigma"], "--fermi-ref", v["fermi"], "--format", v["fmt"], "--dpi", v["dpi"]]
        for key, opt in [("elements", "-e"), ("sites", "--sites"), ("labels", "--labels")]:
            if v[key]:
                a += [opt, v[key]]
        if not b["fat"]:
            a.append("--no-fatbands")
        if not b["defect"]:
            a.append("--no-defect")
        if b["down"]:
            a.append("--down-negative")
        if v["ref"]:
            a += ["--ref", v["ref"]]
        if b["density"]:
            a += ["--field", v["field"], "--diff-sign", v["diffsign"]]
            if v["planes"]:
                a += ["--planes", v["planes"]]
            if v["ref"] and os.path.exists(os.path.join(v["folder"], v["ref"] + ".den_fmt")):
                a += ["--subtract", v["ref"] + ".den_fmt"]
            if b["vesta"]:
                a.append("--vesta")
            if b["chgcar"]:
                a.append("--chgcar")
        if b["gen"]:
            a.append("--gerar-referencias")
        return a

    def _show_cmd(self):
        try:
            cmd = "python3 bruma.py " + " ".join(f'"{x}"' if " " in x else x for x in self._argv())
        except ValueError as e:
            messagebox.showwarning("Bruma", str(e))
            return
        self._log("\nComando equivalente no cluster:\n  " + cmd + "\n", "hd")

    def _run(self):
        if self.running:
            return
        try:
            argv = self._argv()
        except ValueError as e:
            messagebox.showwarning("Bruma", str(e))
            return
        folder = self.v["folder"].get()
        self.running = True
        self.btn_run.state(["disabled"])
        self.pb.start(12)
        self.status.configure(text="Executando…")
        self._log(f"\n▶ {folder}\n  bruma {' '.join(argv)}\n", "hd")

        def work():
            w = QueueWriter(self.q)
            old = os.getcwd()
            ok = True
            try:
                os.chdir(folder)
                with contextlib.redirect_stdout(w), contextlib.redirect_stderr(w):
                    bruma.main(argv)
            except SystemExit as e:
                ok = not e.code
                if e.code and not isinstance(e.code, int):
                    self.q.put(str(e.code) + "\n")
            except Exception as e:  # noqa: BLE001
                ok = False
                self.q.put(f"ERRO: {type(e).__name__}: {e}\n")
            finally:
                os.chdir(old)
                import matplotlib.pyplot as plt
                plt.close("all")
                self.q.put(("__fim__", ok))

        threading.Thread(target=work, daemon=True).start()

    def _poll(self):
        if self._photo_ready is not None:
            im, self._photo_ready = self._photo_ready, None
            self._show_photo(im)
        try:
            while True:
                m = self.q.get_nowait()
                if isinstance(m, tuple) and m[0] == "__fim__":
                    self.running = False
                    self.btn_run.state(["!disabled"])
                    self.pb.stop()
                    self.status.configure(text="Concluído." if m[1] else "Terminou com erro.")
                    self._log("\n✔ Concluído. Veja a aba Resultados.\n" if m[1] else "\n✖ A execução terminou com erro (veja acima).\n", "ok" if m[1] else "err")
                    self._refresh_results()
                    if m[1]:
                        self.nb.select(self.tab_res)
                else:
                    self._log(m, "err" if ("ERRO" in m or "Traceback" in m) else None)
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def _outdir(self):
        seed = self.v["seed"].get().strip()
        return os.path.join(self.v["folder"].get(), f"{seed}_plots")

    def _open_out(self):
        d = self._outdir()
        if os.path.isdir(d):
            open_path(d)
        else:
            messagebox.showinfo("Bruma", "Ainda não há resultados: execute a análise primeiro.")

    # -------------------------------------------------------------- resultados
    def _build_results(self):
        fr = self.tab_res
        fr.columnconfigure(1, weight=1)
        fr.rowconfigure(1, weight=1)
        ttk.Label(fr, text="Arquivos gerados", style="H.TLabel").grid(row=0, column=0, sticky="w")
        self.res_title = ttk.Label(fr, text="", style="Mut.TLabel")
        self.res_title.grid(row=0, column=1, sticky="w", padx=12)
        lf = ttk.Frame(fr)
        lf.grid(row=1, column=0, sticky="ns")
        self.lb = tk.Listbox(lf, width=42, bg=C["bg"], fg=C["tx"], selectbackground=C["cy"], selectforeground="#04110D", relief="flat",
                             highlightthickness=1, highlightbackground=C["line"], font=self.font, activestyle="none")
        self.lb.pack(side="left", fill="y")
        sb = ttk.Scrollbar(lf, command=self.lb.yview)
        sb.pack(side="left", fill="y")
        self.lb.configure(yscrollcommand=sb.set)
        self.lb.bind("<<ListboxSelect>>", self._preview)
        self.lb.bind("<Double-Button-1>", lambda e: self._open_sel())
        self.canvas = tk.Canvas(fr, bg="#ffffff", highlightthickness=1, highlightbackground=C["line"])
        self.canvas.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
        self.canvas.bind("<Configure>", lambda e: self._preview())
        bt = ttk.Frame(fr)
        bt.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Button(bt, text="Atualizar lista", command=self._refresh_results).pack(side="left")
        ttk.Button(bt, text="Abrir arquivo selecionado", command=self._open_sel).pack(side="left", padx=8)
        ttk.Button(bt, text="Abrir pasta", command=self._open_out).pack(side="left")
        ttk.Label(bt, text="Clique duas vezes num arquivo para abri-lo no programa padrão (Origin, editor, visualizador).", style="Mut.TLabel").pack(side="left", padx=12)
        self.files = []

    def _refresh_results(self):
        d = self._outdir()
        self.lb.delete(0, "end")
        self.files = []
        if os.path.isdir(d):
            for root, _, fs in os.walk(d):
                for f in sorted(fs):
                    p = os.path.join(root, f)
                    self.files.append(p)
            order = {".png": 0, ".svg": 1, ".pdf": 1, ".txt": 2, ".dat": 3}
            self.files.sort(key=lambda p: (order.get(os.path.splitext(p)[1], 4), p))
            for p in self.files:
                self.lb.insert("end", os.path.relpath(p, d))
        self.res_title.configure(text=f"{len(self.files)} arquivos em {d}" if self.files else "Nenhum resultado ainda.")
        pngs = [i for i, p in enumerate(self.files) if p.endswith(".png")]
        if pngs:
            self.lb.selection_clear(0, "end")
            self.lb.selection_set(pngs[0])
            self._preview()

    def _sel(self):
        s = self.lb.curselection()
        return self.files[s[0]] if s else None

    def _open_sel(self):
        p = self._sel()
        if p:
            open_path(p)

    def _preview(self, *_):
        p = self._sel()
        self.canvas.delete("all")
        W, H = max(50, self.canvas.winfo_width()), max(50, self.canvas.winfo_height())
        if not p:
            return
        if not p.lower().endswith(".png"):
            try:
                txt = open(p, encoding="utf-8", errors="replace").read(6000)
            except OSError:
                txt = ""
            self.canvas.create_text(12, 12, anchor="nw", text=txt, font=self.mono, fill="#1b2622", width=W - 24)
            return
        try:
            if Image:
                im = Image.open(p)
                im.thumbnail((W - 10, H - 10))
                ph = ImageTk.PhotoImage(im)
            else:
                ph = tk.PhotoImage(file=p)
                k = max(1, int(max(ph.width() / (W - 10), ph.height() / (H - 10)) + 0.999))
                ph = ph.subsample(k, k)
            self.images["prev"] = ph
            self.canvas.create_image(W // 2, H // 2, image=ph)
        except Exception as e:  # noqa: BLE001
            self.canvas.create_text(W // 2, H // 2, text=f"Sem prévia: {e}", fill="#1b2622")

    # -------------------------------------------------------------------- sobre
    def _build_about(self):
        fr = self.tab_about
        fr.columnconfigure(0, weight=1)
        fr.columnconfigure(1, weight=1)
        head = ttk.Frame(fr)
        head.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 14))
        self._logo_big = photo("bruma-128.png")
        if self._logo_big:
            tk.Label(head, image=self._logo_big, bg=C["card"]).pack(side="left", padx=(0, 16))
        t = ttk.Frame(head)
        t.pack(side="left", fill="x", expand=True)
        ttk.Label(t, text=f"{bruma.NOME}", font=(self.font[0], 24, "bold")).pack(anchor="w")
        ttk.Label(t, text=f"versão {bruma.VERSAO} · software livre · web, Python e Windows", style="Mut.TLabel").pack(anchor="w")
        ttk.Label(t, text="Bandas, DOS, PDOS, densidade de carga total e polarizada, defeitos e termodinâmica a partir de cálculos CASTEP, "
                          "com spin up e down e a energia de Fermi exatamente como o CASTEP escreveu.", wraplength=820, justify="left").pack(anchor="w", pady=(6, 0))

        au = ttk.LabelFrame(fr, text="Autor", padding=12)
        au.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        au.columnconfigure(1, weight=1)
        self._wrap_labels = []
        au.bind("<Configure>", lambda e: [w.configure(wraplength=max(180, e.width - 170)) for w in self._wrap_labels])
        self.photo = tk.Label(au, bg=C["card"])
        self.photo.grid(row=0, column=0, rowspan=3, sticky="n", padx=(0, 14))
        self._set_initials()
        nm = ttk.Label(au, text=bruma.AUTOR, font=(self.font[0], 12, "bold"))
        nm.grid(row=0, column=1, sticky="w")
        l1 = ttk.Label(au, text="Engenheiro Físico (UNILA) e mestrando em Física Aplicada (PPGFISA/UNILA), bolsista CNPq.", wraplength=330, justify="left", style="Mut.TLabel")
        l1.grid(row=1, column=1, sticky="w")
        l2 = ttk.Label(au, text="4 anos de iniciação científica em Ciência de Dados e Machine Learning e 3 anos em Ciência dos Materiais "
                           "com Deep Learning e DFT, com foco em sustentabilidade e novos materiais.", wraplength=330, justify="left")
        l2.grid(row=2, column=1, sticky="w", pady=(4, 0))
        self._wrap_labels = [nm, l1, l2]
        links = ttk.Frame(au)
        links.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))
        icons = {"Site": "🌐", "Bruma": "◈", "Codigo-fonte": "</>", "Lattes": "L", "ORCID": "iD", "Google Academico": "GS", "LinkedIn": "in",
                 "GitHub": "GH", "YouTube": "▶", "Instagram": "◎", "E-mail": "✉"}
        names = {"Codigo-fonte": "Código-fonte", "Google Academico": "Google Acadêmico"}
        for i, (n, u) in enumerate(bruma.LINKS):
            ttk.Button(links, text=f"{icons.get(n, '•')}  {names.get(n, n)}", style="Link.TButton", command=lambda u=u: webbrowser.open(u)).grid(row=i // 3, column=i % 3, sticky="we", padx=3, pady=3)

        ci = ttk.LabelFrame(fr, text="Como citar", padding=12)
        ci.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(ci, text="ABNT", style="H.TLabel").pack(anchor="w")
        abnt = tk.Text(ci, height=4, wrap="word", bg=C["bg"], fg=C["tx"], relief="flat", font=self.font, highlightthickness=0)
        abnt.insert("1.0", bruma.CITACAO_ABNT + " Acesso em: [data].")
        abnt.configure(state="disabled")
        abnt.pack(fill="x", pady=(2, 4))
        ttk.Button(ci, text="Copiar ABNT", command=lambda: self._copy(bruma.CITACAO_ABNT + " Acesso em: [data].")).pack(anchor="e")
        ttk.Label(ci, text="BibTeX", style="H.TLabel").pack(anchor="w", pady=(6, 0))
        bib = tk.Text(ci, height=8, wrap="none", bg=C["bg"], fg=C["tx"], relief="flat", font=self.mono, highlightthickness=0)
        bib.insert("1.0", bruma.CITACAO_BIBTEX)
        bib.configure(state="disabled")
        bib.pack(fill="both", expand=True, pady=(2, 4))
        ttk.Button(ci, text="Copiar BibTeX", command=lambda: self._copy(bruma.CITACAO_BIBTEX)).pack(anchor="e")
        ttk.Label(ci, text="Cite também o CASTEP: " + bruma.CITACAO_CASTEP, wraplength=460, justify="left", style="Mut.TLabel").pack(anchor="w", pady=(8, 0))
        fr.rowconfigure(1, weight=1)
        threading.Thread(target=self._load_photo, daemon=True).start()

    def _copy(self, txt):
        self.clipboard_clear()
        self.clipboard_append(txt)
        self.status.configure(text="Copiado para a área de transferência.")

    def _set_initials(self):
        c = tk.Canvas(self.photo, width=112, height=112, bg=C["card"], highlightthickness=0)
        c.create_oval(4, 4, 108, 108, outline=C["cy"], width=3, fill=C["bg"])
        c.create_text(56, 56, text="BM", fill=C["cy"], font=(self.font[0], 28, "bold"))
        c.pack()
        self._initials = c

    def _load_photo(self):
        """Foto do autor: a embutida no programa (assets/autor.*), a do cache ou a do Lattes (a mesma do site)."""
        if not Image:
            return
        cands = [asset("autor.jpg"), asset("autor.png"), os.path.join(CACHE, "autor.jpg")]
        path = next((p for p in cands if p and os.path.exists(p)), None)
        if not path:
            try:
                os.makedirs(CACHE, exist_ok=True)
                req = urllib.request.Request(bruma.FOTO_URL, headers={"User-Agent": "Bruma"})
                data = urllib.request.urlopen(req, timeout=8).read()
                path = os.path.join(CACHE, "autor.jpg")
                open(path, "wb").write(data)
            except Exception:
                return
        try:
            im = Image.open(path).convert("RGB")
            s = min(im.size)
            im = im.crop(((im.width - s) // 2, (im.height - s) // 4, (im.width + s) // 2, (im.height - s) // 4 + s)).resize((112, 112))
            mask = Image.new("L", (112, 112), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 111, 111), fill=255)
            out = Image.new("RGBA", (112, 112), (0, 0, 0, 0))
            out.paste(im, (0, 0), mask)
            self._photo_ready = out
        except Exception:
            pass

    def _show_photo(self, im):
        self.images["autor"] = ImageTk.PhotoImage(im)
        self._initials.destroy()
        tk.Label(self.photo, image=self.images["autor"], bg=C["card"]).pack()


def main():
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    App().mainloop()


if __name__ == "__main__":
    main()
