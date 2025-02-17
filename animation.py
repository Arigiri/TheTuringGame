import pygame
import os

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (100, 150, 255)
LIGHT_GRAY = (230, 230, 230)
LIGHT_RED = (255, 100, 100)

# Constants for layout
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 60
PADDING = 20
TAB_HEIGHT = 40
TAB_PADDING = 5
SCROLLBAR_WIDTH = 15

# Card constants
CARD_PADDING = 20  # Space between cards
MIN_CARD_WIDTH = 350  # Base width for cards
MIN_CARD_HEIGHT = 150  # Minimum height, will expand based on content
CARDS_PER_ROW = 2
COLUMN_SPACING = 10  # Reduced spacing between columns
HEADER_HEIGHT = 40  # Height for card header
ROW_HEIGHT = 25  # Height for each action row

class ScrollableArea:
    def __init__(self, rect, content_height):
        self.rect = rect
        self.content_height = content_height
        self.scroll_y = 0
        self.max_scroll = max(0, content_height - rect.height)
        self.dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0
        self.scroll_speed = 20  # Pixels per scroll
        
        # Create scrollbar rect
        self.scrollbar_rect = pygame.Rect(
            rect.right - SCROLLBAR_WIDTH,
            rect.top,
            SCROLLBAR_WIDTH,
            rect.height
        )
        
        # Calculate scrollbar handle
        self.update_scrollbar()
        
    def update_scrollbar(self):
        if self.content_height <= self.rect.height:
            self.handle_height = self.scrollbar_rect.height
        else:
            self.handle_height = max(30, int(self.rect.height * (self.rect.height / self.content_height)))
        
        
        # Calculate handle position
        scroll_fraction = self.scroll_y / self.max_scroll if self.max_scroll > 0 else 0
        self.handle_y = self.scrollbar_rect.top + scroll_fraction * (self.scrollbar_rect.height - self.handle_height)
        
        self.handle_rect = pygame.Rect(
            self.scrollbar_rect.x,
            self.handle_y,
            SCROLLBAR_WIDTH,
            self.handle_height
        )
    
    def handle_event(self, event):
        # Don't handle scroll events if editor is open
        if event.type == pygame.MOUSEWHEEL and hasattr(self, 'editor') and self.editor.is_editing:
            return False
            
        if event.type == pygame.MOUSEWHEEL and self.max_scroll > 0:
            old_scroll = self.scroll_y
            new_scroll = self.scroll_y - event.y * self.scroll_speed
            # Clamp to valid range
            self.scroll_y = max(0, min(new_scroll, self.max_scroll))
            self.update_scrollbar()
            return True
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.scrollbar_rect.collidepoint(event.pos):
                if self.handle_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_start_y = event.pos[1]
                    self.drag_start_scroll = self.scroll_y
                elif self.max_scroll > 0:
                    # Click on scrollbar track - jump to position
                    scroll_pos = event.pos[1] - self.scrollbar_rect.top - self.handle_height/2
                    scroll_ratio = scroll_pos / (self.scrollbar_rect.height - self.handle_height)
                    old_scroll = self.scroll_y
                    self.scroll_y = max(0, min(self.max_scroll, scroll_ratio * self.max_scroll))
                    self.update_scrollbar()
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_dragging = self.dragging
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION and self.dragging and self.max_scroll > 0:
            # Calculate drag scroll position
            delta_y = event.pos[1] - self.drag_start_y
            scroll_range = self.scrollbar_rect.height - self.handle_height
            scroll_delta = (delta_y / scroll_range) * self.max_scroll
            new_scroll = self.drag_start_scroll + scroll_delta
            old_scroll = self.scroll_y
            # Clamp to valid range
            self.scroll_y = max(0, min(new_scroll, self.max_scroll))
            self.update_scrollbar()
            return True
            
        return False
    
    def draw(self, screen):
        if self.max_scroll > 0:
            # Draw scrollbar background
            pygame.draw.rect(screen, LIGHT_GRAY, self.scrollbar_rect)
            # Draw handle
            pygame.draw.rect(screen, DARK_GRAY, self.handle_rect)

