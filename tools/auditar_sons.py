#!/usr/bin/env python3
"""Auditoria local de integridade, duplicatas e licenças. Não altera áudios.

Uso: python tools/auditar_sons.py --saida docs/audio/auditoria_geral
Inclui os originais em _entrada; separa-os dos arquivos finais nos resultados.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import wave
from collections import defaultdict
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
SONS = RAIZ / "assets/sons"
EXTENSOES = {".wav", ".mp3", ".ogg", ".flac", ".aiff", ".aif"}


def hash_arquivo(caminho):
    with caminho.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def medir(caminho, pygame):
    rel = caminho.relative_to(SONS).as_posix()
    linha = dict(arquivo=rel, final=rel.split("/")[0] in {"sfx", "musica", "ambiencia"},
                 bytes=caminho.stat().st_size, sha256=hash_arquivo(caminho),
                 sha256_pcm="", duracao_s="", pico_db="", rms_db="", saturacao_pct="",
                 silencio_inicio_s="", silencio_final_s="", formato_wav="", erro="")
    with caminho.open("rb") as f:
        cab = f.read(128)
    if cab.startswith(b"version https://git-lfs.github.com/spec/v1"):
        linha["erro"] = "PONTEIRO_LFS"
        return linha
    try:
        if caminho.suffix.lower() == ".wav":
            try:
                with wave.open(str(caminho), "rb") as w:
                    linha["formato_wav"] = f"{w.getframerate()} Hz / {w.getsampwidth()*8} bit / {w.getnchannels()} canais"
            except wave.Error:
                # wave não lê IEEE float; SDL_mixer lê. Não confundir isso com corrupção.
                linha["formato_wav"] = "WAV fora do leitor PCM de wave; validar com SDL_mixer"
        som = pygame.mixer.Sound(str(caminho))
        raw = som.get_raw()
        x = np.frombuffer(raw, dtype="<i2").reshape(-1, 2)
        if not len(x):
            raise ValueError("audio sem amostras")
        pico = max(abs(int(x.min())), abs(int(x.max())))
        rms = float(np.sqrt(np.mean((x.astype(np.float32) / 32768) ** 2)))
        ativos = np.flatnonzero(np.any((x > 32) | (x < -32), axis=1))
        linha.update(
            sha256_pcm=hashlib.sha256(raw).hexdigest(), duracao_s=round(len(x)/44100, 6),
            pico_db=round(20*np.log10(max(pico/32768, 1e-9)), 3),
            rms_db=round(20*np.log10(max(rms, 1e-9)), 3),
            saturacao_pct=round(float(np.mean((x >= 32767) | (x <= -32768))*100), 6),
            silencio_inicio_s=round(int(ativos[0])/44100, 6) if len(ativos) else round(len(x)/44100, 6),
            silencio_final_s=round((len(x)-1-int(ativos[-1]))/44100, 6) if len(ativos) else round(len(x)/44100, 6),
        )
        if pico == 0:
            linha["erro"] = "SILENCIO_TOTAL"
    except Exception as e:
        linha["erro"] = f"{type(e).__name__}: {e}"
    return linha


def agrupar_duplicatas(linhas, chave):
    grupos = defaultdict(list)
    for linha in linhas:
        if linha[chave] and not linha["erro"]:
            grupos[linha[chave]].append(linha["arquivo"])
    return [arquivos for arquivos in grupos.values() if len(arquivos) > 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", type=Path, default=RAIZ / "docs/audio/auditoria_geral")
    args = ap.parse_args()
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
    arquivos = sorted(f for f in SONS.rglob("*") if f.is_file() and f.suffix.lower() in EXTENSOES)
    linhas = []
    for i, caminho in enumerate(arquivos, 1):
        linhas.append(medir(caminho, pygame))
        if i % 100 == 0:
            print(f"{i}/{len(arquivos)} arquivos analisados", flush=True)
    pygame.mixer.quit()
    finais = [r for r in linhas if r["final"]]
    with (SONS / "_config/LICENCAS.csv").open(encoding="utf-8-sig", newline="") as f:
        licencas = list(csv.DictReader(f))
    por_arquivo = defaultdict(list)
    for r in licencas:
        por_arquivo[r["arquivo"]].append(r)
    pasta_vazia = []
    for raiz in ("sfx", "ambiencia", "musica"):
        for p in sorted((SONS / raiz).rglob("*")):
            if p.is_dir() and not any(f.is_dir() or f.suffix.lower() in EXTENSOES for f in p.iterdir()):
                pasta_vazia.append(p.relative_to(SONS).as_posix())
    resumo = dict(
        total=len(linhas), finais=len(finais), triagem=len(linhas)-len(finais),
        erros=[r for r in linhas if r["erro"]],
        duplicatas_bytes=agrupar_duplicatas(linhas, "sha256"),
        duplicatas_pcm_finais=agrupar_duplicatas(finais, "sha256_pcm"),
        pastas_finais_vazias=pasta_vazia,
        licencas_duplicadas={k:v for k,v in por_arquivo.items() if len(v)>1},
        licencas_sem_arquivo=[r for r in licencas if not (SONS/r["arquivo"]).is_file()],
        finais_sem_licenca=[r["arquivo"] for r in finais if r["arquivo"] not in por_arquivo],
        finais_licenca_generica=[r for r in licencas if (r.get("licenca") or "").upper() in {"", "LIVRE", "VERIFICAR", "PENDENTE"}],
        sinais_a_revisar=[r for r in finais if not r["erro"] and (
            r["saturacao_pct"] > 0.01 or r["rms_db"] < -50
            or (r["arquivo"].startswith("sfx/") and (r["duracao_s"]>8 or r["silencio_inicio_s"]>0.25)))],
    )
    args.saida.mkdir(parents=True, exist_ok=True)
    with (args.saida / "ARQUIVOS.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    (args.saida / "RESUMO.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: resumo[k] for k in ("total", "finais", "triagem")}))
    print(f"{len(resumo['erros'])} erros; {len(resumo['duplicatas_pcm_finais'])} grupos finais com PCM identico")


if __name__ == "__main__":
    main()
