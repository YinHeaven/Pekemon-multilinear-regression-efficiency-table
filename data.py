# data.

"""Contiene datos estáticos como la tabla de efectividad."""

# --- Tabla de Efectividad de Tipos (Hardcodeada) ---
# Multiplicador de daño del tipo ATACANTE contra el tipo DEFENSOR.
# Fuente: https://pokemondb.net/type
TYPE_EFFECTIVENESS = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fighting": {"normal": 2, "flying": 0.5, "poison": 0.5, "rock": 2, "bug": 0.5, "ghost": 0, "steel": 2, "psychic": 0.5, "ice": 2, "dark": 2, "fairy": 0.5},
    "flying": {"fighting": 2, "rock": 0.5, "bug": 2, "steel": 0.5, "grass": 2, "electric": 0.5},
    "poison": {"poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "grass": 2, "fairy": 2},
    "ground": {"flying": 0, "poison": 2, "rock": 2, "bug": 0.5, "steel": 2, "fire": 2, "grass": 0.5, "electric": 2},
    "rock": {"fighting": 0.5, "flying": 2, "ground": 0.5, "bug": 2, "steel": 0.5, "fire": 2, "ice": 2},
    "bug": {"fighting": 0.5, "flying": 0.5, "poison": 0.5, "ghost": 0.5, "steel": 0.5, "fire": 0.5, "grass": 2, "psychic": 2, "dark": 2, "fairy": 0.5},
    "ghost": {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5},
    "steel": {"rock": 2, "steel": 0.5, "fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "fairy": 2},
    "fire": {"rock": 0.5, "bug": 2, "steel": 2, "fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "dragon": 0.5},
    "water": {"ground": 2, "rock": 2, "fire": 2, "water": 0.5, "grass": 0.5, "dragon": 0.5},
    "grass": {"flying": 0.5, "poison": 0.5, "ground": 2, "rock": 2, "bug": 0.5, "steel": 0.5, "fire": 0.5, "water": 2, "grass": 0.5, "dragon": 0.5},
    "electric": {"flying": 2, "ground": 0, "water": 2, "grass": 0.5, "electric": 0.5, "dragon": 0.5},
    "psychic": {"fighting": 2, "poison": 2, "steel": 0.5, "psychic": 0.5, "dark": 0},
    "ice": {"flying": 2, "ground": 2, "grass": 2, "dragon": 2, "steel": 0.5, "fire": 0.5, "water": 0.5, "ice": 0.5},
    "dragon": {"dragon": 2, "steel": 0.5, "fairy": 0},
    "dark": {"fighting": 0.5, "ghost": 2, "psychic": 2, "dark": 0.5, "fairy": 0.5},
    "fairy": {"fighting": 2, "poison": 0.5, "steel": 0.5, "fire": 0.5, "dragon": 2, "dark": 2},
}

# Lista de nombres de tipos válidos para la búsqueda, derivada de la tabla
VALID_TYPES = list(TYPE_EFFECTIVENESS.keys())