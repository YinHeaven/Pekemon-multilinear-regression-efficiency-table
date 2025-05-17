# File: Main.py
# Main.py

import pygame
import sys
import constants as C
import data
import pokeapi_client
import game_logic
from ui.input_box import InputBox
from ui import suggestions as suggestion_ui
from ui import drawing as ui_draw
from pygame.transform import scale
import win32gui
import win32con
from PIL import Image
import os
from pygame.transform import scale



def draw_custom_title_bar(screen, font):
    """Dibuja una barra de título"""
    # Fondo rojo
    pygame.draw.rect(screen, (200, 0, 0), (0, 0, C.SCREEN_WIDTH, 30))
    
    # Título blanco
    title_text = font.render("Pokédex", True, (255, 255, 255))
    screen.blit(title_text, (10, 5))
    
    # Botón de cerrar (rojo oscuro)
    close_btn = pygame.Rect(C.SCREEN_WIDTH - 30, 5, 20, 20)
    pygame.draw.rect(screen, (150, 0, 0), close_btn)
    pygame.draw.line(screen, (255, 255, 255), (close_btn.x + 5, close_btn.y + 5), 
                    (close_btn.x + 15, close_btn.y + 15), 2)
    pygame.draw.line(screen, (255, 255, 255), (close_btn.x + 15, close_btn.y + 5), 
                    (close_btn.x + 5, close_btn.y + 15), 2)
    
    return close_btn  # Retorna el rectángulo para detectar clics

def load_proper_icon():
    try:
        icon_path = os.path.join("assets", "pokedex_icon.png")
        icon = pygame.image.load(icon_path).convert_alpha()
        icon = scale(icon, (64, 64))  # Redimensiona a tamaño estándar
        pygame.display.set_icon(icon)
    except Exception as e:
        print(f"No se pudo cargar el icono: {e}")
        # Crea un icono por defecto como fallback
        default_icon = pygame.Surface((64, 64))
        default_icon.fill((200, 0, 0))  # Rojo Pokédex
        pygame.display.set_icon(default_icon)

def create_icon_file():
    try:
        img_path = os.path.join("assets", "pokedex_icon.png")
        ico_path = os.path.join("assets", "pokedex_icon.ico")
        
        # Convierte PNG a ICO con múltiples tamaños
        img = Image.open(img_path)
        img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (64,64)])
        
        return ico_path
    except Exception as e:
        print(f"No se pudo crear archivo .ico: {str(e)}")
        return None

ico_path = create_icon_file()
if ico_path:
    icon = pygame.image.load(ico_path)
    pygame.display.set_icon(icon)

def run_app():

    # --- Inicialización ---
    pygame.init()
    screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
    load_proper_icon()

    pygame.display.set_caption("Pokédex")  # Título en la barra del sistema (opcional)
    
    font = pygame.font.Font(None, C.FONT_SIZE)
    clock = pygame.time.Clock()

    ico_path = create_icon_file()  # Convierte PNG a ICO (si es necesario)
    if ico_path:
        try:
            icon = pygame.image.load(ico_path)
            pygame.display.set_icon(icon)
            print("¡Icono personalizado cargado!")
        except:
            print("Usando icono por defecto (falló la carga)")
    # Oculta la barra nativa (opcional, solo Windows)
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(pygame.display.get_wm_info()["Pokédex"], 6)  # SW_MINIMIZE -> SW_RESTORE
    except:
        pass
    
    # Variable para el botón de cerrar
    close_button = None
    
    try:
        font = pygame.font.Font("assets/Pokemon_Solid.ttf", C.FONT_SIZE)  # Ej: "pkmn_rby_font.ttf"
    except:
        font = pygame.font.Font(None, C.FONT_SIZE)  # Usa fuente por defecto si hay error
        print("¡Advertencia! No se encontró la fuente personalizada.")

