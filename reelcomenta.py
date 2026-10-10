#!/usr/bin/env python3
"""reelcomenta — um reel de terceiro vira o SEU reel comentado:
o vídeo original passa com a música dele baixa, o avatar do Nei comenta no canto,
os números entram num painel com a fonte, vem a pergunta e o fecho com os cursos grátis do inema.club.

  reelcomenta.py novo <link> [--id slug]   baixa o reel, transcreve e cria edicoes/<data>-<slug>/roteiro.yaml
  reelcomenta.py previa <pasta>            quadros de prévia com tempo estimado (antes do avatar)
  reelcomenta.py avatar <pasta>            manda a fala ao estúdio do HeyGen (exige APROVADO_HEYGEN) e espera o MP4
  reelcomenta.py montar <pasta>            monta o vídeo final (<pasta>/video.mp4)
  reelcomenta.py conferir <pasta>          folha de quadros + volume (conferência antes de enviar)
  reelcomenta.py enviar <pasta> [texto]    manda o vídeo pelo bot do Telegram (v3)
"""
import glob, json, math, os, re, shutil, subprocess, sys, time, unicodedata, urllib.request
from datetime import date
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

HOME = Path.home()
RAIZ = Path(__file__).resolve().parent
CFG = {
    "cardshorts": Path(os.environ.get("RC_CARDSHORTS", HOME / "projetos/cardshorts")),
    "explicavideos": Path(os.environ.get("RC_EXPLICAVIDEOS", HOME / "projetos/explicavideos")),
    "inemavox": Path(os.environ.get("RC_INEMAVOX", HOME / "projetos/inemavox")),
    "perfil_heygen": Path(os.environ.get("RC_PERFIL_HEYGEN", HOME / ".cache/inemaccbot/perfil-heygen")),
    "template_heygen": os.environ.get("RC_TEMPLATE_HEYGEN", "TEMPLATE-AVATAR16"),
    "portal_dados": Path(os.environ.get("RC_PORTAL_DADOS", HOME / "projetos/portal/src/data/courses.data.json")),
    "capas": Path(os.environ.get("RC_CAPAS", HOME / ".cache/reelcomenta/capas")),
    "musica_reserva": Path(os.environ.get("RC_MUSICA", HOME / "projetos/cardshorts/musicas/tensa.mp3")),
    "display": os.environ.get("RC_DISPLAY", ":99"),
}
sys.path.insert(0, str(CFG["cardshorts"]))
import cardshorts as cs  # noqa: E402  (transcrição com tempo por palavra, norm() e envio ao Telegram)

W, H, FPS = 1080, 1920, 30
F = HOME / ".local/share/fonts"
ANTON = str(F / "Anton-Regular.ttf"); MBLK = str(F / "Montserrat-Black.ttf"); MXB = str(F / "Montserrat-ExtraBold.ttf")
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CORES = {"ambar": (226, 162, 59), "vermelho": (255, 64, 48), "branco": (255, 255, 255)}
AMB, VERM, BRANCO, ESC = CORES["ambar"], CORES["vermelho"], CORES["branco"], (11, 15, 20)
# caixa do avatar (layout canto): rosto 400x453 em x=640, y=1290
AVX, AVY, AVW, AVH = 640, 1290, 400, 453


def log(*a):
    print("[reelcomenta]", *a, flush=True)


def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "reel"


def total_cursos():
    try:
        return len(json.loads(CFG["portal_dados"].read_text())["platformsData"])
    except Exception:
        return 300


