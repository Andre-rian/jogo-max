from core.combat.ataque import InstanciaAtaque
from core.combat.colisao import Hitbox, construir_hitbox, construir_hitboxes
from core.combat.dano import DamageEvent, RegistroDano
from core.combat.sistema import CombatSystem
from core.combat.tipos import (
    DanoSpec,
    DefinicaoAtaque,
    FaseAtaque,
    HitboxSpec,
    JanelaGolpe,
    KnockbackSpec,
    ModoMovimento,
    PoliticaHit,
)

__all__ = [
    "CombatSystem",
    "DamageEvent",
    "DanoSpec",
    "DefinicaoAtaque",
    "FaseAtaque",
    "Hitbox",
    "HitboxSpec",
    "InstanciaAtaque",
    "JanelaGolpe",
    "KnockbackSpec",
    "ModoMovimento",
    "PoliticaHit",
    "RegistroDano",
    "construir_hitbox",
    "construir_hitboxes",
]
