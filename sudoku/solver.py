from collections import defaultdict

from copy import deepcopy

Cell = int | set[int]
Row = list[Cell]
Box = list[Row]
Band = list[Box]
Grid = list[Band]

# World's hardest sudoku:
# sudoku: Grid = [
#     [[[8, 0, 0], [0, 0, 3], [0, 7, 0]], [[0, 0, 0], [6, 0, 0], [0, 9, 0]], [[0, 0, 0], [0, 0, 0], [2, 0, 0]]],
#     [[[0, 5, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 7], [0, 4, 5], [1, 0, 0]], [[0, 0, 0], [7, 0, 0], [0, 3, 0]]],
#     [[[0, 0, 1], [0, 0, 8], [0, 9, 0]], [[0, 0, 0], [5, 0, 0], [0, 0, 0]], [[0, 6, 8], [0, 1, 0], [4, 0, 0]]]]


def format_sudoku(s):
    lines = []

    for i in range(3):
        for j in range(3):
            lines.append(" │ ".join(["  ".join(str(c) for c in square1[j]) for square1 in s[i]]))

        if i < 2:
            lines.append("────────│─────────│────────")

    return "\n".join(lines)


def print_sudoku(s):
    print(format_sudoku(s))


def validate_lines():
    """
    Makes sure lines don't repeat numbers.
    """

    lines = []

    for row_3_9 in sudoku:
        for r in range(3):
            lines.append(row_3_9[0][r] + row_3_9[1][r] + row_3_9[2][r])

    for line in lines:
        so_far = [i for i in line if isinstance(i, int)]

        if len(set(so_far)) < len(so_far):
            raise ValueError


def solved(s: Grid):
    """
    :param s: Current sudoku puzzle
    :return: Whether the puzzle is solved
    """
    for row_3_9 in s:
        for square in row_3_9:
            for r in square:
                for c in r:
                    if isinstance(c, set) or not c:
                        return False

    return True


def transpose_sudoku():
    """
    Transposes the sudoku fully like a matrix.
    """

    for i in range(3):
        for ii in range(3):
            for j in range(2):
                for jj in range(j + 1, 3):
                    sudoku[i][ii][j][jj], sudoku[i][ii][jj][j] = sudoku[i][ii][jj][j], sudoku[i][ii][j][jj]

    for i in range(3):
        for j in range(i + 1, 3):
            sudoku[i][j], sudoku[j][i] = sudoku[j][i], sudoku[i][j]


def propagate_box_constraints():
    """
    In a box, in positions where the value is a set of possibilities, these
    possibilities get limited based on already present numbers in the square.
    """

    for i in range(3):
        for ii in range(3):
            present_numbers = [x for x in sum(sudoku[i][ii], []) if isinstance(x, int) and x]

            if len(set(present_numbers)) < len(present_numbers):
                raise ValueError

            holder, present_numbers = True, set(present_numbers)

            while holder:
                holder = False

                for j in range(3):
                    for jj in range(3):
                        if not (curr := sudoku[i][ii][j][jj]):
                            sudoku[i][ii][j][jj] = set(range(1, 10)) - present_numbers

                        elif isinstance(curr, set):
                            sudoku[i][ii][j][jj] -= present_numbers

                        else:
                            continue

                        curr: set[int] = sudoku[i][ii][j][jj]

                        if len(curr) == 1:
                            sudoku[i][ii][j][jj] = next(iter(curr))
                            present_numbers.add(curr.pop())
                            holder |= len(present_numbers) < 9

                        elif not curr:
                            raise ValueError


