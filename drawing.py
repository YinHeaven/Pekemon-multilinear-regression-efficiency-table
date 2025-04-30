# drawing.py
"""Funciones auxiliares para dibujar elementos de la UI."""

import pygame
import constants as C

def draw_labels(screen, font, pokemon_input_rect, target_input_rect):
    """Dibuja las etiquetas encima de las cajas de entrada."""
    label_pokemon = font.render("Pokémon:", True, C.TEXT_COLOR)
    screen.blit(label_pokemon, (pokemon_input_rect.x, pokemon_input_rect.y - font.get_height() - 5))

    label_target = font.render("Oponente (Tipo o Nombre):", True, C.TEXT_COLOR)
    screen.blit(label_target, (target_input_rect.x, target_input_rect.y - font.get_height() - 5))

def draw_pokemon_info(screen, font, start_y, pokemon_name, pokemon_types):
    """Dibuja la información del Pokémon seleccionado."""
    current_y = start_y
    if pokemon_name:
        name_surface = font.render(f"Pokémon atacante: {pokemon_name.capitalize()}", True, C.TEXT_COLOR)
        screen.blit(name_surface, (C.PADDING, current_y))
        current_y += font.get_height() + C.PADDING // 2

        types_text = ", ".join([t.capitalize() for t in pokemon_types])
        types_surface = font.render(f"Tipos del atacante: {types_text}", True, C.TEXT_COLOR)
        screen.blit(types_surface, (C.PADDING, current_y))
        current_y += font.get_height() + C.PADDING

    return current_y # Devuelve la siguiente posición Y disponible

def draw_effectiveness_results(screen, font, start_y, multiplier, percentage, attacker_types, opponent_input):
    """Dibuja los resultados del cálculo de efectividad."""
    current_y = start_y
    if multiplier is not None:
        attacker_primary_type_display = attacker_types[0].capitalize() if attacker_types else "N/A"
        opponent_input_display = opponent_input.capitalize() if opponent_input else "N/A"

        effectiveness_text = f"Efectividad ({attacker_primary_type_display} vs {opponent_input_display}): {multiplier}x"
        eff_surface = font.render(effectiveness_text, True, C.TEXT_COLOR)
        screen.blit(eff_surface, (C.PADDING, current_y))
        current_y += font.get_height() + C.PADDING // 2

        percentage_text = f"Mapeo 0-100%: {percentage}%"
        perc_surface = font.render(percentage_text, True, C.TEXT_COLOR)
        screen.blit(perc_surface, (C.PADDING, current_y))
        current_y += font.get_height() + C.PADDING

        # Explicación
        explanation_lines = [
            "Nota: La efectividad real es el multiplicador (0x, 0.5x, 1x, 2x...).",
            "El % es solo un mapeo visual.",
        ]
        for line in explanation_lines:
            explanation_surface = font.render(line, True, C.INFO_TEXT_COLOR)
            screen.blit(explanation_surface, (C.PADDING, current_y))
            current_y += font.get_height()

    return current_y # Devuelve la siguiente posición Y disponible


def draw_status_message(screen, font, message, is_error):
    """Dibuja un mensaje de estado (error o éxito/info) en la parte inferior."""
    if message:
        color = C.ERROR_COLOR if is_error else C.SUCCESS_COLOR
        msg_surface = font.render(message, True, color)
        pos_y = C.SCREEN_HEIGHT - font.get_height() - C.PADDING
        screen.blit(msg_surface, (C.PADDING, pos_y))