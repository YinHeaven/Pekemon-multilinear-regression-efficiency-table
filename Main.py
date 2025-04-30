# Main.py
"""Punto de entrada principal de la aplicación Pokémon Suggester."""

import pygame
import sys
import constants as C
import data
import pokeapi_client
import game_logic
from ui.input_box import InputBox
from ui import suggestions as suggestion_ui
from ui import drawing as ui_draw

def run_app():
    """Inicializa Pygame y ejecuta el bucle principal de la aplicación."""
    # --- Inicialización ---
    pygame.init()
    screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
    pygame.display.set_caption("Buscador Pokémon y Efectividad de Tipo vRefactored")
    font = pygame.font.Font(None, C.FONT_SIZE)
    clock = pygame.time.Clock() # Para controlar FPS si es necesario

    # --- Carga de Datos Iniciales ---
    print("Cargando datos iniciales...")
    all_pokemon_names = pokeapi_client.get_all_pokemon_names()
    if not all_pokemon_names:
        print("Error crítico: No se pudo cargar la lista de Pokémon. Saliendo.")
        pygame.quit()
        sys.exit()
    print(f"Cargados {len(all_pokemon_names)} nombres de Pokémon.")

    # --- Estado de la Aplicación ---
    active_input_box = None # 'pokemon' o 'target' o None
    pokemon_input = InputBox(C.PADDING, C.PADDING * 2 + C.FONT_SIZE, 300, C.INPUT_BOX_HEIGHT, font)
    pokemon_input.set_placeholder("Nombre o Tipo Pokémon")
    target_input = InputBox(C.PADDING, pokemon_input.rect.bottom + C.PADDING * 2 + C.FONT_SIZE, 300, C.INPUT_BOX_HEIGHT, font)
    target_input.set_placeholder("Oponente (Tipo o Nombre)")

    current_pokemon_suggestions = []
    highlighted_pokemon_suggestion_idx = -1
    pokemon_suggestion_rects = []

    current_target_suggestions = []
    highlighted_target_suggestion_idx = -1
    target_suggestion_rects = []

    selected_pokemon_name = ""
    selected_pokemon_types = []
    calculated_multiplier = None
    calculated_percentage = None

    status_message = ""
    is_status_error = False

    # --- Bucle Principal ---
    running = True
    while running:
        # --- Manejo de Eventos ---
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True
                # Desactivar cajas si se hace clic fuera
                if not pokemon_input.rect.collidepoint(event.pos):
                    pokemon_input.active = False
                    pokemon_input.color = C.INPUT_BORDER_COLOR
                if not target_input.rect.collidepoint(event.pos):
                    target_input.active = False
                    target_input.color = C.INPUT_BORDER_COLOR

            # Pasar evento a las cajas de entrada
            pokemon_event_result = pokemon_input.handle_event(event)
            target_event_result = target_input.handle_event(event)

            # Determinar qué caja está activa (si alguna cambió)
            if pokemon_event_result:
                active_input_box = 'pokemon'
                target_input.active = False # Desactivar la otra
                target_input.color = C.INPUT_BORDER_COLOR
            elif target_event_result:
                active_input_box = 'target'
                pokemon_input.active = False # Desactivar la otra
                pokemon_input.color = C.INPUT_BORDER_COLOR

            # --- Lógica de Teclado para Sugerencias y Selección ---
            if event.type == pygame.KEYDOWN:
                current_suggestions = []
                highlighted_idx = -1
                suggestions_len = 0

                if active_input_box == 'pokemon':
                    current_suggestions = current_pokemon_suggestions
                    highlighted_idx = highlighted_pokemon_suggestion_idx
                    suggestions_len = len(current_suggestions)
                elif active_input_box == 'target':
                    current_suggestions = current_target_suggestions
                    highlighted_idx = highlighted_target_suggestion_idx
                    suggestions_len = len(current_suggestions)

                if suggestions_len > 0:
                    if event.key == pygame.K_DOWN:
                        highlighted_idx = (highlighted_idx + 1) % suggestions_len
                    elif event.key == pygame.K_UP:
                        highlighted_idx = (highlighted_idx - 1 + suggestions_len) % suggestions_len
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_TAB: # Tratar TAB como Enter para selección
                        if highlighted_idx != -1:
                            selected_suggestion = current_suggestions[highlighted_idx]
                            # --- Lógica de Selección (Enter/Tab en sugerencia) ---
                            if active_input_box == 'pokemon':
                                process_pokemon_selection(selected_suggestion)
                            elif active_input_box == 'target':
                                process_target_selection(selected_suggestion)
                            # Resetear sugerencias después de seleccionar
                            current_pokemon_suggestions = []
                            current_target_suggestions = []
                            highlighted_pokemon_suggestion_idx = -1
                            highlighted_target_suggestion_idx = -1

                # Actualizar índice resaltado en el estado global
                if active_input_box == 'pokemon':
                    highlighted_pokemon_suggestion_idx = highlighted_idx
                elif active_input_box == 'target':
                    highlighted_target_suggestion_idx = highlighted_idx

            # --- Lógica de Selección con Enter directamente en Input ---
            if (pokemon_event_result == "enter" and active_input_box == 'pokemon' and not current_pokemon_suggestions) or \
               (target_event_result == "enter" and active_input_box == 'target' and not current_target_suggestions):

                if active_input_box == 'pokemon':
                     if pokemon_input.text:
                         process_pokemon_selection(pokemon_input.text)
                     else:
                          status_message = "Introduce un nombre o tipo de Pokémon."
                          is_status_error = True
                elif active_input_box == 'target':
                     if target_input.text:
                          process_target_selection(target_input.text)
                     else:
                          status_message = "Introduce un tipo o nombre de oponente."
                          is_status_error = True

        # --- Lógica de Selección por Clic del Ratón en Sugerencias ---
        if mouse_clicked:
            if active_input_box == 'pokemon' and current_pokemon_suggestions:
                for i, rect in enumerate(pokemon_suggestion_rects):
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        process_pokemon_selection(current_pokemon_suggestions[i])
                        break # Procesar solo un clic
            elif active_input_box == 'target' and current_target_suggestions:
                for i, rect in enumerate(target_suggestion_rects):
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        process_target_selection(current_target_suggestions[i])
                        break # Procesar solo un clic

        # --- Actualización de Sugerencias (basado en la caja activa) ---
        if active_input_box == 'pokemon':
            current_pokemon_suggestions, msg, err = suggestion_ui.update_pokemon_suggestions(
                pokemon_input.text, all_pokemon_names, data.VALID_TYPES
            )
            # Actualizar mensajes solo si se generó uno nuevo al buscar sugerencias
            if msg:
                 status_message = msg
                 is_status_error = err

            # Resetear la otra caja de sugerencias
            current_target_suggestions = []
            highlighted_target_suggestion_idx = -1

            # Resetear índice si las sugerencias cambian o desaparecen
            if not current_pokemon_suggestions or highlighted_pokemon_suggestion_idx >= len(current_pokemon_suggestions):
                 highlighted_pokemon_suggestion_idx = -1


        elif active_input_box == 'target':
            current_target_suggestions = suggestion_ui.update_type_suggestions(
                target_input.text, data.VALID_TYPES
            )
            # Resetear la otra caja de sugerencias
            current_pokemon_suggestions = []
            highlighted_pokemon_suggestion_idx = -1

            # Resetear índice si las sugerencias cambian o desaparecen
            if not current_target_suggestions or highlighted_target_suggestion_idx >= len(current_target_suggestions):
                 highlighted_target_suggestion_idx = -1

        else: # Ninguna caja activa
            current_pokemon_suggestions = []
            highlighted_pokemon_suggestion_idx = -1
            current_target_suggestions = []
            highlighted_target_suggestion_idx = -1


        # --- Lógica de Procesamiento (llamada desde eventos) ---
        def process_pokemon_selection(name_or_type):
            """Intenta obtener datos del Pokémon y actualiza el estado."""
            nonlocal selected_pokemon_name, selected_pokemon_types, status_message, is_status_error
            nonlocal calculated_multiplier, calculated_percentage, current_pokemon_suggestions, highlighted_pokemon_suggestion_idx

            name_lower = name_or_type.lower()
            status_message = f"Buscando {name_lower}..."
            is_status_error = False
            pygame.display.flip() # Mostrar mensaje de búsqueda

            types = pokeapi_client.get_pokemon_types(name_lower)
            if types:
                selected_pokemon_name = name_lower
                selected_pokemon_types = types
                pokemon_input.text = name_lower # Actualizar caja con el nombre encontrado
                pokemon_input.update_text_surface()
                status_message = f"Datos de {name_lower.capitalize()} cargados."
                is_status_error = False
                # Reiniciar cálculo si cambia el atacante
                calculated_multiplier = None
                calculated_percentage = None
            else:
                # Podría ser un tipo válido en lugar de un nombre no encontrado
                if name_lower in data.VALID_TYPES:
                     status_message = f"'{name_lower.capitalize()}' es un tipo. Introduce un nombre de Pokémon."
                     is_status_error = True
                else:
                     status_message = f"Pokémon '{name_lower}' no encontrado."
                     is_status_error = True
                selected_pokemon_name = ""
                selected_pokemon_types = []

            # Limpiar sugerencias después de la selección
            current_pokemon_suggestions = []
            highlighted_pokemon_suggestion_idx = -1


        def process_target_selection(type_or_name):
            """Intenta obtener tipos del oponente y calcula efectividad."""
            nonlocal status_message, is_status_error, calculated_multiplier, calculated_percentage
            nonlocal current_target_suggestions, highlighted_target_suggestion_idx

            target_lower = type_or_name.lower()

            if not selected_pokemon_types:
                status_message = "Selecciona un Pokémon atacante primero."
                is_status_error = True
                return

            status_message = f"Procesando oponente '{target_lower}'..."
            is_status_error = False
            pygame.display.flip()

            opponent_types = None
            opponent_display_name = target_lower # Lo que se usará en el mensaje de éxito/error

            # ¿Es un tipo conocido?
            if target_lower in data.VALID_TYPES:
                opponent_types = [target_lower]
            else:
                # Si no es un tipo, intenta buscarlo como Pokémon
                opponent_types = pokeapi_client.get_pokemon_types(target_lower)
                if opponent_types:
                     opponent_display_name = f"{target_lower.capitalize()} ({', '.join(t.capitalize() for t in opponent_types)})"
                else:
                    status_message = f"Entrada '{target_lower}' no reconocida como Tipo o Pokémon."
                    is_status_error = True
                    calculated_multiplier = None
                    calculated_percentage = None
                    # Limpiar sugerencias después del intento
                    current_target_suggestions = []
                    highlighted_target_suggestion_idx = -1
                    return # Salir si no se encontró nada

            # Si tenemos tipos de oponente (ya sea directo o de un Pokémon)
            if opponent_types:
                 target_input.text = target_lower # Actualizar input con texto procesado
                 target_input.update_text_surface()
                 multiplier = game_logic.calculate_effectiveness(selected_pokemon_types, opponent_types)
                 calculated_multiplier = multiplier
                 calculated_percentage = game_logic.map_multiplier_to_percentage(multiplier)
                 status_message = f"Efectividad calculada contra {opponent_display_name}."
                 is_status_error = False
            else: # Seguridad, no debería llegar aquí si la lógica anterior es correcta
                 status_message = "Error inesperado al procesar oponente."
                 is_status_error = True
                 calculated_multiplier = None
                 calculated_percentage = None

            # Limpiar sugerencias después de la selección/procesamiento
            current_target_suggestions = []
            highlighted_target_suggestion_idx = -1


        # --- Dibujado ---
        screen.fill(C.BG_COLOR)

        # Dibujar Etiquetas
        ui_draw.draw_labels(screen, font, pokemon_input.rect, target_input.rect)

        # Dibujar Cajas de Entrada
        pokemon_input.draw(screen)
        target_input.draw(screen)

        # Dibujar Info Pokémon y Resultados
        info_start_y = target_input.rect.bottom + C.PADDING
        next_y = ui_draw.draw_pokemon_info(screen, font, info_start_y, selected_pokemon_name, selected_pokemon_types)
        next_y = ui_draw.draw_effectiveness_results(screen, font, next_y, calculated_multiplier, calculated_percentage, selected_pokemon_types, target_input.text)

        # Dibujar Mensajes de Estado
        ui_draw.draw_status_message(screen, font, status_message, is_status_error)

        # Dibujar Sugerencias (¡Superpuestas al final!)
        pokemon_suggestion_rects = []
        target_suggestion_rects = []
        if active_input_box == 'pokemon' and current_pokemon_suggestions:
             pokemon_suggestion_rects = suggestion_ui.draw_suggestions(screen, current_pokemon_suggestions, highlighted_pokemon_suggestion_idx, pokemon_input.rect, font)
        elif active_input_box == 'target' and current_target_suggestions:
             target_suggestion_rects = suggestion_ui.draw_suggestions(screen, current_target_suggestions, highlighted_target_suggestion_idx, target_input.rect, font)

        # Actualizar Pantalla
        pygame.display.flip()
        clock.tick(60) # Limitar FPS

    # --- Salida ---
    pygame.quit()
    sys.exit()

# --- Punto de Entrada ---
if __name__ == '__main__':
    run_app()