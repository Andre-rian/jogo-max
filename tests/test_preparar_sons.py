import csv
from types import SimpleNamespace

import numpy as np
import pytest

from tools import preparar_sons as preparo


@pytest.fixture
def promocao(tmp_path, monkeypatch):
    sons = tmp_path / "assets" / "sons"
    fonte = sons / "_entrada" / "teste.wav"
    preparo.salvar_wav(np.sin(np.arange(4410) * 0.1).astype(np.float32) * 0.5, fonte)
    monkeypatch.setattr(preparo, "RAIZ", tmp_path)
    monkeypatch.setattr(preparo, "SONS", sons)
    monkeypatch.setattr(preparo, "ENTRADA", fonte.parent)
    monkeypatch.setattr(preparo, "LICENCAS", sons / "_config" / "LICENCAS.csv")
    tabela = tmp_path / "promocao.csv"

    def gravar(licenca, **campos):
        linha = dict(origem=str(fonte), destino="sfx/teste/teste_01.wav", licenca=licenca,
                     autor="Autor", url="https://example.org/som", atribuicao="", **campos)
        with tabela.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=linha, delimiter=";")
            writer.writeheader()
            writer.writerow(linha)
        return SimpleNamespace(tabela=str(tabela), sobrescrever=False, dry_run=False, pico=-3.0)

    return sons, tabela, gravar


@pytest.mark.parametrize("licenca", ["", "LIVRE", "VERIFICAR", "PENDENTE"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_licenca_incerta_nao_promove_nem_altera_registros(promocao, licenca, dry_run):
    sons, tabela, gravar = promocao
    args = gravar(licenca)
    args.dry_run = dry_run
    original = tabela.read_bytes()
    assert preparo.cmd_promover(args) == 1
    assert not (sons / "sfx").exists()
    assert not preparo.LICENCAS.exists()
    assert tabela.read_bytes() == original


def test_cc_by_sem_atribuicao_nao_promove(promocao):
    sons, _, gravar = promocao
    assert preparo.cmd_promover(gravar("CC-BY-3.0")) == 1
    assert not (sons / "sfx").exists()


def test_promocao_preserva_delimitador_creditos_e_volume_por_arquivo(promocao):
    sons, tabela, gravar = promocao
    args = gravar("CC0-1.0", pico_db="-12")
    assert preparo.cmd_promover(args) == 0
    with tabela.open(encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    assert linhas[0]["origem"].startswith("#")
    with preparo.LICENCAS.open(encoding="utf-8", newline="") as f:
        registros = list(csv.DictReader(f))
    assert registros[0]["licenca"] == "CC0-1.0"
    assert registros[0]["autor"] == "Autor"
    wav = sons / "sfx/teste/teste_01.wav"
    pico = preparo.db(np.abs(preparo._carregar_wave(wav)).max())
    assert pico == pytest.approx(-12, abs=0.01)
    antes = wav.read_bytes(), preparo.LICENCAS.read_bytes(), tabela.read_bytes()
    assert preparo.cmd_promover(args) == 0
    assert antes == (wav.read_bytes(), preparo.LICENCAS.read_bytes(), tabela.read_bytes())
