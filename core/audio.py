import logging
import os
import random
from dataclasses import dataclass
from pathlib import Path

import pygame

logger = logging.getLogger(__name__)

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
PASTA_SONS = RAIZ_PROJETO / "assets" / "sons"

MASTER_VOLUME_INICIAL = 0.8
SFX_VOLUME_INICIAL = 1.0
VOLUMES_CATEGORIA_INICIAIS = {
    "combat": 0.8,
    "player": 0.9,
    "interaction": 0.7,
    "ui": 0.7,
}

ATAQUES_DISPONIVEIS = ("slash", "ataque")
ATAQUE_PLAYER_INICIAL = "slash"


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
    "player_attack_slash": SomSpec("player/slash.mp3", "player", 0.65, 1, 0),
    "player_attack_ataque": SomSpec("player/ataque.mp3", "player", 0.65, 1, 0),
    "player_hurt": SomSpec("player/dano.wav", "player", 1.0, 1, 40),
    "player_death": SomSpec("player/morte.ogg", "player", 1.0, 1, 0),
    "player_dash": SomSpec("player/dash.wav", "player", 1.0, 1, 0),
    "player_step_1": SomSpec("player/passo_1.wav", "player", 1.0, 2, 90),
    "player_step_2": SomSpec("player/passo_2.wav", "player", 1.0, 2, 90),
    "player_step_3": SomSpec("player/passo_3.wav", "player", 1.0, 2, 90),
    "player_land": SomSpec("player/pouso.wav", "player", 1.0, 1, 80),
    "potion_open": SomSpec("interaçao/pocao_abrir.wav", "interaction", 1.0, 1, 0),
    "potion_drink": SomSpec("interaçao/pocao_beber.wav", "interaction", 1.0, 1, 0),
    "hit_1": SomSpec("combate/acerto_1.wav", "combat", 1.0, 3, 60),
    "hit_2": SomSpec("combate/acerto_2.wav", "combat", 1.0, 3, 60),
    "hit_3": SomSpec("combate/acerto_3.wav", "combat", 1.0, 3, 60),
    "block": SomSpec("combate/escudo_bloqueio.wav", "combat", 1.0, 2, 60),
    "enemy_attack": SomSpec("combate/inimigo_ataque.wav", "combat", 1.0, 3, 80),
    "enemy_death": SomSpec("combate/inimigo_morre.wav", "combat", 1.0, 2, 40),
    "bomb_explosion": SomSpec("combate/bomba_explosao.wav", "combat", 0.75, 3, 50),
    "chest_open": SomSpec("interaçao/bau_abrir.wav", "interaction", 1.0, 1, 0),
    "eco_pickup": SomSpec("interaçao/eco_pegar.wav", "interaction", 1.0, 1, 0),
    "item_pickup": SomSpec("interaçao/item_pegar.wav", "interaction", 1.0, 1, 0),
    "equip_weapon": SomSpec("interaçao/equipar_arma.wav", "interaction", 1.0, 1, 0),
    "equip_armor": SomSpec("interaçao/equipar_armadura.wav", "interaction", 1.0, 1, 0),
    "campfire_light": SomSpec("interaçao/fogueira_acender.wav", "interaction", 1.0, 1, 0),
    "campfire_rest": SomSpec("interaçao/fogueira_descansar.wav", "interaction", 1.0, 1, 0),
    "door_open": SomSpec("interaçao/porta_abrir.wav", "interaction", 1.0, 1, 0),
    "door_close": SomSpec("interaçao/porta_fechar.wav", "interaction", 1.0, 1, 0),
    "level_up": SomSpec("interaçao/level_up.wav", "interaction", 1.0, 1, 0),
    "ui_inventory_open": SomSpec("ui/inventario_abrir.wav", "ui", 1.0, 1, 0),
    "ui_inventory_close": SomSpec("ui/inventario_fechar.wav", "ui", 1.0, 1, 0),
    "ui_confirm": SomSpec("ui/menu_confirmar.wav", "ui", 1.0, 2, 50),
    "ui_error": SomSpec("ui/menu_erro.wav", "ui", 1.0, 2, 80),
    "ui_move": SomSpec("ui/menu_navegar.wav", "ui", 1.0, 2, 60),
    "ui_back": SomSpec("ui/menu_voltar.wav", "ui", 1.0, 2, 50),
    "ui_pause_open": SomSpec("ui/pausa_abrir.wav", "ui", 1.0, 1, 0),
    "ui_pause_close": SomSpec("ui/pausa_fechar.wav", "ui", 1.0, 1, 0),
    "ui_save": SomSpec("ui/salvar.wav", "ui", 1.0, 1, 0),
}

