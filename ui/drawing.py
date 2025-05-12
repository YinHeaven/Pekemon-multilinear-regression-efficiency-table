# File: ui/drawing.py
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

# --- Función draw_effectiveness_results CORREGIDA ---
# Esta función ahora espera una LISTA de tipos para el oponente
def draw_effectiveness_results(screen, font, start_y, multiplier, percentage, attacker_types, opponent_types): # Cambiado opponent_input a opponent_types
    """Dibuja los resultados del cálculo de efectividad."""
    current_y = start_y
    if multiplier is not None:
        # Formatear los tipos del atacante (mostrar todos los tipos)
        attacker_types_str = ", ".join([t.capitalize() for t in attacker_types]) if attacker_types else "N/A"

        # Formatear los tipos del oponente (mostrar todos los tipos)
        # Usamos .join() en la lista de tipos recibida
        opponent_types_str = ", ".join([t.capitalize() for t in opponent_types]) if opponent_types else "N/A"

        # Construir la cadena de efectividad
        # Ahora usamos las cadenas de tipos formateadas directamente
        effectiveness_text = f"Efectividad ({attacker_types_str} vs {opponent_types_str}): {multiplier}x"

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
# --- Fin de la Función draw_effectiveness_results CORREGIDA ---


def draw_status_message(screen, font, message, is_error):
    """Dibuja un mensaje de estado (error o éxito/info) en la parte inferior."""
    if message:
        color = C.ERROR_COLOR if is_error else C.SUCCESS_COLOR
        msg_surface = font.render(message, True, color)
        pos_y = C.SCREEN_HEIGHT - font.get_height() - C.PADDING
        screen.blit(msg_surface, (C.PADDING, pos_y))