class StateSelector:
    def __init__(self, screen, states, current_value, x, y):
        self.screen = screen
        self.states = states
        self.current_value = current_value
        self.selected_value = current_value
        self.visible = False
        self.font = pygame.font.Font(None, 24)
        
        # Calculate dimensions
        self.item_height = 30
        self.max_items = 6  # Maximum number of items visible at once
        self.width = 100
        self.scroll_width = 15  # Width of scroll bar
        
        # Calculate total height
        visible_items = min(len(states), self.max_items)
        self.height = visible_items * self.item_height
        
        # Scroll state
        self.scroll_pos = 0
        self.max_scroll = max(0, len(states) - self.max_items)
        self.dragging = False
        
        # Calculate scroll bar height and position
        self.update_scroll_bar()
        
    def update_scroll_bar(self):
        if self.max_scroll > 0:
            # Calculate scroll bar height based on visible portion
            visible_ratio = self.max_items / len(self.states)
            self.scroll_height = max(20, int(self.height * visible_ratio))
            
            # Calculate scroll bar position
            scroll_ratio = self.scroll_pos / self.max_scroll
            max_scroll_y = self.height - self.scroll_height
            self.scroll_y = int(scroll_ratio * max_scroll_y)
        else:
            self.scroll_height = self.height
            self.scroll_y = 0
            
    def show(self, x, y):
        self.visible = True
        screen_height = self.screen.get_height()
        
        # Adjust position if dropdown would go off screen
        if y + self.height > screen_height:
            y = screen_height - self.height - 10
            
        self.rect = pygame.Rect(x, y, self.width + self.scroll_width, self.height)
        self.scroll_rect = pygame.Rect(x + self.width, y, self.scroll_width, self.height)
        
    def hide(self):
        self.visible = False
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.scroll_rect.collidepoint(event.pos):
                    # Handle scroll bar click
                    self.dragging = True
                    return True
                elif self.rect.collidepoint(event.pos):
                    # Calculate which item was clicked
                    rel_y = event.pos[1] - self.rect.top
                    index = self.scroll_pos + (rel_y // self.item_height)
                    if 0 <= index < len(self.states):
                        self.selected_value = self.states[index]
                        self.hide()
                    return True
            elif event.button in (4, 5):  # Mouse wheel
                if self.rect.collidepoint(event.pos) or self.scroll_rect.collidepoint(event.pos):
                    # Scroll up (4) or down (5)
                    direction = -1 if event.button == 4 else 1
                    self.scroll_pos = max(0, min(self.max_scroll, self.scroll_pos + direction))
                    self.update_scroll_bar()
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Update scroll position based on mouse movement
                rel_y = event.pos[1] - self.scroll_rect.top
                scroll_ratio = max(0, min(1, rel_y / (self.height - self.scroll_height)))
                self.scroll_pos = int(scroll_ratio * self.max_scroll)
                self.update_scroll_bar()
                return True
                
        return False
        
    def draw(self):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(self.screen, WHITE, self.rect)
        pygame.draw.rect(self.screen, BLACK, self.rect, 1)
        
        # Draw visible items
        for i in range(self.max_items):
            idx = self.scroll_pos + i
            if idx >= len(self.states):
                break
                
            item_rect = pygame.Rect(
                self.rect.left,
                self.rect.top + (i * self.item_height),
                self.width,
                self.item_height
            )
            
            # Draw item background
            if self.states[idx] == self.current_value:
                pygame.draw.rect(self.screen, LIGHT_GRAY, item_rect)
            
            # Draw item text
            text = self.font.render(str(self.states[idx]), True, BLACK)
            text_rect = text.get_rect(center=item_rect.center)
            self.screen.blit(text, text_rect)
            
            # Draw item border
            pygame.draw.rect(self.screen, BLACK, item_rect, 1)
        
        # Draw scroll bar background
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.scroll_rect)
        
        # Draw scroll bar
        if self.max_scroll > 0:
            scroll_bar = pygame.Rect(
                self.scroll_rect.left,
                self.scroll_rect.top + self.scroll_y,
                self.scroll_width,
                self.scroll_height
            )
            pygame.draw.rect(self.screen, GRAY, scroll_bar)
            pygame.draw.rect(self.screen, BLACK, scroll_bar, 1)

