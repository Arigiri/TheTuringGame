import pygame
import sys
from animation import draw_home_screen, draw_level_interface, CardEditor
from logic import GameLogic

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("The Turing Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Constants
PADDING = 50
BUTTON_HEIGHT = 50
TAB_HEIGHT = 50

# Create game logic instance
game_logic = GameLogic()

def draw_message(message):
    """Draw a message in the center of the screen"""
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
    screen.blit(text, text_rect)

def start_game(level_name=None):
    """Start the game with the selected level"""
    global current_level, card_editor, active_tab, level
    
    if level_name:
        # Initialize game state
        level = game_logic.initialize_level(level_name)
        current_level = level
        card_editor = CardEditor(screen, None, current_level)  # Pass current_level
        level.editor = card_editor
        active_tab = "INFO"
        content_rect = pygame.Rect(
            PADDING,
            PADDING + BUTTON_HEIGHT + PADDING,
            screen.get_width() - 2 * PADDING,
            screen.get_height() - 3 * PADDING - BUTTON_HEIGHT - TAB_HEIGHT
        )
    
    running = True
    while running:
        screen.fill(WHITE)
        
        # Draw level interface and get clickable areas
        result = draw_level_interface(screen, level, active_tab)
        if len(result) == 4:
            home_rect, tab_rects, card_rects, scrollable = result
        else:
            home_rect, tab_rects = result[:2]
            card_rects = None
            scrollable = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            
            # Handle scrolling if scrollable area exists
            if scrollable:
                if scrollable.handle_event(event):
                    continue  # Event was handled by scrollable area
            
            if card_editor.visible:
                if card_editor.handle_event(event, content_rect):
                    continue
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # If card editor is visible, only handle its events
                if card_editor.visible:
                    if card_editor.close_rect and card_editor.close_rect.collidepoint(mouse_pos):
                        card_editor.hide()
                else:
                    # Check if HOME button was clicked
                    if home_rect.collidepoint(mouse_pos):
                        running = False
                    
                    # Check if any tab was clicked
                    for tab, rect in tab_rects.items():
                        if rect.collidepoint(mouse_pos):
                            active_tab = tab
                    
                    # Check if any card was clicked (only on left click)
                    if card_rects and event.button == 1:  # Left click
                        for rect, card in card_rects:
                            if rect.collidepoint(mouse_pos):
                                if card:  # Existing card
                                    card_editor.show(card)
                                else:  # "Add New Card" button
                                    new_card = level.create_new_card()
                                    card_editor.show(new_card)
            
            elif event.type == pygame.MOUSEMOTION:
                if scrollable and scrollable.dragging:
                    scrollable.handle_event(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if scrollable:
                    scrollable.handle_event(event)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if card_editor.visible:
                        card_editor.hide()
                    else:
                        running = False
        
        # Draw card editor on top if visible
        if card_editor.visible:
            card_editor.draw(content_rect)
        
        pygame.display.flip()

def main():
    """Main game loop for the home screen"""
    running = True
    clock = pygame.time.Clock()
    
    while running:
        screen.fill(WHITE)
        
        # Draw the home screen and get the level rectangles
        level_rects = draw_home_screen(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if any level button was clicked
                mouse_pos = pygame.mouse.get_pos()
                for level_name, rect in level_rects.items():
                    if rect.collidepoint(mouse_pos):
                        start_game(level_name)
                        # After returning from the level, redraw the home screen
                        screen.fill(WHITE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()