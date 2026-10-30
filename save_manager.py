import sqlite3
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

CAMINHO_DB = os.path.join(os.path.dirname(__file__), "saves.db")

class Savemaneger:

    def __init__(self):
        self._conexao = None
        try:
            self._conexao = sqlite3.connect(CAMINHO_DB)
            self._criar_tabela()
        except sqlite3.Error as e:
            logger.error(f"[SAVE] não foi possível abrir o banco '{CAMINHO_DB}': {e}")
            self._conexao = None

    @property
    def disponivel(self):
        return self._conexao is not None

    def _criar_tabela(self):
        if self._conexao is None:
            return
        try:
            self._conexao.execute(""" CREATE TABLE IF NOT EXISTS saves (
                                  slot                      INTEGER PRIMARY KEY,
                                  checkpoint_sala           TEXT,
                                  checkpoint_x              INTEGER,
                                  checkpoint_y              INTEGER,
                                  fogueiras_ativas          TEXT,
                                  bosses_derrotados         TEXT,
                                  inventario                TEXT,
                                  drops_fixos_coletados     TEXT,
                                  baus_abertos              TEXT,
                                  ecos                      INTEGER,
                                  drop_eco                  TEXT,
                                  data_hora                 TEXT
                                                                        )
                              """)
            self._conexao.commit()
        except sqlite3.Error as e:
            logger.error(f"[SAVE] falha ao criar tabela: {e}")
            self._conexao.close()
            self._conexao = None

    @staticmethod
    def _decode_json(texto, fallback):
        try:
            return json.loads(texto)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"[SAVE] dado corrompido no save ({texto!r}): {e} — usando fallback")
            return fallback

    def salvar(self, slot, game_scene):
        if self._conexao is None:
            logger.warning("[SAVE] banco indisponível — save ignorado")
            return False

        #serializar os sets como jason
        try:
            fogueiras = json.dumps(list(game_scene.fogueiras_ativas))
            bosses = json.dumps(list(game_scene.bosses_derrotados))
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            baus_abertos = json.dumps([list(b) for b in game_scene.baus_abertos])
            drops_fixos = json.dumps(list(game_scene.drops_fixos_coletados))
            ecos = game_scene.player.ecos

            #searializaçao dos ecos caso exista
            drop_eco_data = None
            for sala, drop in game_scene.drops_ecos_por_sala.items():
                if drop.ativo:
                    drop_eco_data = json.dumps({
                        "sala": sala,
                        "x": drop.x,
                        "y": drop.y,
                        "quantidade": drop.quantidade
                    })
                    break
            if drop_eco_data is None:
                drop_eco_data = json.dumps(None)

            inventario = json.dumps(game_scene.player.inventario)

            self._conexao.execute("""
            INSERT OR REPLACE INTO saves
                                  (slot, checkpoint_sala, checkpoint_x, checkpoint_y,
                                  fogueiras_ativas, bosses_derrotados,  inventario, drops_fixos_coletados, baus_abertos, ecos, drop_eco, data_hora)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (
                                      slot,
                                      game_scene.sala_atual,
                                      int(game_scene.player.rect.x),
                                      int(game_scene.player.rect.y),
                                      fogueiras,
                                      bosses,
                                      inventario,
                                      drops_fixos,
                                      baus_abertos,
                                      ecos,
                                      drop_eco_data,
                                      data_hora
                                  ))
            self._conexao.commit()
            return True
        except (sqlite3.Error, AttributeError, TypeError) as e:
            logger.exception(f"[SAVE] falha ao salvar slot {slot}: {e}")
            return False

    def carregar(self, slot):
        # retorna os dados de cada slot ou NONe se o slot estive vazio
        if self._conexao is None:
            logger.warning("[SAVE] banco indisponível — não dá para carregar")
            return None

        try:
            cursor = self._conexao.execute(
                "SELECT * FROM saves WHERE slot = ?", (slot,)
            )
        except sqlite3.Error as e:
            logger.exception(f"[SAVE] falha ao consultar slot {slot}: {e}")
            return None

        row = cursor.fetchone()
        if row is None:
            return None

        try:
            return {
                "slot"                  : row[0],
                "checkpoint_sala"       : row[1],
                "checkpoint_x"          : row[2],
                "checkpoint_y"          : row[3],
                "fogueiras_ativas"      : set(map(tuple, self._decode_json(row[4], []))),
                "bosses_derrotados"     : set(self._decode_json(row[5], [])),
                "inventario"            : self._decode_json(row[6], {}),
                "drops_fixos_coletados" : set(map(tuple, self._decode_json(row[7], []))),
                "baus_abertos"          : set(map(tuple, self._decode_json(row[8], []))),
                "ecos"                  : row[9],
                "drop_eco"              : self._decode_json(row[10], None),
                "data_hora"             : row[11]
            }
        except (TypeError, ValueError) as e:
            logger.exception(f"[SAVE] save do slot {slot} ilegível: {e}")
            return None

    def listar_slots(self):
        #retorna as infos dos 3 slots, none se vazio

        slots = {}
        for i in range(1, 4):
            slots[i] = self.carregar(i)
        return slots

    def deletar(self, slot):
        if self._conexao is None:
            logger.warning("[SAVE] banco indisponível — não dá para deletar")
            return False
        try:
            self._conexao.execute(
                "DELETE FROM saves WHERE slot = ?", (slot,)
            )
            self._conexao.commit()
            return True
        except sqlite3.Error as e:
            logger.exception(f"[SAVE] falha ao deletar slot {slot}: {e}")
            return False

    def fechar(self):
        if self._conexao is not None:
            try:
                self._conexao.close()
            except sqlite3.Error as e:
                logger.warning(f"[SAVE] falha ao fechar banco: {e}")
            finally:
                self._conexao = None