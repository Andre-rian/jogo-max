import json
import logging
import os
import random
from dataclasses import dataclass
from pathlib import Path

import pygame

logger = logging.getLogger(__name__)
logger_audio_diag = logging.getLogger("audio.diagnostico")

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
PASTA_SONS = RAIZ_PROJETO / "assets" / "sons"
EXTENSOES_AUDIO = {".wav", ".ogg", ".mp3", ".flac", ".aiff", ".aif"}

MASTER_VOLUME_INICIAL = 0.8
SFX_VOLUME_INICIAL = 1.0
VOLUMES_CATEGORIA_INICIAIS = {
    "combat": 0.8,
    "player": 0.9,
    "interaction": 0.7,
    "ui": 0.7,
    "music": 0.35,
    "ambience": 0.4,
}

ATAQUES_DISPONIVEIS = ("slash", "ataque")
ATAQUE_PLAYER_INICIAL = "slash"

CATEGORIA_POR_RAIZ = {
    "sfx/player": "player",
    "sfx/inimigos": "combat",
    "sfx/materiais": "combat",
    "sfx/combate": "combat",
    "sfx/projeteis": "combat",
    "sfx/mundo": "interaction",
    "sfx/interacao": "interaction",
    "sfx/ui": "ui",
    "ambiencia": "ambience",
    "musica": "music",
}

PERFIS_EVENTO = {
    "hit": {"cooldown_ms": 60, "max_instancias": 3, "volume": 1.0},
    "kill": {"cooldown_ms": 40, "max_instancias": 2, "volume": 1.0},
    "block": {"cooldown_ms": 60, "max_instancias": 2, "volume": 1.0},
    "swing": {"cooldown_ms": 0, "max_instancias": 1, "volume": 0.65},
    "enemy_attack": {"cooldown_ms": 80, "max_instancias": 3, "volume": 1.0},
    "enemy_entrada": {"cooldown_ms": 0, "max_instancias": 1, "volume": 1.0},
    "enemy_rugido": {"cooldown_ms": 3200, "max_instancias": 1, "volume": 0.85},
    "enemy_asas": {"cooldown_ms": 2400, "max_instancias": 1, "volume": 0.35},
    "guard_break": {"cooldown_ms": 120, "max_instancias": 1, "volume": 1.0},
    "jump": {"cooldown_ms": 0, "max_instancias": 1, "volume": 0.9},
    "mecanismo": {"cooldown_ms": 0, "max_instancias": 1, "volume": 1.0},
    "ambiente": {"volume": 0.65},
    "tochas": {"volume": 0.25},
    "eco_profano": {"cooldown_ms": 60, "max_instancias": 2, "volume": 0.8},
    "step": {"cooldown_ms": 90, "max_instancias": 2, "volume": 1.0},
    "land": {"cooldown_ms": 80, "max_instancias": 1, "volume": 1.0},
    "projectile": {"cooldown_ms": 50, "max_instancias": 3, "volume": 0.85},
}


@dataclass(frozen=True)
class SomSpec:
    arquivo: str
    categoria: str
    volume_base: float = 1.0
    max_instancias: int = 2
    cooldown_ms: int = 0


@dataclass
class _Reproducao:
    indice_canal: int
    chave: str
    grupo: str
    categoria: str
    volume_base: float
    ajuste: float


ESPECIFICACOES = {
    "player_attack_slash": SomSpec("sfx/player/armas/espada_longa/armas_espada_longa_swing_01.mp3", "player", 0.65, 1, 0),
    "player_attack_ataque": SomSpec("sfx/player/armas/espada_longa/armas_espada_longa_swing_02.wav", "player", 0.65, 1, 0),
    "player_hurt": SomSpec("sfx/player/dano/dano_hurt_01.wav", "player", 1.0, 1, 40),
    "player_death": SomSpec("sfx/player/morte/morte_01.ogg", "player", 1.0, 1, 0),
    "player_dash": SomSpec("sfx/player/movimento/dash/movimento_dash_01.wav", "player", 1.0, 1, 0),
    "player_step_1": SomSpec("sfx/player/movimento/passos/madeira/movimento_passos_madeira_step_01.wav", "player", 1.0, 2, 90),
    "player_step_2": SomSpec("sfx/player/movimento/passos/madeira/movimento_passos_madeira_step_02.wav", "player", 1.0, 2, 90),
    "player_step_3": SomSpec("sfx/player/movimento/passos/madeira/movimento_passos_madeira_step_03.wav", "player", 1.0, 2, 90),
    "player_land": SomSpec("sfx/player/movimento/pouso/madeira/movimento_pouso_madeira_land_01.wav", "player", 1.0, 1, 80),
    "potion_open": SomSpec("sfx/player/pocao/pocao_abrir_01.wav", "interaction", 1.0, 1, 0),
    "potion_drink": SomSpec("sfx/player/pocao/pocao_beber_01.wav", "interaction", 1.0, 1, 0),
    "hit_1": SomSpec("sfx/combate/generico/generico_hit_01.wav", "combat", 1.0, 3, 60),
    "hit_2": SomSpec("sfx/combate/generico/generico_hit_02.wav", "combat", 1.0, 3, 60),
    "hit_3": SomSpec("sfx/combate/generico/generico_hit_03.wav", "combat", 1.0, 3, 60),
    "block": SomSpec("sfx/combate/generico/generico_block_01.wav", "combat", 1.0, 2, 60),
    "enemy_attack": SomSpec("sfx/inimigos/_default/ataque/default_ataque_01.wav", "combat", 1.0, 3, 80),
    "enemy_death": SomSpec("sfx/inimigos/_default/morte/default_morte_01.wav", "combat", 1.0, 2, 40),
    "bomb_explosion": SomSpec("sfx/projeteis/bomba/impacto/bomba_impacto_01.wav", "combat", 0.75, 3, 50),
    "chest_open": SomSpec("sfx/mundo/baus/baus_abrir_01.wav", "interaction", 1.0, 1, 0),
    "eco_pickup": SomSpec("sfx/interacao/itens/itens_eco_01.wav", "interaction", 1.0, 1, 0),
    "item_pickup": SomSpec("sfx/interacao/itens/itens_item_01.wav", "interaction", 1.0, 1, 0),
    "equip_weapon": SomSpec("sfx/interacao/equipar/equipar_arma_01.wav", "interaction", 1.0, 1, 0),
    "equip_armor": SomSpec("sfx/interacao/equipar/equipar_armadura_01.wav", "interaction", 1.0, 1, 0),
    "campfire_light": SomSpec("sfx/mundo/fogueira/fogueira_acender_01.wav", "interaction", 1.0, 1, 0),
    "campfire_rest": SomSpec("sfx/mundo/fogueira/fogueira_descansar_01.wav", "interaction", 1.0, 1, 0),
    "door_open": SomSpec("sfx/mundo/portas/portas_abrir_01.wav", "interaction", 1.0, 1, 0),
    "door_close": SomSpec("sfx/mundo/portas/portas_fechar_01.wav", "interaction", 1.0, 1, 0),
    "level_up": SomSpec("sfx/interacao/itens/itens_level_up_01.wav", "interaction", 1.0, 1, 0),
    "ui_inventory_open": SomSpec("sfx/ui/inventario/inventario_abrir_01.wav", "ui", 1.0, 1, 0),
    "ui_inventory_close": SomSpec("sfx/ui/inventario/inventario_fechar_01.wav", "ui", 1.0, 1, 0),
    "ui_confirm": SomSpec("sfx/ui/confirmar/confirmar_01.wav", "ui", 1.0, 2, 50),
    "ui_error": SomSpec("sfx/ui/erro/erro_01.wav", "ui", 1.0, 2, 80),
    "ui_move": SomSpec("sfx/ui/navegar/navegar_01.wav", "ui", 1.0, 2, 60),
    "ui_back": SomSpec("sfx/ui/voltar/voltar_01.wav", "ui", 1.0, 2, 50),
    "ui_pause_open": SomSpec("sfx/ui/pausa/pausa_abrir_01.wav", "ui", 1.0, 1, 0),
    "ui_pause_close": SomSpec("sfx/ui/pausa/pausa_fechar_01.wav", "ui", 1.0, 1, 0),
    "ui_save": SomSpec("sfx/ui/salvar/salvar_01.wav", "ui", 1.0, 1, 0),
}