GRUPOS_VARIACAO = {
    "hit": ("hit_1", "hit_2", "hit_3"),
    "player_step": ("player_step_1", "player_step_2", "player_step_3"),
}


def _limitar_volume(valor):
    return max(0.0, min(1.0, float(valor)))


class AudioManager:
    def __init__(self, raiz=None, agora_ms=None):
        self.raiz = Path(raiz) if raiz is not None else RAIZ_PROJETO
        self._agora_ms = agora_ms or pygame.time.get_ticks
        self._inicializado = False
        self._sons = {}
        self._falhas = set()
        self._avisos = set()
        self._ativos = []
        self._ultimos = {}
        self._ataque_ativo = ATAQUE_PLAYER_INICIAL
        self._indice_passo = 0
        self.disponivel = False
        self.master_volume = MASTER_VOLUME_INICIAL
        self.sfx_volume = SFX_VOLUME_INICIAL
        self.volumes_categoria = dict(VOLUMES_CATEGORIA_INICIAIS)

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
            pygame.mixer.set_reserved(2)
        except pygame.error as erro:
            logger.warning(f"[AUDIO] mixer indisponível: {erro}")
            return False

        self.disponivel = True
        self._carregar_sons()
        return True

    def _carregar_sons(self):
        carregados = 0
        for chave, spec in ESPECIFICACOES.items():
            caminho = self.raiz / "assets" / "sons" / spec.arquivo
            try:
                self._sons[chave] = pygame.mixer.Sound(str(caminho))
                carregados += 1
            except (pygame.error, FileNotFoundError, OSError) as erro:
                self._falhas.add(chave)
                logger.warning(f"[AUDIO] não foi possível carregar '{caminho}': {erro}")
        logger.info(f"[AUDIO] {carregados} efeitos carregados")

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

    def _volume_final(self, categoria, volume_base, ajuste):
        categoria_volume = self.volumes_categoria.get(categoria, 1.0)
        return _limitar_volume(
            self.master_volume
            * self.sfx_volume
            * categoria_volume
            * volume_base
            * ajuste
        )

    def _aplicar_volume(self, reproducao):
        pygame.mixer.Channel(reproducao.indice_canal).set_volume(
            self._volume_final(
                reproducao.categoria,
                reproducao.volume_base,
                reproducao.ajuste,
            )
        )

    def _atualizar_volumes_ativos(self):
        self._prune_ativos()
        for reproducao in self._ativos:
            self._aplicar_volume(reproducao)

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

    def play_sfx(self, chave, ajuste=1.0):
        if not self.disponivel or pygame.mixer.get_init() is None:
            return False

        chave_som, grupo = self._resolver_chave(chave)
        spec = ESPECIFICACOES.get(chave_som)
        if spec is None:
            self._avisar_uma_vez(chave, f"[AUDIO] evento desconhecido: {chave}")
            return False

        som = self._sons.get(chave_som)
        if som is None:
            self._avisar_uma_vez(chave_som, f"[AUDIO] som indisponível: {chave_som}")
            return False

        agora = int(self._agora_ms())
        ultimo = self._ultimos.get(grupo)
        if ultimo is not None and agora - ultimo < spec.cooldown_ms:
            return False

        if self._contar_grupo(grupo) >= spec.max_instancias:
            return False

        indice_canal = self._escolher_canal(chave_som)
        if indice_canal is None:
            return False

        self._remover_canal(indice_canal)
        reproducao = _Reproducao(
            indice_canal=indice_canal,
            chave=chave_som,
            grupo=grupo,
            categoria=spec.categoria,
            volume_base=spec.volume_base,
            ajuste=float(ajuste),
        )
        self._aplicar_volume(reproducao)
        pygame.mixer.Channel(indice_canal).play(som)
        self._ativos.append(reproducao)
        self._ultimos[grupo] = agora
        return True

    def _escolher_canal(self, chave):
        if chave in ("player_hurt", "player_death"):
            canal = pygame.mixer.Channel(1)
            if canal.get_busy():
                if chave == "player_death":
                    canal.stop()
                    self._remover_canal(1)
                else:
                    return None
            return 1

        if ESPECIFICACOES[chave].categoria == "ui":
            canal = pygame.mixer.Channel(0)
            if canal.get_busy():
                return None
            return 0

        for indice in range(2, pygame.mixer.get_num_channels()):
            if not pygame.mixer.Channel(indice).get_busy():
                return indice
        return None

    def stop_all_sfx(self):
        if pygame.mixer.get_init() is not None:
            for indice in range(pygame.mixer.get_num_channels()):
                pygame.mixer.Channel(indice).stop()
        self._ativos.clear()


audio = AudioManager()