def vars_texto():
    n = total_cursos()
    return {"cursos": n, "cursos_100": (n // 100) * 100, "hoje": date.today().strftime("%d/%m/%Y")}


def fmt(s):
    if not isinstance(s, str):
        return s
    v = vars_texto()  # só {nome} conhecido; o {} do contador fica intacto
    return re.sub(r"\{(\w+)\}", lambda m: str(v.get(m.group(1), m.group(0))), s)


# ======================================================================= novo
MODELO = """# reelcomenta — roteiro da edição {pasta}
# 1) Assista ref/folha.jpg e leia ref/transcricao.txt.  2) Pesquise os números (fonte de verdade, com ano).
# 3) Escreva a fala no tom do Nei: direto, "tu", pergunta ao espectador; ANO E NÚMERO POR EXTENSO na fala.
# 4) As âncoras são palavras da fala (minúsculas, sem acento) que disparam cada tela.
link: {link}
data: "{hoje}"                 # sempre dd/mm/aaaa no quadro 0
lento: {{de: 0, ate: 0}}         # trecho do reel repetido em câmera lenta depois da 1ª passada (0/0 = reel inteiro)
fala: |
  Olha isso. ...
abertura: {{linha1: "O ROBÔ JÁ", linha2: "SUBIU NO PALCO", cor: ambar}}
painel_inicial: {{titulo: "IA + ROBÔS", texto: "o que os números\\ndizem sobre o\\nteu emprego"}}
manchete_numeros: {{linha1: "E NÃO É SÓ", linha2: "DANÇA", cor: vermelho}}
cartoes:                       # entram na ordem; {{}} no número = contador animado até 'conta'
  - {{ancora: noventa, numero: "{{}} MILHÕES", conta: 92, rotulo: "de empregos eliminados\\naté 2030", fonte: "Fórum Econômico Mundial · 2025", cor: vermelho}}
pergunta:
  ancora: pergunto
  linha1: "E O SEU"
  linha2: "TRABALHO?"
  riscado: "ESPERAR"           # aparece apagado e é riscado na âncora 'virada'
  virada: qualific
  depois: ["OU SE", "QUALIFICAR"]
cta:
  ancora: inema
  linha1: "+{{cursos_100}} CURSOS"
  linha2: "GRATUITOS"
  painel: "INEMA.CLUB"
  texto: "+{{cursos_100}} cursos de IA\\n100% gratuitos\\ndo zero ao avançado"
final: ["INEMA.CLUB", "cursos gratuitos de IA", "começa hoje"]
legenda_envio: ""
"""


def cmd_novo(link, ident=None):
    hoje = date.today()
    pasta = RAIZ / "edicoes" / f"{hoje.isoformat()}-{slug(ident or 'reel')}"
    ref = pasta / "ref"; ref.mkdir(parents=True, exist_ok=True)
    alvo = ref / "reel.mp4"
    if not alvo.exists():
        ok = False
        if (CFG["inemavox"] / "baixar_v1.py").exists():
            r = subprocess.run(["python3", "baixar_v1.py", "--url", link, "--outdir", ref, "--quality", "1080p"],
                               cwd=CFG["inemavox"], capture_output=True, text=True, timeout=600)
            achados = sorted(ref.glob("*.mp4"))
            if r.returncode == 0 and achados:
                achados[0].rename(alvo); ok = True
        if not ok:  # Instagram com cookies costuma falhar no inemavox; sem cookies funciona
            log("inemavox não baixou; tentando yt-dlp sem cookies")
            run(["yt-dlp", "-q", "-o", str(ref / "reel.%(ext)s"), "--merge-output-format", "mp4", link], timeout=600)
    log("reel", f"{dur(alvo):.1f} s")
    run(["ffmpeg", "-v", "error", "-y", "-i", alvo, "-vf", f"fps={12 / max(1, dur(alvo))},scale=270:-1,tile=6x2",
         "-frames:v", "1", ref / "folha.jpg"])
    try:
        wav = ref / "reel.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", alvo, "-vn", "-ac", "1", "-ar", "16000", wav])
        pal = cs.transcrever(wav, ref / "t", palavras=True)
        (ref / "transcricao.txt").write_text(" ".join(p["word"].strip() for p in pal) or "(sem fala)")
    except Exception as e:
        (ref / "transcricao.txt").write_text(f"(transcrição falhou: {e})")
    try:
        desc = subprocess.run(["yt-dlp", "--skip-download", "--print", "%(description)s", link],
                              capture_output=True, text=True, timeout=120).stdout.strip()
        (ref / "descricao.txt").write_text(desc)
    except Exception:
        pass
    rot = pasta / "roteiro.yaml"
    if not rot.exists():
        rot.write_text(MODELO.format(pasta=pasta.name, link=link, hoje=hoje.strftime("%d/%m/%Y")))
    log("pronto:", pasta)
    log("veja", ref / "folha.jpg", "e escreva", rot)
    return pasta


