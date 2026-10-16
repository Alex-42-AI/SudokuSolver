from solver import solve, format_sudoku

from time import perf_counter

from pathlib import Path

problems_dir = Path("timer")
problems_dir.mkdir(parents=True, exist_ok=True)
case = len(list(problems_dir.iterdir()))
case_dir = problems_dir / f"case{case:03d}"
case_dir.mkdir(parents=True, exist_ok=True)
puzzle = [8, 0, 0,    0, 0, 0,    0, 0, 0,
          0, 0, 3,    6, 0, 0,    0, 0, 0,
          0, 7, 0,    0, 9, 0,    2, 0, 0,

          0, 5, 0,    0, 0, 7,    0, 0, 0,
          0, 0, 0,    0, 4, 5,    7, 0, 0,
          0, 0, 0,    1, 0, 0,    0, 3, 0,

          0, 0, 1,    0, 0, 0,    0, 6, 8,
          0, 0, 8,    5, 0, 0,    0, 1, 0,
          0, 9, 0,    0, 0, 0,    4, 0, 0]

with open(case_dir / "results.txt", "w", encoding="utf-8") as f:
    to_format = [(1 << d) // 2 for d in puzzle]
    f.write(f"Puzzle:\n{format_sudoku(to_format)}\n")
    results = []
    t = perf_counter()
    solve(puzzle, lambda _: results.append(perf_counter() - t))
    t = 1000 * (perf_counter() - t)

    for i, time in enumerate(results, start=1):
        f.write(f"\nSolution {i}:\nTime: {1000 * time:.3f} milliseconds\n")

    f.write(f"\nFinished exhaustive search in {t:.3f} milliseconds.\n")
