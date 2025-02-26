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
        used_ids = {card.card_id for card in self.cards}
        return max(used_ids) + 1 if used_ids else 1

class TuringGame(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("The Turing Game")
        self.geometry("800x600")

        # Colors
        self.WHITE = "#FFFFFF"
        self.BLACK = "#000000"
        self.GRAY = "#C8C8C8"
        self.DARK_GRAY = "#646464"
        self.LIGHT_BLUE = "#6496FF"
        self.LIGHT_GRAY = "#E6E6E6"
        self.LIGHT_RED = "#FF6464"

        # Setup styles
        self.setup_styles()

        # Constants
        self.PADDING = 50
        self.BUTTON_HEIGHT = 50
        self.TAB_HEIGHT = 50

        # Initialize variables

        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.current_level = None

        self.compute_max_cards_per_row()
            
        print('max_card_each_row', self.max_card_each_row)
        
        # Initialize home screen
        self.show_home_screen()

    def compute_max_cards_per_row(self):
        """Computes the maximum number of cards that can fit in a single row."""
        self.max_card_each_row = 4

    
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
            background="green",
            foreground="white"
        )
        style.configure(
            "Failed.TButton",
            background="red",
            foreground="white"
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
                if os.path.isdir(os.path.join(data_dir, item)):
                    levels.append(item)
        
        return sorted(levels)

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
        
        # Create buttons container
        buttons_frame = ttk.Frame(self.main_container)
        buttons_frame.pack(expand=True)
        
        # Add level buttons
        levels = self.get_available_levels()
        for level in levels:
            btn = ttk.Button(
                buttons_frame,
                text=f"Level {level}",
                command=lambda l=level: self.start_level(l)
            )
            btn.pack(pady=10)

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
        # Create card frame
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        
        # Add card title
        title_frame = ttk.Frame(card_frame)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = ttk.Label(
            title_frame, 
            text=f"Card {card.card_id}",
            font=("Arial", 10, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        edit_btn = ttk.Button(
            title_frame,
            text="Edit",
            command=lambda c=card: self.show_card_editor(c),
            width=8
        )
        edit_btn.pack(side=tk.RIGHT)

        # Create table for actions
        table_frame = ttk.Frame(card_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add headers
        headers = ["State", "Write", "Move", "Next"]
        for col, header in enumerate(headers):
            label = ttk.Label(
                table_frame,
                text=header,
                font=("Arial", 9, "bold")
            )
            label.grid(row=0, column=col, padx=2, pady=2)
            table_frame.grid_columnconfigure(col, weight=1)

        # Add actions
        for row, action in enumerate(card.action, start=1):
            # State
            ttk.Label(table_frame, text=action.get_state()).grid(
                row=row, column=0, padx=2, pady=2)
            # Write
            ttk.Label(table_frame, text=action.get_value()).grid(
                row=row, column=1, padx=2, pady=2)
            # Move
            ttk.Label(table_frame, text=action.get_direction()).grid(
                row=row, column=2, padx=2, pady=2)
            # Next State
            ttk.Label(table_frame, text=action.get_next_state()).grid(
                row=row, column=3, padx=2, pady=2)

        return card_frame

    def setup_tests_tab(self, tab):
        """Setup the tests tab with test cases"""
        # Create main frame for tests tab
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add title
        title_label = ttk.Label(main_frame, text="Test Cases", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Create test instance
        self.test_instance = Test(self.current_level.level_id)
        print(f"Created test instance for level {self.current_level.level_id}")
        
        # Create scrollable frame for test buttons
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add test buttons
        for test in self.test_instance.tests:
            test_id = test['id']
            test_frame = ttk.Frame(scrollable_frame)
            test_frame.pack(fill=tk.X, pady=5)
            
            # Create button with color based on test status
            button_style = "Passed.TButton" if self.test_instance.is_test_passed(test_id) else "Failed.TButton"
            test_button = ttk.Button(
                test_frame,
                text=f"Test - {test_id}",
                command=lambda t=test: self.show_test_runner(t),
                style=button_style
            )
            test_button.pack(fill=tk.X)
            print(f"Added button for Test {test_id}")
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_test_runner(self, test_data):
        """Show the test runner screen"""
        TestRunner(self, test_data, self.current_level)

    def show_card_editor(self, card=None, create_card=False):
        if create_card:
            card = Card(
                self.current_level.level_id,
                self.current_level.get_next_card_id(),
                self.current_level.get_states()
            )
            self.current_level.add_card(card)
        
        available_ids = self.current_level.get_available_card_ids()
        next_id = self.current_level.get_next_card_id()
        editor = CardEditor(
            self,
            card=card,
            level=self.current_level,
            states=self.current_level.get_states(),
            available_ids=available_ids,
            next_id=next_id
        )
        editor.grab_set()

def main():
    app = TuringGame()
    app.mainloop()

if __name__ == "__main__":
    main()