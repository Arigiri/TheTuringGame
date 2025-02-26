import os
import json

class Test:
    def __init__(self, level_id):
        self.level_id = level_id
        self.tests = []
        self.passed_tests = set()  # Store IDs of passed tests
        self.load_tests()
        
    def load_tests(self):
        """Load all test files from the level's test directory"""
        test_dir = f"data/level{self.level_id}/tests"
        print(f"Loading tests from {test_dir}")
        
        if not os.path.exists(test_dir):
            print(f"Test directory {test_dir} does not exist")
            return
            
        # Get all .json files in test directory
        test_files = [f for f in os.listdir(test_dir) if f.endswith('.json')]
        test_files.sort()  # Sort to ensure consistent order
        
        print(f"Found {len(test_files)} test files: {test_files}")
        
        for test_file in test_files:
            test_path = os.path.join(test_dir, test_file)
            try:
                with open(test_path, 'r') as f:
                    test_data = json.load(f)
                    # Extract test number from filename (e.g., 'test1.json' -> '1')
                    test_number = ''.join(filter(str.isdigit, test_file))
                    test_data['id'] = test_number
                    self.tests.append(test_data)
                    print(f"Loaded test {test_number}: {test_data}")
            except Exception as e:
                print(f"Error loading test file {test_file}: {e}")
                
    def get_test_count(self):
        """Return the number of loaded tests"""
        return len(self.tests)
        
    def get_test_data(self, test_id):
        """Get data for a specific test by its ID"""
        for test in self.tests:
            if test['id'] == str(test_id):
                return test
        return None

    def mark_test_passed(self, test_id):
        """Mark a test as passed"""
        self.passed_tests.add(str(test_id))
        print(f"Test {test_id} marked as passed")
        
    def is_test_passed(self, test_id):
        """Check if a test has passed"""
        return str(test_id) in self.passed_tests