class CardEditor:
    def __init__(self, screen, card, level):
        self.screen = screen
        self.card = card
        self.level = level
        self.visible = False
        self.rect = None
        self.save_rect = None
        self.cancel_rect = None
        self.close_rect = None
        self.state_selector = None
        self.cell_rects = []  # Store rects for each cell
        self.active_cell = None
        self.is_editing = False
        
    def show(self, card):
        self.card = card
        self.visible = True
        self.is_editing = True
        self.state_selector = None
        
    def hide(self):
        self.visible = False
        self.is_editing = False
        if self.state_selector:
            self.state_selector.hide()
        
    def handle_event(self, event, content_rect):
        """Handle mouse events for the editor"""
        if not self.visible:
            return False
            
        # Handle state selector if visible
        if self.state_selector and self.state_selector.visible:
            # Only handle state selector events when in WRITE tab
            if event.type == pygame.MOUSEWHEEL and self.rect and self.rect.collidepoint(event.pos):
                if self.state_selector.handle_event(event):
                    return True
            elif self.state_selector.handle_event(event):
                # Update card value if state was selected
                if self.state_selector.selected_value != self.state_selector.current_value:
                    action_index, col_index = self.active_cell
                    if col_index == 1:  # WRITE column
                        self.card.action[action_index].action[0] = self.state_selector.selected_value
                return True
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            
            # Draw to get latest positions
            self.draw(content_rect)
            
            # Check if any button was clicked
            if self.close_rect and self.close_rect.collidepoint(event.pos):
                self.hide()
                return True
                
            if self.save_rect and self.save_rect.collidepoint(event.pos):
                self.hide()
                return True
                
            if self.cancel_rect and self.cancel_rect.collidepoint(event.pos):
                self.hide()
                return True
                
            # Check if any cell was clicked
            for i, row in enumerate(self.cell_rects):
                for j, rect in enumerate(row):
                    if rect and rect.collidepoint(event.pos):
                        if j == 1:  # WRITE column
                            self.active_cell = (i, j)
                            self.state_selector = StateSelector(
                                self.screen,
                                self.level.problem['state'],
                                self.card.action[i].action[0],
                                rect.left,
                                rect.bottom
                            )
                            self.state_selector.show(rect.left, rect.bottom)
                            return True
            
        return False
    
    def draw(self, content_rect):
        if not self.visible or not self.card:
            return
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.fill(WHITE)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # Calculate minimum required height for card content
        text_font = pygame.font.Font(None, 24)
        header_height = HEADER_HEIGHT
        action_height = len(self.card.action) * ROW_HEIGHT + 80  # Tăng padding giữa các action
        button_section_height = 80  # Tăng space cho buttons
        
        # Calculate total required height with more vertical space
        required_height = header_height + action_height + button_section_height + 6*PADDING  # Tăng padding dọc
        min_height = 700  # Tăng chiều cao tối thiểu
        
        # Calculate card dimensions with constraints
        card_width = min(600, content_rect.width - 2*PADDING)
        card_height = min(max(min_height, required_height), content_rect.height + 2*PADDING)
        
        # Create editor rectangle - đặt cao hơn 1/3 khoảng cách từ center
        vertical_offset = (content_rect.height // 3)  # Tăng offset
        editor_rect = pygame.Rect(
            content_rect.centerx - card_width//2,
            max(PADDING, content_rect.centery - card_height//2 - vertical_offset),  # Đảm bảo không vượt quá top
            card_width,
            card_height
        )
        
        # Draw editor background
        pygame.draw.rect(self.screen, WHITE, editor_rect)
        pygame.draw.rect(self.screen, BLACK, editor_rect, 2)
        
        # Draw card content using the same layout as display
        self.cell_rects = self.draw_card(self.screen, editor_rect.left + PADDING, editor_rect.top + PADDING, 
                            self.card, editor_rect, editor_rect.width - 2*PADDING)
        
        if self.cell_rects:
            # Draw buttons at the bottom
            button_y = editor_rect.bottom + 2 * PADDING
            button_width = 100
            button_height = 40
            
            # Save button
            self.save_rect = pygame.Rect(
                editor_rect.centerx - button_width - 10,
                button_y,
                button_width,
                button_height
            )
            pygame.draw.rect(self.screen, LIGHT_GRAY, self.save_rect)
            pygame.draw.rect(self.screen, BLACK, self.save_rect, 2)
            
            font = pygame.font.Font(None, 24)
            save_text = font.render("Save", True, BLACK)
            save_text_rect = save_text.get_rect(center=self.save_rect.center)
            self.screen.blit(save_text, save_text_rect)
            
            # Cancel button
            self.cancel_rect = pygame.Rect(
                editor_rect.centerx + 10,
                button_y,
                button_width,
                button_height
            )
            pygame.draw.rect(self.screen, LIGHT_GRAY, self.cancel_rect)
            pygame.draw.rect(self.screen, BLACK, self.cancel_rect, 2)
            
            cancel_text = font.render("Cancel", True, BLACK)
            cancel_text_rect = cancel_text.get_rect(center=self.cancel_rect.center)
            self.screen.blit(cancel_text, cancel_text_rect)
            
            # Close button
            self.close_rect = pygame.Rect(editor_rect.right - 30, editor_rect.top + 10, 20, 20)
            pygame.draw.rect(self.screen, LIGHT_GRAY, self.close_rect)
            pygame.draw.line(self.screen, BLACK, 
                           (self.close_rect.left + 5, self.close_rect.top + 5),
                           (self.close_rect.right - 5, self.close_rect.bottom - 5), 2)
            pygame.draw.line(self.screen, BLACK,
                           (self.close_rect.left + 5, self.close_rect.bottom - 5),
                           (self.close_rect.right - 5, self.close_rect.top + 5), 2)
        
        # Draw state selector if visible
        if self.state_selector and self.state_selector.visible:
            self.state_selector.draw()
    
    def draw_card(self, screen, x, y, card=None, content_rect=None, width=None):
        """Draw a single card"""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)  # Smaller font for values
        
        # Calculate card size
        card_width = width if width is not None else MIN_CARD_WIDTH
        if card:
            _, card_height = calculate_card_size(card, font)
        else:
            card_height = MIN_CARD_HEIGHT
        
        rect = pygame.Rect(x, y, card_width, card_height)
        
        # Only draw if card is at least partially visible
        if content_rect and (rect.bottom > content_rect.top and 
                rect.top < content_rect.bottom and
                rect.right > content_rect.left and
                rect.left < content_rect.right):
            # Draw card background
            visible_rect = rect.clip(content_rect)
            if visible_rect.width > 0 and visible_rect.height > 0:
                pygame.draw.rect(screen, WHITE, visible_rect)
                pygame.draw.rect(screen, BLACK, visible_rect, 2)
            
            if card:
                # Draw card title and edit icon
                title = f"CARD_{card.card_id}"
                title_text = font.render(title, True, BLACK)
                title_rect = title_text.get_rect(left=x + 10, top=y + 10)
                
                # Only draw title if it's within content rect
                if title_rect.bottom > content_rect.top and title_rect.top < content_rect.bottom:
                    clip_rect = title_rect.clip(content_rect)
                    if clip_rect.width > 0 and clip_rect.height > 0:
                        screen.blit(title_text, clip_rect, 
                                  (max(0, content_rect.left - title_rect.left),
                                   max(0, content_rect.top - title_rect.top),
                                   clip_rect.width,
                                   clip_rect.height))
                
                # Draw column headers
                columns = ["READ", "WRITE", "MOVE", "NEXT"]
                header_y = y + HEADER_HEIGHT
                usable_width = card_width - (2 * COLUMN_SPACING)  # Adjust spacing
                column_width = usable_width // len(columns)
                
                for i, col in enumerate(columns):
                    x_pos = x + COLUMN_SPACING + (i * column_width) + (column_width // 2)
                    text = font.render(col, True, BLACK)
                    text_rect = text.get_rect(center=(x_pos, header_y))
                    
                    # Only draw column header if it's within content rect
                    if text_rect.bottom > content_rect.top and text_rect.top < content_rect.bottom:
                        clip_rect = text_rect.clip(content_rect)
                        if clip_rect.width > 0 and clip_rect.height > 0:
                            screen.blit(text, clip_rect, 
                                      (max(0, content_rect.left - text_rect.left),
                                       max(0, content_rect.top - text_rect.top),
                                       clip_rect.width,
                                       clip_rect.height))
                
                # Draw separator line under headers
                separator_rect = pygame.Rect(x, header_y + 25, card_width, 1)
                
                # Only draw separator line if it's within content rect
                if separator_rect.bottom > content_rect.top and separator_rect.top < content_rect.bottom:
                    clip_rect = separator_rect.clip(content_rect)
                    if clip_rect.width > 0 and clip_rect.height > 0:
                        pygame.draw.rect(screen, BLACK, clip_rect)
                
                # Draw action data with smaller font
                start_y = header_y + 35
                self.cell_rects = []  # Reset cell_rects
                
                for idx, action in enumerate(card.action):
                    values = [str(action.state)] + [str(v) for v in action.action]
                    row_rects = []
                    
                    for i, value in enumerate(values):
                        # Calculate cell position
                        x_pos = x + COLUMN_SPACING + (i * column_width)
                        y_pos = start_y + (idx * ROW_HEIGHT)
                        cell_rect = pygame.Rect(x_pos, y_pos, column_width, ROW_HEIGHT)
                        row_rects.append(cell_rect)
                        
                        # Draw cell background for WRITE column
                        if i == 1:  # WRITE column
                            pygame.draw.rect(self.screen, LIGHT_GRAY, cell_rect)
                            pygame.draw.rect(self.screen, BLACK, cell_rect, 1)  # Add border
                        
                        text = small_font.render(value, True, BLACK)
                        text_rect = text.get_rect(center=cell_rect.center)
                        
                        # Only draw action data if it's within content rect
                        if text_rect.bottom > content_rect.top and text_rect.top < content_rect.bottom:
                            clip_rect = text_rect.clip(content_rect)
                            if clip_rect.width > 0 and clip_rect.height > 0:
                                screen.blit(text, clip_rect, 
                                          (max(0, content_rect.left - text_rect.left),
                                           max(0, content_rect.top - text_rect.top),
                                           clip_rect.width,
                                           clip_rect.height))
                    
                    self.cell_rects.append(row_rects)
            else:
                # Draw "ADD NEW CARD" text
                font = pygame.font.Font(None, 36)
                text = font.render("ADD NEW CARD", True, BLACK)
                text_rect = text.get_rect(center=(x + card_width//2, y + card_height//2))
                
                # Only draw text if it's within content rect
                if text_rect.bottom > content_rect.top and text_rect.top < content_rect.bottom:
                    clip_rect = text_rect.clip(content_rect)
                    if clip_rect.width > 0 and clip_rect.height > 0:
                        screen.blit(text, clip_rect, 
                                  (max(0, content_rect.left - text_rect.left),
                                   max(0, content_rect.top - text_rect.top),
                                   clip_rect.width,
                                   clip_rect.height))
    
        return self.cell_rects

def calculate_card_size(card, font):
    """Calculate required card size based on content"""
    width = MIN_CARD_WIDTH
    
    if card:
        # Calculate height based on number of actions
        num_actions = len(card.action)
        height = HEADER_HEIGHT + 30 + (num_actions * ROW_HEIGHT) + 20  # Header + column headers + rows + padding
    else:
        height = MIN_CARD_HEIGHT
    
    return width, height

def draw_card(screen, x, y, card=None, content_rect=None, width=None):
    """Draw a single card"""
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)  # Smaller font for values
    
    # Calculate card size
    card_width = width if width is not None else MIN_CARD_WIDTH
    if card:
        _, card_height = calculate_card_size(card, font)
    else:
        card_height = MIN_CARD_HEIGHT
    
    rect = pygame.Rect(x, y, card_width, card_height)
    
    # Only draw if card is at least partially visible
    if content_rect and (rect.bottom > content_rect.top and 
            rect.top < content_rect.bottom and
            rect.right > content_rect.left and
            rect.left < content_rect.right):
        # Draw card background
        visible_rect = rect.clip(content_rect)
        if visible_rect.width > 0 and visible_rect.height > 0:
            pygame.draw.rect(screen, WHITE, visible_rect)
            pygame.draw.rect(screen, BLACK, visible_rect, 2)
        
        if card:
            # Draw card title and edit icon
            title = f"CARD_{card.card_id}"
            title_text = font.render(title, True, BLACK)
            title_rect = title_text.get_rect(left=x + 10, top=y + 10)
            
            # Only draw title if it's within content rect
            if title_rect.bottom > content_rect.top and title_rect.top < content_rect.bottom:
                clip_rect = title_rect.clip(content_rect)
                if clip_rect.width > 0 and clip_rect.height > 0:
                    screen.blit(title_text, clip_rect, 
                              (max(0, content_rect.left - title_rect.left),
                               max(0, content_rect.top - title_rect.top),
                               clip_rect.width,
                               clip_rect.height))
            
            # Draw column headers
            columns = ["READ", "WRITE", "MOVE", "NEXT"]
            header_y = y + HEADER_HEIGHT
            usable_width = card_width - (COLUMN_SPACING)
            column_width = usable_width // len(columns)
            
            for i, col in enumerate(columns):
                x_pos = x + COLUMN_SPACING + (i * column_width) + (column_width // 2)
                text = font.render(col, True, BLACK)
                text_rect = text.get_rect(center=(x_pos, header_y))
                
                # Only draw column header if it's within content rect
                if text_rect.bottom > content_rect.top and text_rect.top < content_rect.bottom:
                    clip_rect = text_rect.clip(content_rect)
                    if clip_rect.width > 0 and clip_rect.height > 0:
                        screen.blit(text, clip_rect, 
                                  (max(0, content_rect.left - text_rect.left),
                                   max(0, content_rect.top - text_rect.top),
                                   clip_rect.width,
                                   clip_rect.height))
            
            # Draw separator line under headers
            separator_rect = pygame.Rect(x, header_y + 25, card_width, 1)
            
            # Only draw separator line if it's within content rect
            if separator_rect.bottom > content_rect.top and separator_rect.top < content_rect.bottom:
                clip_rect = separator_rect.clip(content_rect)
                if clip_rect.width > 0 and clip_rect.height > 0:
                    pygame.draw.rect(screen, BLACK, clip_rect)
            
            # Draw action data with smaller font
            start_y = header_y + 35
            for idx, action in enumerate(card.action):
                values = [str(action.state)] + [str(v) for v in action.action]
                for i, value in enumerate(values):
                    x_pos = x + COLUMN_SPACING + (i * column_width) + (column_width // 2)
                    text = small_font.render(value, True, BLACK)
                    text_rect = text.get_rect(center=(x_pos, start_y + (idx * ROW_HEIGHT)))
                    
                    # Only draw action data if it's within content rect
                    if text_rect.bottom > content_rect.top and text_rect.top < content_rect.bottom:
                        clip_rect = text_rect.clip(content_rect)
                        if clip_rect.width > 0 and clip_rect.height > 0:
                            screen.blit(text, clip_rect, 
                                      (max(0, content_rect.left - text_rect.left),
                                       max(0, content_rect.top - text_rect.top),
                                       clip_rect.width,
                                       clip_rect.height))
        else:
            # Draw "ADD NEW CARD" text
            font = pygame.font.Font(None, 36)
            text = font.render("ADD NEW CARD", True, BLACK)
            text_rect = text.get_rect(center=(x + card_width//2, y + card_height//2))
            
            # Only draw text if it's within content rect
            if text_rect.bottom > content_rect.top and text_rect.top < content_rect.bottom:
                clip_rect = text_rect.clip(content_rect)
                if clip_rect.width > 0 and clip_rect.height > 0:
                    screen.blit(text, clip_rect, 
                              (max(0, content_rect.left - text_rect.left),
                               max(0, content_rect.top - text_rect.top),
                               clip_rect.width,
                               clip_rect.height))
    
    return rect

def draw_home_screen(screen):
    """Draw the home screen with level selection buttons"""
    # Font setup
    pygame.font.init()
    font = pygame.font.Font(None, 36)
    
    # Get all level folders
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    level_folders = [f for f in os.listdir(data_path) if f.startswith('level') and os.path.isdir(os.path.join(data_path, f))]
    level_folders.sort()
    
    # Calculate layout
    start_x = (screen.get_width() - (len(level_folders) * (BUTTON_WIDTH + PADDING))) // 2
    start_y = screen.get_height() // 2 - BUTTON_HEIGHT // 2
    
    # Store rectangles for click detection
    level_rects = {}
    
    # Draw each level button
    for i, folder in enumerate(level_folders):
        level_num = folder.replace('level', '')
        x = start_x + i * (BUTTON_WIDTH + PADDING)
        rect = pygame.Rect(x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        pygame.draw.rect(screen, GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        
        text = font.render(level_num, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        
        level_rects[folder] = rect
    
    return level_rects

def draw_level_interface(screen, level, active_tab="INFO"):
    """Draw the level interface with header and tabs"""
    # Font setup
    title_font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)
    text_font = pygame.font.Font(None, 24)
    
    # Draw level title (top left)
    level_text = f"Level {level.level_id}"
    level_surface = title_font.render(level_text, True, BLACK)
    screen.blit(level_surface, (PADDING, PADDING))
    
    # Draw HOME button (top right)
    home_rect = pygame.Rect(screen.get_width() - BUTTON_WIDTH - PADDING, 
                          PADDING, 
                          BUTTON_WIDTH, 
                          BUTTON_HEIGHT)
    pygame.draw.rect(screen, GRAY, home_rect)
    pygame.draw.rect(screen, BLACK, home_rect, 2)
    home_text = button_font.render("HOME", True, BLACK)
    home_text_rect = home_text.get_rect(center=home_rect.center)
    screen.blit(home_text, home_text_rect)
    
    # Draw tabs
    tabs = ["INFO", "CARDS", "TESTS"]
    tab_width = (screen.get_width() - 2 * PADDING) // len(tabs)
    tab_rects = {}
    
    for i, tab in enumerate(tabs):
        tab_rect = pygame.Rect(PADDING + i * tab_width, 
                             screen.get_height() - TAB_HEIGHT - PADDING,
                             tab_width - TAB_PADDING,
                             TAB_HEIGHT)
        
        # Highlight active tab
        color = LIGHT_BLUE if tab == active_tab else GRAY
        pygame.draw.rect(screen, color, tab_rect)
        pygame.draw.rect(screen, BLACK, tab_rect, 2)
        
        tab_text = button_font.render(tab, True, BLACK)
        tab_text_rect = tab_text.get_rect(center=tab_rect.center)
        screen.blit(tab_text, tab_text_rect)
        
        tab_rects[tab] = tab_rect
    
    # Draw content area
    content_rect = pygame.Rect(PADDING,
                             PADDING + BUTTON_HEIGHT + PADDING,
                             screen.get_width() - 2 * PADDING,
                             screen.get_height() - 3 * PADDING - BUTTON_HEIGHT - TAB_HEIGHT)
    pygame.draw.rect(screen, WHITE, content_rect)
    pygame.draw.rect(screen, BLACK, content_rect, 2)
    
    # Draw content based on active tab
    if active_tab == "INFO":
        description = level.get_problem_description()
        # Wrap text to fit in content area
        words = description.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            text = ' '.join(current_line)
            if text_font.size(text)[0] > content_rect.width - 20:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate total content height
        total_height = len(lines) * text_font.get_linesize()
        
        # Create or update scrollable area
        if not hasattr(draw_level_interface, 'info_scroll'):
            draw_level_interface.info_scroll = ScrollableArea(content_rect, total_height)
            draw_level_interface.info_scroll.editor = level.editor
        elif draw_level_interface.info_scroll.content_height != total_height:
            # Only update if content height changed
            scroll_y = draw_level_interface.info_scroll.scroll_y
            draw_level_interface.info_scroll = ScrollableArea(content_rect, total_height)
            draw_level_interface.info_scroll.editor = level.editor
            draw_level_interface.info_scroll.scroll_y = scroll_y
            draw_level_interface.info_scroll.update_scrollbar()
        
        # Draw wrapped text
        y = content_rect.top + 10 - draw_level_interface.info_scroll.scroll_y
        for line in lines:
            if content_rect.top <= y <= content_rect.bottom:
                text_surface = text_font.render(line, True, BLACK)
                screen.blit(text_surface, (content_rect.left + 10, y))
            y += text_font.get_linesize()
        
        draw_level_interface.info_scroll.draw(screen)
        return home_rect, tab_rects, None, draw_level_interface.info_scroll
    
    elif active_tab == "CARDS":
        cards = level.get_cards()
        card_rects = []
        
        # Calculate card layout
        usable_width = content_rect.width - 2 * CARD_PADDING - SCROLLBAR_WIDTH
        card_width = (usable_width - CARD_PADDING) // CARDS_PER_ROW
        
        # Calculate total content height
        total_height = CARD_PADDING  # Start with padding
        current_row_max_height = 0
        row_heights = []
        
        # Calculate heights for each row
        for i, card in enumerate(cards):
            _, card_height = calculate_card_size(card, text_font)
            if i % CARDS_PER_ROW == 0:  # New row
                if current_row_max_height > 0:
                    row_heights.append(current_row_max_height)
                current_row_max_height = card_height
            else:
                current_row_max_height = max(current_row_max_height, card_height)
                
        # Add last row height
        if current_row_max_height > 0:
            row_heights.append(current_row_max_height)
        
        # Add height for "Add New Card" if needed
        if len(cards) % CARDS_PER_ROW == 0:
            row_heights.append(MIN_CARD_HEIGHT)
        
        # Calculate total height
        total_height = CARD_PADDING + sum(row_heights) + (len(row_heights) * CARD_PADDING)
        
        # Create or update scrollable area
        if not hasattr(draw_level_interface, 'cards_scroll'):
            draw_level_interface.cards_scroll = ScrollableArea(content_rect, total_height)
            draw_level_interface.cards_scroll.editor = level.editor
        elif draw_level_interface.cards_scroll.content_height != total_height:
            # Only update if content height changed
            scroll_y = draw_level_interface.cards_scroll.scroll_y
            draw_level_interface.cards_scroll = ScrollableArea(content_rect, total_height)
            draw_level_interface.cards_scroll.editor = level.editor
            draw_level_interface.cards_scroll.scroll_y = scroll_y
            draw_level_interface.cards_scroll.update_scrollbar()
        
        # Draw existing cards
        current_y = content_rect.top + CARD_PADDING - draw_level_interface.cards_scroll.scroll_y
        for i, card in enumerate(cards):
            row = i // CARDS_PER_ROW
            col = i % CARDS_PER_ROW
            
            x = content_rect.left + CARD_PADDING + col * (card_width + CARD_PADDING)
            y = current_y
            
            if col == 0 and i > 0:  # Start of new row
                current_y += row_heights[row-1] + CARD_PADDING
                y = current_y
            
            card_rect = draw_card(screen, x, y, card, content_rect, card_width)
            if card_rect and card_rect.bottom > content_rect.top and card_rect.top < content_rect.bottom:
                card_rects.append((card_rect, card))
        
        # Draw "Add New Card" card
        if len(cards) % CARDS_PER_ROW == 0:
            current_y += (row_heights[-2] if row_heights else 0) + CARD_PADDING
        x = content_rect.left + CARD_PADDING + (len(cards) % CARDS_PER_ROW) * (card_width + CARD_PADDING)
        new_card_rect = draw_card(screen, x, current_y, None, content_rect, card_width)
        if new_card_rect and new_card_rect.bottom > content_rect.top and new_card_rect.top < content_rect.bottom:
            card_rects.append((new_card_rect, None))
        
        draw_level_interface.cards_scroll.draw(screen)
        return home_rect, tab_rects, card_rects, draw_level_interface.cards_scroll
    
    return home_rect, tab_rects, None, None