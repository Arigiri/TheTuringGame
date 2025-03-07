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
        """Mark a test as passed and save the status"""
        # Ensure we have the passed_tests attribute initialized
        if not hasattr(self, 'passed_tests'):
            self.passed_tests = set()
            self.load_passed_tests()
        
        # Convert test_id to int for consistent comparison
        test_id = int(test_id)
        
        # Add the test to passed tests set
        self.passed_tests.add(test_id)
        print(f"Marked test {test_id} as passed. All passed tests: {self.passed_tests}")
        
        # Save the updated passed tests
        self.save_passed_tests()

    def load_passed_tests(self):
        """Load the list of passed tests from file"""
        if not hasattr(self, 'passed_tests'):
            self.passed_tests = set()
        
        save_path = os.path.join('data', f'level{self.level_id}', 'progress.json')
        
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    data = json.load(f)
                    passed_tests = data.get('passed_tests', [])
                    # Convert all test ids to integers
                    self.passed_tests = set(int(test_id) for test_id in passed_tests)
                    print(f"Loaded passed tests for level {self.level_id}: {self.passed_tests}")
            except Exception as e:
                print(f"Error loading test progress: {e}")
        else:
            print(f"No progress file found at {save_path}")
            self.passed_tests = set()

    def save_passed_tests(self):
        """Save the list of passed tests to file"""
        save_dir = os.path.join('data', f'level{self.level_id}')
        save_path = os.path.join(save_dir, 'progress.json')
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            with open(save_path, 'w') as f:
                json.dump({"passed_tests": list(self.passed_tests)}, f)
                print(f"Saved progress for level {self.level_id}: {self.passed_tests}")
        except Exception as e:
            print(f"Error saving test progress: {e}")

    def is_test_passed(self, test_id):
        """Check if a test has been passed"""
        if not hasattr(self, 'passed_tests'):
            self.load_passed_tests()
        return int(test_id) in self.passed_tests
