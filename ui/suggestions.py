#suggestions.py
"""Lógica para generar y dibujar las sugerencias."""

import pygame
import constants as C
from pokeapi_client import get_pokemon_by_type # Necesario para buscar por tipo

def update_pokemon_suggestions(search_text, all_pokemon_names, valid_types):
    """Genera sugerencias de Pokémon por nombre y tipo."""
    search_text_lower = search_text.lower()
    name_suggestions = []
    type_suggestions = []
    message = "" # Un solo mensaje para simplificar (éxito o informativo)
    is_error = False

    # 1. Buscar por nombre (prefijo)
    if search_text_lower:
        name_suggestions = [name for name in all_pokemon_names if name.startswith(search_text_lower)]

    # 2. Buscar por tipo si el texto coincide exactamente con un tipo conocido
    if search_text_lower in valid_types:
        message = f"Buscando Pokémon de tipo {search_text_lower}..."
        # NOTA: Idealmente asíncrono, aquí es síncrono
        type_pokemon_names = get_pokemon_by_type(search_text_lower)
        if type_pokemon_names is not None: # get_pokemon_by_type devuelve [] en error, no None
             if type_pokemon_names:
                 type_suggestions = type_pokemon_names
                 message = f"Mostrando Pokémon de tipo {search_text_lower}."
             else: # La API respondió pero no encontró Pokémon de ese tipo (raro pero posible)
                 message = f"No se encontraron Pokémon de tipo {search_text_lower}."
                 # Podríamos considerarlo un "warning" más que un error fatal.
        else: # Hubo un error en la llamada API
             message = f"Error al buscar tipo {search_text_lower}."
             is_error = True


    # 3. Combinar y limitar
    # Priorizar sugerencias de nombre si también se busca por tipo
    combined_suggestions = name_suggestions + [p for p in type_suggestions if p not in name_suggestions]
    combined_suggestions.sort()
    suggestions = combined_suggestions[:C.MAX_SUGGESTIONS]

    return suggestions, message, is_error


def update_type_suggestions(search_text, valid_types):
    """Genera sugerencias de tipos válidos."""
    search_text_lower = search_text.lower()
    if search_text_lower:
        suggestions = [t for t in valid_types if t.startswith(search_text_lower)]
        suggestions.sort()
        return suggestions[:C.MAX_SUGGESTIONS]
    return []


def draw_suggestions(screen, suggestions, highlighted_index, input_rect, font):
    """Dibuja la lista de sugerencias debajo de la caja de entrada."""
    if not suggestions:
        return

    suggestion_box_x = input_rect.x
    suggestion_box_y = input_rect.y + input_rect.height + C.PADDING // 2 # Un poco más cerca
    suggestion_box_width = input_rect.width

    for i, suggestion in enumerate(suggestions):
        suggestion_rect = pygame.Rect(suggestion_box_x, suggestion_box_y + i * C.SUGGESTION_HEIGHT,
                                      suggestion_box_width, C.SUGGESTION_HEIGHT)

        # Determinar color de fondo
        bg_color = C.SUGGESTION_BG_COLOR
        if i == highlighted_index:
            bg_color = C.SUGGESTION_HIGHLIGHT_COLOR
        if suggestion_rect.collidepoint(pygame.mouse.get_pos()):
            bg_color = C.SUGGESTION_HOVER_COLOR

        pygame.draw.rect(screen, bg_color, suggestion_rect)
        pygame.draw.rect(screen, C.INPUT_BORDER_COLOR, suggestion_rect, 1) # Borde

        text_surface = font.render(suggestion.capitalize(), True, C.TEXT_COLOR)
        text_y = suggestion_rect.y + (C.SUGGESTION_HEIGHT - text_surface.get_height()) // 2
        screen.blit(text_surface, (suggestion_rect.x + C.PADDING, text_y))

    # Devolver las rects para la detección de clics en Main.py
    suggestion_rects = [pygame.Rect(suggestion_box_x, suggestion_box_y + i * C.SUGGESTION_HEIGHT, suggestion_box_width, C.SUGGESTION_HEIGHT) for i in range(len(suggestions))]
    return suggestion_rects