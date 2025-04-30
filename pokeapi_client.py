# pokeapi_client.py
"""Funciones para interactuar con la PokeAPI."""

import requests
from constants import POKEAPI_BASE_URL

def get_all_pokemon_names():
    """Obtiene una lista de todos los nombres de Pokémon de la PokeAPI."""
    print("Obteniendo lista completa de Pokémon...")
    url = f"{POKEAPI_BASE_URL}pokemon?limit=10000"
    try:
        response = requests.get(url, timeout=15) # Añadir timeout
        response.raise_for_status()
        data = response.json()
        print("Lista de Pokémon obtenida.")
        return [pokemon['name'] for pokemon in data.get('results', [])]
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la lista de Pokémon: {e}")
        return []

def get_pokemon_types(pokemon_name):
    """Obtiene los tipos de un Pokémon específico de la PokeAPI."""
    if not pokemon_name:
        return None
    print(f"Obteniendo tipos para {pokemon_name}...")
    url = f"{POKEAPI_BASE_URL}pokemon/{pokemon_name.lower()}"
    try:
        response = requests.get(url, timeout=10) # Añadir timeout
        response.raise_for_status()
        data = response.json()
        types = [t['type']['name'] for t in data.get('types', [])]
        print(f"Tipos para {pokemon_name}: {types}")
        return types if types else None # Devolver None si no se encontraron tipos
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de {pokemon_name}: {e}")
        return None

def get_pokemon_by_type(type_name):
    """Obtiene una lista de nombres de Pokémon de un tipo específico de la PokeAPI."""
    if not type_name:
        return []
    print(f"Obteniendo Pokémon de tipo {type_name}...")
    url = f"{POKEAPI_BASE_URL}type/{type_name.lower()}"
    try:
        response = requests.get(url, timeout=10) # Añadir timeout
        response.raise_for_status()
        data = response.json()
        pokemon_list = [entry['pokemon']['name'] for entry in data.get('pokemon', [])]
        print(f"Obtenidos {len(pokemon_list)} Pokémon de tipo {type_name}.")
        return pokemon_list
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener Pokémon de tipo {type_name}: {e}")
        return []