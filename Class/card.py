class Card:
    def __init__(self, level_id, card_id, all_states=None):
        self.level_id = level_id
        self.card_id = card_id
        if all_states is None:
            all_states = []
        else:
            self.action = self.create_default_actions(all_states)
    
    def save_card(self):
        pass
    
    def load_card(self):
        pass

    def create_default_actions(self, all_states):
        default_actions = []
        for state in all_states:
            default_actions.append(Action(state, [state, 1, self.card_id]))
        return default_actions
    
class Action:
    def __init__(self, state, action):
        """
        state: int
        action: [new_value, move_direction, new_state]
        """
        self.state = state
        self.action = action
    
    def change_value(self, new_value):
        self.action[0] = new_value
    
    def change_direction(self, new_direction):
        self.action[1] = new_direction
    
    def change_state(self, new_state):
        self.action[2] = new_state