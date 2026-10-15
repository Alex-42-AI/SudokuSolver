# Sudoku Solver

A Python Sudoku solver with a Tkinter GUI that finds **all possible solutions** to a given Sudoku puzzle.

Unlike many Sudoku solvers that stop after finding the first solution, this project exhaustively searches the solution space and reports every valid solution it finds.

## Features

- Graphical interface built with Tkinter
- Enter a Sudoku puzzle directly into a 9×9 grid
- Finds **all possible solutions**
- Displays solutions as they are discovered
- Supports puzzles with multiple solutions
- Can be interrupted while solving
- Uses constraint propagation and recursive backtracking
- Includes a timer file, recording how quickly each solution of a puzzle is found in text files

## How It Works

The solver first changes empty cells into cells where each number is a possibility. It then applies cell constraints based on given values.

When no more constraints can be applied, it recursively tries possible values and continues applying the constraints. This process continues until all possible solutions have been enumerated.

The solver does not assume that a valid Sudoku has exactly one solution. If the puzzle has multiple solutions, they are all yielded.

## Usage

Run the GUI:

```bash
python3 main.py
```

Run the timer:

```bash
python3 timer.py

