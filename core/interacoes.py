import logging

logger = logging.getLogger(__name__)


class GerenciadorInteracoes:
    """Seleciona de forma deterministica o alvo de interacao e prompt visivel."""

    def __init__(self):
        self._alvo_prompt = None
        self._candidatos = []

    @staticmethod
    def _distancia_quadrada(player, obj):
        pr = player.rect
        try:
            r = obj.interacao
        except Exception:
            r = getattr(obj, 'rect', None)
        if r is None:
            return 10**12
        dx = pr.centerx - r.centerx
        dy = pr.centery - r.centery
        return dx * dx + dy * dy

    def _limpar_prompts(self, hud):
        if hud is None:
            return
        try:
            hud.limpar_prompt_interacao()
        except Exception:
            hud.limpar_prompt()

    def atualizar(self, player, hud, teclas, contexto):
        # contexto: dict com listas e flags de supressao/carregamento
        self._candidatos = []
        suprimido = bool(contexto.get('suprimido'))
        pausado = bool(contexto.get('pausado'))
        inventario_aberto = bool(contexto.get('inventario_aberto'))
        menu_fogueira_aberto = bool(contexto.get('menu_fogueira_aberto'))
        morrendo = bool(contexto.get('morrendo'))

        if suprimido or pausado or inventario_aberto or menu_fogueira_aberto or morrendo:
            self._alvo_prompt = None
            self._limpar_prompts(hud)
            return None

        grupos = [
            ("bau", list(contexto.get('baus', []))),
            ("drop", list(contexto.get('drops', []))),
            ("drop_eco", list(contexto.get('drops_ecos', []))),
            ("fogueira", list(contexto.get('fogueiras', []))),
            ("porta", list(contexto.get('portas', []))),
        ]

        melhor = None
        melhor_chave = None

        # ordem historica dos grupos, depois proximidade e ordem interna estavel
        for gi, (tipo, objetos) in enumerate(grupos):
            for idx, obj in enumerate(objetos):
                disponivel = False
                try:
                    disponivel = bool(obj.disponivel_para_prompt(player))
                except Exception:
                    # fallback conservador
                    try:
                        inter = getattr(obj, 'interacao', None)
                        disponivel = inter is not None and player.rect.colliderect(inter)
                    except Exception:
                        disponivel = False
                if not disponivel:
                    continue
                dist = self._distancia_quadrada(player, obj)
                chave = (gi, dist, idx)
                if melhor is None or chave < melhor_chave:
                    melhor = obj
                    melhor_chave = chave

        self._alvo_prompt = melhor
        # limpar prompt global antes; apenas o alvo podera exibir
        self._limpar_prompts(hud)
        return melhor

    @property
    def alvo_prompt(self):
        return self._alvo_prompt
