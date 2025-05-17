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
    panel_rect = pygame.Rect(C.PADDING, start_y, C.SCREEN_WIDTH - 2*C.PADDING, 90)
    pygame.draw.rect(screen, C.PANEL_BG_COLOR, panel_rect, border_radius=C.BORDER_RADIUS)
    pygame.draw.rect(screen, C.INPUT_BORDER_COLOR, panel_rect, 2, border_radius=C.BORDER_RADIUS)

    # Título del panel
    title = font.render("DATOS DEL POKÉMON", True, C.INPUT_BORDER_COLOR)
    screen.blit(title, (panel_rect.x + 15, panel_rect.y + 10))

    current_y = panel_rect.y + 35
    if pokemon_name:
        name_text = font.render(f"Nombre: {pokemon_name.capitalize()}", True, C.TEXT_COLOR)
        screen.blit(name_text, (panel_rect.x + 15, current_y))
        current_y += 25

        types_text = font.render(f"Tipo(s): {', '.join([t.capitalize() for t in pokemon_types])}", True, C.TEXT_COLOR)
        screen.blit(types_text, (panel_rect.x + 15, current_y))

    return panel_rect.bottom + C.PADDING

def draw_effectiveness_results(screen, font, start_y, multiplier, percentage, attacker_types, opponent_types):
    panel_rect = pygame.Rect(C.PADDING, start_y, C.SCREEN_WIDTH - 2*C.PADDING, 120)
    pygame.draw.rect(screen, C.PANEL_BG_COLOR, panel_rect, border_radius=C.BORDER_RADIUS)
    pygame.draw.rect(screen, C.INPUT_BORDER_COLOR, panel_rect, 2, border_radius=C.BORDER_RADIUS)

    # Título del panel
    title = font.render("EFECTIVIDAD", True, C.INPUT_BORDER_COLOR)
    screen.blit(title, (panel_rect.x + 15, panel_rect.y + 10))

    current_y = panel_rect.y + 35
    if multiplier is not None:
        attacker_str = ", ".join([t.capitalize() for t in attacker_types]) if attacker_types else "???"
        opponent_str = ", ".join([t.capitalize() for t in opponent_types]) if opponent_types else "???"
        
        eff_text = font.render(f"{attacker_str} vs {opponent_str}: {multiplier}x", True, C.TEXT_COLOR)
        screen.blit(eff_text, (panel_rect.x + 15, current_y))
        current_y += 25

        # Mensaje descriptivo basado en el multiplicador
        if multiplier >= 2:
            message = "¡Es muy efectivo!"
        elif multiplier <= 0.5:
            message = "No es muy efectivo..."
        else:
            message = "Efectividad normal."
        
        message_surface = font.render(message, True, C.SUCCESS_COLOR if multiplier >= 2 else C.ERROR_COLOR if multiplier <= 0.5 else C.TEXT_COLOR)
        screen.blit(message_surface, (panel_rect.x + 15, current_y))

    return panel_rect.bottom + C.PADDING


def draw_status_message(screen, font, message, is_error):
    """Dibuja un mensaje de estado (error o éxito/info) en la parte inferior."""
    if message:
        color = C.ERROR_COLOR if is_error else C.SUCCESS_COLOR
        msg_surface = font.render(message, True, color)
        pos_y = C.SCREEN_HEIGHT - font.get_height() - C.PADDING
        screen.blit(msg_surface, (C.PADDING, pos_y))
