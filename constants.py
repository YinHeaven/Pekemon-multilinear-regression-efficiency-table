# constants.py
"""Define todas las constantes usadas en la aplicación."""

# API
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/"

# Pantalla y Colores
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (230, 230, 230) # Gris claro
TEXT_COLOR = (50, 50, 50)
INPUT_BG_COLOR = (255, 255, 255) # Blanco
INPUT_BORDER_COLOR = (100, 100, 100) # Gris oscuro
INPUT_ACTIVE_BORDER_COLOR = (0, 128, 255) # Azul
PLACEHOLDER_COLOR = (150, 150, 150) # Gris
SUGGESTION_BG_COLOR = (240, 240, 240)
SUGGESTION_HOVER_COLOR = (200, 200, 255) # Azul claro para mouse hover
SUGGESTION_HIGHLIGHT_COLOR = (150, 150, 255) # Azul más oscuro para selección con teclado
ERROR_COLOR = (255, 0, 0) # Rojo
SUCCESS_COLOR = (0, 128, 0) # Verde
INFO_TEXT_COLOR = (80, 80, 80) # Gris oscuro para explicaciones

# Fuentes y UI
FONT_SIZE = 24
PADDING = 10
INPUT_BOX_HEIGHT = 40
SUGGESTION_HEIGHT = 30
MAX_SUGGESTIONS = 15