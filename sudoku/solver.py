from collections import deque

from copy import deepcopy

Cell = int | set[int]
Row = list[Cell]
Box = list[Row]
Band = list[Box]
Grid = list[Band]


def format_sudoku(s: Grid):
    lines = []

    for i in range(3):
        for j in range(3):
            lines.append(" │ ".join(["  ".join(str(c) for c in sq[j]) for sq in s[i]]))

        if i < 2:
            lines.append("────────│─────────│────────")

    return "\n".join(lines)


def print_sudoku(s: Grid):
    print(format_sudoku(s))


def solve(sudoku: Grid, on_solution=None, stop_event=None):
    def apply_cell_constraints(coord: tuple[int, int, int, int]):
        i, ii, j, jj = coord
        cell = sudoku[i][ii][j][jj]

        if isinstance(cell, set) and len(cell) == 1:
            sudoku[i][ii][j][jj] = next(iter(cell))

        cell = sudoku[i][ii][j][jj]

        if isinstance(cell, int):
            for conf in conflicts[coord]:
                b, s, r, c = conf

                if isinstance(curr_cell := sudoku[b][s][r][c], set):
                    if cell in curr_cell:
                        stack.append((conf, curr_cell.copy()))

                        if conf not in queue:
                            queue.append(conf)

                        sudoku[b][s][r][c].discard(cell)

                        if not sudoku[b][s][r][c]:
                            raise ValueError("No options left for a cell")

    def generator():
        nonlocal sudoku

        while queue:
            apply_cell_constraints(queue.popleft())

            if stop_event is not None and stop_event.is_set():
                return

        for i in range(3):
            for ii in range(3):
                for j in range(3):
                    for jj in range(3):
                        if isinstance(cell := sudoku[i][ii][j][jj], set):
                            for el in cell:
                                if stop_event is not None and stop_event.is_set():
                                    return

                                stack_length = len(stack)
                                stack.append(((i, ii, j, jj), cell.copy()))
                                queue_length = len(queue)
                                queue.append((i, ii, j, jj))
                                sudoku[i][ii][j][jj] = el

                                try:
                                    yield from generator()

                                except ValueError:
                                    ...

                                for _ in range(len(queue) - queue_length):
                                    queue.pop()

                                for _ in range(len(stack) - stack_length):
                                    (b, bx, r, c), old = stack.pop()
                                    sudoku[b][bx][r][c] = old

                            return

        yield deepcopy(sudoku)

    for band in range(3):
        for box in range(3):
            for box_row in range(3):
                for row_col in range(3):
                    if not sudoku[band][box][box_row][row_col]:
                        sudoku[band][box][box_row][row_col] = {1, 2, 3, 4, 5, 6, 7, 8, 9}

    stack, queue = [], deque([])

    for band in range(3):
        for box in range(3):
            for box_row in range(3):
                for row_col in range(3):
                    if isinstance(sudoku[band][box][box_row][row_col], int):
                        apply_cell_constraints((band, box, box_row, row_col))

    for sol in generator():
        if stop_event is not None and stop_event.is_set():
            return

        if on_solution is not None:
            on_solution(sol)


conflicts = {}

for g_i in range(3):
    for g_ii in range(3):
        square = {(g_i, g_ii, r, c) for r in range(3) for c in range(3)}

        for g_j in range(3):
            for g_jj in range(3):
                coords = (g_i, g_ii, g_j, g_jj)
                conflicts[coords] = square.union({(g_i, c // 3, g_j, c % 3) for c in range(9)}).union(
                    {(r // 3, g_ii, r % 3, g_jj) for r in range(9)}) - {coords}
