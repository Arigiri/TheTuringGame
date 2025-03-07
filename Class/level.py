from Class.card import Card, Action
from utils import *
class Level:
    def __init__(self, level_id):
        self.level_id = level_id
        self.problem = None
        self.cards = []
        self.editor = None  # Will be set by main.py
        self.problem = self.read_problem()
        self.load_initial_cards()
    
    def read_problem(self):
        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        problem_file = os.path.join(data_path, f'data\level{self.level_id}\problems_description.json')
        return read_json_file(problem_file)
    
    def load_initial_cards(self):
        total_card = len(os.listdir(f"./data/level{self.level_id}/card"))
        for i in range(1, total_card + 1):
            new_cards = Card(self.level_id, i, self.problem['state'])
            new_cards.load_card()
            self.cards.append(new_cards)
        if total_card == 0:
            for i in range(1, 3):
                new_cards = Card(self.level_id, i, self.problem['state'])
                new_cards.save_card(f'data\level{self.level_id}\card\c{i}.json')
                self.cards.append(new_cards)
    def get_problem_description(self):
        return self.problem['description']
    
    def get_state(self):
        return self.problem['state']
    
    def add_card(self, card):
        self.cards.append(card)
    
    def remove_card(self, card):
        self.cards.remove(card)
    
    def get_cards(self):
        return self.cards
    
    def get_description(self):
        return self.problem
    
    def excution(self, card):
        pass
    
    def create_new_card(self):
        """Create a new card with default values"""
        new_card_id = len(self.cards) + 1
        new_card = Card(self.level_id, new_card_id, self.problem['state'])
        self.cards.append(new_card)
        return new_card
