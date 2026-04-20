import sqlite3
import json
import os
from datetime import datetime

CAMINHO_DB = "saves.db"

class Savemaneger:

    def __init__(self):
        self._conexao = sqlite3.connect(CAMINHO_DB)
        self._criar_tabela()


    def _criar_tabela(self):

        self._conexao.execute(""" CREATE TABLE IF NOT EXISTS saves (
                              slot  INTEGER PRIMARY KEY,
                              checkpoint_sala   TEXT,
                              checkpoint_x      INTEGER,
                              checkpoint_y      INTEGER,
                              fogueiras_ativas  TEXT,
                              bosses_derrotados TEXT,
                              tem_espada        INTEGER,
                              data_hora         TEXT
                                                                    )
                            """)
        
        self._conexao.commit()



    def salvar(self, slot, game_scene):
        
        
        #serializar os sets como jason

        fogueiras = json.dumps(list(game_scene.fogueiras_ativas))
        bosses = json.dumps(list(game_scene.bosses_derrotados))
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")


        self._conexao.execute("""
        INSERT OR REPLACE INTO saves
                              (slot, checkpoint_sala, checkpoint_x, checkpoint_y,
                              fogueiras_ativas, bosses_derrotados, tem_espada, data_hora)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                              (
                                  slot,
                                  game_scene.sala_atual,
                                  int(game_scene.player.rect.x),
                                  int(game_scene.player.rect.y),
                                  fogueiras,
                                  bosses,
                                  int(game_scene.player.tem_espada),
                                  data_hora

                              ))
        self._conexao.commit()

    def carregar(self, slot):
        # retorna os dados de cada slot ou NONe se o slot estive vazio
        
        cursor = self._conexao.execute(
            "SELECT * FROM saves WHERE slot = ?", (slot,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        
        return {
            "slot"              : row[0],
            "checkpoint_sala"   : row[1],
            "checkpoint_x"      : row[2],
            "checkpoint_y"      : row[3],
            "fogueiras_ativas"  : set(map(tuple, json.loads(row[4]))),
            "bosses_derrotados" : set(json.loads(row[5])),
            "tem_espada"        : bool(row[6]),
            "data_hora"         : row[7],
        }


    def listar_slots(self):
        #retorna as infos dos 3 slots, none se vazio

        slots = {}
        for i in range(1, 4):
            slots[i] = self.carregar(i)
        return slots
    
    def deletar(self, slot):
        self._conexao.execute(
            "DELETE FROM saves WHERE slot = ?", (slot,)
        )
        self._conexao.commit()


    def fechar(self):
        self._conexao.close()
