# game_logic.py
"""Lógica del juego no relacionada directamente con la UI o API."""

from data import TYPE_EFFECTIVENESS

def calculate_effectiveness(attacker_types, defender_types):
    """Calcula la efectividad del primer tipo del atacante contra los tipos del defensor."""
    if not attacker_types or not defender_types:
        return 1.0 # Efectividad normal por defecto

    attacker_primary_type = attacker_types[0]
    calculated_multiplier = 1.0

    for defender_type in defender_types:
        multiplier = TYPE_EFFECTIVENESS.get(attacker_primary_type, {}).get(defender_type, 1.0)
        calculated_multiplier *= multiplier

    return calculated_multiplier

def map_multiplier_to_percentage(multiplier):
    """Mapea arbitrariamente el multiplicador a un rango 0-100% para visualización."""
    if multiplier == 0: return 0
    if multiplier == 0.25: return 5
    if multiplier == 0.5: return 25
    if multiplier == 1: return 50
    if multiplier == 2: return 75
    if multiplier == 4: return 100
    # Mapeo simple para otros valores, limitado a 0-100
    return min(100, max(0, int(multiplier * 25)))