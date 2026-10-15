# from collections import deque
# 
# 
# def solved(mask: int) -> bool:
#     return not (mask & (mask - 1))
# 
# 
# def format_sudoku(s: list[int]):
#     lines = []
# 
#     for l in range(9):
#         lines.append(" | ".join(["  ".join(map(lambda b: str(b.bit_length()), s[9 * l: 9 * (l + 1)][3 * c:3 * c + 3])) for c in range(3)]))
# 
#     lines.insert(6, "────────│─────────│────────")
#     lines.insert(3, "────────│─────────│────────")
# 
#     return "\n".join(lines)
# 
# 
# def print_sudoku(s: list[int]):
#     print(format_sudoku(s))
# 
# 
# def solve(sudoku: list[int], on_solution=None, stop_event=None):
#     def apply_cell_constraints(coord: int):
#         bit = sudoku[coord]
# 
#         for conf in conflicts[coord]:
#             if not solved(curr_cell := sudoku[conf]):
#                 if bit & curr_cell:
#                     stack.append((conf, curr_cell))
#                     sudoku[conf] ^= bit
# 
#                     if not (curr_cell := sudoku[conf]):
#                         raise ValueError("No options left for a cell")
# 
#                     if conf not in queue and solved(curr_cell):
#                         queue.append(conf)
# 
#     def generator():
#         nonlocal sudoku
# 
#         while queue:
#             apply_cell_constraints(queue.popleft())
# 
#             if stop_event is not None and stop_event.is_set():
#                 return
# 
#         for i in range(81):
#             if not solved(cell := sudoku[i]):
#                 original_cell = cell
# 
#                 while cell:
#                     bit = cell & -cell
#                     cell ^= bit
# 
#                     if stop_event is not None and stop_event.is_set():
#                         return
# 
#                     stack_length = len(stack)
#                     stack.append((i, original_cell))
#                     queue_length = len(queue)
#                     queue.append(i)
#                     sudoku[i] = bit
# 
#                     try:
#                         yield from generator()
# 
#                     except ValueError:
#                         ...
# 
#                     for _ in range(len(queue) - queue_length):
#                         queue.pop()
# 
#                     for _ in range(len(stack) - stack_length):
#                         c, old = stack.pop()
#                         sudoku[c] = old
# 
#                 return
# 
#         yield sudoku.copy()
# 
#     for i, cell in enumerate(sudoku):
#         if cell and any(sudoku[j] == cell for j in conflicts[i] if j > i):
#             raise ValueError("Invalid puzzle")
# 
#     for i in range(81):
#         if d := sudoku[i]:
#             sudoku[i] = 1 << (d - 1)
# 
#         else:
#             sudoku[i] = (1 << 9) - 1
# 
#     stack, queue = [], deque([])
# 
#     for i in range(81):
#         if solved(sudoku[i]):
#             apply_cell_constraints(i)
# 
#     for s in generator():
#         if stop_event is not None and stop_event.is_set():
#             return
# 
#         if on_solution is not None:
#             on_solution(s)
# 
# 
# conflicts: list[set] = []
# 
# for i in range(81):
#     r, c = divmod(i, 9)
#     line = set(range(9 * r, 9 * r + 9))
#     column = set(range(c, 81, 9))
#     box_r, box_c = 3 * (r // 3), 3 * (c // 3)
#     box = {9 * r + c for r in range(box_r, box_r + 3) for c in range(box_c, box_c + 3)}
#     conflicts.append((line | column | box) - {i})


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
        conflicts[(g_i, g_j)] = square | set(zip(9 * [g_i], range(9))) | set(zip(range(9), 9 * [g_j])) - {(g_i, g_j)}