# ======================================================================= roteiro + tempos
def carregar(pasta):
    pasta = Path(pasta).resolve()
    r = yaml.safe_load((pasta / "roteiro.yaml").read_text())
    r["_dir"] = pasta
    r["_b"] = pasta / "build"; r["_b"].mkdir(exist_ok=True)
    r["_reel"] = pasta / "ref/reel.mp4"
    r["_av"] = pasta / "avatar/avatar.mp4"
    return r


def palavras_estimadas(fala, cps=16.0):
    t, out = 0.3, []
    for w in fala.split():
        d = max(0.18, len(w) / cps)
        out.append({"w": w, "t": round(t, 2), "f": round(t + d, 2)}); t += d + 0.06
    return out


def palavras_reais(r):
    tj = r["_b"] / "palavras.json"
    if not tj.exists() or tj.stat().st_mtime < r["_av"].stat().st_mtime:
        wav = r["_b"] / "avatar.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", r["_av"], "-vn", "-ac", "1", "-ar", "48000", wav])
        pal = cs.transcrever(wav, r["_b"] / "t", palavras=True)
        tj.write_text(json.dumps([{"w": p["word"].strip(), "t": p["start"], "f": p["end"]} for p in pal], ensure_ascii=False))
    return json.loads(tj.read_text())


def semelhanca(fala, pal):
    import difflib
    a = cs.norm(fala); b = [w for p in pal for w in cs.norm(p["w"])]
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


class Linha:
    """tempos de cada tela, achados pelas âncoras na fala"""

    def __init__(self, r, pal, dur_av):
        self.pal = pal
        def em(palavra, depois=0.0):
            palavra = slug(palavra).replace("-", " ")
            for p in pal:
                if p["t"] >= depois and (palavra in slug(p["w"]).replace("-", " ") or palavra in " ".join(cs.norm(p["w"]))):
                    return p["t"]
            sys.exit(f"âncora '{palavra}' não achada na fala depois de {depois:.1f} s")
        self.cartoes = []
        t = 0.0
        for c in r["cartoes"]:
            t = em(c["ancora"], t); self.cartoes.append(t)
        self.perg = em(r["pergunta"]["ancora"], t)
        self.virada = em(r["pergunta"].get("virada") or r["pergunta"]["ancora"], self.perg)
        self.cta_fala = em(r["cta"]["ancora"], self.virada)
        self.cta = self.cta_fala - 0.3
        self.fim = pal[-1]["f"]
        self.total = max(dur_av, self.fim) + 1.8
        self.primeiro = self.cartoes[0] if self.cartoes else self.perg

    def resumo(self):
        c = " · ".join(f"{t:.1f}" for t in self.cartoes)
        return f"cartões {c} · pergunta {self.perg:.1f} · virada {self.virada:.1f} · cta {self.cta:.1f} · fim {self.fim:.1f} · total {self.total:.1f}"


# ======================================================================= desenho
_fontes = {}
def fnt(p, s):
    if not Path(p).exists():
        p = DEJAVU
    if (p, s) not in _fontes:
        _fontes[(p, s)] = ImageFont.truetype(p, s)
    return _fontes[(p, s)]


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def borda(d, xy, s, f, cor, b=6, anchor="la"):
    d.text(xy, s, font=f, fill=cor, anchor=anchor, stroke_width=b, stroke_fill=(0, 0, 0))


def cor(nome, padrao=AMB):
    return CORES.get(nome or "", padrao)


