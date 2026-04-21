
class Item:
    #classe bas para todos os itens do jogo

    def __init__(self, nome, descriçao, tipo):
        self.nome = nome
        self.descricao = descriçao
        self.tipo = tipo    #fala se é arma, consumivel, armadura, chave e ect


class Arma(Item):
    def __init__(self, nome, descriçao, dano, escalonamento, req_força=0, req_destreza=0):
        super().__init__(nome, descriçao, tipo="arma")

        self.dano = dano
        self.escalonamento = escalonamento #se a arma é pesada ou argil

        self.requesitos = {
            "força" : req_força,
            "destreza" : req_destreza
        }

    def pode_equipar(self, stats_player):
        #por enquanto que nao existe o status, sempre ira rertona True
        return True
    

class Consumivel(Item):

    def __init__(self, nome, descriçao, efeito, quantidade=1):
        super().__init__(nome, descriçao, tipo="consumivel")

        self.efeito = efeito
        self.quantidade = quantidade


class Chave(Item):

    def __init__(self, nome, descriçao):
        super().__init__(nome, descriçao, tipo="chave")




#itens do jogo, por enquanto vai ficar aq


EspadaLonga = Arma(
    nome= "Espada Longa",
    descriçao= "Espada padrão dos cavaleiros do reino."
                "Equilibrada e confiavel, serve bem para qualquer combatente",
    dano= 25,
    escalonamento= "agil",
    req_força= 8,
    req_destreza= 10
)