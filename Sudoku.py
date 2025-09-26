from collections import defaultdict

from time import time

from copy import deepcopy


sudoku = [[[[8, 0, 0], [0, 0, 3], [0, 7, 0]], [[0, 0, 0], [6, 0, 0], [0, 9, 0]], [[0, 0, 0], [0, 0, 0], [2, 0, 0]]],
          [[[0, 5, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 7], [0, 4, 5], [1, 0, 0]], [[0, 0, 0], [7, 0, 0], [0, 3, 0]]],
          [[[0, 0, 1], [0, 0, 8], [0, 9, 0]], [[0, 0, 0], [5, 0, 0], [0, 0, 0]], [[0, 6, 8], [0, 1, 0], [4, 0, 0]]]]


def print_sudoku():
    for i in range(3):
        for j in range(3):
            print(" │ ".join(["  ".join(str(c) for c in square1[j]) for square1 in sudoku[i]]))

        print("────────│─────────│────────" * (i < 2))


def error_in_lines():
    lines = []

    for row_3_9 in sudoku:
        for r in range(3):
            lines.append(row_3_9[0][r] + row_3_9[1][r] + row_3_9[2][r])

    for line in lines:
        so_far = [i for i in line if isinstance(i, int)]

        if len(set(so_far)) < len(so_far):
            raise ValueError


def solved():
    for row_3_9 in sudoku:
        for square in row_3_9:
            for r in square:
                for c in r:
                    if isinstance(c, set) or not c:
                        return False

    return True


def transpose_sudoku():
    for i in range(3):
        for ii in range(3):
            if ii > i:
                sudoku[i][ii], sudoku[ii][i] = sudoku[ii][i], sudoku[i][ii]

            for j in range(2):
                for jj in range(j + 1, 3):
                    sudoku[i][ii][j][jj], sudoku[i][ii][jj][j] = sudoku[i][ii][jj][j], sudoku[i][ii][j][jj]


def limiting_possibilities_in_squares():
    """
    In a middle 3x3 square, in positions where the value is an iterable of possibilities, these possibilities get limited based on already present numbers in the square
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

                        if len(curr := sudoku[i][ii][j][jj]) == 1:
                            sudoku[i][ii][j][jj] = next(iter(curr))
                            present_numbers.add(sudoku[i][ii][j][jj])
                            holder = len(present_numbers) < 9

                        elif not curr:
                            raise ValueError


def limiting_possibilities_in_lines():
    """
    In a given line, in positions where the value is an iterable of possibilities, these possibilities get limited based on already present numbers in a given line
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
                            holder = len(present_numbers) < 9

                        elif not curr:
                            raise ValueError


def filling_in_els_met_only_once_squares():
    """
    If a given number has only 1 possible position in a 3x3 square, it's placed there as the value in the given square. Since this removes other possibilities from there, this process is repeated for all numbers that might remain possible in only 1 position
    """

    for i in range(3):
        for ii in range(3):
            holder = True

            while holder:
                holder, possibilities_coordinates, total = False, {}, set()

                for r in range(3):
                    for c in range(3):
                        if isinstance(cell := sudoku[i][ii][r][c], set):
                            for n in cell:
                                if n in total:
                                    if n in possibilities_coordinates:
                                        possibilities_coordinates.pop(n)
                                else:
                                    possibilities_coordinates[n] = (r, c)
                                    total.add(n)

                for k, (r, c) in possibilities_coordinates.items():
                    holder |= len(sudoku[i][ii][r][c]) > 1
                    sudoku[i][ii][r][c] = k