def propagate_line_constraints():
    """
    In a given line, in positions where the value is a set of possibilities,
    these possibilities get limited based on already present numbers in the line.
    """

    lines = []

    for row_3_9 in sudoku:
        for r in range(3):
            lines.append(row_3_9[0][r] + row_3_9[1][r] + row_3_9[2][r])

    for i in range(3):
        for l in range(3 * i, 3 * (i + 1)):
            present_numbers, holder = [x for x in lines[l] if isinstance(x, int)], True

            if len(set(present_numbers)) < len(present_numbers):
                raise ValueError

            present_numbers = set(present_numbers)

            while holder:
                holder, line = False, sudoku[i][0][l % 3] + sudoku[i][1][l % 3] + sudoku[i][2][l % 3]

                for j in range(9):
                    if isinstance(curr := line[j], set):
                        sudoku[i][j // 3][l % 3][j % 3] -= present_numbers

                        if len(sudoku[i][j // 3][l % 3][j % 3]) == 1:
                            sudoku[i][j // 3][l % 3][j % 3] = next(iter(curr))
                            present_numbers.add(sudoku[i][j // 3][l % 3][j % 3])
                            holder |= len(present_numbers) < 9

                        elif not curr:
                            raise ValueError


def apply_box_hidden_singles():
    """
    If a given number has only 1 possible position in a box, it's placed there as the value in the given square.
    """

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

            if not curr_nums.isdisjoint(num_coordinates) or curr_nums.union(num_coordinates) != set(range(1, 10)):
                raise ValueError

            num_coordinates = dict(num_coordinates)

            if not num_coordinates:
                continue

            while num_coordinates:
                n, s = min(num_coordinates.items(), key=lambda p: len(p[1]))
                num_coordinates.pop(n)

                if not s:
                    raise ValueError

                if len(s) > 1:
                    break

                r, c = s.pop()

                for m in sudoku[i][ii][r][c].intersection(num_coordinates):
                    num_coordinates[m].discard((r, c))

                sudoku[i][ii][r][c] = n


def apply_line_hidden_singles():
    """
    If a given number has only 1 possible position in a line, it's placed there as the value in the given square.
    """

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

            if not curr_nums.isdisjoint(num_coordinates) or curr_nums.union(num_coordinates) != set(range(1, 10)):
                raise ValueError

            num_coordinates = dict(num_coordinates)

            if not num_coordinates:
                continue

            while num_coordinates:
                n, s = min(num_coordinates.items(), key=lambda p: len(p[1]))
                num_coordinates.pop(n)

                if not s:
                    raise ValueError

                if len(s) > 1:
                    break

                c = s.pop()

                for m in sudoku[i][c // 3][j][c % 3].intersection(num_coordinates):
                    num_coordinates[m].discard(c)

                sudoku[i][c // 3][j][c % 3] = n


def apply_pointing_pairs():
    """
    In a given box, it's possible a number only appears within the same 1x3 row. In that
    case, all other instances of it on the same line in the other 2 boxes are cleared out.
    """

    for row_3_9 in range(3):
        holder = True

        while holder:
            lines, all_helpful_rows_of_nums, holder = [], [], False

            for r in range(3):
                lines.append(sudoku[row_3_9][0][r] + sudoku[row_3_9][1][r] + sudoku[row_3_9][2][r])

            for square in range(3):
                helpful_rows_of_nums = defaultdict(list)

                for n in range(1, 10):
                    for r in range(3):
                        for c in sudoku[row_3_9][square][r]:
                            if isinstance(c, set) and n in c:
                                helpful_rows_of_nums[n].append(r)

                all_helpful_rows_of_nums.append({k: v[0] for k, v in helpful_rows_of_nums.items() if len(v) == 1})

            for i, l in enumerate(lines):
                for cell in l:
                    if isinstance(cell, set):
                        for n in cell:
                            for r, helpful_rows in enumerate(all_helpful_rows_of_nums):
                                if helpful_rows.get(n) == i:
                                    for c in list(range(3 * r)) + list(range(3 * (r + 1), 9)):
                                        if isinstance(l[c], set) and n in l[c]:
                                            sudoku[row_3_9][c // 3][i][c % 3].remove(n)

                                            if len(curr := sudoku[row_3_9][c // 3][i][c % 3].copy()) == 1:
                                                sudoku[row_3_9][c // 3][i][c % 3] = curr.pop()

                                            holder = True

                                        elif l[c] == n:
                                            raise ValueError


def apply_claiming_pairs():
    """
    In a given row of boxes, if the possible positions of a number in two boxes are confined
    to the same two rows, that number can be eliminated from those rows in the remaining box.
    """

    for row_3_9 in range(3):
        lines, all_helpful_rows_of_nums = [], []

        for r in range(3):
            lines.append(sudoku[row_3_9][0][r] + sudoku[row_3_9][1][r] + sudoku[row_3_9][2][r])

        for missing_square in range(3):
            indexes = {0, 1, 2} - {missing_square}
            square0, square1 = sudoku[row_3_9][indexes.pop()], sudoku[row_3_9][indexes.pop()]
            rows_of_nums0, rows_of_nums1, helpful_rows_of_nums = defaultdict(set), defaultdict(set), {}

            for n in range(1, 10):
                helpful = True

                for r in range(3):
                    for c in square0[r]:
                        if isinstance(c, set) and n in c:
                            rows_of_nums0[n].add(r)

                            if len(rows_of_nums0[n]) == 3:
                                helpful = False

                                break

                    if not helpful:
                        break

                if not helpful:
                    continue

                for r in range(3):
                    for c in square1[r]:
                        if isinstance(c, set) and n in c:
                            rows_of_nums1[n].add(r)

                            if len(rows_of_nums1[n]) == 3:
                                helpful = False

                                break

                    if not helpful:
                        break

                if not helpful:
                    continue

                if n in set(rows_of_nums0).intersection(rows_of_nums1):
                    if rows_of_nums0[n] != rows_of_nums1[n] and not (
                            rows_of_nums0[n] <= rows_of_nums1[n] or rows_of_nums1[n] <= rows_of_nums0[n]):
                        helpful = False

                if helpful and n in set(rows_of_nums0).intersection(rows_of_nums1):
                    helpful_rows_of_nums[n] = rows_of_nums0[n]

            all_helpful_rows_of_nums.append(helpful_rows_of_nums)

        for square, nums_rows in zip(sudoku[row_3_9], all_helpful_rows_of_nums):
            for n in range(1, 10):
                if n in nums_rows:
                    for r in nums_rows[n]:
                        for c in square[r]:
                            if isinstance(c, set):
                                c.discard(n)


def pigeonhole_principle_squares():
    """
    If, in a given 3x3 square, there's a set of numbers, the total set of possible positions of which is as big as the
    set of numbers, then no other numbers are options for either of these positions. If the set of positions has fewer
    elements than the set of numbers, the sudoku is wrong.
    """

    for row_3_9 in sudoku:
        for square in row_3_9:
            nums_positions = defaultdict(set)

            for n in set(range(1, 10)) - {i for i in sum(square, []) if isinstance(i, int)}:
                for r, row in enumerate(square):
                    for c, cell in enumerate(row):
                        if isinstance(cell, set) and n in cell:
                            nums_positions[n].add((r, c))

            nums_positions = {k: v for k, v in sorted(nums_positions.items(), key=lambda x: len(x[1]))}

            for n, positions in nums_positions.items():
                if list(nums_positions).index(n) + 1 >= len(positions):
                    full, so_far, checked = False, {n}, {n}

                    for pair in positions:
                        for m in square[pair[0]][pair[1]]:
                            if m not in checked:
                                if nums_positions[m] <= positions:
                                    if full:
                                        raise ValueError

                                    so_far.add(m)

                                    if so_far == positions:
                                        full = True

                                checked.add(m)

                    if full:
                        for r, c in positions:
                            square[r][c].intersection_update(so_far)


def pigeonhole_principle_lines():
    """
    If, in a given line, there's a set of numbers, the total set of possible positions of which is
    as big as the set of numbers, then no other numbers are options for either of these positions.
    If the set of positions has fewer elements than the set of numbers, the sudoku is wrong.
    """

    lines = []

    for row_3_9 in sudoku:
        for r in range(3):
            lines.append(row_3_9[0][r] + row_3_9[1][r] + row_3_9[2][r])

    for l, line in enumerate(lines):
        nums_positions = defaultdict(set)

        for n in {i for i in range(1, 10) if i not in line}:
            for c in range(9):
                if isinstance(line[c], set) and n in line[c]:
                    nums_positions[n].add(c)

        nums_positions = {k: v for k, v in sorted(nums_positions.items(), key=lambda T: len(T[1]))}

        for n, positions in nums_positions.items():
            if list(nums_positions).index(n) + 1 >= len(positions):
                full, so_far, checked = False, {n}, {n}

                for el in positions:
                    for each in line[el]:
                        if each not in checked:
                            if nums_positions[each] <= positions:
                                if full:
                                    raise ValueError

                                so_far.add(each)

                                if so_far == positions:
                                    full = True

                            checked.add(each)

                if full:
                    for el in positions:
                        sudoku[l // 3][el // 3][l % 3][el % 3].intersection_update(so_far)


def solve(initial_sudoku: Grid, on_solution=None, stop_event=None):
    global sudoku

    sudoku = deepcopy(initial_sudoku)

    def generator():
        global sudoku

        holder = True

        while holder:
            if stop_event is not None and stop_event.is_set():
                return

            holder = False

            last_sudoku = deepcopy(sudoku)

            propagate_box_constraints(), apply_box_hidden_singles(), propagate_line_constraints()
            apply_line_hidden_singles(), propagate_box_constraints(), apply_box_hidden_singles()
            apply_pointing_pairs(), apply_box_hidden_singles(), propagate_box_constraints()
            apply_claiming_pairs(), apply_box_hidden_singles(), propagate_line_constraints()
            pigeonhole_principle_lines(), apply_line_hidden_singles()

            if stop_event is not None and stop_event.is_set():
                return

            transpose_sudoku()

            propagate_line_constraints(), apply_line_hidden_singles(), propagate_box_constraints()
            apply_box_hidden_singles(), apply_pointing_pairs(), apply_box_hidden_singles()
            propagate_box_constraints(), apply_claiming_pairs(), apply_box_hidden_singles()
            propagate_line_constraints(), pigeonhole_principle_lines(), apply_line_hidden_singles()

            if stop_event is not None and stop_event.is_set():
                return

            validate_lines(), transpose_sudoku()

            propagate_box_constraints(), pigeonhole_principle_squares(), apply_box_hidden_singles()

            if stop_event is not None and stop_event.is_set():
                return

            validate_lines()

            for i in sudoku:
                for ii in i:
                    for j in ii:
                        for el in j:
                            if isinstance(el, set):
                                holder = True

                                break

                            if holder:
                                break

                        if holder:
                            break

                    if holder:
                        break

                if holder:
                    break

            if holder and sudoku == last_sudoku:
                for i in range(3):
                    for ii in range(3):
                        for j in range(3):
                            for jj in range(3):
                                if isinstance(cell := sudoku[i][ii][j][jj], set):
                                    last_attempt = deepcopy(sudoku)

                                    for el in cell:
                                        if stop_event is not None and stop_event.is_set():
                                            return

                                        sudoku[i][ii][j][jj] = el

                                        try:
                                            yield from generator()

                                        except ValueError:
                                            ...

                                        last_attempt[i][ii][j][jj].remove(el)
                                        sudoku = deepcopy(last_attempt)

                                    return

        yield deepcopy(sudoku)

    for s in generator():
        if stop_event is not None and stop_event.is_set():
            return

        if on_solution is not None:
            on_solution(s)