def caber(d, s, fonte, tam, larg):
    while tam > 40 and d.textlength(s, font=fnt(fonte, tam)) > larg:
        tam -= 4
    return fnt(fonte, tam)


class Desenho:
    def __init__(self, r, L):
        self.r, self.L = r, L
        self.blocos = [L.pal[i:i + 3] for i in range(0, len(L.pal), 3)]

    def topo(self, d, t):
        r, L = self.r, self.L
        d.rounded_rectangle((40, 60, 330, 122), 14, fill=VERM + (255,))
        d.text((185, 91), fmt(r.get("data") or "{hoje}"), font=fnt(MBLK, 38), fill=BRANCO, anchor="mm")
        d.text((350, 91), "INEMA.CLUB", font=fnt(MXB, 30), fill=BRANCO + (220,), anchor="lm")
        if t < L.primeiro:
            m = r["abertura"]
        elif t < L.perg:
            m = r.get("manchete_numeros") or r["abertura"]
        elif t < L.cta:
            m = r["pergunta"]
        else:
            m = r["cta"]
        borda(d, (40, 140), fmt(m["linha1"]), caber(d, fmt(m["linha1"]), ANTON, 120, W - 80), BRANCO, 8)
        borda(d, (40, 270), fmt(m["linha2"]), caber(d, fmt(m["linha2"]), ANTON, 150, W - 80), cor(m.get("cor")), 8)

    def painel(self, d, t):
        r, L = self.r, self.L
        x, y, w, h = 40, 1290, 580, 460
        d.rounded_rectangle((x, y, x + w, y + h), 26, fill=ESC + (215,))
        d.rectangle((x, y + 24, x + 8, y + h - 24), fill=AMB + (255,))
        if t < L.primeiro:
            p = r["painel_inicial"]
            d.text((x + 40, y + 50), fmt(p["titulo"]), font=caber(d, fmt(p["titulo"]), ANTON, 110, w - 70), fill=AMB)
            d.text((x + 40, y + 200), fmt(p["texto"]), font=fnt(MXB, 44), fill=BRANCO, spacing=10)
            return
        if t < L.perg:
            k = max(i for i, c in enumerate(L.cartoes) if t >= c)
            c = r["cartoes"][k]; ini = L.cartoes[k]
            p = ease((t - ini) / 0.9)
            num = fmt(c["numero"]).replace("{}", str(int(round(c["conta"] * p)))) if "conta" in c else fmt(c["numero"])
            final = fmt(c["numero"]).replace("{}", str(c.get("conta", "")))
            dx = int((1 - ease((t - ini) / 0.35)) * -60)
            fnum = caber(d, final, ANTON, 132, w - 80)
            d.text((x + 40 + dx, y + 40), num, font=fnum, fill=cor(c.get("cor"), VERM))
            d.text((x + 40 + dx, y + 210), fmt(c["rotulo"]), font=fnt(MXB, 40), fill=BRANCO, spacing=10)
            d.text((x + 40, y + h - 60), fmt(c.get("fonte", "")), font=caber(d, fmt(c.get("fonte", "")), MXB, 22, w - 70), fill=(190, 200, 210))
            n = len(L.cartoes)
            for i in range(n):
                cx = x + w - 30 - (n - i) * 30
                d.ellipse((cx, y + 30, cx + 16, y + 46), fill=(AMB if i <= k else (80, 90, 100)) + (255,))
            return
        if t < L.cta:
            q = r["pergunta"]
            d.text((x + 40, y + 50), fmt(q.get("riscado", "ESPERAR")), font=fnt(ANTON, 92), fill=(150, 160, 170))
            if t >= L.virada:
                larg = d.textlength(fmt(q.get("riscado", "ESPERAR")), font=fnt(ANTON, 92))
                d.line((x + 36, y + 110, x + 44 + larg, y + 110), fill=VERM + (255,), width=10)
                a, b = (q.get("depois") or ["OU SE", "QUALIFICAR"])[:2]
                d.text((x + 40, y + 190), fmt(a), font=fnt(ANTON, 80), fill=BRANCO)
                d.text((x + 40, y + 290), fmt(b), font=caber(d, fmt(b), ANTON, 112, w - 70), fill=AMB)
            else:
                d.text((x + 40, y + 190), "OU...", font=fnt(ANTON, 92), fill=BRANCO)
            return
        c = r["cta"]
        d.text((x + 40, y + 40), fmt(c.get("painel", "INEMA.CLUB")), font=caber(d, fmt(c.get("painel", "INEMA.CLUB")), ANTON, 104, w - 70), fill=AMB)
        d.text((x + 40, y + 190), fmt(c.get("texto", "")), font=fnt(MXB, 42), fill=BRANCO, spacing=12)

    def legenda(self, d, t):
        for bl in self.blocos:
            if bl[0]["t"] - 0.05 <= t < bl[-1]["f"] + 0.25:
                pal = [p["w"].upper() for p in bl]
                f = caber(d, " ".join(pal), MBLK, 66, W - 60)
                larg = [d.textlength(p + " ", font=f) for p in pal]
                xx = (W - sum(larg)) / 2
                for p, l, raw in zip(pal, larg, bl):
                    borda(d, (xx, 1150), p, f, AMB if raw["t"] <= t else BRANCO, 7)
                    xx += l
                return

    def quadro(self, t):
        L = self.L
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if t >= L.total - 1.8 and t >= L.fim + 0.2:
            a = int(255 * ease((t - (L.total - 1.8)) / 0.4))
            d.rectangle((0, 0, W, H), fill=ESC + (a,))
            fin = [fmt(s) for s in (self.r.get("final") or ["INEMA.CLUB"])]
            d.text((W / 2, 820), fin[0], font=caber(d, fin[0], ANTON, 190, W - 80), fill=AMB + (a,), anchor="mm")
            for i, s in enumerate(fin[1:]):
                d.text((W / 2, 980 + i * 80), s, font=fnt(MXB, 54), fill=BRANCO + (a,), anchor="mm")
            return im
        self.topo(d, t); self.painel(d, t); self.legenda(d, t)
        return im


