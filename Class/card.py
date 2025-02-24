import os
import json

class Card:
    def __init__(self, level_id, card_id, all_states=None):
        self.level_id = level_id
        self.card_id = card_id
        if all_states is None:
            self.all_states = []
        else:
            self.all_states = all_states
        
        self.action = self.create_default_actions(self.all_states)
        
    def save_card(self, card_path):
        os.makedirs(os.path.dirname(card_path), exist_ok=True)
        with open(card_path, 'w') as f:
            json.dump(self.to_json(), f, indent=2)
    
    def load_card(self):
        pass

    def create_default_actions(self, all_states):
        default_actions = []
        for state in all_states:
            default_actions.append(Action(state, [state, state, 1, self.card_id + 1]))
        return default_actions

    def to_json(self):
        return {
            'level_id': self.level_id,
            'card_id': self.card_id,
            'action': [action.action for action in self.action],
            'state': [s for s in self.all_states]
        }
    
class Action:
    def __init__(self, state, action):
        """
        state: int
        action: [current_state, new_value, move_direction, new_state]
        """
        self.state = state
        self.action = action
    
    def change_value(self, new_value):
        self.action[0] = new_value
    
    def change_direction(self, new_direction):
        self.action[1] = new_direction
    
    def change_state(self, new_state):
        self.action[2] = new_state
    
    def get_state(self):
        return self.action[0]
    
    def get_value(self):
        return self.action[1]
    
    def get_direction(self):
        return self.action[2]
    
    def get_next_state(self):
        return self.action[3]