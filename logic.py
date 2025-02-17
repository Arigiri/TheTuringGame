from Class.level import Level

class GameLogic:
    def __init__(self):
        self.current_level = None
        
    def initialize_level(self, level_name):
        """
        Initialize a new level when player clicks on a level button
        Args:
            level_name (str): Name of the level folder (e.g., 'level1')
        Returns:
            Level: The initialized level object
        """
        # Extract level number from folder name
        level_id = int(level_name.replace('level', ''))
        
        # Create new level instance
        self.current_level = Level(level_id)
        return self.current_level
    
    def get_current_level(self):
        """Get the currently active level"""
        return self.current_level