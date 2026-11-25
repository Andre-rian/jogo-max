import json
import logging
from copy import deepcopy
from pathlib import Path

logger = logging.getLogger(__name__)

TAMANHOS_TEXTO = ("padrao", "grande", "extra_grande")
ROTULOS_TAMANHO_TEXTO = {
    "padrao": "Padrão 100%",
    "grande": "Grande 125%",
    "extra_grande": "Extra grande 150%",
}
ESCALAS_TEXTO = {
    "padrao": 1.0,
    "grande": 1.25,
    "extra_grande": 1.5,
}

PADRAO = {
    "versao": 1,
    "acessibilidade": {
        "tamanho_texto": "padrao",
    },
    "audio": {
        "geral": 100,
        "musica": 100,
        "efeitos": 100,
        "interface": 100,
        "ambiencia": 100,
    },
}

LIMITES_AUDIO = {
    "geral": (0, 100),
    "musica": (0, 100),
    "efeitos": (0, 100),
    "interface": (0, 100),
    "ambiencia": (0, 100),
}


def _clamp_int(valor, minimo, maximo, padrao):
    try:
        valor = int(round(float(valor)))
    except (TypeError, ValueError):
        return padrao
    return max(minimo, min(maximo, valor))


def normalizar(dados=None):
    dados = dados if isinstance(dados, dict) else {}
    resultado = deepcopy(PADRAO)

    acess = dados.get("acessibilidade", {})
    if not isinstance(acess, dict):
        acess = {}
    tamanho = acess.get("tamanho_texto", PADRAO["acessibilidade"]["tamanho_texto"])
    if tamanho not in TAMANHOS_TEXTO:
        tamanho = PADRAO["acessibilidade"]["tamanho_texto"]
    resultado["acessibilidade"]["tamanho_texto"] = tamanho

    audio = dados.get("audio", {})
    if not isinstance(audio, dict):
        audio = {}
    for chave, (minimo, maximo) in LIMITES_AUDIO.items():
        resultado["audio"][chave] = _clamp_int(
            audio.get(chave, PADRAO["audio"][chave]),
            minimo,
            maximo,
            PADRAO["audio"][chave],
        )
    return resultado


def caminho_padrao(raiz=None):
    base = Path(raiz) if raiz is not None else Path(__file__).resolve().parents[1]
    return base / "configuracoes_usuario.json"


def carregar(caminho=None, raiz=None):
    caminho = Path(caminho) if caminho is not None else caminho_padrao(raiz)
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return normalizar(dados)
    except FileNotFoundError:
        return deepcopy(PADRAO)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as erro:
        logger.warning("[CONFIG] preferencias invalidas em '%s': %s", caminho, erro)
        return deepcopy(PADRAO)


def salvar(preferencias, caminho=None, raiz=None):
    caminho = Path(caminho) if caminho is not None else caminho_padrao(raiz)
    dados = normalizar(preferencias)
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        tmp = caminho.with_suffix(caminho.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
        tmp.replace(caminho)
        return True
    except OSError as erro:
        logger.warning("[CONFIG] nao foi possivel salvar preferencias: %s", erro)
        return False


def escala_texto(preferencias):
    prefs = normalizar(preferencias)
    return ESCALAS_TEXTO[prefs["acessibilidade"]["tamanho_texto"]]


def volumes_normalizados(preferencias):
    prefs = normalizar(preferencias)
    return {chave: valor / 100.0 for chave, valor in prefs["audio"].items()}
