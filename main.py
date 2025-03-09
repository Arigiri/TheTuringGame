from constant import *  # Import all constants
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from animation import CardEditor, TestRunner
from Class.level import Level as LevelLogic
from Class.card import Card
from Class.test import Test

class Level:
    def __init__(self, level_id, problem_data, cards):
        self.level_id = level_id
        self.name = f"level{self.level_id}"
        self.logic = LevelLogic(level_id)
        self.problem_data = problem_data
        self.cards = self.logic.cards
        self.states = self.logic.get_state()
        self.transitions = self.extract_transitions()

    def add_card(self, card):
        print('added')
        self.logic.cards.append(card)
    
    def sort_cards(self, cards):
        return sorted(cards, key=lambda x: x.card_id)
        
    def extract_states(self):
        states = set()
        # Add states from problem description
        if isinstance(self.problem_data, dict):
            states.update([
                self.problem_data.get('initial_state', ''),
                self.problem_data.get('final_state', '')
            ])
        
        # Add states from cards
        for card in self.cards:
            for action in card.action:
                if isinstance(action, dict):
                    states.add(action.get('state', ''))
                    if isinstance(action.get('action'), list) and len(action['action']) > 2:
                        states.add(action['action'][2])  # next state
        
        # Remove empty states
        states.discard('')
        return sorted(list(states))
    
    def extract_transitions(self):
        transitions = set()
        for card in self.cards:
            for action in card.action:
               pass
        return transitions
    
    def get_cards(self):
        return self.cards
    
    def get_states(self):
        return self.states
    
    def get_transitions(self):
        return self.transitions
    
    def get_problem_description(self):
        return self.logic.get_problem_description()
    
    def get_max_cards(self):
        # Calculate maximum cards based on state transitions
        if not self.states:
            return 0
        
        # Maximum cards is the number of unique state transitions needed
        return len(self.transitions) if self.transitions else len(self.states)
    
    def get_available_card_ids(self):
        used_ids = {card.card_id for card in self.cards}
        max_id = max(used_ids) if used_ids else 0
        available_ids = set(range(1, max_id + 2)) - used_ids
        return sorted(list(available_ids))
    
    def get_next_card_id(self):
        return len(self.cards) + 1