# Carga el logo (opcional)
    try:
        logo = pygame.image.load("assets/pokedex_logo.png").convert_alpha()
        logo = pygame.transform.scale(logo, (120, 50))
    except:
        logo = None
        screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        pygame.display.set_caption("Buscador Pokémon y Efectividad de Tipo vRefactored")
        font = pygame.font.Font(None, C.FONT_SIZE)
        clock = pygame.time.Clock() # Para controlar FPS si es necesario

    # --- Activar repetición de teclas ---
    # delay: 350 ms antes de empezar a repetir
    # interval: 50 ms entre repeticiones
    pygame.key.set_repeat(350, 50)
    # -----------------------------------


    # --- Activar repetición de teclas ---
    # delay: 350 ms antes de empezar a repetir
    # interval: 50 ms entre repeticiones
    pygame.key.set_repeat(350, 50)
    # -----------------------------------


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
    input_width = 300 # Ancho de las cajas de entrada
    input_height = C.INPUT_BOX_HEIGHT
    input_y = C.PADDING * 2 + C.FONT_SIZE # Posición vertical común para ambos inputs
    spacing = C.PADDING * 2 # Espacio entre las cajas

    pokemon_input = InputBox(C.PADDING, input_y, input_width, input_height, font)
    pokemon_input.set_placeholder("Nombre o Tipo Pokémon")

    target_input = InputBox(pokemon_input.rect.right + spacing, input_y, input_width, input_height, font)
    target_input.set_placeholder("Oponente (Tipo o Nombre)")


    current_pokemon_suggestions = []
    highlighted_pokemon_suggestion_idx = -1
    pokemon_suggestion_rects = []

    current_target_suggestions = []
    highlighted_target_suggestion_idx = -1
    target_suggestion_rects = []

    selected_pokemon_name = ""
    selected_pokemon_types = []
    selected_target_name = ""
    selected_target_types = []
    calculated_multiplier = None
    calculated_percentage = None

    status_message = ""
    is_status_error = False

    # --- Lógica de Procesamiento Unificada ---

    def process_input_selection(input_text, role):
        """
        Procesa la entrada de texto o la selección de sugerencia para un rol dado.
        Determina si es un tipo o un nombre de Pokémon y actualiza el estado.
        """
        nonlocal selected_pokemon_name, selected_pokemon_types, selected_target_types, status_message, is_status_error # <-- Añadir selected_target_types
        nonlocal calculated_multiplier, calculated_percentage
        nonlocal current_pokemon_suggestions, highlighted_pokemon_suggestion_idx
        nonlocal current_target_suggestions, highlighted_target_suggestion_idx
        nonlocal active_input_box

        text_lower = input_text.lower()
        input_box_to_process = pokemon_input if role == 'pokemon' else target_input

        status_message = f"Procesando '{text_lower}' para {role}..."
        is_status_error = False
        pygame.display.flip() # Mostrar mensaje de procesamiento

        processed_types = None
        display_name = text_lower # Lo que se usará en el mensaje de éxito/error

        # Intentar como tipo primero
        if text_lower in data.VALID_TYPES:
            processed_types = [text_lower]
            display_name = text_lower.capitalize()
        else:
            # Si no es un tipo, intentar como nombre de Pokémon
            pokemon_types = pokeapi_client.get_pokemon_types(text_lower)
            if pokemon_types:
                processed_types = pokemon_types
                display_name = f"{text_lower.capitalize()} ({', '.join(t.capitalize() for t in pokemon_types)})"

        # --- Actualizar estado basado en el rol y los tipos encontrados ---
        if role == 'pokemon':
            # Para el atacante, aceptamos nombres de Pokémon O tipos
            if processed_types: # Si se encontró como tipo o como nombre de Pokémon
                if text_lower in all_pokemon_names: # Es un nombre de Pokémon válido
                    selected_pokemon_name = text_lower
                    selected_pokemon_types = processed_types # Estos son los tipos del Pokémon
                    input_box_to_process.text = text_lower # Actualizar caja con el nombre encontrado
                    input_box_to_process.update_text_surface()
                    status_message = f"Datos de {display_name} cargados."
                    is_status_error = False
                    # Reiniciar cálculo si cambia el atacante
                    calculated_multiplier = None
                    calculated_percentage = None
                    selected_target_types = [] # <-- Limpiar tipos del oponente si cambia el atacante

                    # Desactivar input y limpiar estado de caja activa
                    input_box_to_process.active = False
                    active_input_box = None

                elif text_lower in data.VALID_TYPES: # Es un tipo válido, pero no un nombre de Pokémon
                    selected_pokemon_name = text_lower.capitalize() # Guardar el nombre del tipo como "nombre" para mostrar
                    selected_pokemon_types = [text_lower] # El tipo es solo el tipo ingresado
                    input_box_to_process.text = text_lower # Actualizar caja con el nombre del tipo
                    input_box_to_process.update_text_surface()
                    status_message = f"Tipo atacante '{display_name}' seleccionado."
                    is_status_error = False
                    # Reiniciar cálculo si cambia el atacante (incluso si es solo un tipo)
                    calculated_multiplier = None
                    calculated_percentage = None
                    selected_target_types = [] # <-- Limpiar tipos del oponente si cambia el atacante

                    # Desactivar input y limpiar estado de caja activa
                    input_box_to_process.active = False
                    active_input_box = None

                else: # processed_types no es None, pero no es ni nombre ni tipo válido (caso de seguridad)
                    status_message = f"Entrada '{text_lower}' procesada pero no reconocida como Pokémon o Tipo válido."
                    is_status_error = True
                    selected_pokemon_name = ""
                    selected_pokemon_types = []
                    calculated_multiplier = None # <-- Resetear si la entrada del atacante es inválida
                    calculated_percentage = None # <-- Resetear si la entrada del atacante es inválida
                    selected_target_types = [] # <-- Limpiar tipos del oponente si la entrada del atacante es inválida
                    # Mantener input activo para permitir corregir

            else: # processed_types es None - no se encontró ni tipo válido ni nombre de Pokémon válido
                status_message = f"Entrada '{text_lower}' no reconocida como Tipo o Pokémon."
                is_status_error = True
                selected_pokemon_name = ""
                selected_pokemon_types = []
                calculated_multiplier = None # <-- Resetear si la entrada del atacante es inválida
                calculated_percentage = None # <-- Resetear si la entrada del atacante es inválida
                selected_target_types = [] # <-- Limpiar tipos del oponente si la entrada del atacante es inválida
                # Mantener input activo para permitir corregir


        elif role == 'target':
            if not selected_pokemon_types:
                status_message = "Selecciona un Pokémon atacante primero."
                is_status_error = True
                # No desactivar input
                # Limpiar sugerencias del target
                current_target_suggestions = []
                highlighted_target_suggestion_idx = -1
                selected_target_types = [] # <-- Asegurarse de limpiar si no hay atacante
                calculated_multiplier = None # <-- Resetear si no hay atacante
                calculated_percentage = None # <-- Resetear si no hay atacante
                return # Salir si no hay atacante seleccionado

            if processed_types: # Si se encontró como tipo o como nombre de Pokémon
              
                selected_target_types = processed_types # <-- Guardar los tipos del oponente
                input_box_to_process.text = text_lower # Actualizar input con texto procesado
                input_box_to_process.update_text_surface()
                multiplier = game_logic.calculate_effectiveness(selected_pokemon_types, selected_target_types) # <-- Usar selected_target_types
                calculated_multiplier = multiplier
                calculated_percentage = game_logic.map_multiplier_to_percentage(multiplier)
                status_message = f"Efectividad calculada contra {display_name}."
                is_status_error = False

                # Desactivar input y limpiar estado de caja activa
                input_box_to_process.active = False
                active_input_box = None

            else: # No encontrado como tipo ni como nombre de pokemon
                status_message = f"Entrada '{text_lower}' no reconocida como Tipo o Pokémon."
                is_status_error = True
                selected_target_types = [] # <-- Limpiar si no se encontró
                calculated_multiplier = None
                calculated_percentage = None
                # No desactivar input si no se encontró, para permitir corregir

        # Limpiar sugerencias después del procesamiento (éxito o error de no encontrado)
        # Solo limpiar si la caja fue desactivada, de lo contrario, las sugerencias se actualizarán en el siguiente frame
        if not input_box_to_process.active:
            if role == 'pokemon':
                current_pokemon_suggestions = []
                highlighted_pokemon_suggestion_idx = -1
            elif role == 'target':
                current_target_suggestions = []
                highlighted_target_suggestion_idx = -1


    # --- Fin de la Lógica de Procesamiento Unificada ---


    # --- Bucle Principal ---
    running = True
    while running:
        #dibujado
        screen.fill(C.BG_COLOR)
    
    # Dibuja la barra personalizada (¡primero para que esté encima!)
        close_button = draw_custom_title_bar(screen, font)
        # --- Manejo de Eventos ---
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True
                
                if close_button and close_button.collidepoint(event.pos):
                    running = False
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

            # --- Lógica de Teclado ---
            if event.type == pygame.KEYDOWN:
                # --- Lógica para cambiar de input con TAB ---
                if event.key == pygame.K_TAB:
                    if active_input_box == 'pokemon':
                        pokemon_input.active = False
                        target_input.active = True
                        active_input_box = 'target'
                        # Limpiar sugerencias de ambas cajas al cambiar con TAB
                        current_pokemon_suggestions = []
                        highlighted_pokemon_suggestion_idx = -1
                        current_target_suggestions = [] # Limpiar también las del target por si acaso
                        highlighted_target_suggestion_idx = -1
                    elif active_input_box == 'target':
                        target_input.active = False
                        pokemon_input.active = True
                        active_input_box = 'pokemon'
                        # Limpiar sugerencias de ambas cajas al cambiar con TAB
                        current_pokemon_suggestions = [] # Limpiar también las del pokemon por si acaso
                        highlighted_pokemon_suggestion_idx = -1
                        current_target_suggestions = []
                        highlighted_target_suggestion_idx = -1
                    else: # Si ninguna está activa, activar la primera (pokemon)
                        pokemon_input.active = True
                        active_input_box = 'pokemon'
                        # Limpiar sugerencias por si acaso
                        current_pokemon_suggestions = []
                        highlighted_pokemon_suggestion_idx = -1
                        current_target_suggestions = []
                        highlighted_target_suggestion_idx = -1

                    # Consumir el evento TAB para que no sea procesado por la lógica de sugerencias
                    continue # Salta al siguiente evento

                # --- Lógica de navegación y selección de Sugerencias (solo UP, DOWN, RETURN) ---
                # Esta lógica se ejecuta SOLO si la tecla presionada NO fue TAB.
                current_suggestions = []
                highlighted_idx = -1
                suggestions_len = 0
                input_box_to_process = None # Necesitamos saber qué input procesar si se selecciona con Enter

                if active_input_box == 'pokemon':
                    current_suggestions = current_pokemon_suggestions
                    highlighted_idx = highlighted_pokemon_suggestion_idx
                    suggestions_len = len(current_suggestions)
                    input_box_to_process = pokemon_input
                elif active_input_box == 'target':
                    current_suggestions = current_target_suggestions
                    highlighted_idx = highlighted_target_suggestion_idx
                    suggestions_len = len(current_suggestions)
                    input_box_to_process = target_input


                if suggestions_len > 0:
                    if event.key == pygame.K_DOWN:
                        highlighted_idx = (highlighted_idx + 1) % suggestions_len
                    elif event.key == pygame.K_UP:
                        highlighted_idx = (highlighted_idx - 1 + suggestions_len) % suggestions_len
                    # Solo K_RETURN selecciona sugerencia
                    elif event.key == pygame.K_RETURN:
                        if highlighted_idx != -1 and active_input_box: # Asegurarse de que haya una sugerencia resaltada y una caja activa
                            selected_suggestion = current_suggestions[highlighted_idx]
                            # --- Lógica de Selección (Enter en sugerencia) ---
                            process_input_selection(selected_suggestion, active_input_box)
                            # process_input_selection handles clearing suggestions and deactivating input/active_input_box

                # Actualizar índice resaltado en el estado global (solo si no se seleccionó nada con Enter)
                # Si se seleccionó, highlighted_idx ya se reseteó a -1 inside process_input_selection.
                if active_input_box == 'pokemon':
                    highlighted_pokemon_suggestion_idx = highlighted_idx
                elif active_input_box == 'target':
                    highlighted_target_suggestion_idx = highlighted_idx

                # --- Lógica de Selección con Enter directamente en Input (si no hay sugerencias) ---
                # Esta parte se mantiene igual, ya que maneja Enter cuando NO hay sugerencias.
                # La lógica de arriba maneja Enter cuando SÍ hay sugerencias.
                if event.key == pygame.K_RETURN:
                    if active_input_box and \
                        ((active_input_box == 'pokemon' and not current_pokemon_suggestions) or \
                        (active_input_box == 'target' and not current_target_suggestions)):

                        input_box_to_process = pokemon_input if active_input_box == 'pokemon' else target_input
                        if input_box_to_process.text:
                            process_input_selection(input_box_to_process.text, active_input_box)
                        else:
                            # Mensaje de error si el input está vacío al presionar Enter sin sugerencias
                            if active_input_box == 'pokemon':
                                status_message = "Introduce un nombre o tipo de Pokémon."
                            elif active_input_box == 'target':
                                status_message = "Introduce un tipo o nombre de oponente."
                            is_status_error = True

            # --- Fin del Manejo de Eventos de Teclado ---


            # --- Lógica de Selección por Clic del Ratón en Sugerencias ---
            if mouse_clicked:
                if active_input_box == 'pokemon' and current_pokemon_suggestions:
                    for i, rect in enumerate(pokemon_suggestion_rects):
                        if rect.collidepoint(pygame.mouse.get_pos()):
                            process_input_selection(current_pokemon_suggestions[i], 'pokemon')
                            break # Procesar solo un clic
                elif active_input_box == 'target' and current_target_suggestions:
                    for i, rect in enumerate(target_suggestion_rects):
                        if rect.collidepoint(pygame.mouse.get_pos()):
                            process_input_selection(current_target_suggestions[i], 'target')
                            break # Procesar solo un clic

        # --- Actualización de Sugerencias (basado en la caja activa) ---
        # Usamos la misma función de sugerencias para ambos inputs
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
            # Usar la misma función de sugerencias que para el pokemon input
            current_target_suggestions, msg, err = suggestion_ui.update_pokemon_suggestions(
                target_input.text, all_pokemon_names, data.VALID_TYPES
            )
            # Actualizar mensajes solo si se generó uno nuevo al buscar sugerencias
            if msg:
                status_message = msg
                is_status_error = err

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


        # --- Dibujado ---
        # Dibuja el marco rojo exterior
        pygame.draw.rect(screen, (200, 0, 0), (0, 0, C.SCREEN_WIDTH, C.SCREEN_HEIGHT), 10)
        # Dibuja el logo (si existe)
        if logo:
            screen.blit(logo, (C.SCREEN_WIDTH - 130, 15))

        screen.fill(C.BG_COLOR)

        # Dibujar Etiquetas
        ui_draw.draw_labels(screen, font, pokemon_input.rect, target_input.rect)

        # Dibujar Cajas de Entrada
        pokemon_input.draw(screen)
        target_input.draw(screen)

        # Dibujar Info Pokémon y Resultados
        info_start_y = target_input.rect.bottom + C.PADDING
        next_y = ui_draw.draw_pokemon_info(screen, font, info_start_y, selected_pokemon_name, selected_pokemon_types)

        # --- Preparar texto de tipos del oponente para la visualización ---
        opponent_display_text = target_input.text # Texto por defecto si no hay tipos seleccionados
        if selected_target_types:
            opponent_display_text = f"({', '.join(t.capitalize() for t in selected_target_types)})"

        # -----------------------------------------------------------------

        # Pasar la lista de tipos del oponente directamente a la función de dibujo
        next_y = ui_draw.draw_effectiveness_results(screen, font, next_y, calculated_multiplier, calculated_percentage, selected_pokemon_types, selected_target_types)

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
