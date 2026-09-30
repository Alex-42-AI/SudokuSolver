from collections import defaultdict

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
            lines.append(" │ ".join(["  ".join(str(c) for c in square1[j]) for square1 in s[i]]))

        if i < 2:
            lines.append("────────│─────────│────────")

    return "\n".join(lines)


def print_sudoku(s: Grid):
    print(format_sudoku(s))


def solve(sudoku: Grid, on_solution=None, stop_event=None):
    def validate_lines():
        for bd in sudoku:
            for r in range(3):
                line = bd[0][r] + bd[1][r] + bd[2][r]
                so_far = [i for i in line if isinstance(i, int)]

                if len(set(so_far)) < len(so_far):
                    raise ValueError("Repeating numbers on a line")

    def transpose_sudoku():
        for i in range(3):
            for ii in range(3):
                for j in range(2):
                    for jj in range(j + 1, 3):
                        sudoku[i][ii][j][jj], sudoku[i][ii][jj][j] = sudoku[i][ii][jj][j], sudoku[i][ii][j][jj]

        for i in range(3):
            for j in range(i + 1, 3):
                sudoku[i][j], sudoku[j][i] = sudoku[j][i], sudoku[i][j]

    def propagate_box_constraints():
        for i in range(3):
            for ii in range(3):
                present_numbers = [x for x in sum(sudoku[i][ii], []) if isinstance(x, int)]

                if len(set(present_numbers)) < len(present_numbers):
                    raise ValueError("Repeating numbers in a box")

                holder, present_numbers = True, set(present_numbers)

                while holder:
                    holder = False

                    for j in range(3):
                        for jj in range(3):
                            if isinstance(cell := sudoku[i][ii][j][jj], set):
                                if not cell.isdisjoint(present_numbers):
                                    stack.append(((i, ii, j, jj), cell.copy()))

                                sudoku[i][ii][j][jj] -= present_numbers

                                if not (cell := sudoku[i][ii][j][jj]):
                                    raise ValueError("No options left for a cell")

                                if len(cell) == 1:
                                    sudoku[i][ii][j][jj] = next(iter(cell))
                                    present_numbers.add(sudoku[i][ii][j][jj])
                                    holder |= len(present_numbers) < 9

    def apply_box_hidden_singles():
        for i in range(3):
            for ii in range(3):
                num_coordinates, curr_nums = defaultdict(set), set()

                for r in range(3):
                    for c in range(3):
                        if isinstance(cell := sudoku[i][ii][r][c], set):
                            for n in cell:
                                num_coordinates[n].add((r, c))

                        else:
                            curr_nums.add(cell)

                if not curr_nums.isdisjoint(num_coordinates) or curr_nums.union(num_coordinates) != NUMS:
                    raise ValueError("Missing candidate numbers in a box")

                num_coordinates = dict(num_coordinates)

                if not num_coordinates:
                    continue

                while num_coordinates:
                    n, coordinates = min(num_coordinates.items(), key=lambda p: len(p[1]))
                    num_coordinates.pop(n)

                    if not coordinates:
                        raise ValueError("Nowhere left to place a candidate number in a box")

                    if len(coordinates) > 1:
                        break

                    r, c = coordinates.pop()

                    for m in sudoku[i][ii][r][c].intersection(num_coordinates):
                        num_coordinates[m].discard((r, c))

                    stack.append(((i, ii, r, c), sudoku[i][ii][r][c]))
                    sudoku[i][ii][r][c] = n

    def propagate_line_constraints():
        lines = []

        for row_3_9 in sudoku:
            for r in range(3):
                lines.append(row_3_9[0][r] + row_3_9[1][r] + row_3_9[2][r])

        for i in range(3):
            for l in range(3 * i, 3 * (i + 1)):
                present_numbers, holder = [x for x in lines[l] if isinstance(x, int)], True

                if len(set(present_numbers)) < len(present_numbers):
                    raise ValueError("Repeating numbers in a line")

                present_numbers = set(present_numbers)

                while holder:
                    holder, line = False, sudoku[i][0][l % 3] + sudoku[i][1][l % 3] + sudoku[i][2][l % 3]

                    for j in range(9):
                        if isinstance(cell := line[j], set):
                            if not cell.isdisjoint(present_numbers):
                                stack.append(((i, j // 3, l % 3, j % 3), cell.copy()))

                            sudoku[i][j // 3][l % 3][j % 3] -= present_numbers

                            if not (cell := sudoku[i][j // 3][l % 3][j % 3]):
                                raise ValueError("No options left for a cell")

                            if len(cell) == 1:
                                sudoku[i][j // 3][l % 3][j % 3] = next(iter(cell))
                                present_numbers.add(sudoku[i][j // 3][l % 3][j % 3])
                                holder |= len(present_numbers) < 9

    def apply_line_hidden_singles():
        for i in range(3):
            for j in range(3):
                line = []

                for ii in range(3):
                    line += sudoku[i][ii][j]

                num_coordinates, curr_nums = defaultdict(set), set()

                for c, cell in enumerate(line):
                    if isinstance(cell, set):
                        for n in cell:
                            num_coordinates[n].add(c)

                    else:
                        curr_nums.add(cell)

                if not curr_nums.isdisjoint(num_coordinates) or curr_nums.union(num_coordinates) != NUMS:
                    raise ValueError("Missing candidate numbers in a line")

                num_coordinates = dict(num_coordinates)

                if not num_coordinates:
                    continue

                while num_coordinates:
                    n, coordinates = min(num_coordinates.items(), key=lambda p: len(p[1]))
                    num_coordinates.pop(n)

                    if not coordinates:
                        raise ValueError("Nowhere left to place a candidate number in a line")

                    if len(coordinates) > 1:
                        break

                    c = coordinates.pop()

                    for m in sudoku[i][c // 3][j][c % 3].intersection(num_coordinates):
                        num_coordinates[m].discard(c)

                    stack.append(((i, c // 3, j, c % 3), sudoku[i][c // 3][j][c % 3]))
                    sudoku[i][c // 3][j][c % 3] = n

    def generator():
        nonlocal sudoku

        if stop_event is not None and stop_event.is_set():
            return

        propagate_box_constraints()
        apply_box_hidden_singles()
        propagate_line_constraints()
        apply_line_hidden_singles()

        if stop_event is not None and stop_event.is_set():
            return

        transpose_sudoku()
        stack.append(-1)

        propagate_box_constraints()
        apply_box_hidden_singles()
        propagate_line_constraints()
        apply_line_hidden_singles()

        if stop_event is not None and stop_event.is_set():
            return

        validate_lines()
        transpose_sudoku()
        stack.append(-1)

        if stop_event is not None and stop_event.is_set():
            return

        validate_lines()

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
                                sudoku[i][ii][j][jj] = el

                                try:
                                    yield from generator()

                                except ValueError:
                                    ...

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

    stack = []

    for s in generator():
        if stop_event is not None and stop_event.is_set():
            return

        if on_solution is not None:
            on_solution(s)
