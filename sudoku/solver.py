from collections import deque

from copy import deepcopy

Cell = int | set[int]
Line = list[Cell]
Grid = list[Line]


def format_sudoku(s: Grid):
    lines = []

    for l in range(9):
        lines.append(" | ".join(["  ".join(map(str, s[l][3 * c:3 * c + 3])) for c in range(3)]))

    lines.insert(6, "────────│─────────│────────")
    lines.insert(3, "────────│─────────│────────")

    return "\n".join(lines)


def print_sudoku(s: Grid):
    print(format_sudoku(s))


def solve(sudoku: Grid, on_solution=None, stop_event=None):
    def apply_cell_constraints(coord: tuple[int, int]):
        i, j = coord
        cell = sudoku[i][j]

        if isinstance(cell, set) and len(cell) == 1:
            sudoku[i][j] = next(iter(cell))

        cell = sudoku[i][j]

        if isinstance(cell, int):
            for conf in conflicts[coord]:
                r, c = conf

                if isinstance(curr_cell := sudoku[r][c], set):
                    if cell in curr_cell:
                        stack.append((conf, curr_cell.copy()))

                        if conf not in queue:
                            queue.append(conf)

                        sudoku[r][c].discard(cell)

                        if not sudoku[r][c]:
                            raise ValueError("No options left for a cell")

    def generator():
        nonlocal sudoku

        while queue:
            apply_cell_constraints(queue.popleft())

            if stop_event is not None and stop_event.is_set():
                return

        for i in range(9):
            for j in range(9):
                if isinstance(cell := sudoku[i][j], set):
                    for el in cell:
                        if stop_event is not None and stop_event.is_set():
                            return

                        stack_length = len(stack)
                        stack.append(((i, j), cell.copy()))
                        queue_length = len(queue)
                        queue.append((i, j))
                        sudoku[i][j] = el

                        try:
                            yield from generator()

                        except ValueError:
                            ...

                        for _ in range(len(queue) - queue_length):
                            queue.pop()

                        for _ in range(len(stack) - stack_length):
                            (r, c), old = stack.pop()
                            sudoku[r][c] = old

                    return

        yield deepcopy(sudoku)

    for row in range(9):
        for col in range(9):
            if not sudoku[row][col]:
                sudoku[row][col] = {1, 2, 3, 4, 5, 6, 7, 8, 9}

    stack, queue = [], deque([])

    for row in range(9):
        for col in range(9):
            if isinstance(sudoku[row][col], int):
                apply_cell_constraints((row, col))

    for s in generator():
        if stop_event is not None and stop_event.is_set():
            return

        if on_solution is not None:
            on_solution(s)


conflicts = {}

for g_i in range(9):
    for g_j in range(9):
        sq_r, sq_c = 3 * (g_i // 3), 3 * (g_j // 3)
        square = {(r, c) for r in range(sq_r, sq_r + 3) for c in range(sq_c, sq_c + 3)}
        conflicts[(g_i, g_j)] = square.union(zip(9 * [g_i], range(9))).union(zip(range(9), 9 * [g_j])) - {(g_i, g_j)}
