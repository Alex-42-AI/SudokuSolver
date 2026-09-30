from collections import deque

from copy import deepcopy

Cell = int | set[int]
Row = list[Cell]
Box = list[Row]
Band = list[Box]
Grid = list[Band]

NUMS = set(range(1, 10))


def format_sudoku(s: Grid):
    lines = []

    for i in range(3):
        for j in range(3):
            lines.append(" │ ".join(["  ".join(str(c) for c in square[j]) for square in s[i]]))

        if i < 2:
            lines.append("────────│─────────│────────")

    return "\n".join(lines)


def print_sudoku(s: Grid):
    print(format_sudoku(s))


def solve(sudoku: Grid, on_solution=None, stop_event=None):
    def transpose_sudoku():
        for i in range(3):
            for ii in range(3):
                for j in range(2):
                    for jj in range(j + 1, 3):
                        sudoku[i][ii][j][jj], sudoku[i][ii][jj][j] = sudoku[i][ii][jj][j], sudoku[i][ii][j][jj]

        for i in range(3):
            for j in range(i + 1, 3):
                sudoku[i][j], sudoku[j][i] = sudoku[j][i], sudoku[i][j]

    def apply_cell_constraints(coord: tuple[int, int, int, int]):
        i, ii, j, jj = coord
        cell = sudoku[i][ii][j][jj]

        if isinstance(cell, set) and len(cell) == 1:
            sudoku[i][ii][j][jj] = next(iter(cell))

        cell = sudoku[i][ii][j][jj]

        if isinstance(cell, int):
            square = sudoku[i][ii]

            for r in range(3):
                for c in range(3):
                    if isinstance(curr_cell := square[r][c], set):
                        if cell in curr_cell:
                            coords = (i, ii, r, c)
                            stack.append((coords, curr_cell.copy()))

                            if coords not in queue:
                                queue.append(coords)

                        sudoku[i][ii][r][c].discard(cell)

                        if not sudoku[i][ii][r][c]:
                            raise ValueError("No options left for a cell")

            row = sudoku[i][0][j] + sudoku[i][1][j] + sudoku[i][2][j]

            for c in [*range(3 * ii), *range(3 * (ii + 1), 9)]:
                if isinstance(curr_cell := row[c], set):
                    if cell in curr_cell:
                        coords = (i, c // 3, j, c % 3)
                        stack.append((coords, curr_cell.copy()))

                        if coords not in queue:
                            queue.append(coords)

                    sudoku[i][c // 3][j][c % 3].discard(cell)

                    if not sudoku[i][c // 3][j][c % 3]:
                        raise ValueError("No options left for a cell")

            col = [sudoku[b][ii][r][jj] for b in range(3) for r in range(3)]

            for r in [*range(3 * i), *range(3 * (i + 1), 9)]:
                if isinstance(curr_cell := col[r], set):
                    if cell in curr_cell:
                        coords = (r // 3, ii, r % 3, jj)
                        stack.append((coords, curr_cell.copy()))

                        if coords not in queue:
                            queue.append(coords)

                    sudoku[r // 3][ii][r % 3][jj].discard(cell)

                    if not sudoku[r // 3][ii][r % 3][jj]:
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
                                    value = stack.pop()

                                    if value == -1:
                                        transpose_sudoku()

                                    else:
                                        (b, bx, r, c), old = value
                                        sudoku[b][bx][r][c] = old

                            return

        yield deepcopy(sudoku)

    for band in range(3):
        for box in range(3):
            for box_row in range(3):
                for row_col in range(3):
                    if not sudoku[band][box][box_row][row_col]:
                        sudoku[band][box][box_row][row_col] = NUMS.copy()

    stack, queue = [], deque([])

    for band in range(3):
        for box in range(3):
            for box_row in range(3):
                for row_col in range(3):
                    if isinstance(sudoku[band][box][box_row][row_col], int):
                        apply_cell_constraints((band, box, box_row, row_col))

    for s in generator():
        if stop_event is not None and stop_event.is_set():
            return

        if on_solution is not None:
            on_solution(s)
