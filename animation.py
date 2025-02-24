import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from Class.card import Card, Action

class CardEditor(tk.Toplevel):
    def __init__(self, parent, card=None, level=None, states=None, available_ids=None, next_id=None):
        super().__init__(parent)
        self.title("Card Editor")
        self.geometry("600x400")
        
        self.parent = parent
        self.card = card
        self.level = level
        self.states = states or []
        self.available_ids = available_ids or []
        self.next_id = next_id
        
        self.next_card_var = tk.StringVar(value="")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add card ID selection
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(id_frame, text="Card ID:").pack(side=tk.LEFT)
        
        # Use available IDs for new cards, or current ID for existing cards
        current_id = self.card.card_id if self.card else self.next_id
        
        self.card_id_var = tk.StringVar(value=str(current_id))
        self.card_id_combo = ttk.Combobox(
            id_frame,
            textvariable=self.card_id_var,
            values=self.available_ids if not self.card else [current_id],
            width=10,
            state="readonly" if self.card else "normal"
        )
        self.card_id_combo.pack(side=tk.LEFT, padx=5)
        
        # Create table header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        headers = ["Read", "Write", "Move", "Next Card"]
        for col, header in enumerate(headers):
            ttk.Label(
                header_frame,
                text=header,
                width=13,
                font=("Arial", 10, "bold"),
                anchor="center"
            ).grid(row=0, column=col, padx=2)
        
        # Create scrollable frame for actions
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add actions
        self.action_rows = []
        if self.card:
            for action in self.card.action:
                self.add_action_row(action)
        else:
            self.add_action_row()  # Add one empty row for new card
        
        # Add action buttons
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add save/cancel buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            bottom_frame,
            text="Save",
            command=self.save_card
        ).pack(side=tk.BOTTOM, padx=5)
        
        ttk.Button(
            bottom_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side=tk.BOTTOM)

    def add_action_row(self, action=None):
        """Adds a row of widgets representing an action to the UI.

        Args:
            action (optional): The action object containing initial values.
        """
        row = len(self.action_rows)
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, pady=2)
        
        # State (Fixed value, displayed as a Label)
        state_value = action.get_state() if action else ''
        state_label = ttk.Label(frame, text=state_value, width=13, anchor="center")
        state_label.grid(row=0, column=0, padx=2)
        
        # Write value
        write_var = tk.StringVar(
            value=action.get_value() if action else ''
        )
        write_entry = ttk.Entry(
            frame,
            textvariable=write_var,
            width=15
        )
        write_entry.grid(row=0, column=1, padx=2)
        
        # Move direction
        move_var = tk.StringVar(
            value=action.get_direction() if action else ''
        )
        move_combo = ttk.Combobox(
            frame,
            textvariable=move_var,
            values=['-1', '1', '0'],  # Left, Right, Stay
            width=15,
            state="readonly"
        )
        move_combo.grid(row=0, column=2, padx=2)
        
        # Next state
        next_state_var = tk.StringVar(
            value=action.get_next_state() if action else ''
        )
        next_state_combo = ttk.Combobox(
            frame,
            textvariable=next_state_var,
            values= list(range(1, len(self.level.cards) + 1)),
            width=15
        )
        next_state_combo.grid(row=0, column=3, padx=2)
        
        self.action_rows.append({
            'frame': frame,
            'state': state_value,  # Fixed value instead of a variable
            'write': write_var,
            'move': move_var,
            'next_state': next_state_var
        })

    def save_card(self):
        try:
            # Validate card ID
            card_id = self.card_id_var.get().strip()
            print('card_id', card_id)
            if not card_id:
                raise ValueError("Card ID is required")


            # Collect actions
            actions = []
            for row in self.action_rows:
                state = row['state']  # Fixed value, no .get()
                write = row['write'].get().strip()
                move = row['move'].get().strip()
                next_state = row['next_state'].get().strip()

                if not all([state, write, move, next_state]):
                    raise ValueError("All fields in each action row are required")

                actions.append(Action(state, [state, write, move, next_state]))

            # Create Card instance
            card = self.card
            card.action = actions

            # Check if level name exists
            if not hasattr(self.parent.current_level, 'name'):
                raise ValueError("Invalid level data")

            # Save to file
            card_path = os.path.join(
                'data',
                self.parent.current_level.name,
                'card',
                f'c{card_id}.json'
            )

            card.save_card(card_path)

            self.destroy()
            print("self.parent.notebook.select()", self.parent.notebook.select())
            # self.parent.setup_cards_tab((self.parent.notebook.select()))
            current_tab = self.parent.notebook.nametowidget(self.parent.notebook.select())
            self.parent.setup_cards_tab(current_tab)


        except Exception as e:
            messagebox.showerror("Error", str(e))
