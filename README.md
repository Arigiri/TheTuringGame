# The Turing Game

A graphical educational tool for learning about Turing machines through an interactive puzzle-solving experience.

## Overview

The Turing Game is an educational application designed to help users understand the fundamental concepts of Turing machines through a series of interactive puzzles. Users create and modify cards (states) with actions to process input strings and produce desired outputs, reinforcing computational theory concepts in a visual and engaging way.

## Features

- **Visual Turing Machine Simulation**: Watch your Turing machine execute step by step.
- **Multiple Levels**: Progress through increasingly complex computational challenges.
- **Card-based Programming**: Create and modify cards with actions for different inputs.
- **Test-based Verification**: Verify your solution against multiple test cases.
- **Interactive UI**: Drag-and-drop interface for building and testing Turing machines.
- **Progress Tracking**: Track completed levels and tests with visual indicators.

## Installation

### Prerequisites

- Python 3.6 or higher
- Tkinter (usually comes with Python)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/Arigiri/TheTuringGame.git
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

## How to Play

1. **Select a Level**: Choose from available levels on the home screen.
2. **Understand the Problem**: Read the problem description in the Info tab.
3. **Create/Edit Cards**: In the Cards tab, add or modify cards with specific actions.
4. **Test Your Solution**: Run tests in the Tests tab to verify your solution.
5. **Run Tests**: Each test provides an input string and expects a specific output.
6. **Complete Levels**: Pass all tests to complete a level.

## Card Structure

Each card represents a state in the Turing machine and contains actions based on the symbol read from the tape:

- **Read**: The symbol to match on the tape.
- **Write**: The symbol to write to the tape.
- **Move**: The direction to move the head (left, stay, right).
- **Next Card**: The next card (state) to transition to.

## Project Structure

- `/data/`: Contains level definitions, problem descriptions, and test cases.
- `/Class/`: Core classes for the application.
  - `card.py`: Defines Card and Action classes.
  - `level.py`: Handles level loading and management.
  - `test.py`: Manages test cases and validation.
- `main.py`: Main application entry point and UI.
- `animation.py`: Handles the animation and simulation of the Turing machine.
- `constant.py`: Centralizes constants used throughout the application.

## Understanding Turing Machines

A Turing machine is a mathematical model of computation that defines an abstract machine which manipulates symbols on a strip of tape according to a table of rules. Despite its simplicity, a Turing machine can simulate any computer algorithm's logic.

The Turing Game visualizes this concept by allowing you to create and test your own Turing machines through cards (states) and actions (transitions).

## License

[Your chosen license]

## Acknowledgments

- Alan Turing, whose work on computability inspired this educational tool.
- [Any other acknowledgments]