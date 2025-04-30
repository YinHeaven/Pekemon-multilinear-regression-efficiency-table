# Pokémon Type Effectiveness Suggester

<h1>Codigo refactorizado siguendo una arquitectura de software simple para mejor lectura y actualizacion del codigo para futuras funciones (la regresion multilineal esta en proceso) Dejare el archivo PokemonRlAI.py como ejemplo de la versiones anteriores está en su criterio si borrar o no.</h1> <br>
Una sencilla aplicación de escritorio creada con Pygame que te permite buscar Pokémon por nombre o tipo, obtener sus datos de la PokeAPI y calcular la efectividad de tipo de su tipo primario contra un oponente especificado.

![Screenshot Placeholder](nota 'pon aqui el link )

## Descripción

Esta herramienta utiliza la [PokeAPI](https://pokeapi.co/) para obtener información sobre los Pokémon, incluyendo sus tipos. Proporciona una interfaz gráfica simple donde puedes:

1.  **Buscar un Pokémon atacante:** Escribe el nombre (o el inicio del nombre) o el tipo exacto del Pokémon. Aparecerá una lista de sugerencias que puedes seleccionar con el teclado (flechas arriba/abajo y Enter) o el ratón.
2.  **Especificar un oponente:** Introduce el nombre de un Pokémon oponente o directamente uno de sus tipos. También aparecerán sugerencias para los tipos válidos.
3.  **Ver Resultados:** Una vez seleccionado el atacante y especificado el oponente, la aplicación mostrará los tipos del atacante y calculará la efectividad del *tipo primario* del atacante contra el(los) tipo(s) del oponente, mostrando el multiplicador de daño (ej: 0.5x, 1x, 2x).

## Características Principales

* Búsqueda de Pokémon por prefijo de nombre o nombre de tipo exacto.
* Autocompletado con lista de sugerencias para la entrada de Pokémon y Tipos.
* Navegación por las sugerencias usando teclado (flechas, Enter) y ratón.
* Integración con [PokeAPI](https://pokeapi.co/) para obtener los tipos de los Pokémon en tiempo real.
* Cálculo de efectividad de tipos basado en la tabla estándar del juego (hardcodeada en `data.py`).
* Interfaz gráfica de usuario (GUI) implementada con Pygame.
* Mensajes de estado para indicar progreso y errores.
* Código refactorizado en módulos para mejor organización y mantenibilidad.

## Tecnologías Utilizadas

* **Python 3:** Lenguaje de programación principal.
* **Pygame:** Biblioteca para la creación de la interfaz gráfica y manejo de eventos.
* **Requests:** Biblioteca para realizar las llamadas a la PokeAPI.
* **PokeAPI (pokeapi.co):** API pública utilizada para obtener los datos de los Pokémon.
|<img src="https://www.pygame.org/ftp/pygame-badge-SMA.png" width ="20%">|<img src="https://miro.medium.com/v2/resize:fit:305/1*Q1Nue45Q7N2xMFc6ehEOdg.png">|

## Instalación

Asegúrate de tener Python 3 instalado en tu sistema. Luego, clona este repositorio e instala las dependencias necesarias:

```bash
git clone [https://github.com/tu_usuario/tu_repositorio.git](https://github.com/tu_usuario/tu_repositorio.git)
cd tu_repositorio
pip install -r requirements.txt