# ======================================================================= fundo
def capas(n=40):
    """capas reais dos cursos do portal (cache local)"""
    CFG["capas"].mkdir(parents=True, exist_ok=True)
    tem = sorted(CFG["capas"].glob("[0-9]*.png"), key=lambda f: -int(f.stem))
    if len(tem) >= n:
        return tem[:n]
    import concurrent.futures as cf
    cursos = sorted(json.loads(CFG["portal_dados"].read_text())["platformsData"], key=lambda c: -c["id"])[:n * 2]
    def baixa(c):
        destino = CFG["capas"] / f"{c['id']}.png"
        if destino.exists():
            return
        u = c["url"].rstrip("/").rsplit("/index.html", 1)[0]
        for cand in (u + "/capa/capa.png", u.rsplit("/", 1)[0] + "/capa/capa.png"):
            try:
                req = urllib.request.Request(cand, headers={"User-Agent": "Mozilla/5.0"})
                b = urllib.request.urlopen(req, timeout=15).read()
                if len(b) > 20000:
                    destino.write_bytes(b); return
            except Exception:
                pass
    with cf.ThreadPoolExecutor(12) as ex:
        list(ex.map(baixa, cursos))
    return sorted(CFG["capas"].glob("[0-9]*.png"), key=lambda f: -int(f.stem))[:n]