class TuringGame(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("The Turing Game")
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")

        # Colors now come from constants
        self.WHITE = WHITE
        self.BLACK = BLACK
        self.GRAY = GRAY
        self.DARK_GRAY = DARK_GRAY
        self.LIGHT_BLUE = LIGHT_BLUE
        self.LIGHT_GRAY = LIGHT_GRAY
        self.LIGHT_RED = LIGHT_RED

        # Constants from the constants file
        self.PADDING = PADDING
        self.BUTTON_HEIGHT = BUTTON_HEIGHT
        self.TAB_HEIGHT = TAB_HEIGHT

        # Setup styles - THIS LINE WAS MISSING
        self.setup_styles()

        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.current_level = None

        self.compute_max_cards_per_row()
            
        print('max_card_each_row', self.max_card_each_row)
        
        # Initialize home screen
        self.show_home_screen()

    def compute_max_cards_per_row(self):
        """Computes the maximum number of cards that can fit in a single row based on window width."""
        # Get window width
        self.update_idletasks()  # Make sure window geometry is updated
        window_width = self.winfo_width()
        
        # If window hasn't been drawn yet, use a default width
        if (window_width <= 1):
            window_width = 800  # Default window width
        
        # Estimate card width including padding
        estimated_card_width = 300  # Base estimate for card width in pixels
        
        # Calculate max cards per row (minimum 1, maximum 6)
        available_width = window_width - 40  # Subtract some padding
        max_cards = max(1, min(6, available_width // estimated_card_width))
        
        print(f"Window width: {window_width}, Estimated card width: {estimated_card_width}")
        print(f"Calculated max cards per row: {max_cards}")
        
        self.max_card_each_row = max_cards
        
        # Add a binding to recalculate when window is resized
        self.bind("<Configure>", self.on_window_resize)

    def on_window_resize(self, event):
        """Recalculate max cards per row when window is resized."""
        # Only respond to changes in the main window, not child widgets
        if event.widget == self:
            old_max = self.max_card_each_row
            self.compute_max_cards_per_row()
            
            # Only refresh if the value actually changed
            if old_max != self.max_card_each_row and hasattr(self, 'notebook'):
                current_tab = self.notebook.select()
                if current_tab and len(self.notebook.tabs()) > 1:
                    tab_name = self.notebook.tab(current_tab, "text")
                    if tab_name == "Cards":
                        cards_tab = self.notebook.nametowidget(current_tab)
                        self.setup_cards_tab(cards_tab)
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure(
            "Card.TFrame",
            background=self.LIGHT_GRAY,
            relief="raised",
            borderwidth=1
        )
        style.configure(
            "CardHeader.TLabel",
            font=("Arial", 12, "bold")
        )
        style.configure(
            "Title.TLabel",
            font=("Arial", 16, "bold")
        )
        style.configure(
            "Passed.TButton",
            background="#90EE90",  # Light green for better contrast
            foreground="black"     # Black text for better readability
        )
        style.configure(
            "Failed.TButton",
            background="#FFB6C1",  # Light red for better contrast
            foreground="black"     # Black text for better readability
        )
        style.configure(
            "Action.TFrame",
            background="white"
        )

    def get_level_cards(self, level_path):
        cards = []
        card_dir = os.path.join(level_path, "card")
        
        if os.path.exists(card_dir):
            for card_file in sorted(os.listdir(card_dir)):
                if card_file.endswith('.json'):
                    card_path = os.path.join(card_dir, card_file)
                    try:
                        with open(card_path, 'r') as f:
                            card_data = json.load(f)
                            cards.append(card_data)
                    except Exception as e:
                        messagebox.showerror(
                            "Error", 
                            f"Error reading card {card_file}: {str(e)}"
                        )
        return cards

    def get_problem_description(self, level_path):
        problem_file = os.path.join(
            level_path, 
            "problems_description.json"
        )
        print('problem_file', problem_file)
        if os.path.exists(problem_file):
            try:
                with open(problem_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"Error reading problem description: {str(e)}"
                )
        return None

    def load_level(self, level_name):
        level_path = os.path.join("data", level_name)
        print('level_path', level_path)
        if not os.path.exists(level_path):
            raise Exception(f"Level {level_name} not found")

        # Load problem description first
        problem_data = self.get_problem_description(level_path)
        if not problem_data:
            raise Exception("No problem description found")

        # Load all cards
        cards = self.get_level_cards(level_path)
        level_id = problem_data['level_id']
        # Create level instance with all data
        self.current_level = Level(
            level_id,
            problem_data,
            cards
        )

    def get_available_levels(self):
        levels = []
        data_dir = "data"
        
        if os.path.exists(data_dir):
            for item in os.listdir(data_dir):
                if os.path.isdir(os.path.join(data_dir, item)) and item.startswith("level"):
                    levels.append(item)
        
        # Sort numerically by level number instead of alphabetically
        return sorted(levels, key=lambda x: int(x.replace("level", "")))

    def show_home_screen(self):
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create title
        title = ttk.Label(
            self.main_container,
            text="Select a Level",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)
        
        # Calculate how many buttons can fit in a row
        self.update_idletasks()
        window_width = self.winfo_width()
        button_width = 120  # Approximate width of each button in pixels
        button_padding = 10  # Padding between buttons
        buttons_per_row = max(1, (window_width - 40) // (button_width + button_padding))
        
        # Create a frame for the grid of level buttons
        grid_frame = ttk.Frame(self.main_container)
        grid_frame.pack(expand=True, fill=tk.BOTH, padx=20)
        
        # Configure grid columns to have equal weight
        for i in range(buttons_per_row):
            grid_frame.columnconfigure(i, weight=1)
        
        # Add level buttons in a grid layout
        levels = self.get_available_levels()
        row, col = 0, 0
        
        for level in levels:
            level_name = level.replace('level', '')
            
            # Check if all tests for this level are passed
            level_completed = self.is_level_completed(level)
            
            # Create a frame for this level button and checkmark
            level_frame = ttk.Frame(grid_frame)
            level_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Add button
            btn_text = f"Level {level_name}"
            
            # Configure button style
            if level_completed:
                button_style = "Completed.TButton"
                btn_text = f"✓ {btn_text}"
            else:
                button_style = "TButton"
            
            # Create the button
            btn = ttk.Button(
                level_frame,
                text=btn_text,
                command=lambda l=level: self.start_level(l),
                width=15
            )
            btn.pack(side=tk.LEFT)
            
            # Add separate checkmark label for completed levels
            
            # Move to next column or row as needed
            col += 1
            if col >= buttons_per_row:
                col = 0
                row += 1

    def start_level(self, level_name):
        try:
            self.load_level(level_name)
            self.show_level_screen()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.show_home_screen()

    def show_level_screen(self):
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create header
        header = ttk.Frame(self.main_container)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        # Add back button
        back_btn = ttk.Button(
            header,
            text="Back to Home",
            command=self.show_home_screen
        )
        back_btn.pack(side=tk.LEFT)
        
        # Add level title
        title = ttk.Label(
            header,
            text=f"Level {self.current_level.name}",
            font=("Arial", 16, "bold")
        )
        title.pack(side=tk.LEFT, padx=20)
        
        # Setup tabs
        self.setup_tabs()

    def setup_tabs(self):
        # Create notebook
        self.notebook = ttk.Notebook(self.main_container)
        
        # Create tabs
        info_tab = ttk.Frame(self.notebook)
        cards_tab = ttk.Frame(self.notebook)
        tests_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(info_tab, text="Info")
        self.notebook.add(cards_tab, text="Cards")
        self.notebook.add(tests_tab, text="Tests")
        
        # Setup content for each tab
        self.setup_info_tab(info_tab)
        self.setup_cards_tab(cards_tab)
        self.setup_tests_tab(tests_tab)
        
        self.notebook.pack(expand=True, fill=tk.BOTH)

    def setup_info_tab(self, tab):
        # Add problem description
        desc_label = ttk.Label(
            tab,
            text=self.current_level.get_problem_description(),
            wraplength=600,
            font=("Arial", 12)
        )
        desc_label.pack(pady=20)

    def setup_cards_tab(self, tab):
        for widget in tab.winfo_children():
            widget.destroy()
        # Add header
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            header_frame,
            text="+ Add New Card",
            command=lambda: self.show_card_editor(create_card=True)
        ).pack(side=tk.RIGHT)

        # Create scrollable frame for cards
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create cards container
        cards_frame = ttk.Frame(scrollable_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Display existing cards
        row = 0
        col = 0
        cards = self.current_level.get_cards()
        
        for card in cards:
            card_frame = self.create_card_frame(cards_frame, card)
            card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            col += 1
            if col >= self.max_card_each_row:  # 2 cards per row
                col = 0
                row += 1

        # Configure grid
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_card_frame(self, parent, card):
        # Card container
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        
        # Header with card ID
        header = ttk.Frame(card_frame)
        header.pack(fill=tk.X, padx=5, pady=5)
      
        # Card title
        card_title = ttk.Label(
            header,
            text=f"Card {card.card_id}",
            style="CardHeader.TLabel"
        )
        card_title.pack(side=tk.LEFT)
        
        # Add edit button
        edit_btn = ttk.Button(
            header,
            text="Edit",
            command=lambda c=card: self.show_card_editor(c)
        )
        edit_btn.pack(side=tk.RIGHT)
        
        # Add delete button
        delete_btn = ttk.Button(
            header,
            text="Delete",
            command=lambda c=card: self.delete_card(c)
        )
        delete_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Add card content display
        content_frame = ttk.Frame(card_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure column widths for consistent alignment - REDUCED WIDTH
        for i in range(4):
            content_frame.columnconfigure(i, weight=1, minsize=60)  # Reduced from 80 to 60
        
        # Create a table for actions
        headers = ["Read", "Write", "Move", "Next"]  # Shortened "Next Card" to "Next"
        for i, header_text in enumerate(headers):
            header_label = ttk.Label(content_frame, text=header_text, font=("Arial", 9, "bold"))
            header_label.grid(row=0, column=i, padx=3, pady=2, sticky="w")  # Reduced padx from 5 to 3
        
        # Add separator
        separator = ttk.Separator(content_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=4, sticky="ew", pady=2)
        
        # Add actions
        for i, action in enumerate(card.action):
            # Add each part of the action directly in the content frame
            for j, component in enumerate(action.action):
                value = component
                # Convert -1 to "HALT" for better readability
                if j == 3 and value == '-1':
                    value = "HALT"
                # Convert movement codes to readable text
                if j == 2:
                    if value == '-1':
                        value = "←"
                    elif value == '0':
                        value = "-"
                    elif value == '1':
                        value = "→"
                
                cell_label = ttk.Label(
                    content_frame, 
                    text=str(value), 
                    width=6,  # Reduced from 8 to 6
                    anchor="center"
                )
                cell_label.grid(row=i+2, column=j, padx=3, pady=2, sticky="w")  # Reduced padx from 5 to 3
        
        return card_frame

    def setup_tests_tab(self, tab):
        """Setup the tests tab with test cases in a grid layout"""
        # Clear existing content
        for widget in tab.winfo_children():
            widget.destroy()
            
        # Create main frame for tests tab
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add title
        title_label = ttk.Label(main_frame, text="Test Cases", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Create test instance if it doesn't exist
        if not hasattr(self, 'test_instance'):
            self.test_instance = Test(self.current_level.level_id)
        else:
            # Make sure we have the correct test instance for current level
            if hasattr(self, 'current_level') and self.test_instance.level_id != self.current_level.level_id:
                self.test_instance = Test(self.current_level.level_id)
        
        # Make sure passed tests are loaded
        self.test_instance.load_passed_tests()
        
        # Calculate how many buttons can fit in a row
        self.update_idletasks()
        window_width = self.winfo_width()
        button_width = 120  # Approximate width of each button in pixels
        button_padding = 10  # Padding between buttons
        buttons_per_row = max(1, (window_width - 40) // (button_width + button_padding))
        
        # Create scrollable canvas for tests grid
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        tests_frame = ttk.Frame(canvas)
        
        tests_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=tests_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add mouse wheel scrolling
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        # Define custom styles for test buttons
        style = ttk.Style()
        style.configure("Passed.TButton", background="#90EE90", foreground="black")
        style.map("Passed.TButton", background=[("active", "#70DA70")])
        
        # Add test buttons in a grid layout
        row, col = 0, 0
        for test in self.test_instance.tests:
            test_id = test['id']
            
            # Check if test is passed
            is_passed = self.test_instance.is_test_passed(test_id)
            
            # Choose style based on test status
            button_style = "Passed.TButton" if is_passed else "TButton"
            
            # Add checkmark for passed tests
            button_text = f"✓ Test {test_id}" if is_passed else f"Test {test_id}"
            
            # Create button with custom style based on test status
            test_button = ttk.Button(
                tests_frame,
                text=button_text,
                command=lambda t=test: self.show_test_runner(t),
                width=12,
                style=button_style
            )
            test_button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Force style for passed tests
            if is_passed:
                test_button.configure(style="Passed.TButton")
            
            # Increment column and check if we need to wrap to next row
            col += 1
            if col >= buttons_per_row:
                col = 0
                row += 1
        
        # Configure grid columns to have equal weight
        for i in range(buttons_per_row):
            tests_frame.columnconfigure(i, weight=1)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_test_runner(self, test_data):
        """Show the test runner screen"""
        TestRunner(self, test_data, self.current_level)

    def show_card_editor(self, card=None, create_card=False):
        # Create a new card object but don't add it to the level yet
        if create_card:
            new_card = Card(
                self.current_level.level_id,
                self.current_level.get_next_card_id(),
                self.current_level.get_states()
            )
            card = new_card
            # Note: We're not adding to self.current_level.add_card(card) here anymore
        
        available_ids = self.current_level.get_available_card_ids()
        next_id = self.current_level.get_next_card_id()
        editor = CardEditor(
            self,
            card=card,
            level=self.current_level,
            states=self.current_level.get_states(),
            available_ids=available_ids,
            next_id=next_id,
            is_new_card=create_card  # Pass this flag to the editor
        )
        editor.grab_set()

    def mark_test_completed(self, test_id):
        """Mark a test as completed in the UI and save its status"""
        print(f"Marking test {test_id} as completed")
        
        # Make sure test instance exists and matches current level
        if not hasattr(self, 'test_instance') or self.test_instance is None:
            level_id = self.current_level.level_id
            self.test_instance = Test(level_id)
        elif hasattr(self, 'current_level') and self.test_instance.level_id != self.current_level.level_id:
            self.test_instance = Test(self.current_level.level_id)
            
        # Save the completion status
        self.test_instance.mark_test_passed(test_id)
        
        # Refresh the tests tab to update UI
        if hasattr(self, 'notebook'):
            test_tab_idx = 2  # Assuming tests tab is the third tab (index 2)
            if test_tab_idx < len(self.notebook.tabs()):
                test_tab = self.notebook.nametowidget(self.notebook.tabs()[test_tab_idx])
                self.setup_tests_tab(test_tab)
                
        print(f"Test {test_id} marked as completed and UI updated")

    def is_level_completed(self, level_name):
        """Check if all tests for a level have been passed"""
        try:
            # Extract level number from name
            level_id = int(level_name.replace("level", ""))
            
            # Create a test instance to check completion
            test_instance = Test(level_id)
            
            # Explicitly load passed tests
            test_instance.load_passed_tests()
            
            # Convert all test IDs to integers for consistent comparison
            all_test_ids = {int(test.get('id')) for test in test_instance.tests}
            passed_test_ids = {int(test_id) for test_id in test_instance.passed_tests}
            
            # Debug output
            print(f"Level {level_id}:")
            print(f"  - All tests: {all_test_ids}")
            print(f"  - Passed tests: {passed_test_ids}")
            
            # Check if all tests are passed
            if len(all_test_ids) == 0:
                return False
                
            is_completed = all_test_ids.issubset(passed_test_ids)
            print(f"  - Level completed: {is_completed}")
            return is_completed
        except Exception as e:
            print(f"Error checking level completion: {e}")
            import traceback
            traceback.print_exc()
            return False

    def delete_card(self, card):
        """Delete a card if it's not referenced by other cards"""
        # Check if card is referenced by other cards
        if not self.can_delete_card(card):
            messagebox.showwarning(
                "Cannot Delete Card",
                f"Card {card.card_id} cannot be deleted because it is referenced by other cards."
            )
            return
            
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete Card {card.card_id}?"
        )
        
        if not confirm:
            return
        
        # Get the card ID that will be deleted
        deleted_id = card.card_id
        
        # Delete the card from memory
        self.current_level.logic.cards.remove(card)
        
        # Remove the card file from disk
        card_path = os.path.join('data', f'level{self.current_level.level_id}', 'card', f'c{deleted_id}.json')
        if os.path.exists(card_path):
            os.remove(card_path)
        
        # Update references in other cards and renumber cards
        self.update_card_ids_after_deletion(deleted_id)
        
        # Refresh cards tab
        cards_tab = self.notebook.nametowidget(self.notebook.tabs()[1])
        self.setup_cards_tab(cards_tab)
        
        messagebox.showinfo(
            "Card Deleted",
            f"Card {deleted_id} deleted successfully. Card IDs have been updated."
        )

    def can_delete_card(self, card):
        """Check if a card can be deleted (not referenced by other cards)"""
        card_id = card.card_id
        
        # Check all cards for references to this card
        for other_card in self.current_level.logic.cards:
            if other_card.card_id == card_id:
                continue  # Skip the card itself
            
            for action in other_card.action:
                # Check if this action references the card to delete
                if action.action[3] and int(action.action[3]) == card_id:
                    return False  # Card is referenced
        
        return True

    def update_card_ids_after_deletion(self, deleted_id):
        """Update card IDs and references after a card is deleted"""
        # Sort cards by ID
        cards = sorted(self.current_level.logic.cards, key=lambda c: c.card_id)
        
        # Track which cards need saving due to reference changes
        cards_to_save = set()
        
        # First update all references to higher card IDs
        for card in cards:
            for action in card.action:
                if len(action.action) >= 4 and action.action[3]:
                    next_card_id = int(action.action[3])
                    if next_card_id > deleted_id:
                        # This reference points to a card that needs to be renumbered
                        action.action[3] = str(next_card_id - 1)
                        cards_to_save.add(card)
                        # print(card.card_id)
        
        # Now update the card IDs sequentially starting from 1
        for i, card in enumerate(cards):
            new_id = i + 1 # New sequential ID (1-based)
            
            # Only update cards if their ID needs to change
            if card.card_id != new_id:
                old_id = card.card_id
                
                # Update the card ID
                card.card_id = new_id
                
                # Save the card with its new ID
                new_path = os.path.join('data', f'level{self.current_level.level_id}', 'card', f'c{new_id}.json')
                card.save_card(new_path)
                
                # Delete the old file if needed
                old_path = os.path.join('data', f'level{self.current_level.level_id}', 'card', f'c{old_id}.json')
                if os.path.exists(old_path) and old_path != new_path:
                    os.remove(old_path)
                
                # Remove from the set as it's already been saved
                if card in cards_to_save:
                    cards_to_save.remove(card)
        
        # Save any remaining cards that had reference changes but no ID changes
        for card in cards_to_save:
            save_path = os.path.join('data', f'level{self.current_level.level_id}', 'card', f'c{card.card_id}.json')
            card.save_card(save_path)

def main():
    app = TuringGame()
    app.mainloop()

if __name__ == "__main__":
    main()