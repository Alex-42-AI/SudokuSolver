from solver import solve, format_sudoku

from pathlib import Path

counter_dir = Path("counter")
counter_dir.mkdir(parents=True, exist_ok=True)
case = len(list(counter_dir.iterdir()))
case_dir = counter_dir / f"case{case:03d}"
case_dir.mkdir(parents=True, exist_ok=True)
puzzle = [9, 0, 0,    0, 0, 0,    0, 0, 0,
          0, 0, 3,    6, 0, 0,    0, 0, 0,
          0, 7, 0,    0, 9, 0,    2, 0, 0,

          0, 5, 0,    0, 0, 7,    0, 0, 0,
          0, 0, 0,    0, 4, 5,    7, 0, 0,
          0, 0, 0,    1, 0, 0,    0, 3, 0,

          0, 0, 1,    0, 0, 0,    0, 6, 8,
          0, 0, 8,    5, 0, 0,    0, 1, 0,
          0, 9, 0,    0, 0, 0,    0, 0, 0]

with open(case_dir / "results.txt", "w", encoding="utf-8") as f:
    def on_solution(_):
        total[0] += 1


    to_format = [(1 << d) // 2 for d in puzzle]
    f.write(f"{format_sudoku(to_format)}\n")
    total = [0]
    solve(puzzle, on_solution)
    f.write(f"Total solutions: {total[0]}\n")