def filling_in_els_met_only_once_lines():
    """
    If a given number has only 1 possible position in a line, it's placed there as the value in the given square. Since this removes other possibilities from there, this process is repeated for all numbers that might remain possible in only 1 position
    """

    for i in range(3):
        for j in range(3):
            line = []

            for ii in range(3):
                line += sudoku[i][ii][j]

            holder, possibilities_indexes, total = True, {}, set()

            while holder:
                holder = False

                for c, cell in enumerate(line):
                    if isinstance(cell, set):
                        for n in cell:
                            if n in total:
                                if n in possibilities_indexes:
                                    possibilities_indexes.pop(n)
                            else:
                                possibilities_indexes[n] = c
                                total.add(n)

                for k, v in possibilities_indexes.items():
                    holder |= len(line[v]) > 1
                    sudoku[i][v // 3][j][v % 3] = k


def cleaning_els_met_on_the_same_row_in_a_square_from_the_rest_of_the_line():
    """
    In a given 3x3 square, it's possible a number only appears within the same 1x3 row. In that case, all other instances of it on the same line in the other 2 3x3 squares are cleared out
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
                        for n in cell.copy():
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


def limiting_els_in_third_square_if_number_is_met_only_within_the_same_2_rows_in_the_first_2_squares():
    """
    On a given 3x9 row in the sudoku, it's possible there're 2 3x3 squares such that for a given number's possible positions, in both middle squares, the positions are within the same 2 1x3 rows. In that case, wherever the number is in goth 3x3 squares, in the third one, it can't appear in either of these 2 1x3 rows
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


def set_of_nums_met_within_the_same_cells_squares():
    """
    If, in a given 3x3 square, there's a set of numbers, the total set of possible positions of which is as big as the set of numbers, then no other numbers are options for either of these positions. If the set of positions has fewer elements than the set of numbers, the sudoku is wrong
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


def set_of_nums_met_within_the_same_cells_lines():
    """
    If, in a given line, there's a set of numbers, the total set of possible positions of which is as big as the set of numbers, then no other numbers are options for either of these positions. If the set of positions has fewer elements than the set of numbers, the sudoku is wrong
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


def solve():
    global sudoku

    holder = True

    while holder:
        holder = False
        last_sudoku = deepcopy(sudoku)
        limiting_possibilities_in_squares()
        filling_in_els_met_only_once_squares()
        limiting_possibilities_in_lines()
        filling_in_els_met_only_once_lines()
        limiting_possibilities_in_squares()
        filling_in_els_met_only_once_squares()
        cleaning_els_met_on_the_same_row_in_a_square_from_the_rest_of_the_line()
        filling_in_els_met_only_once_squares()
        limiting_possibilities_in_squares()
        limiting_els_in_third_square_if_number_is_met_only_within_the_same_2_rows_in_the_first_2_squares()
        filling_in_els_met_only_once_squares()
        limiting_possibilities_in_lines()
        set_of_nums_met_within_the_same_cells_lines()
        filling_in_els_met_only_once_lines()
        transpose_sudoku()
        limiting_possibilities_in_lines()
        filling_in_els_met_only_once_lines()
        limiting_possibilities_in_squares()
        filling_in_els_met_only_once_squares()
        cleaning_els_met_on_the_same_row_in_a_square_from_the_rest_of_the_line()
        filling_in_els_met_only_once_squares()
        limiting_possibilities_in_squares()
        limiting_els_in_third_square_if_number_is_met_only_within_the_same_2_rows_in_the_first_2_squares()
        filling_in_els_met_only_once_squares()
        limiting_possibilities_in_lines()
        set_of_nums_met_within_the_same_cells_lines()
        filling_in_els_met_only_once_lines()
        error_in_lines(), transpose_sudoku()
        limiting_possibilities_in_squares()
        set_of_nums_met_within_the_same_cells_squares()
        filling_in_els_met_only_once_squares()
        error_in_lines()

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

                                for el in cell.copy():
                                    sudoku[i][ii][j][jj] = el

                                    try:
                                        solve()

                                        if solved():
                                            return

                                    except ValueError:
                                        last_attempt[i][ii][j][jj].remove(el)
                                        sudoku = deepcopy(last_attempt)

                                if not solved():
                                    raise ValueError


if __name__ == '__main__':

    t1 = time() * 1000
    solve()
    t2 = time() * 1000

    if not solved():
        raise ValueError('This sudoku is incorrect!')

    print_sudoku(), print('Milliseconds:', t2 - t1)