GRUPOS_VARIACAO = {
    "hit": ("hit_1", "hit_2", "hit_3"),
    "player_step": ("player_step_1", "player_step_2", "player_step_3"),
}

ARMAS_POR_ICONE = {
    "espada": "espada_longa",
    "machado": "machado_guerra",
    "soco": "soco",
}


def _limitar_volume(valor):
    return max(0.0, min(1.0, float(valor)))


def resolver_arma_id(atacante):
    arma_id = getattr(atacante, "arma_id", None)
    if arma_id:
        return arma_id
    arma = getattr(atacante, "arma_equipada", None)
    icone = getattr(arma, "icone", None)
    return ARMAS_POR_ICONE.get(icone, "soco")


def _categoria_da_pasta(pasta):
    for prefixo, categoria in CATEGORIA_POR_RAIZ.items():
        if pasta == prefixo or pasta.startswith(prefixo + "/"):
            return categoria
    return "combat"


class AudioManager:
    def __init__(self, raiz=None, agora_ms=None):
        self.raiz = Path(raiz) if raiz is not None else RAIZ_PROJETO
        self.pasta_sons = self.raiz / "assets" / "sons"
        self._agora_ms = agora_ms or pygame.time.get_ticks
        self._inicializado = False
        self._sons = {}
        self._falhas = set()
        self._avisos = set()
        self._ativos = []
        self._ultimos = {}
        self._ultimos_arquivo = {}
        self._indices_cascata = {}
        self._indice = {}
        self._musica_contexto = None
        self._musica_caminho = None
        self.music_volume = 1.0
        self._config = self._ler_config()
        self._ataque_ativo = ATAQUE_PLAYER_INICIAL
        self._indice_passo = 0
        self.disponivel = False
        self.master_volume = _limitar_volume(
            self._config.get("master", MASTER_VOLUME_INICIAL)
        )
        self.sfx_volume = _limitar_volume(
            self._config.get("sfx", SFX_VOLUME_INICIAL)
        )
        self.volumes_categoria = dict(VOLUMES_CATEGORIA_INICIAIS)
        self.volumes_categoria.update(self._config.get("categorias", {}))
        self.user_volumes = {
            "geral": 1.0,
            "musica": 1.0,
            "efeitos": 1.0,
            "interface": 1.0,
            "ambiencia": 1.0,
        }
        self.diagnostico_ativo = False
        self._diag_ultimos = {}
        self._diag_intervalo_ms = 300
        self._musica_estado = "parada"  # parada | tocando | fade_in | fade_out
        self._musica_volume_alvo = 1.0
        self._musica_fade_ms = 0
        self._musica_fade_inicio_ms = 0
        self._musica_fade_de = 0.0
        self._musica_fade_para = 0.0
        self._musica_contexto_pendente = None
        self._musica_caminho_pendente = None
        self._musica_fade_in_pendente_ms = 0
        self._musica_motivo_transicao = ""
        self._musica_contexto_solicitado = None
        self._musica_sala_atual = None
        self._ambiencia_ativa_nome = None
        self._ambiencia_ativa_caminho = None
        self.menu_music_fade_ms = 2500
        self.ultimo_sfx_debug = {}

    def _ler_config(self):
        caminho = self.pasta_sons / "_config" / "audio.json"
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return {}

    def _config_evento(self, nome):
        perfil = dict(PERFIS_EVENTO.get(nome, {}))
        perfil.update(self._config.get("eventos", {}).get(nome, {}))
        return perfil

    def inicializar(self):
        if self._inicializado:
            return self.disponivel
        self._inicializado = True

        if os.environ.get("PROFANE_AUDIO", "1") == "0":
            logger.info("[AUDIO] desabilitado por PROFANE_AUDIO=0")
            return False

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(24)
            # UI, jogador, ambiência e tochas; música usa o stream separado.
            pygame.mixer.set_reserved(4)
        except pygame.error as erro:
            logger.warning(f"[AUDIO] mixer indisponível: {erro}")
            return False

        self.disponivel = True
        self._indexar_pastas()
        self._carregar_sons()
        return True

    def _indexar_pastas(self):
        self._indice = {}
        for raiz_nome in ("sfx", "ambiencia", "musica"):
            base = self.pasta_sons / raiz_nome
            if not base.is_dir():
                continue
            for pasta, _, arquivos in os.walk(base):
                caminho_pasta = Path(pasta)
                sons = sorted(
                    caminho_pasta / nome
                    for nome in arquivos
                    if Path(nome).suffix.lower() in EXTENSOES_AUDIO
                )
                if not sons:
                    continue
                chave = caminho_pasta.relative_to(self.pasta_sons).as_posix()
                self._indice[chave] = sons
        logger.info(f"[AUDIO] {len(self._indice)} pastas indexadas")

    def _carregar_sons(self):
        carregados = 0
        for chave, spec in ESPECIFICACOES.items():
            caminho = self.pasta_sons / spec.arquivo
            try:
                self._sons[chave] = pygame.mixer.Sound(str(caminho))
                carregados += 1
            except (pygame.error, FileNotFoundError, OSError) as erro:
                self._falhas.add(chave)
                logger.warning(f"[AUDIO] não foi possível carregar '{caminho}': {erro}")
        logger.info(f"[AUDIO] {carregados} efeitos carregados")

    def _carregar_som(self, caminho):
        chave = str(caminho)
        if chave in self._sons:
            return self._sons[chave]
        if chave in self._falhas:
            return None
        try:
            som = pygame.mixer.Sound(chave)
        except (pygame.error, FileNotFoundError, OSError) as erro:
            self._falhas.add(chave)
            self._avisar_uma_vez(
                chave, f"[AUDIO] não foi possível carregar '{caminho}': {erro}"
            )
            return None
        self._sons[chave] = som
        return som

    def _avisar_uma_vez(self, chave, mensagem):
        if chave in self._avisos:
            return
        self._avisos.add(chave)
        logger.warning(mensagem)

    def _prune_ativos(self):
        self._ativos = [
            repro for repro in self._ativos
            if pygame.mixer.Channel(repro.indice_canal).get_busy()
        ]

    def _remover_canal(self, indice_canal):
        self._ativos = [
            repro for repro in self._ativos
            if repro.indice_canal != indice_canal
        ]

    def _contar_grupo(self, grupo):
        self._prune_ativos()
        return sum(1 for repro in self._ativos if repro.grupo == grupo)

    def _resolver_chave(self, chave):
        if chave == "player_attack":
            return f"player_attack_{self._ataque_ativo}", "player_attack"
        if chave in GRUPOS_VARIACAO:
            variacoes = GRUPOS_VARIACAO[chave]
            if chave == "player_step":
                variacao = variacoes[self._indice_passo % len(variacoes)]
                self._indice_passo += 1
            else:
                variacao = random.choice(variacoes)
            return variacao, chave
        return chave, chave

    def _fator_usuario_categoria(self, categoria):
        geral = self.user_volumes.get("geral", 1.0)
        if categoria == "music":
            return geral * self.user_volumes.get("musica", 1.0)
        if categoria == "ui":
            return geral * self.user_volumes.get("interface", 1.0)
        if categoria == "ambience":
            return geral * self.user_volumes.get("ambiencia", 1.0)
        return geral * self.user_volumes.get("efeitos", 1.0)

    def _volume_final(self, categoria, volume_base, ajuste):
        categoria_volume = self.volumes_categoria.get(categoria, 1.0)
        base = (
            self.master_volume
            * (self.music_volume if categoria == "music" else self.sfx_volume)
            * categoria_volume
            * volume_base
            * ajuste
        )
        return _limitar_volume(base * self._fator_usuario_categoria(categoria))

    def _log_diagnostico(self, evento, origem, arquivo, categoria, volume, canal, resultado, motivo="", grupo=None):
        if not self.diagnostico_ativo:
            return
        try:
            agora = int(self._agora_ms())
        except Exception:
            agora = 0
        chave = (
            str(evento),
            str(origem or ""),
            str(arquivo or ""),
            str(categoria or ""),
            bool(resultado),
            str(motivo or ""),
            canal if canal is not None else -1,
        )
        ultimo = self._diag_ultimos.get(chave)
        # evita inundar log com tentativas repetidas rapidamente rejeitadas
        if not resultado and ultimo is not None and agora - ultimo < self._diag_intervalo_ms:
            return
        self._diag_ultimos[chave] = agora
        if len(self._diag_ultimos) > 512:
            corte = agora - self._diag_intervalo_ms * 4
            self._diag_ultimos = {
                k: v for k, v in self._diag_ultimos.items() if v >= corte
            }
        logger_audio_diag.info(
            "[AUDIO-DIAG] evento=%s origem=%s arquivo=%s categoria=%s grupo=%s volume=%.3f canal=%s resultado=%s motivo=%s",
            evento,
            origem or "-",
            arquivo or "-",
            categoria or "-",
            grupo or "-",
            float(volume or 0.0),
            canal if canal is not None else "-",
            "reproduzido" if resultado else "rejeitado",
            motivo or "-",
        )

    def aplicar_preferencias_audio(self, preferencias_audio=None):
        if not isinstance(preferencias_audio, dict):
            return
        for chave in self.user_volumes:
            if chave in preferencias_audio:
                self.user_volumes[chave] = _limitar_volume(
                    float(preferencias_audio[chave]) / 100.0
                    if float(preferencias_audio[chave]) > 1.0
                    else float(preferencias_audio[chave])
                )
        self._atualizar_volumes_ativos()

    def obter_volumes_usuario_percentual(self):
        return {chave: int(round(valor * 100)) for chave, valor in self.user_volumes.items()}

    def _aplicar_volume(self, reproducao):
        pygame.mixer.Channel(reproducao.indice_canal).set_volume(
            self._volume_final(
                reproducao.categoria,
                reproducao.volume_base,
                reproducao.ajuste,
            )
        )

    def _atualizar_volumes_ativos(self):
        if pygame.mixer.get_init() is None:
            return
        self._prune_ativos()
        for reproducao in self._ativos:
            self._aplicar_volume(reproducao)
        self._aplicar_volume_musica_atual()

    def _volume_musica_alvo(self):
        return self._volume_final("music", self._musica_volume_alvo, 1.0)

    def _aplicar_volume_musica_atual(self):
        if pygame.mixer.get_init() is None or self._musica_caminho is None:
            return
        if self._musica_estado in ("fade_in", "fade_out") and self._musica_fade_ms > 0:
            agora = int(self._agora_ms())
            progresso = max(0.0, min(1.0, (agora - self._musica_fade_inicio_ms) / float(self._musica_fade_ms)))
            fator = self._musica_fade_de + (self._musica_fade_para - self._musica_fade_de) * progresso
            pygame.mixer.music.set_volume(_limitar_volume(self._volume_musica_alvo() * fator))
            if progresso >= 1.0:
                self._concluir_fade_musica()
            return
        pygame.mixer.music.set_volume(self._volume_musica_alvo())

    def _iniciar_fade_musica(self, estado, de, para, duracao_ms):
        self._musica_estado = estado
        self._musica_fade_de = _limitar_volume(de)
        self._musica_fade_para = _limitar_volume(para)
        self._musica_fade_ms = max(0, int(duracao_ms))
        self._musica_fade_inicio_ms = int(self._agora_ms())
        if self._musica_fade_ms <= 0:
            self._concluir_fade_musica()
        else:
            self._aplicar_volume_musica_atual()

    def _concluir_fade_musica(self):
        if pygame.mixer.get_init() is None:
            self._musica_estado = "parada"
            return
        if self._musica_estado == "fade_out":
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.unload()
            except Exception:
                pass
            contexto_pendente = self._musica_contexto_pendente
            caminho_pendente = self._musica_caminho_pendente
            fade_in_pendente = self._musica_fade_in_pendente_ms
            motivo = self._musica_motivo_transicao or "fade_out_concluido"
            self._musica_contexto = None
            self._musica_caminho = None
            self._musica_contexto_pendente = None
            self._musica_caminho_pendente = None
            self._musica_fade_in_pendente_ms = 0
            self._musica_estado = "parada"
            if contexto_pendente and caminho_pendente:
                self._iniciar_musica_carregada(contexto_pendente, caminho_pendente, fade_ms=fade_in_pendente, motivo=motivo)
            return
        if self._musica_estado == "fade_in":
            self._musica_estado = "tocando"
            pygame.mixer.music.set_volume(self._volume_musica_alvo())

    def atualizar(self, dt_ms=None):
        if not self.disponivel or pygame.mixer.get_init() is None:
            return
        if self._musica_estado in ("fade_in", "fade_out"):
            self._aplicar_volume_musica_atual()

    def set_music_volume(self, valor):
        self.music_volume = _limitar_volume(valor)
        self._atualizar_volumes_ativos()

    def set_master_volume(self, valor):
        self.master_volume = _limitar_volume(valor)
        self._atualizar_volumes_ativos()

    def set_sfx_volume(self, valor):
        self.sfx_volume = _limitar_volume(valor)
        self._atualizar_volumes_ativos()

    def set_categoria_volume(self, categoria, valor):
        self.volumes_categoria[categoria] = _limitar_volume(valor)
        self._atualizar_volumes_ativos()

    def set_ataque_player(self, nome):
        if nome not in ATAQUES_DISPONIVEIS:
            return self._ataque_ativo
        self._ataque_ativo = nome
        logger.info(f"[AUDIO] ataque do jogador: {nome}")
        return self._ataque_ativo

    def alternar_ataque_player(self):
        indice = ATAQUES_DISPONIVEIS.index(self._ataque_ativo)
        return self.set_ataque_player(
            ATAQUES_DISPONIVEIS[(indice + 1) % len(ATAQUES_DISPONIVEIS)]
        )

    @property
    def ataque_player(self):
        return self._ataque_ativo

    def play_sfx(self, chave, ajuste=1.0, origem=None):
        if not self.disponivel or pygame.mixer.get_init() is None:
            self._log_diagnostico(chave, origem, None, None, 0.0, None, False, "mixer_indisponivel")
            return False

        chave_som, grupo = self._resolver_chave(chave)
        spec = ESPECIFICACOES.get(chave_som)
        if spec is None:
            self._avisar_uma_vez(chave, f"[AUDIO] evento desconhecido: {chave}")
            self._log_diagnostico(chave, origem, None, None, 0.0, None, False, "evento_desconhecido", grupo)
            return False

        som = self._sons.get(chave_som)
        chave_reproducao = chave_som
        caminho_base = self.pasta_sons / spec.arquivo
        if som is not None:
            self._sons.setdefault(str(caminho_base), som)

        if spec.categoria == "ui":
            # UI: arquivo canônico por evento para evitar variantes desbalanceadas
            # (duração/pico/RMS) que causavam loudness/overlaps inconsistentes em hover/navegação.
            # Fallback determinístico só se o canônico estiver indisponível.
            if som is None:
                pasta = Path(spec.arquivo).parent.as_posix()
                prefixo = caminho_base.stem.rsplit("_", 1)[0]
                arquivos = sorted(
                    [p for p in self._indice.get(pasta, [])
                     if p.stem.rsplit("_", 1)[0] == prefixo
                     and p.stem.rsplit("_", 1)[-1].isdigit()],
                    key=lambda p: p.name,
                )
                for caminho in arquivos:
                    som_cand = self._carregar_som(caminho)
                    if som_cand is not None:
                        som = som_cand
                        chave_reproducao = str(caminho)
                        break
        elif spec.categoria == "interaction":
            pasta = Path(spec.arquivo).parent.as_posix()
            prefixo = caminho_base.stem.rsplit("_", 1)[0]
            # Abrir e fechar compartilham pasta, mas nǜo compartilham variantes.
            arquivos = [
                p for p in self._indice.get(pasta, [])
                if p.stem.rsplit("_", 1)[0] == prefixo
                and p.stem.rsplit("_", 1)[-1].isdigit()
            ]
            encontrado = self._som_valido(chave_som, arquivos)
            if encontrado is not None:
                caminho, som = encontrado
                if caminho != caminho_base:
                    chave_reproducao = str(caminho)

        if som is None:
            self._avisar_uma_vez(chave_som, f"[AUDIO] som indispon��vel: {chave_som}")
            self._log_diagnostico(chave, origem, getattr(spec, "arquivo", None), spec.categoria, 0.0, None, False, "som_indisponivel", grupo)
            return False

        perfil = self._config.get("eventos", {}).get(grupo, {})
        return self._tocar_som(
            som,
            chave_reproducao,
            grupo,
            spec.categoria,
            perfil.get("volume", spec.volume_base),
            perfil.get("cooldown_ms", spec.cooldown_ms),
            perfil.get("max_instancias", spec.max_instancias),
            ajuste,
            critico=chave_som in ("player_hurt", "player_death"),
            interrompe=chave_som == "player_death",
            evento=chave,
            origem=origem,
        )

    def _tocar_som(
        self,
        som,
        chave,
        grupo,
        categoria,
        volume_base,
        cooldown_ms,
        max_instancias,
        ajuste=1.0,
        critico=False,
        interrompe=False,
        evento=None,
        origem=None,
    ):
        evento_nome = evento or grupo or chave
        if not self.disponivel or pygame.mixer.get_init() is None:
            self._log_diagnostico(evento_nome, origem, chave, categoria, 0.0, None, False, "mixer_indisponivel", grupo)
            return False

        volume_final = self._volume_final(categoria, volume_base, ajuste)

        agora = int(self._agora_ms())
        ultimo = self._ultimos.get(grupo)
        if ultimo is not None and agora - ultimo < cooldown_ms:
            self._log_diagnostico(evento_nome, origem, chave, categoria, volume_final, None, False, "cooldown", grupo)
            return False

        if self._contar_grupo(grupo) >= max_instancias:
            if grupo not in ("swing", "player_attack"):
                self._log_diagnostico(evento_nome, origem, chave, categoria, volume_final, None, False, "max_instancias", grupo)
                return False
            # Um novo golpe substitui a cauda do swing anterior, sem ficar mudo.
            for repro in list(self._ativos):
                if repro.grupo == grupo:
                    pygame.mixer.Channel(repro.indice_canal).stop()
                    self._remover_canal(repro.indice_canal)

        indice_canal = self._escolher_canal(
            categoria, critico=critico, interrompe=interrompe
        )
        if indice_canal is None:
            self._log_diagnostico(evento_nome, origem, chave, categoria, volume_final, None, False, "sem_canal", grupo)
            return False

        self._remover_canal(indice_canal)
        reproducao = _Reproducao(
            indice_canal=indice_canal,
            chave=chave,
            grupo=grupo,
            categoria=categoria,
            volume_base=volume_base,
            ajuste=float(ajuste),
        )
        self._aplicar_volume(reproducao)
        pygame.mixer.Channel(indice_canal).play(som)
        self._ativos.append(reproducao)
        self._ultimos[grupo] = agora
        self.ultimo_sfx_debug[evento_nome] = {"chave": chave, "grupo": grupo, "categoria": categoria}
        self._log_diagnostico(evento_nome, origem, chave, categoria, volume_final, indice_canal, True, "", grupo)
        return True

    def _escolher_canal(self, categoria, critico=False, interrompe=False):
        if critico:
            canal = pygame.mixer.Channel(1)
            if canal.get_busy():
                if interrompe:
                    canal.stop()
                    self._remover_canal(1)
                else:
                    return None
            return 1

        if categoria == "ui":
            canal = pygame.mixer.Channel(0)
            if canal.get_busy():
                return None
            return 0

        for indice in range(4, pygame.mixer.get_num_channels()):
            if not pygame.mixer.Channel(indice).get_busy():
                return indice
        return None

    # Subconjuntos curados para passos: evita variantes com timbre/material inconsistente.
    _PASSOS_CURADOS = {
        "sfx/player/movimento/passos/pedra": {
            "movimento_passos_pedra_step_01.wav",
            "movimento_passos_pedra_step_02.wav",
            "movimento_passos_pedra_step_03.wav",
            "movimento_passos_pedra_step_04.wav",
            "movimento_passos_pedra_step_05.wav",
            "movimento_passos_pedra_step_06.wav",
        },
    }

    def _arquivos_para_grupo(self, pasta, arquivos, grupo=None):
        if grupo == "step":
            curados = self._PASSOS_CURADOS.get(pasta)
            if curados:
                filtrados = [a for a in arquivos if a.name in curados]
                if filtrados:
                    return filtrados
        return arquivos

    def _escolher_arquivo(self, pasta, arquivos, grupo=None):
        arquivos = self._arquivos_para_grupo(pasta, arquivos, grupo=grupo)
        # Passos usam sequ?ncia determin?stica para evitar altern?ncia inconsistente.
        if grupo == "step":
            indice = self._indices_cascata.get(pasta, 0) % len(arquivos)
            self._indices_cascata[pasta] = indice + 1
            escolhido = arquivos[indice]
            self._ultimos_arquivo[pasta] = escolhido
            return escolhido
        ultimo = self._ultimos_arquivo.get(pasta)
        opcoes = [arquivo for arquivo in arquivos if arquivo != ultimo] or arquivos
        escolhido = random.choice(opcoes)
        self._ultimos_arquivo[pasta] = escolhido
        return escolhido


    def _tocar_cascata(
        self, pastas, grupo, evento, categoria=None, ajuste=1.0,
        prefixo_generico=None, fallback_sfx=None,
    ):
        if not self.disponivel or pygame.mixer.get_init() is None:
            return False
        for pasta in pastas:
            arquivos = self._indice.get(pasta)
            if not arquivos:
                continue
            if pasta == "sfx/combate/generico" and prefixo_generico:
                arquivos = [
                    arquivo for arquivo in arquivos
                    if prefixo_generico in arquivo.stem
                ]
                if not arquivos:
                    continue
            encontrado = self._som_valido(pasta, arquivos, grupo=grupo)
            if encontrado is None:
                continue
            caminho, som = encontrado
            perfil = self._config_evento(evento)
            return self._tocar_som(
                som,
                str(caminho),
                grupo,
                categoria or _categoria_da_pasta(pasta),
                perfil.get("volume", 1.0),
                perfil.get("cooldown_ms", 0),
                perfil.get("max_instancias", 2),
                ajuste,
            )
        return self.play_sfx(fallback_sfx) if fallback_sfx else False

    def _som_valido(self, pasta, arquivos=None, grupo=None):
        restantes = list(self._indice.get(pasta, []) if arquivos is None else arquivos)
        tentativas = len(restantes)
        while restantes and tentativas > 0:
            caminho = self._escolher_arquivo(pasta, restantes, grupo=grupo)
            som = self._carregar_som(caminho)
            if som is not None:
                return caminho, som
            if caminho in restantes:
                restantes.remove(caminho)
            tentativas -= 1
        return None

    def _tocar_loop(self, pasta, grupo, evento, canal, categoria="ambience", origem=None):
        if not self.disponivel or pygame.mixer.get_init() is None:
            self._log_diagnostico(evento, origem, pasta, categoria, 0.0, canal, False, "mixer_indisponivel", grupo)
            return False
        atual = next((r for r in self._ativos if r.indice_canal == canal), None)
        if (pasta and atual and Path(atual.chave).parent == self.pasta_sons / pasta
                and pygame.mixer.Channel(canal).get_busy()):
            return True
        pygame.mixer.Channel(canal).stop()
        self._remover_canal(canal)
        if not pasta:
            return False
        encontrado = self._som_valido(pasta)
        if encontrado is None:
            self._log_diagnostico(evento, origem, pasta, categoria, 0.0, canal, False, "sem_arquivo", grupo)
            return False
        caminho, som = encontrado
        volume_base = self._config_evento(evento).get("volume", 1.0)
        repro = _Reproducao(canal, str(caminho), grupo, categoria, volume_base, 1.0)
        self._aplicar_volume(repro)
        pygame.mixer.Channel(canal).play(som, loops=-1, fade_ms=200)
        self._ativos.append(repro)
        self._log_diagnostico(evento, origem, str(caminho), categoria, self._volume_final(categoria, volume_base, 1.0), canal, True, "loop", grupo)
        return True

    def _resolver_caminho_musica(self, contexto):
        pasta = f"musica/{contexto}"
        for caminho in self._indice.get(pasta, []):
            if caminho.exists():
                return caminho
        return None

    def _volume_alvo_contexto(self, contexto):
        # H.1: descanso mais discreto que combate/boss; menu e exploração preservam base.
        return {
            "menu": 1.0,
            "exploracao": 1.0,
            "boss": 1.0,
            "descanso": 0.72,
        }.get(contexto, 1.0)

    def _iniciar_musica_carregada(self, contexto, caminho, fade_ms=0, motivo=""):
        if pygame.mixer.get_init() is None:
            return False
        self._musica_volume_alvo = self._volume_alvo_contexto(contexto)
        try:
            pygame.mixer.music.load(str(caminho))
            if fade_ms > 0:
                pygame.mixer.music.set_volume(_limitar_volume(self._volume_musica_alvo() * 0.0))
                pygame.mixer.music.play(loops=-1)
                self._musica_contexto = contexto
                self._musica_caminho = caminho
                self._iniciar_fade_musica("fade_in", 0.0, 1.0, fade_ms)
            else:
                pygame.mixer.music.set_volume(self._volume_musica_alvo())
                pygame.mixer.music.play(loops=-1)
                self._musica_contexto = contexto
                self._musica_caminho = caminho
                self._musica_estado = "tocando"
        except (pygame.error, OSError) as erro:
            self._avisar_uma_vez(str(caminho), f"[AUDIO] música indisponível: {caminho}: {erro}")
            self._log_diagnostico(f"music:{contexto}", "audio", str(caminho), "music", 0.0, "music", False, "erro_load", "music")
            return False
        self._musica_motivo_transicao = motivo or self._musica_motivo_transicao
        self._log_diagnostico_musica(f"music:{contexto}", "audio", str(caminho), True, motivo)
        return True

    def play_music(self, contexto, origem=None, fade_ms=500, fade_out_ms=0, motivo=""):
        if not self.disponivel or pygame.mixer.get_init() is None:
            self._musica_contexto_solicitado = contexto
            self._musica_motivo_transicao = motivo or self._musica_motivo_transicao
            self._log_diagnostico(f"music:{contexto}", origem, None, "music", 0.0, "music", False, "mixer_indisponivel", "music")
            return False
        self._musica_contexto_solicitado = contexto
        if motivo:
            self._musica_motivo_transicao = motivo
        if contexto == self._musica_contexto and pygame.mixer.music.get_busy():
            self._musica_volume_alvo = self._volume_alvo_contexto(contexto)
            self._aplicar_volume_musica_atual()
            return True
        if not contexto:
            self.stop_music(fade_ms=fade_out_ms, motivo=motivo or "contexto_nulo")
            return False
        caminho = self._resolver_caminho_musica(contexto)
        if caminho is None:
            self._log_diagnostico(f"music:{contexto}", origem, f"musica/{contexto}", "music", 0.0, "music", False, "sem_arquivo", "music")
            self.stop_music(fade_ms=fade_out_ms, motivo=motivo or "sem_arquivo")
            return False

        if self._musica_caminho is not None and pygame.mixer.music.get_busy() and fade_out_ms > 0:
            # H.1: fade-out real antes de trocar; concluído em atualizar().
            self._musica_contexto_pendente = contexto
            self._musica_caminho_pendente = caminho
            self._musica_fade_in_pendente_ms = max(0, int(fade_ms))
            self._musica_motivo_transicao = motivo or f"transicao_para_{contexto}"
            self._iniciar_fade_musica("fade_out", 1.0, 0.0, fade_out_ms)
            return True

        self.stop_music(fade_ms=0)
        return self._iniciar_musica_carregada(contexto, caminho, fade_ms=fade_ms, motivo=motivo or f"iniciar_{contexto}")

    def stop_music(self, fade_ms=0, motivo=""):
        if motivo:
            self._musica_motivo_transicao = motivo
        if pygame.mixer.get_init() is None:
            self._musica_contexto = None
            self._musica_caminho = None
            self._musica_estado = "parada"
            return
        if fade_ms > 0 and self._musica_caminho is not None and pygame.mixer.music.get_busy():
            self._musica_contexto_pendente = None
            self._musica_caminho_pendente = None
            self._iniciar_fade_musica("fade_out", 1.0, 0.0, fade_ms)
            return
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.unload()
        except Exception:
            pass
        self._musica_contexto = None
        self._musica_caminho = None
        self._musica_contexto_pendente = None
        self._musica_caminho_pendente = None
        self._musica_estado = "parada"

    def _log_diagnostico_musica(self, evento, origem, arquivo, resultado, motivo=""):
        volume = self._volume_musica_alvo() if self._musica_caminho else 0.0
        extra_motivo = motivo or self._musica_motivo_transicao or "-"
        if self.diagnostico_ativo:
            self._log_diagnostico(
                evento, origem, arquivo, "music", volume, "music", resultado, extra_motivo, "music"
            )
            logger_audio_diag.info(
                "[AUDIO-DIAG] sala=%s musica_estado=%s musica_solicitada=%s musica_arquivo=%s musica_volume=%.3f ambiencia=%s ambiencia_arquivo=%s transicao=%s fade=%s",
                self._musica_sala_atual or "-",
                self._musica_estado,
                self._musica_contexto_solicitado or "-",
                arquivo or "-",
                float(volume),
                self._ambiencia_ativa_nome or "-",
                self._ambiencia_ativa_caminho or "-",
                extra_motivo,
                self._musica_estado,
            )

    def set_contexto_sala(self, sala, ambiencia_nome=None):
        self._musica_sala_atual = sala
        if ambiencia_nome is not None:
            self._ambiencia_ativa_nome = ambiencia_nome

    def obter_estado_musical(self):
        return {
            "sala_atual": self._musica_sala_atual,
            "musica_estado": self._musica_estado,
            "musica_solicitada": self._musica_contexto_solicitado,
            "musica_contexto": self._musica_contexto,
            "musica_arquivo": str(self._musica_caminho) if self._musica_caminho else None,
            "musica_volume_final": self._volume_musica_alvo() if self._musica_caminho else 0.0,
            "ambiencia_ativa": self._ambiencia_ativa_nome,
            "ambiencia_arquivo": self._ambiencia_ativa_caminho,
            "motivo_transicao": self._musica_motivo_transicao,
        }

    def _pastas_hit(self, inimigo, arma, material):
        return [
            f"sfx/inimigos/{inimigo}/hit/{arma}",
            f"sfx/inimigos/{inimigo}/hit/_default",
            f"sfx/materiais/{material}/{arma}",
            f"sfx/materiais/{material}/_default",
            "sfx/combate/generico",
        ]

    def _pastas_morte(self, inimigo, arma, material):
        return [
            f"sfx/inimigos/{inimigo}/morte/{arma}",
            f"sfx/inimigos/{inimigo}/morte/_default",
            f"sfx/inimigos/{inimigo}/morte",
            f"sfx/inimigos/_default/morte/{arma}",
            "sfx/inimigos/_default/morte",
            f"sfx/materiais/{material}/{arma}",
            f"sfx/materiais/{material}/_default",
            "sfx/combate/generico",
        ]

    def resolver_pasta(self, inimigo, arma, material, tipo="hit"):
        if tipo == "morte":
            pastas = self._pastas_morte(inimigo, arma, material)
        else:
            pastas = self._pastas_hit(inimigo, arma, material)
        for pasta in pastas:
            if self._indice.get(pasta):
                return pasta
        return None

    def play_hit(self, inimigo, arma, material, kill=False, ajuste=1.0):
        if kill:
            return self._tocar_cascata(
                self._pastas_morte(inimigo, arma, material),
                "kill",
                "kill",
                "combat",
                ajuste,
                prefixo_generico="hit",
            )
        return self._tocar_cascata(
            self._pastas_hit(inimigo, arma, material),
            "hit",
            "hit",
            "combat",
            ajuste,
            prefixo_generico="hit",
        )

    def play_kill(self, inimigo, arma, material, ajuste=1.0):
        return self.play_hit(inimigo, arma, material, kill=True, ajuste=ajuste)

    def play_block(self, inimigo):
        pastas = [
            f"sfx/inimigos/{inimigo}/hit/escudo_bloqueio",
            "sfx/combate/generico",
        ]
        return self._tocar_cascata(
            pastas, "block", "block", "combat", prefixo_generico="block"
        )

    def play_swing(self, arma, ajuste=1.0):
        # Swing = whoosh da arma no ar; nunca usar hits met?licos.
        # espada_longa swing_01/02 cont?m impacto met?lico aud?vel - usar _default whoosh.
        pastas_por_arma = {
            "espada_longa": ["sfx/player/armas/_default"],
        }
        pastas = pastas_por_arma.get(arma, [f"sfx/player/armas/{arma}", "sfx/player/armas/_default"])
        return self._tocar_cascata(
            pastas, "swing", "swing", "player", ajuste
        )

    def play_step(self, material):
        pastas = [
            f"sfx/player/movimento/passos/{material}",
            "sfx/player/movimento/passos/_default",
            "sfx/player/movimento/passos/madeira",
        ]
        return self._tocar_cascata(pastas, "step", "step", "player")

    def play_jump(self):
        pastas = ["sfx/player/movimento/pulo"]
        return self._tocar_cascata(pastas, "jump", "jump", "player")

    def play_eco_profano(self):
        pastas = ["sfx/interacao/eco_profano"]
        return self._tocar_cascata(
            pastas, "eco_profano", "eco_profano", "interaction", fallback_sfx="eco_pickup"
        )

    def play_mecanismo(self):
        pastas = ["sfx/mundo/mecanismos"]
        return self._tocar_cascata(
            pastas, "mecanismo", "mecanismo", "interaction", fallback_sfx="door_open"
        )

    def play_tochas(self, ativo=True):
        return self._tocar_loop("sfx/mundo/tochas" if ativo else None, "tochas", "tochas", 3, categoria="ambience", origem="tochas")

    def play_ambiente(self, nome):
        resultado = self._tocar_loop(f"ambiencia/{nome}" if nome else None, "ambiente", "ambiente", 2, categoria="ambience", origem=f"ambiente:{nome}")
        self._ambiencia_ativa_nome = nome if nome else None
        atual = next((r for r in self._ativos if r.indice_canal == 2), None)
        self._ambiencia_ativa_caminho = atual.chave if atual else None
        return resultado

    def play_enemy_step(self, inimigo):
        pastas = [
            f"sfx/inimigos/{inimigo}/passos",
            "sfx/inimigos/_default/passos",
        ]
        return self._tocar_cascata(
            pastas, "enemy_step", "enemy_step", "combat"
        )

    def play_land(self, material):
        pastas = [
            f"sfx/player/movimento/pouso/{material}",
            "sfx/player/movimento/pouso/_default",
            "sfx/player/movimento/pouso/madeira",
        ]
        return self._tocar_cascata(pastas, "land", "land", "player")

    def play_enemy_attack(self, inimigo, tipo="normal"):
        if tipo == "esporo":
            return self.play_enemy_esporo(inimigo)
        pastas = [
            f"sfx/inimigos/{inimigo}/ataque/{tipo}",
            f"sfx/inimigos/{inimigo}/ataque",
            "sfx/inimigos/_default/ataque",
        ]
        return self._tocar_cascata(pastas, "enemy_attack", "enemy_attack", "combat")

    def play_enemy_esporo(self, inimigo):
        pastas = [
            f"sfx/inimigos/{inimigo}/esporo",
            "sfx/inimigos/_default/ataque",
        ]
        return self._tocar_cascata(
            pastas, "enemy_esporo", "enemy_attack", "combat"
        )

    def play_enemy_entrada(self, inimigo):
        pastas = [
            f"sfx/inimigos/{inimigo}/entrada",
            "sfx/inimigos/_default/entrada",
        ]
        return self._tocar_cascata(
            pastas, "enemy_entrada", "enemy_entrada", "combat"
        )

    def play_enemy_rugido(self, inimigo):
        return self._tocar_cascata(
            [f"sfx/inimigos/{inimigo}/rugido"], "enemy_rugido", "enemy_rugido", "combat"
        )

    def play_enemy_asas(self, inimigo):
        return self._tocar_cascata(
            [f"sfx/inimigos/{inimigo}/asas"], "enemy_asas", "enemy_asas", "combat"
        )

    def play_enemy_quebra_guarda(self, inimigo):
        pastas = [
            f"sfx/inimigos/{inimigo}/hit/quebra_guarda",
            f"sfx/inimigos/{inimigo}/hit/_default",
            "sfx/combate/generico",
        ]
        return self._tocar_cascata(
            pastas,
            "guard_break",
            "guard_break",
            "combat",
            prefixo_generico="hit",
        )

    def play_projectile(self, tipo, fase):
        pastas = [f"sfx/projeteis/{tipo}/{fase}"]
        if fase == "impacto":
            pastas.append("sfx/combate/generico")
        return self._tocar_cascata(pastas, f"projectile_{tipo}_{fase}", "projectile",
                                  "combat", prefixo_generico="hit")

    def stop_world_sfx(self):
        if pygame.mixer.get_init() is not None:
            for repro in list(self._ativos):
                if repro.categoria != "ui":
                    pygame.mixer.Channel(repro.indice_canal).stop()
                    self._remover_canal(repro.indice_canal)
                    self._ultimos.pop(repro.grupo, None)

    def stop_all_sfx(self):
        if pygame.mixer.get_init() is not None:
            for indice in range(pygame.mixer.get_num_channels()):
                pygame.mixer.Channel(indice).stop()
        self._ativos.clear()
        self._ultimos.clear()


audio = AudioManager()
