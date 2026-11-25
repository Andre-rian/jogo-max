import json
from core import preferencias


def test_preferencias_normaliza_clamp_e_defaults(tmp_path):
    caminho = tmp_path / 'configuracoes_usuario.json'
    caminho.write_text(json.dumps({
        'acessibilidade': {'tamanho_texto': 'gigante'},
        'audio': {'geral': 999, 'musica': -5, 'efeitos': '50', 'interface': None}
    }), encoding='utf-8')
    prefs = preferencias.carregar(caminho)
    assert prefs['acessibilidade']['tamanho_texto'] == 'padrao'
    assert prefs['audio']['geral'] == 100
    assert prefs['audio']['musica'] == 0
    assert prefs['audio']['efeitos'] == 50
    assert prefs['audio']['interface'] == 100
    assert prefs['audio']['ambiencia'] == 100


def test_preferencias_salvar_e_carregar_atomico(tmp_path):
    caminho = tmp_path / 'configuracoes_usuario.json'
    prefs = preferencias.normalizar({
        'acessibilidade': {'tamanho_texto': 'extra_grande'},
        'audio': {'geral': 70, 'musica': 60, 'efeitos': 50, 'interface': 40, 'ambiencia': 30}
    })
    assert preferencias.salvar(prefs, caminho) is True
    lido = preferencias.carregar(caminho)
    assert lido == prefs
    assert preferencias.escala_texto(lido) == 1.5
    vols = preferencias.volumes_normalizados(lido)
    assert vols['geral'] == 0.7
    assert vols['ambiencia'] == 0.3
