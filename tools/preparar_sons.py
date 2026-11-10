#!/usr/bin/env python3
"""Preparação de SFX do Profane Echo.

Converte (WAV 44,1 kHz mono 16-bit), corta, aplica fades, normaliza o pico e
promove sons de assets/sons/_entrada/ para a árvore sfx/, registrando a licença.

Dependências: numpy e pygame-ce (já usado no jogo). Sem rede, sem ffmpeg.

Comandos
--------
  inspecionar [CAMINHO ...]     duração, pico, RMS e nº de golpes detectados
  fatiar ARQUIVO                recorta uma compilação em golpes candidatos
  promover promocao.csv         processa a tabela e grava em assets/sons/

Exemplos (rodar na raiz do projeto, jogo-max/)
----------------------------------------------
  python tools/preparar_sons.py inspecionar assets/sons/_entrada/murro
  python tools/preparar_sons.py fatiar 158783 --max 8 --dur-max 1.0
  python tools/preparar_sons.py promover tools/promocao.csv --dry-run
  python tools/preparar_sons.py promover tools/promocao.csv
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import unicodedata
import wave
from datetime import date
from pathlib import Path

import numpy as np

SR = 44100
RAIZ = Path(__file__).resolve().parents[1]
if not (RAIZ / "assets" / "sons").is_dir():
    RAIZ = RAIZ.parent
SONS = RAIZ / "assets" / "sons"
ENTRADA = SONS / "_entrada"
LICENCAS = SONS / "_config" / "LICENCAS.csv"
EXTENSOES = {".wav", ".mp3", ".ogg", ".flac", ".aiff", ".aif"}


# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------
def _carregar_pygame(caminho: Path) -> np.ndarray:
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame

    if pygame.mixer.get_init():
        pygame.mixer.quit()
    pygame.mixer.init(frequency=SR, size=-16, channels=1)
    som = pygame.mixer.Sound(str(caminho))  # o mixer converte para 44,1 kHz mono
    x = np.frombuffer(som.get_raw(), dtype=np.int16).astype(np.float32) / 32768.0
    return x


def _carregar_wave(caminho: Path) -> np.ndarray:
    """Fallback para WAV PCM quando o pygame não está disponível."""
    with wave.open(str(caminho), "rb") as w:
        n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(n)
    if sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif sw == 4:
        x = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    elif sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        v = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
        v = np.where(v >= 1 << 23, v - (1 << 24), v)
        x = v.astype(np.float32) / 8388608.0
    elif sw == 1:
        x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise ValueError(f"largura de amostra não suportada: {sw}")
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        t_old = np.arange(len(x)) / sr
        t_new = np.arange(int(len(x) * SR / sr)) / SR
        x = np.interp(t_new, t_old, x).astype(np.float32)
    return x


def carregar(caminho: Path) -> np.ndarray:
    """Devolve o áudio como float32 mono em 44,1 kHz."""
    try:
        return _carregar_pygame(caminho)
    except ImportError:
        if caminho.suffix.lower() != ".wav":
            raise SystemExit("pygame-ce é necessário para ler MP3/OGG/FLAC/AIFF (pip install pygame-ce)")
        return _carregar_wave(caminho)


# --------------------------------------------------------------------------
# Processamento
# --------------------------------------------------------------------------
def db(v: float) -> float:
    return 20.0 * np.log10(max(float(v), 1e-9))


def aparar_silencio(x: np.ndarray, limiar_db: float = -50.0, pre_ms: float = 5.0, pos_ms: float = 30.0) -> np.ndarray:
    ativo = np.flatnonzero(np.abs(x) > 10 ** (limiar_db / 20))
    if ativo.size == 0:
        return x
    ini = max(0, ativo[0] - int(SR * pre_ms / 1000))
    fim = min(len(x), ativo[-1] + 1 + int(SR * pos_ms / 1000))
    return x[ini:fim]


def fade(x: np.ndarray, entrada_ms: float = 2.0, saida_ms: float = 40.0) -> np.ndarray:
    x = x.copy()
    ni = min(len(x), int(SR * entrada_ms / 1000))
    no = min(len(x), int(SR * saida_ms / 1000))
    if ni > 1:
        x[:ni] *= np.linspace(0.0, 1.0, ni, dtype=np.float32)
    if no > 1:
        x[-no:] *= np.linspace(1.0, 0.0, no, dtype=np.float32)
    return x


def mudar_pitch(x: np.ndarray, fator: float) -> np.ndarray:
    """fator > 1 = mais agudo e mais curto; < 1 = mais grave e mais longo."""
    if abs(fator - 1.0) < 1e-3:
        return x
    n = int(len(x) / fator)
    return np.interp(np.arange(n) * fator, np.arange(len(x)), x).astype(np.float32)


def normalizar_pico(x: np.ndarray, alvo_db: float = -3.0) -> np.ndarray:
    pico = float(np.abs(x).max())
    if pico < 1e-6:
        raise ValueError("arquivo silencioso")
    return (x * (10 ** (alvo_db / 20) / pico)).astype(np.float32)


def processar(x, inicio=None, fim=None, pitch=1.0, dur_max=None, fade_out_ms=40.0, alvo_db=-3.0):
    if inicio or fim:
        a = int((inicio or 0.0) * SR)
        b = int(fim * SR) if fim else len(x)
        x = x[a:b]
    x = x - float(np.mean(x))  # remove DC
    x = aparar_silencio(x)
    x = mudar_pitch(x, pitch)
    if dur_max:
        x = x[: int(dur_max * SR)]
    x = fade(x, 2.0, fade_out_ms)
    return normalizar_pico(x, alvo_db)


def salvar_wav(x: np.ndarray, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x, -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# --------------------------------------------------------------------------
# Detecção de golpes em compilações
# --------------------------------------------------------------------------
def detectar_golpes(x, sens=0.10, gap_ms=150.0, hop_ms=5.0, dur_max=1.5, pre_ms=10.0, cauda_ms=120.0):
    """Devolve [(inicio_amostra, fim_amostra, pico)] dos trechos com energia."""
    hop = max(1, int(SR * hop_ms / 1000))
    n = len(x) // hop
    if n < 3:
        return []
    env = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    env = np.convolve(env, np.ones(3) / 3, mode="same")
    limiar = max(float(env.max()) * sens, 1e-4)
    idx = np.flatnonzero(env > limiar)
    if idx.size == 0:
        return []
    gap = max(1, int(gap_ms / hop_ms))
    segs, ini, ult = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - ult > gap:
            segs.append((ini, ult))
            ini = i
        ult = i
    segs.append((ini, ult))

    saida = []
    for a, b in segs:
        s = max(0, a * hop - int(SR * pre_ms / 1000))
        e = min(len(x), (b + 1) * hop + int(SR * cauda_ms / 1000))
        e = min(e, s + int(SR * dur_max))
        pico = float(np.abs(x[s:e]).max())
        if e - s > SR * 0.03:
            saida.append((s, e, pico))
    return saida


# --------------------------------------------------------------------------
# Origem e licença
# --------------------------------------------------------------------------
def resolver_origem(origem: str) -> Path:
    """Aceita caminho, nome de arquivo ou prefixo (ex.: o ID do Freesound)."""
    p = Path(origem)
    for cand in (p, RAIZ / p, ENTRADA / p):
        if cand.is_file():
            return cand
    achados = [f for f in ENTRADA.rglob(origem + "*") if f.is_file() and f.suffix.lower() in EXTENSOES]
    if len(achados) == 1:
        return achados[0]
    if not achados:
        raise FileNotFoundError(f"origem não encontrada em _entrada: {origem}")
    raise FileNotFoundError(f"origem ambígua ({len(achados)} arquivos): {origem}")


def derivar_fonte(caminho: Path) -> dict:
    """Deduz autor/URL do padrão Freesound: <id>__<autor>__<nome>.ext (fatias herdam da pasta)."""
    nome = caminho.parent.name if "_fatias" in caminho.parts else caminho.stem
    m = re.match(r"^(\d+)__(.+?)__(.+)$", nome)
    if not m:
        return {"autor": "", "url": ""}
    sid, autor = m.group(1), m.group(2)
    return {"autor": autor, "url": f"https://freesound.org/people/{autor}/sounds/{sid}/"}


def _norm(h: str) -> str:
    return unicodedata.normalize("NFKD", h).encode("ascii", "ignore").decode().strip().lower()


def validar_licenca(linha: dict, fonte: Path) -> dict:
    """Exige uma licença identificada; nome de arquivo não comprova permissão."""
    licenca = (linha.get("licenca") or "").strip()
    if _norm(licenca) in {"", "livre", "verificar", "pendente", "desconhecida", "a confirmar"}:
        raise ValueError("licença não confirmada; informe a licença exata, autor e URL da fonte")
    meta = derivar_fonte(fonte)
    autor = (linha.get("autor") or meta["autor"]).strip()
    url = (linha.get("url") or meta["url"]).strip()
    atribuicao = (linha.get("atribuicao") or "").strip()
    if not autor or not url.startswith(("https://", "http://")):
        raise ValueError("registre autor e URL da fonte que comprova a licença")
    if "ccby" in re.sub(r"[^a-z0-9]", "", _norm(licenca)) and not atribuicao:
        raise ValueError("licença CC BY exige texto de atribuição")
    return {"autor": autor, "url": url, "licenca": licenca, "atribuicao": atribuicao}


def registrar_licencas(linhas: list[dict]) -> None:
    LICENCAS.parent.mkdir(parents=True, exist_ok=True)
    cabecalho = ["arquivo", "origem", "autor", "url", "licenca", "atribuicao", "data"]
    existentes = []
    if LICENCAS.exists() and LICENCAS.stat().st_size:
        with open(LICENCAS, newline="", encoding="utf-8-sig") as f:
            leitor = csv.DictReader(f, delimiter=_delim(LICENCAS))
            cabecalho = leitor.fieldnames or cabecalho
            existentes = list(leitor)
    chave = {_norm(h): h for h in cabecalho}
    col_arquivo = chave.get("arquivo")
    novos = {l["arquivo"] for l in linhas}
    mantidas = [r for r in existentes if not col_arquivo or r.get(col_arquivo) not in novos]
    saida = list(mantidas)
    for l in linhas:
        reg = {h: "" for h in cabecalho}
        for k, v in l.items():
            if k in chave:
                reg[chave[k]] = v
        saida.append(reg)
    with open(LICENCAS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cabecalho)
        w.writeheader()
        w.writerows(saida)


def _delim(caminho: Path) -> str:
    with open(caminho, encoding="utf-8-sig") as f:
        cab = f.readline()
    return ";" if cab.count(";") > cab.count(",") else ","


def proximo_livre(destino: str) -> Path:
    base = SONS / destino
    if "{n}" not in destino:
        return base
    for n in range(1, 100):
        cand = SONS / destino.replace("{n}", f"{n:02d}")
        if not cand.exists():
            return cand
    raise RuntimeError(f"pasta cheia: {destino}")


# --------------------------------------------------------------------------
# Comandos
# --------------------------------------------------------------------------
def cmd_inspecionar(args) -> int:
    alvos = [Path(a) for a in args.caminhos] or [ENTRADA]
    arquivos = []
    for a in alvos:
        if a.is_dir():
            arquivos += sorted(f for f in a.rglob("*") if f.suffix.lower() in EXTENSOES)
        else:
            arquivos.append(resolver_origem(str(a)))
    print(f"{'arquivo':60} {'dur(s)':>8} {'pico':>7} {'rms':>7} {'golpes':>7}")
    for f in arquivos:
        try:
            x = carregar(f)
        except Exception as e:  # noqa: BLE001
            print(f"{f.name[:60]:60}  ERRO: {e}")
            continue
        rms = float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0
        golpes = len(detectar_golpes(x))
        print(f"{f.name[:60]:60} {len(x) / SR:8.2f} {db(np.abs(x).max()):7.1f} {db(rms):7.1f} {golpes:7d}")
    return 0


def cmd_fatiar(args) -> int:
    origem = resolver_origem(args.arquivo)
    x = carregar(origem)
    golpes = detectar_golpes(x, sens=args.sens, gap_ms=args.gap_ms, dur_max=args.dur_max)
    if not golpes:
        print("nenhum golpe detectado; tente --sens menor (ex.: 0.04)")
        return 1
    if len(golpes) > args.max:
        golpes = sorted(sorted(golpes, key=lambda g: g[2], reverse=True)[: args.max])
    pasta = ENTRADA / "_fatias" / origem.stem
    pasta.mkdir(parents=True, exist_ok=True)
    print(f"{origem.name}: {len(x) / SR:.1f}s -> {len(golpes)} fatias em {pasta.relative_to(RAIZ)}")
    for k, (s, e, pico) in enumerate(golpes, 1):
        y = processar(x[s:e], fade_out_ms=60.0)
        nome = f"fatia_{k:03d}__t{s / SR:07.2f}s.wav"
        salvar_wav(y, pasta / nome)
        print(f"  {nome}  dur {(e - s) / SR:4.2f}s  pico original {db(pico):6.1f} dBFS")
    print("Ouça as fatias, escolha as boas e referencie-as na promocao.csv (origem = nome da fatia).")
    return 0


def cmd_promover(args) -> int:
    tabela = Path(args.tabela)
    delimitador = _delim(tabela)
    with open(tabela, newline="", encoding="utf-8-sig") as f:
        linhas = list(csv.DictReader(f, delimiter=delimitador))
    registros, feitos, erros = [], [], 0
    hoje = date.today().isoformat()
    for i, l in enumerate(linhas, 2):
        origem_txt, destino_txt = (l.get("origem") or "").strip(), (l.get("destino") or "").strip()
        if not origem_txt or not destino_txt or origem_txt.startswith("#"):
            continue
        try:
            fonte = resolver_origem(origem_txt)
            meta = validar_licenca(l, fonte)
            destino = proximo_livre(destino_txt)
            if destino.exists() and not args.sobrescrever:
                raise FileExistsError(f"já existe: {destino.relative_to(SONS)} (use --sobrescrever)")
            flt = lambda k, d=None: float(l[k]) if (l.get(k) or "").strip() else d  # noqa: E731
            y = processar(
                carregar(fonte),
                inicio=flt("inicio_s"), fim=flt("fim_s"), pitch=flt("pitch", 1.0),
                dur_max=flt("dur_max_s"), fade_out_ms=flt("fade_out_ms", 40.0),
                alvo_db=flt("pico_db", args.pico),
            )
            rel = destino.relative_to(SONS).as_posix()
            print(f"[linha {i}] {fonte.name[:50]} -> {rel}  ({len(y) / SR:.2f}s)")
            if not args.dry_run:
                salvar_wav(y, destino)
                feitos.append(i - 2)
                registros.append({"arquivo": rel, "origem": fonte.name, **meta, "data": hoje})
        except Exception as e:  # noqa: BLE001
            erros += 1
            print(f"[linha {i}] ERRO ({origem_txt}): {e}")
    if registros:
        registrar_licencas(registros)
        # marca as linhas promovidas com '#', para uma segunda execução não duplicar os arquivos
        for k in feitos:
            linhas[k]["origem"] = "#" + linhas[k]["origem"]
        with open(tabela, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()), delimiter=delimitador)
            w.writeheader()
            w.writerows(linhas)
        print(f"{len(registros)} arquivo(s) promovido(s); licenças registradas em {LICENCAS.relative_to(RAIZ)}")
    if args.dry_run:
        print("dry-run: nada foi gravado.")
    return 1 if erros else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("inspecionar")
    p.add_argument("caminhos", nargs="*")
    p.set_defaults(fn=cmd_inspecionar)

    p = sub.add_parser("fatiar")
    p.add_argument("arquivo", help="caminho, nome ou prefixo (ID do Freesound) dentro de _entrada")
    p.add_argument("--max", type=int, default=10, help="máximo de fatias (as mais fortes)")
    p.add_argument("--dur-max", type=float, default=1.5, help="duração máxima de cada fatia (s)")
    p.add_argument("--sens", type=float, default=0.10, help="limiar relativo ao pico; menor = mais sensível")
    p.add_argument("--gap-ms", type=float, default=150.0, help="silêncio mínimo entre golpes")
    p.set_defaults(fn=cmd_fatiar)

    p = sub.add_parser("promover")
    p.add_argument("tabela")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--sobrescrever", action="store_true")
    p.add_argument("--pico", type=float, default=-3.0, help="pico alvo em dBFS (padrão -3)")
    p.set_defaults(fn=cmd_promover)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