def mosaico(r):
    out = r["_b"] / "mosaico.png"
    fs = capas()
    cw, ch, g = 520, 293, 14
    m = Image.new("RGB", (W, math.ceil(len(fs) / 2) * (ch + g) + ch + g), ESC)
    for i, f in enumerate(fs):
        m.paste(Image.open(f).convert("RGB").resize((cw, ch)), (g + (i % 2) * (cw + g), g + (i // 2) * (ch + g) + (ch // 2 if i % 2 else 0)))
    m.save(out)
    return out, m.height


def fundo_reel(r, ate):
    """1ª passada do reel inteiro, depois o trecho 'lento' em câmera lenta com zoom até cobrir 'ate'"""
    out = r["_b"] / "reel_corte.mp4"
    dr = dur(r["_reel"])
    de, at = (r.get("lento") or {}).get("de", 0) or 0, (r.get("lento") or {}).get("ate", 0) or 0
    if at <= de:
        de, at = 0, dr
    at = min(at, dr)
    primeira = min(dr, ate)
    resto = max(0.5, ate - primeira)
    fator = max(1.0, resto / (at - de))
    escala = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    run(["ffmpeg", "-y", "-v", "error", "-i", r["_reel"], "-filter_complex",
         f"[0:v]{escala},split=2[a][b];[a]trim=0:{primeira:.3f},setpts=PTS-STARTPTS,fps={FPS}[p1];"
         f"[b]trim={de}:{at},setpts=(PTS-STARTPTS)*{fator:.4f},fps={FPS},scale=1188:2112,crop={W}:{H}:54:60[p2];"
         f"[p1][p2]concat=n=2:v=1:a=0,eq=brightness=-0.04:saturation=1.1,trim=0:{ate:.3f}[v]",
         "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])
    return out


def gradientes(r):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for y in range(520):
        d.line((0, y, W, y), fill=(0, 0, 0, int(190 * (1 - y / 520))))
    for y in range(1050, H):
        d.line((0, y, W, y), fill=(0, 0, 0, int(200 * min(1, (y - 1050) / 300))))
    p = r["_b"] / "grad.png"; g.save(p); return p


def recorte_rosto(r):
    """acha o rosto no avatar (OpenCV) e devolve crop w:h:x:y na proporção 400x453 com a cabeça inteira"""
    if r.get("recorte_avatar"):
        return r["recorte_avatar"]
    import cv2
    cap = cv2.VideoCapture(str(r["_av"]))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    vw, vh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cx = []
    for k in range(1, 8):
        cap.set(cv2.CAP_PROP_POS_FRAMES, n * k // 8)
        ok, fr = cap.read()
        if not ok:
            continue
        fs = casc.detectMultiScale(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), 1.1, 6, minSize=(vh // 6, vh // 6))
        if len(fs):
            x, y, w, h = max(fs, key=lambda f: f[2] * f[3]); cx.append(x + w / 2)
    cap.release()
    ch = vh; cw = int(round(ch * AVW / AVH))
    centro = sorted(cx)[len(cx) // 2] if cx else vw / 2
    x0 = int(max(0, min(vw - cw, centro - cw / 2)))
    return f"{cw}:{ch}:{x0}:0"


# ======================================================================= comandos
def cmd_previa(pasta):
    r = carregar(pasta)
    pal = palavras_reais(r) if r["_av"].exists() else palavras_estimadas(r["fala"])
    L = Linha(r, pal, max(p["f"] for p in pal)); D = Desenho(r, L)
    log(L.resumo())
    ts = [0.0] + [t + 1.0 for t in L.cartoes] + [L.perg + 0.5, L.virada + 0.5, L.cta + 1.0, L.total - 0.5]
    dr = dur(r["_reel"]); ims = []
    for i, t in enumerate(ts):
        bg = r["_b"] / f"bg{i}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{min(t, dr - 0.2) if t < L.cta else 0:.2f}", "-i", r["_reel"], "-frames:v", "1",
             "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", bg])
        c = Image.open(bg).convert("RGBA")
        if t >= L.cta:
            c = Image.new("RGBA", (W, H), ESC + (255,))
        c.alpha_composite(D.quadro(t)); ims.append(c.convert("RGB").resize((360, 640)))
    folha = Image.new("RGB", (360 * min(5, len(ims)), 640 * math.ceil(len(ims) / 5)), ESC)
    for i, im in enumerate(ims):
        folha.paste(im, ((i % 5) * 360, (i // 5) * 640))
    out = r["_dir"] / "previa.jpg"; folha.save(out, quality=88)
    log("prévia", out)


def cmd_avatar(pasta):
    r = carregar(pasta)
    av = r["_dir"] / "avatar"; av.mkdir(exist_ok=True)
    if not (av / "APROVADO_HEYGEN").exists():
        sys.exit(f"falta {av}/APROVADO_HEYGEN (o HeyGen só roda com aprovação registrada)")
    fala = av / "fala.txt"; fala.write_text(r["fala"].strip() + "\n")
    vid_f = av / "video_id.txt"
    if not vid_f.exists():
        titulo = f"RC-{r['_dir'].name}"
        env = dict(os.environ, DISPLAY=CFG["display"])
        with open(av / "studio.log", "w") as lg:
            subprocess.run(["node", "heygen-studio.mjs", "--titulo", titulo, "--fala-arquivo", fala, "--perfil", CFG["perfil_heygen"],
                            "--template", CFG["template_heygen"]], cwd=CFG["explicavideos"] / "engine", env=env,
                           stdout=lg, stderr=subprocess.STDOUT, timeout=900)
        m = re.search(r"create-v4/([0-9a-f]{32})", (av / "studio.log").read_text())
        if not m:
            sys.exit("estúdio não devolveu o id do vídeo; veja avatar/studio.log")
        vid_f.write_text(m.group(1))
    vid = vid_f.read_text().strip()
    sys.path.insert(0, str(CFG["explicavideos"] / "engine"))
    from heygen_read import get  # leitura de status (sem gerar nada)
    for _ in range(240):  # até 4 h
        d = get("/v3/videos/" + vid); d = d.get("data", d)
        st = d.get("status"); log(time.strftime("%H:%M"), st)
        if st == "completed":
            tmp = av / "avatar.part.mp4"
            with urllib.request.urlopen(d["video_url"], timeout=300) as src, tmp.open("wb") as f:
                shutil.copyfileobj(src, f)
            tmp.replace(av / "avatar.mp4"); log("avatar baixado", av / "avatar.mp4"); return
        if st == "failed":
            sys.exit(f"HeyGen falhou: {d.get('failure_message')}")
        if st is None:
            sys.exit(f"vídeo {vid} não encontrado no HeyGen (o estúdio enviou?) — veja avatar/studio.log")
        time.sleep(60)
    sys.exit("passou de 4 h sem ficar pronto")


def cmd_montar(pasta):
    r = carregar(pasta); B = r["_b"]
    pal = palavras_reais(r)
    sem = semelhanca(r["fala"], pal)
    log(f"fala do avatar × roteiro: {sem:.0%}")
    if sem < 0.85:
        sys.exit("a fala ouvida diverge do roteiro (< 85%); confira avatar/avatar.mp4")
    L = Linha(r, pal, dur(r["_av"])); D = Desenho(r, L)
    log(L.resumo())
    ov = B / "ov"
    shutil.rmtree(ov, ignore_errors=True); ov.mkdir()
    for i in range(int(L.total * FPS)):
        D.quadro(i / FPS).save(ov / f"{i:05d}.png", compress_level=1)
    reel = fundo_reel(r, L.cta + 0.5); mos, mh = mosaico(r); grad = gradientes(r)
    vel = (mh - H) / max(1.0, L.total - L.cta)
    crop = recorte_rosto(r); log("recorte do rosto", crop)
    tag = B / "tag.txt"; tag.write_text(r.get("tag", "NEI MALDANER  |  INEMA"))
    ate = L.fim + 0.3
    tem_audio = bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0",
                                     str(r["_reel"])], capture_output=True, text=True).stdout.strip())
    musica = r["_reel"] if tem_audio and not r.get("musica") else Path(r.get("musica") or CFG["musica_reserva"])
    vol = r.get("volume_musica", 0.22)
    fc = (
        f"[0:v]tpad=stop_mode=clone:stop_duration=60,trim=0:{L.total:.3f}[r];"
        f"[1:v]loop=-1:1,fps={FPS},trim=0:{L.total - L.cta:.3f},crop={W}:{H}:0:'min({mh - H},t*{vel:.2f})',"
        f"eq=brightness=-0.08,setpts=PTS-STARTPTS+{L.cta:.3f}/TB,format=yuva420p,fade=t=in:st={L.cta:.3f}:d=0.5:alpha=1[m];"
        f"[r][m]overlay=0:0:eof_action=pass[bg0];[2:v]loop=-1:1,trim=0:{L.total:.3f}[g];[bg0][g]overlay=0:0[bg1];"
        f"[3:v]crop={crop},scale={AVW}:{AVH},setsar=1,fps={FPS}[av];"
        f"[bg1]drawbox=x={AVX - 4}:y={AVY - 4}:w={AVW + 8}:h={AVH + 8}:color=0xE2A23B@1:t=fill:enable='lt(t,{ate:.2f})'[bg2];"
        f"[bg2][av]overlay={AVX}:{AVY}:eof_action=pass:enable='lt(t,{ate:.2f})',"
        f"drawbox=x={AVX}:y={AVY + AVH - 43}:w={AVW}:h=43:color=0x0b0f14@0.85:t=fill:enable='lt(t,{ate:.2f})',"
        f"drawtext=fontfile={DEJAVU}:textfile={tag}:x={AVX + 16}:y={AVY + AVH - 31}:fontsize=19:fontcolor=white:enable='lt(t,{ate:.2f})'[bg3];"
        f"[4:v]format=rgba[o];[bg3][o]overlay=0:0,format=yuv420p[v];"
        f"[3:a]aresample=48000,apad,atrim=0:{L.total:.3f},asplit=2[voz][sc];"
        f"[5:a]volume={vol},aresample=48000[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
        f"[voz][md]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={L.total - 1.4:.2f}:d=1.4[a]"
    )
    saida = r["_dir"] / "video.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", reel, "-i", mos, "-i", grad, "-i", r["_av"], "-framerate", FPS, "-i", ov / "%05d.png",
         "-stream_loop", "-1", "-i", musica, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{L.total:.3f}",
         "-c:v", "libx264", "-crf", "21", "-preset", "slow", "-maxrate", "6M", "-bufsize", "12M",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida])
    shutil.rmtree(ov, ignore_errors=True)
    log("vídeo", saida, f"{dur(saida):.1f} s", f"{saida.stat().st_size / 1e6:.1f} MB")
    return saida


def cmd_conferir(pasta):
    r = carregar(pasta); v = r["_dir"] / "video.mp4"
    d = dur(v); n = 10
    sel = "+".join(f"eq(n\\,{int(d * FPS * k / n)})" for k in range(n))
    run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vf", f"select='{sel}',scale=324:576,tile=5x2", "-vsync", "0", "-frames:v", "1",
         r["_dir"] / "conferencia.jpg"])
    vol = subprocess.run(["ffmpeg", "-hide_banner", "-i", v, "-af", "volumedetect", "-vn", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    log("duração", f"{d:.1f} s", " ".join(re.findall(r"(mean_volume: \S+ dB|max_volume: \S+ dB)", vol)))
    log("folha", r["_dir"] / "conferencia.jpg")


def cmd_enviar(pasta, texto=None):
    r = carregar(pasta)
    cs.enviar({"_dir": r["_dir"], "saida": "video.mp4"}, texto or r.get("legenda_envio") or r["_dir"].name)


def main(a):
    if len(a) < 2 or a[0] not in ("novo", "previa", "avatar", "montar", "conferir", "enviar"):
        sys.exit(__doc__)
    if a[0] == "novo":
        ident = a[a.index("--id") + 1] if "--id" in a else None
        cmd_novo(a[1], ident)
    elif a[0] == "enviar":
        cmd_enviar(a[1], a[2] if len(a) > 2 else None)
    else:
        {"previa": cmd_previa, "avatar": cmd_avatar, "montar": cmd_montar, "conferir": cmd_conferir}[a[0]](a[1])


if __name__ == "__main__":
    main(sys.argv[1:])
