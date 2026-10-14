from solver import solve, format_sudoku

from time import perf_counter

from pathlib import Path

problems_dir = Path("problems")
problems_dir.mkdir(parents=True, exist_ok=True)
case = len(list(problems_dir.iterdir()))
case_dir = problems_dir / f"case{case:03d}"
case_dir.mkdir(parents=True, exist_ok=True)
puzzle = [[8, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 3, 6, 0, 0, 0, 0, 0],
          [0, 7, 0, 0, 9, 0, 2, 0, 0],
          [0, 5, 0, 0, 0, 7, 0, 0, 0],
          [0, 0, 0, 0, 4, 5, 7, 0, 0],
          [0, 0, 0, 1, 0, 0, 0, 3, 0],
          [0, 0, 1, 0, 0, 0, 0, 6, 8],
          [0, 0, 8, 5, 0, 0, 0, 1, 0],
          [0, 9, 0, 0, 0, 0, 0, 0, 0]]

with open(case_dir / "puzzle.txt", "w", encoding="utf-8") as f:
    f.write(f"Puzzle:\n{format_sudoku(puzzle)}\n")

with open(case_dir / "solutions.txt", "w", encoding="utf-8") as f:
    def on_solution(sol):
        f.write(f"Solution {i[0]}:\n{format_sudoku(sol)}\nTime: {1000 * (perf_counter() - t):.3f} milliseconds\n\n")
        i[0] += 1


    i = [1]
    t = perf_counter()
    solve(puzzle, on_solution)
    t = 1000 * (perf_counter() - t)
    f.write(f"Finished in {t:.3f} milliseconds.\n")
