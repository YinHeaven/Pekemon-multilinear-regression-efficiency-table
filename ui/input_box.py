# ui/input_box.py

import pygame
import constants as C # Usar alias para claridad

class InputBox:
    def __init__(self, x, y, w, h, font, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = C.INPUT_BORDER_COLOR
        self.text = text
        self.font = font
        self.txt_surface = self.font.render(text, True, C.TEXT_COLOR)
        self.active = False
        self.placeholder = ""
        self.placeholder_surface = None

    def set_placeholder(self, text):
        self.placeholder = text
        # self.placeholder_surface = self.font.render(text, True, C.PLACEHOLDER_COLOR)
        self.placeholder_surface = self.font.render(text, True, (150, 150, 150))  # Gris manual

    def handle_event(self, event):
        """Maneja eventos de ratón y teclado para la caja de entrada."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = C.INPUT_ACTIVE_BORDER_COLOR if self.active else C.INPUT_BORDER_COLOR
            # Retorna True si se activó para que Main.py pueda manejar la lógica de foco
            return self.active
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # La acción de Enter se maneja en Main.py
                    return "enter" # Indica que se presionó Enter
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_TAB:
                    # Podría usarse para cambiar de foco, manejado en Main.py
                    return "tab"
                else:
                    self.text += event.unicode
                self.update_text_surface()
                return "keydown" # Indica que se cambió el texto
        return None # Ningún evento relevante manejado

    def update_text_surface(self):
        """Actualiza la superficie de texto renderizada."""
        self.txt_surface = self.font.render(self.text, True, C.TEXT_COLOR)


    def draw(self, screen):
        # Fondo con bordes redondeados
        pygame.draw.rect(screen, C.INPUT_BG_COLOR, self.rect, border_radius=C.BORDER_RADIUS)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=C.BORDER_RADIUS)
        
        # Texto o placeholder
        if self.text:
            text_surface = self.font.render(self.text, True, C.TEXT_COLOR)
            screen.blit(text_surface, (self.rect.x + 10, self.rect.y + (self.rect.h - text_surface.get_height()) // 2))
        elif self.placeholder_surface and not self.active:
            screen.blit(self.placeholder_surface, (self.rect.x + 10, self.rect.y + (self.rect.h - self.placeholder_surface.get_height()) // 2))

        # Texto o Placeholder
        if self.text:
            # Simple recorte si el texto es muy largo
            available_width = self.rect.width - C.PADDING * 2
            rendered_text = self.text
            text_width = self.txt_surface.get_width()
            blit_pos_x = self.rect.x + C.PADDING
            # Si el texto se pasa, muestra el final
            if text_width > available_width:
                # Muestra los últimos caracteres que quepan
                visible_chars = 0
                current_width = 0
                for i in range(len(rendered_text) -1, -1, -1):
                    char_width = self.font.size(rendered_text[i])[0]
                    if current_width + char_width <= available_width:
                        current_width += char_width
                        visible_chars += 1
                    else:
                        break
                rendered_text_final = rendered_text[-visible_chars:]
                self.txt_surface = self.font.render(rendered_text_final, True, C.TEXT_COLOR)


            screen.blit(self.txt_surface, (blit_pos_x, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2))

        elif self.placeholder_surface and not self.active:
            screen.blit(self.placeholder_surface, (self.rect.x + C.PADDING, self.rect.y + (self.rect.height - self.placeholder_surface.get_height()) // 2))
