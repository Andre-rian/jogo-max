import json
import os


#carrega o banco de itens
_caminho = os.path.join(os.path.dirname(__file__), "..", "..", "itens.json")
with open(_caminho, encoding="utf-8") as f:
    _banco = json.load(f)

class Item:
    #classe bas para todos os itens do jogo

    def __init__(self, id_, dados):
        
        self.id = id_
        self.nome = dados["nome"]
        self.descricao = dados["descriçao"]
        self.tipo = dados["tipo"]    #fala se é arma, consumivel, armadura, chave e ect


class Arma(Item):
    def __init__(self, id_, dados):
        super().__init__(id_, dados)

        self.dano = dados["dano"]
        self.escalonamento = dados["escalonamento"] #se a arma é pesada ou argil

        self.requisitos = {
            "força" : dados["req_força"],
            "destreza" : dados["req_destreza"]
        }

    def pode_equipar(self, stats_player):
        #por enquanto que nao existe o status, sempre ira rertona True
        return True
    

class Consumivel(Item):

    def __init__(self, id_, dados):
        super().__init__(id_, dados) 

        self.efeito = dados["efeito"]
        self.quantidade = dados["quantidade"]
        self.cargas = self.cargas_max


class Chave(Item):

    def __init__(self, id_, dados):
        super().__init__(id_, dados)


class Material(Item):
    def __init__(self, id_, dados):
        super().__init__(id_, dados)
        self.quantidade = dados.get("quantidade", 1)



# Registro - mapea os ids dos objetos
_fabricas = {
    "arma" : Arma,
    "consumivel" : Consumivel,
    "chave" : Chave,
    "material" : Material,
}

Registro_Itens = {}
for id_str, dados in _banco.items():
    id_ = int(id_str)
    fabrica = _fabricas.get(dados["tipo"])
    if fabrica:
        Registro_Itens[id_] = fabrica(id_, dados)



def get_item(id):
    #retorna uma nova istancia de itens pelo o id
    dados = _banco.get(str(id_))
    if not dados:
        return None
    fabrica = _fabricas.get(dados["tipo"])
    return fabrica(int(id_), dados) if fabrica else None



#atalhos pra quebra galho
EspadaLonga = Registro_Itens[1]