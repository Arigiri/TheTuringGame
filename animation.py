import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from Class.card import Card, Action
from constant import *  # Import all constants

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
            values= list(range(1, len(self.level.cards) + 1)) + [-1],
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
            print([action.action[2] for action in actions])
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

class TestRunner(tk.Toplevel):
    def __init__(self, parent, test_data, level):
        super().__init__(parent)
        self.title(f"Test Runner - Test {test_data['id']}")
        self.geometry(f"{TEST_RUNNER_WIDTH}x{TEST_RUNNER_HEIGHT}")
        
        self.test_data = test_data
        self.level = level
        self.input_tape = list(TAPE_PADDING_BEFORE * '_' + test_data['input'] + TAPE_PADDING_AFTER * '_')
        self.current_pos = TAPE_PADDING_BEFORE  # Start at first input character
        self.current_card = self.level.cards[0]  # Start with first card
        self.current_action_index = None  # Track current action index
        self.next_action = None  # Store next action to be executed
        self.speed_options = SPEED_OPTIONS
        self.speed_index = DEFAULT_SPEED_INDEX
        self.is_playing = False
        self.after_id = None
        
        print(f"Starting test with card {self.current_card.card_id}")
        self.setup_ui()
        self.find_next_action()  # Find first action on startup
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current card label
        self.card_label = ttk.Label(main_frame, text=f"Current Card: {self.current_card.card_id}")
        self.card_label.pack(pady=5)
        
        # Tape display frame
        self.tape_frame = ttk.Frame(main_frame)
        self.tape_frame.pack(fill=tk.X, pady=20)
        self.create_tape_display()
        
        # Card display frame
        card_display_frame = ttk.Frame(main_frame)
        card_display_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Add title for card actions
        ttk.Label(card_display_frame, text="Card Actions:", font=("Arial", 10, "bold")).pack(anchor="center")
        
        # Create scrollable frame for actions
        self.action_canvas = tk.Canvas(card_display_frame)
        scrollbar = ttk.Scrollbar(card_display_frame, orient="vertical", command=self.action_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.action_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.action_canvas.configure(scrollregion=self.action_canvas.bbox("all"))
        )
        
        self.action_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="center")
        self.action_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.action_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.update_card_display()
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=20)
        
        # Left side - Vertical buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(side=tk.LEFT, padx=20)
        
        self.pause_btn = ttk.Button(button_frame, text="Pause", command=self.pause)
        self.pause_btn.pack(pady=5)
        
        self.next_btn = ttk.Button(button_frame, text="Next", command=self.next_step)
        self.next_btn.pack(pady=5)
        
        self.play_btn = ttk.Button(button_frame, text="Play", command=self.play)
        self.play_btn.pack(pady=5)
        
        # Right side - Speed controls
        speed_frame = ttk.Frame(controls_frame)
        speed_frame.pack(side=tk.RIGHT, padx=20)
        
        left_btn = ttk.Button(speed_frame, text="←", width=3, command=self.decrease_speed)
        left_btn.pack(side=tk.LEFT, padx=5)
        
        self.speed_label = ttk.Label(speed_frame, text=f"{self.speed_options[self.speed_index]}x", width=6)
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        right_btn = ttk.Button(speed_frame, text="→", width=3, command=self.increase_speed)
        right_btn.pack(side=tk.LEFT, padx=5)
        
        # Back button
        back_btn = ttk.Button(main_frame, text="Back to Tests", command=self.destroy)
        back_btn.pack(side=tk.BOTTOM, pady=20)
        
    def update_card_display(self):
        """Update the card actions display"""
        # Clear existing actions
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Add header
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame, text="Read", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Write", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Direction", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Next Card", width=10).pack(side=tk.LEFT, padx=5)
        
        # Add each action
        for i, action in enumerate(self.current_card.action):
            action_frame = ttk.Frame(self.scrollable_frame)
            action_frame.pack(fill=tk.X, pady=2)
            
            # Determine if this is the current action
            is_current = (i == self.current_action_index)
            font_style = ("Arial", 10, "bold") if is_current else ("Arial", 10)
            bg_color = "#e6e6e6" if is_current else "white"
            
            # Create labels for each part of the action
            action_frame.configure(style="Action.TFrame")
            for value in action.action:
                label = ttk.Label(
                    action_frame,
                    text=str(value),
                    width=10,
                    font=font_style,
                    background=bg_color
                )
                label.pack(side=tk.LEFT, padx=5)
        
    def create_tape_display(self):
        # Clear existing tape cells
        for widget in self.tape_frame.winfo_children():
            widget.destroy()
            
        # Calculate visible range (show 15 cells centered on current position)
        start_pos = max(0, self.current_pos - 7)
        end_pos = min(len(self.input_tape), self.current_pos + 8)
        
        # Create cell frames
        for i in range(start_pos, end_pos):
            cell_frame = ttk.Frame(self.tape_frame, borderwidth=1, relief="solid")
            cell_frame.pack(side=tk.LEFT, padx=1)
            
            # Configure cell style based on position
            bg_color = "black" if i == self.current_pos else "white"
            fg_color = "white" if i == self.current_pos else "black"
            
            cell_label = ttk.Label(
                cell_frame,
                text=self.input_tape[i],
                width=2,
                anchor="center",
                background=bg_color,
                foreground=fg_color
            )
            cell_label.pack(padx=2, pady=2)
            
    def increase_speed(self):
        if self.speed_index < len(self.speed_options) - 1:
            self.speed_index += 1
            self.speed_label.config(text=f"{self.speed_options[self.speed_index]}x")
            
    def decrease_speed(self):
        if self.speed_index > 0:
            self.speed_index -= 1
            self.speed_label.config(text=f"{self.speed_options[self.speed_index]}x")
            
    def play(self):
        self.is_playing = True
        self.play_btn.state(['disabled'])
        self.next_btn.state(['disabled'])
        self.schedule_next_step()
        
    def pause(self):
        self.is_playing = False
        if self.after_id:
            self.after_cancel(self.after_id)
        self.play_btn.state(['!disabled'])
        self.next_btn.state(['!disabled'])
        
    def find_next_action(self):
        """Find the next action to be executed based on current position"""
        current_char = str(self.input_tape[self.current_pos])
        print(f"Finding next action for position {self.current_pos}, char: {current_char}, card: {self.current_card.card_id}")
        
        # Find matching action for current character
        self.next_action = None
        for i, action in enumerate(self.current_card.action):
            if str(action.action[0]) == str(current_char):
                self.next_action = (i, action)
                self.current_action_index = i
                self.update_card_display()
                print(f"Found next action: {action.action}")
                return True
                
        print(f"No matching action found for char {current_char}")
        self.current_action_index = None
        self.update_card_display()
        return False
        
    def execute_next_action(self):
        """Execute the previously found action"""
        if not self.next_action:
            return self.check_output()
            
        i, action = self.next_action
        print(f"Executing action: {action.action}")
        
        # Update tape with write value
        self.input_tape[self.current_pos] = str(action.action[1])
        
        # Get direction (-1: left, 0: stay, 1: right)
        direction = int(action.action[2])
        
        # Get next card ID
        next_card_id = int(action.action[3])
        print('next_card_id', next_card_id)
        
        # Update current card
        if next_card_id == -1:  # Special case for halt
            print("Reached halt state")
            self.pause()
            return self.check_output()
        
        # Fix: Make sure we're using 0-based indexing to access cards array
        # Card IDs are 1-based in the UI, but array indices are 0-based
        self.current_card = self.level.cards[next_card_id - 1]
        self.current_action_index = None
        
        print(f"Moving direction: {direction}, Next card: {self.current_card.card_id}")
        self.card_label.config(text=f"Current Card: {self.current_card.card_id}")
        self.update_card_display()
        
        # Update position
        self.current_pos += direction
        self.create_tape_display()
        
        # Find next action
        return self.find_next_action()
        
    def check_output(self):
        """Check if current tape matches expected output"""
        # Get current tape content (excluding leading/trailing _)
        current_output = ''.join(self.input_tape).strip('_')
        expected_output = self.test_data['output']
        
        print(f"Checking output: Current={current_output}, Expected={expected_output}")
        
        if current_output == expected_output:
            # Create a success message with green text
            result_window = tk.Toplevel(self)
            result_window.title("Test Result")
            result_window.geometry("400x200")
            
            frame = ttk.Frame(result_window, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Create a custom style for green text
            style = ttk.Style()
            style.configure("Success.TLabel", foreground="green", font=("Arial", 12, "bold"))
            
            # Show success message with green color
            success_label = ttk.Label(
                frame, 
                text=f"✓ Test Passed! Test #{self.test_data['id']} completed successfully.",
                style="Success.TLabel"
            )
            success_label.pack(pady=20)
            
            # Update test status in the parent window if method exists
            if hasattr(self.master, 'mark_test_completed'):
                self.master.mark_test_completed(self.test_data['id'])
                
            # Add a close button
            ttk.Button(frame, text="Close", command=result_window.destroy).pack(pady=10)
            
            return True
        else:
            # Create a failure message with red text
            result_window = tk.Toplevel(self)
            result_window.title("Test Result")
            result_window.geometry("400x250")
            
            frame = ttk.Frame(result_window, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Create a custom style for red text
            style = ttk.Style()
            style.configure("Failure.TLabel", foreground="red", font=("Arial", 12, "bold"))
            style.configure("Details.TLabel", font=("Arial", 10))
            
            # Show failure message with red color
            failure_label = ttk.Label(
                frame, 
                text=f"✗ Test Failed! Test #{self.test_data['id']} did not match expected output.",
                style="Failure.TLabel"
            )
            failure_label.pack(pady=(20, 10))
            
            # Show expected and actual outputs
            ttk.Label(frame, text=f"Expected:", style="Details.TLabel").pack(anchor="w")
            ttk.Label(frame, text=f"{expected_output}", style="Details.TLabel").pack(anchor="w", padx=20)
            
            ttk.Label(frame, text=f"Got:", style="Details.TLabel").pack(anchor="w", pady=(10, 0))
            ttk.Label(frame, text=f"{current_output}", style="Details.TLabel").pack(anchor="w", padx=20)
            
            # Add a close button
            ttk.Button(frame, text="Close", command=result_window.destroy).pack(pady=20)
            
            return False
        
    def next_step(self):
        """Execute next step of the Turing machine"""
        return self.execute_next_action()
            
    def schedule_next_step(self):
        """Schedule the next step based on current speed"""
        if self.is_playing:
            if self.next_step():
                delay = int(1000 / self.speed_options[self.speed_index])
                self.after_id = self.after(delay, self.schedule_next_step)
            else:
                # First pause the execution
                self.pause()
                print("Machine stopped")
                # ONLY check output here, not in next_step or execute_next_action
                self.check_output()
