from settings import Screen_widht, Screen_height

# Painel de debug do player (apenas quando settings.DEBUG == True).

class DebugPainel:

    def __init__(self, fonte_pequena):
        self.fonte_pequena = fonte_pequena

    def desenhar(self, tela, player):
        linhas = [
            f'Estado : {player.estado}',
            f'Pos    : ({player.rect.x}, {player.rect.y})',
            f'Vel    : ({player.vel.x:.1f}, {player.vel.y:.1f})',
            f'Dash CD: {player.cooldown_dash}',
            f'No chao: {player.no_chao}',
            f'Stamina: {int(player.stamina)}',
        ]
        for i, linha in enumerate(linhas):
            txt = self.fonte_pequena.render(linha, True, (140, 140, 140))
            tela.blit(txt, (Screen_widht - 240,
                            Screen_height - 400 + i * 18))