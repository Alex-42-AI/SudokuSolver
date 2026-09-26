# Sudoku Solver

A Python Sudoku solver with a Tkinter GUI that finds **all possible solutions** to a given Sudoku puzzle.

Unlike many Sudoku solvers that stop after finding the first solution, this project exhaustively searches the solution space and reports every valid solution it finds.

## Features

- Graphical interface built with Tkinter
- Enter a Sudoku puzzle directly into a 9×9 grid
- Finds **all possible solutions**
- Displays solutions as they are discovered
- Reports the time at which each solution was found
- Supports puzzles with multiple solutions
- Can be interrupted while solving
- Uses constraint propagation and recursive backtracking
- Includes several custom Sudoku deduction techniques

## How It Works

The solver first applies a collection of constraint-based techniques to reduce the possible values of each cell.

When logical deduction alone cannot complete the puzzle, it recursively tries possible values and continues applying the constraints. This process continues until all possible solutions have been enumerated.

The solver does not assume that a valid Sudoku has exactly one solution. If the puzzle has multiple solutions, they are all returned.

## Usage

Run the GUI:

```bash
python main.py
