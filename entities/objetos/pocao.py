import pygame


Cura_percentual = 0.40 #cura 40% do hp maximo'
Cargas_inicias = 3
Cooldown_uso_max = 90 #1.5 segundos entre os usos

class Pocao:

    def __init__(self):
        self.cargas_max = Cargas_inicias
        self.cargas = Cargas_inicias
        self._colldown = 0
        self._curando = False       #flag para usamos na sprite futuramente
        self._timer_cura = 0
        self.icone = "pocao"


        self.nome = "Poção de Vida"
        self.descricao = "Um frasco com líquido curativo. Recupera boa parte da vitalidade do combatente"
        self.tipo      = "consumivel"

    def atualizar(self):
        if self._colldown > 0:
            self._colldown -= 1

    def usar(self, player):
        if self.cargas <= 0:
            return False
        if self._colldown > 0:
            return False
        
        if player.hp >= player.hp_max:
            return False
        
        cura = int(player.hp_max * Cura_percentual)
        player.hp = min(player.hp_max, player.hp + cura)
        self.cargas -= 1
        self._colldown = Cooldown_uso_max
        return True
    
    def recarregar(self):
        self.cargas = self.cargas_max