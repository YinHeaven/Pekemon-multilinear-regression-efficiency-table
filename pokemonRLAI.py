import pygame
import requests
import sys
import json # Para depuración si es necesario

# --- Constantes ---
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/"
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (230, 230, 230) # Gris claro
TEXT_COLOR = (50, 50, 50)
INPUT_BG_COLOR = (255, 255, 255) # Blanco
INPUT_BORDER_COLOR = (100, 100, 100) # Gris oscuro
SUGGESTION_BG_COLOR = (240, 240, 240)
SUGGESTION_HOVER_COLOR = (200, 200, 255) # Azul claro para mouse hover
SUGGESTION_HIGHLIGHT_COLOR = (150, 150, 255) # Azul más oscuro para selección con teclado
ERROR_COLOR = (255, 0, 0) # Rojo
SUCCESS_COLOR = (0, 128, 0) # Verde
FONT_SIZE = 24
PADDING = 10
INPUT_BOX_HEIGHT = 40
SUGGESTION_HEIGHT = 30
MAX_SUGGESTIONS = 15 # Aumentar el límite para mostrar más Pokémon por tipo

# --- Tabla de Efectividad de Tipos (Hardcodeada) ---
# Esto representa el multiplicador de daño del tipo ATACANTE contra el tipo DEFENSOR.
# 0   -> Sin efecto
# 0.5 -> Poco efectivo
# 1   -> Efectividad normal
# 2   -> Súper efectivo
# Una tabla completa es muy larga. Este es un subconjunto relevante.
# Puedes encontrar tablas completas en línea, por ejemplo, https://pokemondb.net/type
TYPE_EFFECTIVENESS = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fighting": {"normal": 2, "flying": 0.5, "poison": 0.5, "rock": 2, "bug": 0.5, "ghost": 0, "steel": 2, "fire": 1, "water": 1, "grass": 1, "electric": 1, "psychic": 0.5, "ice": 2, "dragon": 1, "dark": 2, "fairy": 0.5},
    "flying": {"fighting": 2, "rock": 0.5, "bug": 2, "steel": 0.5, "grass": 2, "electric": 0.5},
    "poison": {"poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "grass": 2, "fairy": 2},
    "ground": {"flying": 0, "poison": 2, "rock": 2, "bug": 0.5, "steel": 2, "fire": 2, "grass": 0.5, "electric": 2},
    "rock": {"fighting": 0.5, "flying": 2, "ground": 0.5, "bug": 2, "steel": 0.5, "fire": 2, "ice": 2},
    "bug": {"flying": 0.5, "poison": 0.5, "fighting": 0.5, "ghost": 0.5, "steel": 0.5, "fire": 0.5, "grass": 2, "psychic": 2, "dark": 2, "fairy": 0.5},
    "ghost": {"normal": 0, "fighting": 0, "poison": 1, "bug": 1, "ghost": 2, "steel": 1, "fire": 1, "water": 1, "grass": 1, "electric": 1, "psychic": 2, "ice": 1, "dragon": 1, "dark": 0.5, "fairy": 1},
    "steel": {"rock": 2, "steel": 0.5, "fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "fairy": 2},
    "fire": {"rock": 0.5, "bug": 2, "steel": 2, "fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "dragon": 0.5},
    "water": {"ground": 2, "rock": 2, "fire": 2, "water": 0.5, "grass": 0.5, "dragon": 0.5},
    "grass": {"flying": 0.5, "poison": 0.5, "ground": 2, "bug": 0.5, "steel": 0.5, "fire": 0.5, "water": 2, "grass": 0.5, "electric": 1, "ice": 1, "dragon": 0.5},
    "electric": {"flying": 2, "ground": 0, "steel": 1, "electric": 0.5, "grass": 0.5, "ice": 1, "dragon": 0.5, "water": 2},
    "psychic": {"fighting": 2, "poison": 2, "steel": 0.5, "psychic": 0.5, "dark": 0, "fairy": 1},
    "ice": {"flying": 2, "ground": 2, "steel": 0.5, "fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "dragon": 2},
    "dragon": {"steel": 0.5, "dragon": 2, "fairy": 0},
    "dark": {"fighting": 0.5, "ghost": 2, "psychic": 2, "dark": 0.5, "fairy": 0.5},
    "fairy": {"fighting": 2, "poison": 0.5, "steel": 0.5, "fire": 0.5, "dragon": 2, "dark": 2},
    # Añadir entradas para todos los tipos para una tabla completa
}
# Lista de nombres de tipos válidos para la búsqueda
VALID_TYPES = list(TYPE_EFFECTIVENESS.keys())


# --- Función para obtener la lista completa de nombres de Pokémon ---
def get_all_pokemon_names():
    """Obtiene una lista de todos los nombres de Pokémon de la PokeAPI."""
    print("Obteniendo lista completa de Pokémon...")
    url = f"{POKEAPI_BASE_URL}pokemon?limit=10000" # Usar un límite alto para obtener la mayoría de los Pokémon
    try:
        response = requests.get(url)
        response.raise_for_status() # Lanza una excepción para códigos de error HTTP
        data = response.json()
        print("Lista de Pokémon obtenida.")
        return [pokemon['name'] for pokemon in data.get('results', [])]
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la lista de Pokémon: {e}")
        return []

# --- Función para obtener los tipos de un Pokémon ---
def get_pokemon_types(pokemon_name):
    """Obtiene los tipos de un Pokémon específico de la PokeAPI."""
    print(f"Obteniendo tipos para {pokemon_name}...")
    url = f"{POKEAPI_BASE_URL}pokemon/{pokemon_name.lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Los tipos vienen en una lista con slot y type.name
        types = [t['type']['name'] for t in data.get('types', [])]
        print(f"Tipos para {pokemon_name}: {types}")
        return types
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de {pokemon_name}: {e}")
        return None

# --- Función para obtener Pokémon por tipo ---
def get_pokemon_by_type(type_name):
    """Obtiene una lista de nombres de Pokémon de un tipo específico de la PokeAPI."""
    print(f"Obteniendo Pokémon de tipo {type_name}...")
    url = f"{POKEAPI_BASE_URL}type/{type_name.lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # La lista de Pokémon está en data['pokemon'], cada entrada tiene 'pokemon' -> {'name': '...', 'url': '...'}
        pokemon_list = [entry['pokemon']['name'] for entry in data.get('pokemon', [])]
        print(f"Obtenidos {len(pokemon_list)} Pokémon de tipo {type_name}.")
        return pokemon_list
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener Pokémon de tipo {type_name}: {e}")
        return []


# --- Función para calcular la efectividad ---
def calculate_effectiveness(attacker_types, defender_types):
    """
    Calcula el multiplicador de efectividad de un ataque de los tipos del atacante
    contra los tipos del defensor usando las reglas del juego.
    """
    if not attacker_types or not defender_types:
        return 1.0 # Efectividad normal si faltan tipos

    # En el juego real, la efectividad de un ataque se determina por el
    # tipo del ataque contra el(los) tipo(s) del defensor. Si un Pokémon tiene múltiples
    # tipos, los multiplicadores se multiplican.
    # Para simplificar en este ejemplo, calcularemos la efectividad
    # del *primer* tipo del Pokémon atacante contra el(los) tipo(s) del defensor.
    # Una implementación completa calcularía la efectividad para cada uno de los tipos del atacante.

    attacker_primary_type = attacker_types[0]
    calculated_multiplier = 1.0

    for defender_type in defender_types:
         # Obtener el multiplicador para attacker_primary_type vs defender_type
         # Si attacker_primary_type no está en nuestra tabla, asumimos 1x contra este defender_type
         # Si defender_type no está en la sub-tabla de attacker_primary_type, asumimos 1x
         multiplier = TYPE_EFFECTIVENESS.get(attacker_primary_type, {}).get(defender_type, 1.0)
         calculated_multiplier *= multiplier

    return calculated_multiplier

# --- Mapear multiplicador a 0-100% (NO ES UNA REGRESIÓN) ---
def map_multiplier_to_percentage(multiplier):
    """
    Mapea el multiplicador de efectividad a un rango de 0-100%.
    Este es un mapeo arbitrario para visualización y NO proviene de
    un modelo de regresión ni representa una probabilidad verdadera.
    """
    if multiplier == 0:
        return 0
    elif multiplier == 0.25: # Raro, pero posible con resistencias 4x
         return 5
    elif multiplier == 0.5:
        return 25
    elif multiplier == 1:
        return 50 # Efectividad normal mapeada a 50%
    elif multiplier == 2:
        return 75 # Súper efectivo mapeado a 75%
    elif multiplier == 4: # Doble súper efectivo
        return 100
    else: # Para otros valores inesperados
        return min(100, max(0, int(multiplier * 25))) # Intento simple de mapeo lineal, limitado

# --- Clase para la Caja de Entrada de Texto ---
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = INPUT_BORDER_COLOR
        self.text = text
        self.txt_surface = FONT.render(text, True, TEXT_COLOR)
        self.active = False
        self.placeholder = "" # Texto de marcador de posición
        self.placeholder_surface = None

    def set_placeholder(self, text):
        self.placeholder = text
        self.placeholder_surface = FONT.render(text, True, (150, 150, 150)) # Color gris para el marcador de posición

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Si el usuario hizo clic en la caja de entrada
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            # Cambiar el color de la caja de entrada
            self.color = INPUT_BORDER_COLOR if not self.active else (0, 128, 255) # Azul cuando está activo
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # Manejar la selección con Enter (lo hará el bucle principal)
                    pass # La selección con Enter para sugerencias se maneja en el bucle principal
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode # Usar event.unicode para manejar mayúsculas, minúsculas, etc.
                # Re-renderizar el texto
                self.txt_surface = FONT.render(self.text, True, TEXT_COLOR)
                # Asegurarse de que el texto no se salga de la caja (recorte simple o desplazamiento si fuera necesario)
                # Aquí, solo renderizamos lo que quepa. Implementar desplazamiento es más complejo.

    def update(self):
         # Ajustar el ancho si el texto se alarga (opcional)
         # width = max(self.rect.w, self.txt_surface.get_width()+10)
         # self.rect.w = width
         pass # No se necesita actualización compleja en este ejemplo

    def draw(self, screen):
        # Dibujar la caja
        pygame.draw.rect(screen, self.color, self.rect, 2) # Borde de 2px
        pygame.draw.rect(screen, INPUT_BG_COLOR, (self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, self.rect.height - 4)) # Fondo blanco

        # Dibujar el texto o el marcador de posición
        if self.text:
            # Recortar el texto si es demasiado largo para la caja
            rendered_text = self.text
            text_width, text_height = FONT.size(rendered_text)
            while text_width > self.rect.width - PADDING*2 and len(rendered_text) > 0:
                 rendered_text = rendered_text[:-1]
                 text_width, text_height = FONT.size(rendered_text)

            screen.blit(FONT.render(rendered_text, True, TEXT_COLOR), (self.rect.x + PADDING, self.rect.y + (self.rect.height - text_height) // 2))
        elif self.placeholder_surface and not self.active:
             screen.blit(self.placeholder_surface, (self.rect.x + PADDING, self.rect.y + (self.rect.height - self.placeholder_surface.get_height()) // 2))

# --- Función para actualizar las sugerencias de Pokémon (para el primer InputBox) ---
def update_pokemon_suggestions(search_text, all_pokemon_names, valid_types):
    """
    Genera y devuelve una lista de sugerencias de Pokémon basada en el texto de búsqueda.
    Busca por prefijo de nombre y por tipo si el texto coincide con un tipo válido.
    """
    search_text_lower = search_text.lower()
    name_suggestions = []
    type_suggestions = []
    current_error_message = ""
    current_success_message = ""

    # 1. Buscar por nombre (prefijo)
    if search_text_lower:
        name_suggestions = [name for name in all_pokemon_names if name.startswith(search_text_lower)]

    # 2. Buscar por tipo si el texto coincide exactamente con un tipo conocido
    if search_text_lower in valid_types:
         current_success_message = f"Buscando Pokémon de tipo {search_text_lower}..."
         # Nota: En una aplicación real, querrías manejar esto de forma asíncrona
         # para no bloquear la UI mientras se espera la respuesta de la API.
         # Aquí, bloquearemos brevemente para simplificar.
         type_pokemon_names = get_pokemon_by_type(search_text_lower)
         if type_pokemon_names:
             type_suggestions = type_pokemon_names
             current_success_message = f"Sugerencias por tipo {search_text_lower} cargadas."
         else:
             current_error_message = f"No se encontraron Pokémon de tipo {search_text_lower}."
             current_success_message = "" # Limpiar mensaje de éxito si hubo error al buscar por tipo


    # 3. Combinar y limpiar duplicados
    combined_suggestions = list(set(name_suggestions + type_suggestions))

    # 4. Ordenar alfabéticamente
    combined_suggestions.sort()

    # 5. Limitar el número de sugerencias
    suggestions = combined_suggestions[:MAX_SUGGESTIONS]

    return suggestions, current_error_message, current_success_message

# --- Función para actualizar las sugerencias de Tipos (para el segundo InputBox) ---
def update_type_suggestions(search_text, valid_types):
    """
    Genera y devuelve una lista de sugerencias de tipos válidos basada en el texto de búsqueda.
    """
    search_text_lower = search_text.lower()
    if search_text_lower:
        # Buscar tipos que empiecen con el texto de búsqueda
        suggestions = [type_name for type_name in valid_types if type_name.startswith(search_text_lower)]
        suggestions.sort() # Ordenar alfabéticamente
        return suggestions[:MAX_SUGGESTIONS] # Limitar el número de sugerencias
    else:
        return [] # No mostrar sugerencias si la caja está vacía


# --- Inicialización de Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Buscador Pokémon y Efectividad de Tipo")
FONT = pygame.font.Font(None, FONT_SIZE) # Usar fuente predeterminada

# --- Cargar datos ---
print("Cargando lista de Pokémon... esto puede tardar un momento.")
all_pokemon_names = get_all_pokemon_names()
if not all_pokemon_names:
    print("No se pudo cargar la lista de Pokémon. Saliendo.")
    pygame.quit()
    sys.exit()
print(f"Cargados {len(all_pokemon_names)} nombres de Pokémon.")

# --- Configuración de la UI ---
pokemon_input_box = InputBox(PADDING, PADDING + FONT_SIZE + 5, 300, INPUT_BOX_HEIGHT) # Ajustada posición Y
pokemon_input_box.set_placeholder("Nombre o Tipo de Pokémon") # Actualizado placeholder

target_type_input_box = InputBox(PADDING, PADDING + FONT_SIZE + 5 + INPUT_BOX_HEIGHT + PADDING + FONT_SIZE + 5, 200, INPUT_BOX_HEIGHT) # Ajustada posición Y
target_type_input_box.set_placeholder("Tipo o Nombre de Oponente") # Actualizado placeholder

# Variables para sugerencias del primer InputBox
pokemon_suggestions = []
highlighted_pokemon_suggestion_index = -1

# Variables para sugerencias del segundo InputBox
target_type_suggestions = []
highlighted_target_type_suggestion_index = -1

selected_pokemon_name = ""
selected_pokemon_types = []
calculated_effectiveness_multiplier = None
calculated_effectiveness_percentage = None
error_message = ""
success_message = ""

# --- Bucle Principal del Juego ---
running = True
while running:
    # --- Manejo de Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Manejar eventos de las cajas de entrada (para escribir texto)
        # handle_event de InputBox actualiza el texto y el estado activo
        pokemon_input_box.handle_event(event)
        target_type_input_box.handle_event(event)

        # --- Manejar eventos de teclado adicionales para la navegación y selección de sugerencias ---
        if event.type == pygame.KEYDOWN:
            # Si la caja de Pokémon está activa y hay sugerencias
            if pokemon_input_box.active and pokemon_suggestions:
                if event.key == pygame.K_DOWN:
                    highlighted_pokemon_suggestion_index = (highlighted_pokemon_suggestion_index + 1) % len(pokemon_suggestions)
                elif event.key == pygame.K_UP:
                    highlighted_pokemon_suggestion_index = (highlighted_pokemon_suggestion_index - 1 + len(pokemon_suggestions)) % len(pokemon_suggestions) # Asegurar índice positivo
                elif event.key == pygame.K_RETURN:
                    # Si hay una sugerencia resaltada, seleccionarla
                    if highlighted_pokemon_suggestion_index != -1:
                        name_to_select = pokemon_suggestions[highlighted_pokemon_suggestion_index].lower() # Usar minúsculas para la búsqueda API
                        # --- Lógica de selección de Pokémon (duplicada del clic del ratón) ---
                        error_message = "" # Limpiar errores anteriores
                        success_message = "Buscando Pokémon..."
                        pygame.display.flip() # Actualizar pantalla para mostrar el mensaje "Buscando Pokémon..."

                        # Obtener datos del Pokémon seleccionado
                        pokemon_data = get_pokemon_types(name_to_select)
                        if pokemon_data is not None:
                            selected_pokemon_name = name_to_select.capitalize()
                            selected_pokemon_types = pokemon_data
                            pokemon_input_box.text = name_to_select # Poner el nombre completo en la caja
                            pokemon_suggestions = [] # Limpiar sugerencias después de la selección
                            highlighted_pokemon_suggestion_index = -1 # Resetear índice resaltado
                            success_message = f"Datos de {selected_pokemon_name} cargados."
                            error_message = ""
                            calculated_effectiveness_multiplier = None # Reiniciar cálculo de efectividad
                            calculated_effectiveness_percentage = None

                        else:
                            selected_pokemon_name = ""
                            selected_pokemon_types = []
                            error_message = f"Pokémon '{name_to_select}' no encontrado."
                            success_message = ""
                        # --- Fin Lógica de selección de Pokémon ---
                    else:
                        # Si no hay sugerencia resaltada, pero se presiona Enter, intentar buscar el texto actual
                         name_to_select = pokemon_input_box.text.lower() # Usar minúsculas para la búsqueda API
                         if name_to_select:
                            error_message = "" # Limpiar errores anteriores
                            success_message = "Buscando Pokémon..."
                            pygame.display.flip() # Actualizar para mostrar el mensaje de buscando

                            pokemon_data = get_pokemon_types(name_to_select)
                            if pokemon_data is not None:
                                selected_pokemon_name = name_to_select.capitalize()
                                selected_pokemon_types = pokemon_data
                                pokemon_input_box.text = name_to_select # Poner el nombre completo en la caja
                                pokemon_suggestions = [] # Limpiar sugerencias
                                highlighted_pokemon_suggestion_index = -1 # Resetear índice resaltado
                                success_message = f"Datos de {selected_pokemon_name} cargados."
                                error_message = ""
                                calculated_effectiveness_multiplier = None # Reiniciar cálculo de efectividad
                                calculated_effectiveness_percentage = None
                            else:
                                selected_pokemon_name = ""
                                selected_pokemon_types = []
                                error_message = f"Pokémon '{name_to_select}' no encontrado."
                                success_message = ""
                         else:
                            error_message = "Introduce un nombre o tipo de Pokémon."
                            success_message = ""

            # Si la caja de tipo oponente está activa y hay sugerencias de tipo
            elif target_type_input_box.active and target_type_suggestions:
                 if event.key == pygame.K_DOWN:
                    highlighted_target_type_suggestion_index = (highlighted_target_type_suggestion_index + 1) % len(target_type_suggestions)
                 elif event.key == pygame.K_UP:
                    highlighted_target_type_suggestion_index = (highlighted_target_type_suggestion_index - 1 + len(target_type_suggestions)) % len(target_type_suggestions) # Asegurar índice positivo
                 elif event.key == pygame.K_RETURN:
                     # Si hay una sugerencia de tipo resaltada, seleccionarla y usarla para el cálculo
                     if highlighted_target_type_suggestion_index != -1:
                         opponent_input_text = target_type_suggestions[highlighted_target_type_suggestion_index].lower()
                         target_type_input_box.text = opponent_input_text # Poner el tipo en la caja
                         target_type_suggestions = [] # Limpiar sugerencias
                         highlighted_target_type_suggestion_index = -1 # Resetear índice

                         # --- Lógica de cálculo de efectividad (modificada) ---
                         if selected_pokemon_types:
                             error_message = ""
                             # Usar el tipo seleccionado directamente para el cálculo
                             opponent_type_raw = opponent_input_text
                             if opponent_type_raw in TYPE_EFFECTIVENESS:
                                error_message = ""
                                attacker_primary_type = selected_pokemon_types[0]
                                calculated_multiplier = calculate_effectiveness([attacker_primary_type], [opponent_type_raw])
                                calculated_effectiveness_multiplier = calculated_multiplier
                                calculated_effectiveness_percentage = map_multiplier_to_percentage(calculated_multiplier)
                                success_message = f"Efectividad calculada contra tipo {opponent_type_raw.capitalize()}."
                             else:
                                # Esto no debería ocurrir si la sugerencia es de VALID_TYPES, pero como fallback
                                error_message = f"Tipo '{opponent_type_raw}' no reconocido."
                                calculated_effectiveness_multiplier = None
                                calculated_effectiveness_percentage = None
                                success_message = ""
                         elif not selected_pokemon_types:
                              error_message = "Selecciona un Pokémon atacante primero."
                              success_message = ""
                         # --- Fin Lógica de cálculo de efectividad ---
                     else:
                         # Si no hay sugerencia de tipo resaltada, pero se presiona Enter,
                         # intentar usar el texto actual como tipo o nombre de Pokémon
                         opponent_input_text = target_type_input_box.text.lower()
                         if opponent_input_text:
                              # --- Lógica de cálculo de efectividad (modificada) ---
                              if selected_pokemon_types:
                                   error_message = ""
                                   success_message = "Procesando entrada del oponente..."
                                   pygame.display.flip() # Actualizar para mostrar mensaje

                                   # Intentar como tipo primero
                                   if opponent_input_text in TYPE_EFFECTIVENESS:
                                        opponent_type_raw = opponent_input_text
                                        attacker_primary_type = selected_pokemon_types[0]
                                        calculated_multiplier = calculate_effectiveness([attacker_primary_type], [opponent_type_raw])
                                        calculated_effectiveness_multiplier = calculated_multiplier
                                        calculated_effectiveness_percentage = map_multiplier_to_percentage(calculated_multiplier)
                                        success_message = f"Efectividad calculada contra tipo {opponent_type_raw.capitalize()}."
                                        error_message = "" # Limpiar error si tuvo éxito

                                   # Si no es un tipo válido, intentar como nombre de Pokémon
                                   else:
                                        pokemon_data = get_pokemon_types(opponent_input_text)
                                        if pokemon_data is not None:
                                             opponent_types = pokemon_data
                                             # Usar el primer tipo del Pokémon oponente para el cálculo
                                             if opponent_types:
                                                opponent_type_raw = opponent_types[0] # Usar el primer tipo del oponente
                                                attacker_primary_type = selected_pokemon_types[0]
                                                calculated_multiplier = calculate_effectiveness([attacker_primary_type], [opponent_type_raw])
                                                calculated_effectiveness_multiplier = calculated_multiplier
                                                calculated_effectiveness_percentage = map_multiplier_to_percentage(calculated_multiplier)
                                                success_message = f"Efectividad calculada contra {opponent_input_text.capitalize()} ({opponent_type_raw.capitalize()})."
                                                error_message = "" # Limpiar error si tuvo éxito
                                             else: # Pokémon encontrado pero sin tipos (no debería pasar en PokeAPI, pero como seguridad)
                                                error_message = f"Pokémon '{opponent_input_text.capitalize()}' encontrado pero sin tipos."
                                                success_message = ""
                                                calculated_effectiveness_multiplier = None
                                                calculated_effectiveness_percentage = None
                                        else:
                                             # No es un tipo ni un nombre de Pokémon válido
                                             error_message = f"Entrada '{opponent_input_text}' no reconocida como tipo o Pokémon."
                                             success_message = ""
                                             calculated_effectiveness_multiplier = None
                                             calculated_effectiveness_percentage = None

                              elif not selected_pokemon_types:
                                   error_message = "Selecciona un Pokémon atacante primero."
                                   success_message = ""
                              # --- Fin Lógica de cálculo de efectividad (modificada) ---
                         else:
                              error_message = "Introduce un tipo o nombre de Pokémon oponente."
                              success_message = ""


        # --- Manejar clics del ratón ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Clic en sugerencias de Pokémon
            if pokemon_input_box.active and pokemon_suggestions:
                suggestion_y = pokemon_input_box.rect.y + INPUT_BOX_HEIGHT + PADDING
                suggestion_rects = [pygame.Rect(pokemon_input_box.rect.x, suggestion_y + i * SUGGESTION_HEIGHT, pokemon_input_box.rect.width, SUGGESTION_HEIGHT) for i in range(len(pokemon_suggestions))]
                for i, rect in enumerate(suggestion_rects):
                    if rect.collidepoint(event.pos):
                        # --- Seleccionar esta sugerencia de Pokémon ---
                        name_to_select = pokemon_suggestions[i].lower() # Usar minúsculas para la búsqueda API
                        error_message = "" # Limpiar errores anteriores
                        success_message = "Buscando Pokémon..."
                        pygame.display.flip() # Actualizar pantalla para mostrar el mensaje "Buscando Pokémon..."

                        # Obtener datos del Pokémon seleccionado
                        pokemon_data = get_pokemon_types(name_to_select)
                        if pokemon_data is not None:
                            selected_pokemon_name = name_to_select.capitalize()
                            selected_pokemon_types = pokemon_data
                            pokemon_input_box.text = name_to_select # Poner el nombre completo en la caja
                            pokemon_suggestions = [] # Limpiar sugerencias después de la selección
                            highlighted_pokemon_suggestion_index = -1 # Resetear índice resaltado
                            success_message = f"Datos de {selected_pokemon_name} cargados."
                            error_message = ""
                            calculated_effectiveness_multiplier = None # Reiniciar cálculo de efectividad
                            calculated_effectiveness_percentage = None

                        else:
                            selected_pokemon_name = ""
                            selected_pokemon_types = []
                            error_message = f"Pokémon '{name_to_select}' no encontrado."
                            success_message = ""
                        break # Salir del bucle después de seleccionar una sugerencia
            # Clic en sugerencias de Tipo Oponente
            elif target_type_input_box.active and target_type_suggestions:
                 suggestion_y = target_type_input_box.rect.y + INPUT_BOX_HEIGHT + PADDING
                 suggestion_rects = [pygame.Rect(target_type_input_box.rect.x, suggestion_y + i * SUGGESTION_HEIGHT, target_type_input_box.rect.width, SUGGESTION_HEIGHT) for i in range(len(target_type_suggestions))]
                 for i, rect in enumerate(suggestion_rects):
                     if rect.collidepoint(event.pos):
                         # --- Seleccionar esta sugerencia de Tipo ---
                         opponent_input_text = target_type_suggestions[i].lower()
                         target_type_input_box.text = opponent_input_text # Poner el tipo en la caja
                         target_type_suggestions = [] # Limpiar sugerencias
                         highlighted_target_type_suggestion_index = -1 # Resetear índice

                         # --- Lógica de cálculo de efectividad (duplicada del Enter) ---
                         if selected_pokemon_types:
                             error_message = ""
                             # Usar el tipo seleccionado directamente para el cálculo
                             opponent_type_raw = opponent_input_text
                             if opponent_type_raw in TYPE_EFFECTIVENESS:
                                error_message = ""
                                attacker_primary_type = selected_pokemon_types[0]
                                calculated_multiplier = calculate_effectiveness([attacker_primary_type], [opponent_type_raw])
                                calculated_effectiveness_multiplier = calculated_multiplier
                                calculated_effectiveness_percentage = map_multiplier_to_percentage(calculated_multiplier)
                                success_message = f"Efectividad calculada contra tipo {opponent_type_raw.capitalize()}."
                             else:
                                # Esto no debería ocurrir si la sugerencia es de VALID_TYPES, pero como fallback
                                error_message = f"Tipo '{opponent_type_raw}' no reconocido."
                                calculated_effectiveness_multiplier = None
                                calculated_effectiveness_percentage = None
                                success_message = ""
                         elif not selected_pokemon_types:
                              error_message = "Selecciona un Pokémon atacante primero."
                              success_message = ""
                         # --- Fin Lógica de cálculo de efectividad ---
                         break # Salir del bucle después de seleccionar una sugerencia

            # Si se hace clic fuera de una caja de entrada activa con sugerencias, desactiva el resaltado y limpia sugerencias
            elif not pokemon_input_box.rect.collidepoint(event.pos) and pokemon_input_box.active:
                 pokemon_suggestions = []
                 highlighted_pokemon_suggestion_index = -1
            elif not target_type_input_box.rect.collidepoint(event.pos) and target_type_input_box.active:
                 target_type_suggestions = []
                 highlighted_target_type_suggestion_index = -1


    # --- Lógica de Autocompletado ---
    # Actualizar sugerencias solo si la caja de Pokémon está activa
    if pokemon_input_box.active:
        # Llamar a la función para obtener las sugerencias de Pokémon
        new_pokemon_suggestions, current_error, current_success = update_pokemon_suggestions(
            pokemon_input_box.text,
            all_pokemon_names,
            VALID_TYPES
        )
        # Actualizar las variables globales con los resultados de la función
        pokemon_suggestions = new_pokemon_suggestions
        # Solo actualizar mensajes si la función devolvió algo
        if current_error:
            error_message = current_error
            success_message = "" # Limpiar éxito si hay error
        elif current_success:
            success_message = current_success
            error_message = "" # Limpiar error si hay éxito
        else:
             # Si la función no devolvió mensajes específicos, mantener los mensajes generales
             pass

        # Si la lista de sugerencias de Pokémon cambia, resetear o ajustar el índice resaltado
        if not pokemon_suggestions:
             highlighted_pokemon_suggestion_index = -1
        elif highlighted_pokemon_suggestion_index >= len(pokemon_suggestions):
             highlighted_pokemon_suggestion_index = len(pokemon_suggestions) - 1
        elif highlighted_pokemon_suggestion_index == -1 and pokemon_suggestions:
             highlighted_pokemon_suggestion_index = 0 # Resaltar la primera sugerencia por defecto si hay alguna

        # Limpiar sugerencias del segundo input si el primero está activo
        target_type_suggestions = []
        highlighted_target_type_suggestion_index = -1


    # Actualizar sugerencias solo si la caja de Tipo Oponente está activa
    elif target_type_input_box.active:
         # Llamar a la función para obtener las sugerencias de Tipos
         new_target_type_suggestions = update_type_suggestions(
             target_type_input_box.text,
             VALID_TYPES
         )
         target_type_suggestions = new_target_type_suggestions

         # Si la lista de sugerencias de Tipo Oponente cambia, resetear o ajustar el índice resaltado
         if not target_type_suggestions:
              highlighted_target_type_suggestion_index = -1
         elif highlighted_target_type_suggestion_index >= len(target_type_suggestions):
              highlighted_target_type_suggestion_index = len(target_type_suggestions) - 1
         elif highlighted_target_type_suggestion_index == -1 and target_type_suggestions:
              highlighted_target_type_suggestion_index = 0 # Resaltar la primera sugerencia por defecto si hay alguna

         # Limpiar sugerencias del primer input si el segundo está activo
         pokemon_suggestions = []
         highlighted_pokemon_suggestion_index = -1
         # No limpiar mensajes de error/éxito aquí, ya que podrían ser relevantes para el Pokémon seleccionado

    # Si ninguna caja está activa, limpiar sugerencias y resaltados
    else:
        pokemon_suggestions = []
        highlighted_pokemon_suggestion_index = -1
        target_type_suggestions = []
        highlighted_target_type_suggestion_index = -1


    # --- Dibujar ---
    screen.fill(BG_COLOR)

    # Dibujar cajas de entrada
    pokemon_input_box.draw(screen)
    target_type_input_box.draw(screen)

    # Dibujar etiquetas de las cajas de entrada
    # Ajuste de la posición Y para que las etiquetas aparezcan encima de los inputs
    label_pokemon = FONT.render("Pokémon:", True, TEXT_COLOR)
    screen.blit(label_pokemon, (pokemon_input_box.rect.x, pokemon_input_box.rect.y - FONT_SIZE - 5)) # Posición ajustada
    label_target_type = FONT.render("Oponente (Tipo o Nombre):", True, TEXT_COLOR) # Etiqueta actualizada
    screen.blit(label_target_type, (target_type_input_box.rect.x, target_type_input_box.rect.y - FONT_SIZE - 5)) # Posición ajustada


    # --- Dibujar sugerencias (solo para la caja activa que tenga sugerencias) ---
    current_suggestions = []
    current_highlighted_index = -1
    suggestion_box_x = 0
    suggestion_box_y = 0

    if pokemon_input_box.active and pokemon_suggestions:
        current_suggestions = pokemon_suggestions
        current_highlighted_index = highlighted_pokemon_suggestion_index
        suggestion_box_x = pokemon_input_box.rect.x
        suggestion_box_y = pokemon_input_box.rect.y + INPUT_BOX_HEIGHT + PADDING
        suggestion_box_width = pokemon_input_box.rect.width

    elif target_type_input_box.active and target_type_suggestions:
        current_suggestions = target_type_suggestions
        current_highlighted_index = highlighted_target_type_suggestion_index
        suggestion_box_x = target_type_input_box.rect.x
        suggestion_box_y = target_type_input_box.rect.y + INPUT_BOX_HEIGHT + PADDING
        suggestion_box_width = target_type_input_box.rect.width


    if current_suggestions:
        for i, suggestion in enumerate(current_suggestions):
            suggestion_rect = pygame.Rect(suggestion_box_x, suggestion_box_y + i * SUGGESTION_HEIGHT, suggestion_box_width, SUGGESTION_HEIGHT)

            # Determinar el color de fondo de la sugerencia
            bg_color = SUGGESTION_BG_COLOR
            if i == current_highlighted_index:
                 bg_color = SUGGESTION_HIGHLIGHT_COLOR # Color para sugerencia resaltada por teclado
            # Si el ratón está sobre la sugerencia, tiene prioridad sobre el resaltado de teclado
            if suggestion_rect.collidepoint(pygame.mouse.get_pos()):
                 bg_color = SUGGESTION_HOVER_COLOR # Color para mouse hover

            pygame.draw.rect(screen, bg_color, suggestion_rect)
            pygame.draw.rect(screen, INPUT_BORDER_COLOR, suggestion_rect, 1) # Borde

            text_surface = FONT.render(suggestion.capitalize(), True, TEXT_COLOR) # Capitalizar la primera letra para mostrar
            screen.blit(text_surface, (suggestion_rect.x + PADDING, suggestion_rect.y + (SUGGESTION_HEIGHT - text_surface.get_height()) // 2))

    # Dibujar información del Pokémon seleccionado (atacante)
    info_y = target_type_input_box.rect.y + INPUT_BOX_HEIGHT + PADDING * 2
    if selected_pokemon_name:
        name_surface = FONT.render(f"Pokémon atacante: {selected_pokemon_name}", True, TEXT_COLOR) # Etiqueta actualizada
        screen.blit(name_surface, (PADDING, info_y))
        info_y += FONT_SIZE + PADDING

        types_text = ", ".join([t.capitalize() for t in selected_pokemon_types])
        types_surface = FONT.render(f"Tipos del atacante: {types_text}", True, TEXT_COLOR) # Etiqueta actualizada
        screen.blit(types_surface, (PADDING, info_y))
        info_y += FONT_SIZE + PADDING

    # Dibujar resultados de efectividad
    if calculated_effectiveness_multiplier is not None:
        # Mostrar la efectividad real del juego (multiplicador)
        # Mostrando la efectividad para el tipo primario del atacante contra el(los) tipo(s) del oponente
        attacker_primary_type_display = selected_pokemon_types[0].capitalize() if selected_pokemon_types else "N/A"
        opponent_input_display = target_type_input_box.text.capitalize() if target_type_input_box.text else "N/A" # Usar texto de la caja para mostrar
        effectiveness_text = f"Efectividad ({attacker_primary_type_display} vs {opponent_input_display}): {calculated_effectiveness_multiplier}x"
        effectiveness_surface = FONT.render(effectiveness_text, True, TEXT_COLOR)
        screen.blit(effectiveness_surface, (PADDING, info_y))
        info_y += FONT_SIZE + PADDING

        # Mostrar el valor mapeado a 0-100%
        percentage_text = f"Efectividad (0-100% mapeado): {calculated_effectiveness_percentage}%"
        percentage_surface = FONT.render(percentage_text, True, TEXT_COLOR)
        screen.blit(percentage_surface, (PADDING, info_y))
        info_y += FONT_SIZE + PADDING

        # Explicación sobre la "probabilidad" y la regresión
        explanation_lines = [
            "Nota sobre 'probabilidad' y regresión:",
            "La efectividad de tipo Pokémon es una regla fija (0x, 0.5x, 1x, 2x, 4x).",
            "El valor 0-100% mostrado es un mapeo arbitrario del multiplicador real.",
        ]
        for line in explanation_lines:
            explanation_surface = FONT.render(line, True, (80, 80, 80)) # Gris oscuro para la explicación
            screen.blit(explanation_surface, (PADDING, info_y))
            info_y += FONT_SIZE


    # Dibujar mensajes de error o éxito
    message_y = SCREEN_HEIGHT - FONT_SIZE - PADDING # Posición en la parte inferior
    if error_message:
        error_surface = FONT.render(error_message, True, ERROR_COLOR)
        screen.blit(error_surface, (PADDING, message_y))
    elif success_message:
        success_surface = FONT.render(success_message, True, SUCCESS_COLOR)
        screen.blit(success_surface, (PADDING, message_y))


  
    pygame.display.flip()


pygame.quit()
sys.exit()
