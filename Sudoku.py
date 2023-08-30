from time import time

sudoku = [[[[], [], []], [[], [], []], [[], [], []]], 
          [[[], [], []], [[], [], []], [[], [], []]],
          [[[], [], []], [[], [], []], [[], [], []]]]


def print_sudoku():
    for Row1 in range(3):
        for row1 in range(3):
            print(' | '.join(['  '.join(str(i) for i in square1[row1]) for square1 in sudoku[Row1]]))
        print('--------|---------|--------' * (Row1 < 2))


def error_in_lines():
    rows = []
    for Row1 in sudoku:
        for r in range(3):
            rows.append(Row1[0][r] + Row1[1][r] + Row1[2][r])
    for r in rows:
        so_far = list(sorted(i for i in r if isinstance(i, int)))
        so_far_unique = []
        for i in so_far:
            if i in so_far_unique:
                raise ValueError
            so_far_unique.append(i)


def solved():
    for Row1 in sudoku:
        for square1 in Row1:
            for row1 in square1:
                for col1 in row1:
                    if isinstance(col1, list) or not col1:
                        return False
    return True


def make_equal(original, copy):
    for Row1 in range(3):
        for square1 in range(3):
            for row1 in range(3):
                for col1 in range(3):
                    if isinstance(original[Row1][square1][row1][col1], int):
                        copy[Row1][square1][row1][col1] = original[Row1][square1][row1][col1]
                    elif isinstance(original[Row1][square1][row1][col1], list):
                        copy[Row1][square1][row1][col1] = original[Row1][square1][row1][col1].copy()


def TransposeSudoku():
    for i in range(3):
        for j in range(i + 1, 3):
            sudoku[i][j], sudoku[j][i] = sudoku[j][i], sudoku[i][j]
    for Row1 in range(3):
        for square1 in range(3):
            for i in range(3):
                for j in range(i + 1, 3):
                    sudoku[Row1][square1][i][j], sudoku[Row1][square1][j][i] = sudoku[Row1][square1][j][i], sudoku[Row1][square1][i][j]


def filling_in_els_only_met_once_squares():
    for Row1 in sudoku:
        for square1 in Row1:
            histogram = {I: 0 for I in range(1, 10)}
            for row1 in square1:
                for element in row1:
                    if isinstance(element, list):
                        for each in element:
                            histogram[each] += 1
            Holder = True
            while Holder:
                Holder = False
                for k, v in histogram.items():
                    if v == 1:
                        for row1 in square1:
                            for element in range(3):
                                if isinstance(row1[element], list):
                                    if k in row1[element]:
                                        for num in row1[element]:
                                            histogram[num] -= 1
                                        row1[element], Holder = k, True
                                        break
                            if Holder:
                                break
                        if Holder:
                            break


def limiting_possibilities_for_nums_in_squares():
    for Row1 in sudoku:
        for square1 in Row1:
            current_numbers = []
            for row1 in square1:
                for element in row1:
                    if element and isinstance(element, int):
                        if element in current_numbers:
                            raise ValueError
                        current_numbers.append(element)
            Holder = True
            while Holder:
                Holder = False
                for row1 in square1:
                    for i in range(3):
                        if not row1[i]:
                            row1[i] = [num for num in range(1, 10) if num not in current_numbers]
                        elif isinstance(row1[i], list):
                            for j in current_numbers:
                                if j in row1[i]:
                                    row1[i].remove(j)
                        else:
                            continue
                        if len(row1[i]) == 1:
                            row1[i] = row1[i][0]
                            current_numbers.append(row1[i])
                            Holder = len(current_numbers) < 9
                        elif not row1[i]:
                            raise ValueError


def limiting_possibilities_for_nums_in_lines():
    rows = []
    for Row1 in sudoku:
        for r in range(3):
            rows.append(Row1[0][r] + Row1[1][r] + Row1[2][r])
    for Row1 in range(3):
        for l in range(3 * Row1, 3 * (Row1 + 1)):
            so_far = [i for i in rows[l] if isinstance(i, int)]
            Holder = 1
            while Holder:
                Holder = 0
                row1 = sudoku[Row1][0][l % 3] + sudoku[Row1][1][l % 3] + sudoku[Row1][2][l % 3]
                for i in range(9):
                    if isinstance(row1[i], list):
                        for j in so_far:
                            if j in row1[i]:
                                row1[i].remove(j)
                        if len(row1[i]) == 1:
                            row1[i] = row1[i][0]
                            for _ in range(3):
                                sudoku[Row1][_][l % 3] = row1[3 * _: 3 * (_ + 1)]
                            so_far.append(row1[i])
                            Holder = len(so_far) < 9
                        elif not row1[i]:
                            raise ValueError


def filling_in_els_only_met_once_lines():
    for Row1 in sudoku:
        for row1 in range(3):
            line = []
            for square1 in range(3):
                line += Row1[square1][row1]
            histogram = {I: 0 for I in range(1, 10)}
            for element in line:
                if isinstance(element, list):
                    for num in element:
                        histogram[num] += 1
            breaker = True
            while breaker:
                breaker = False
                for K, V in histogram.items():
                    if V == 1:
                        for R in range(3):
                            for L in range(9):
                                if L != 3 * R + L % 3:
                                    continue
                                total = sudoku[R][0][L % 3] + sudoku[R][1][L % 3] + sudoku[R][2][L % 3]
                                for element in range(9):
                                    if isinstance(total[element], list):
                                        if K in total[element]:
                                            for num in total[element]:
                                                histogram[num] -= 1
                                            total[element] = K
                                            breaker = True
                                            break
                                if breaker:
                                    break
                            if breaker:
                                break
                        if breaker:
                            break


def cleaning_els_met_on_the_same_row_in_a_square_from_the_rest_of_the_line():
    again = False
    for Row1 in range(3):
        lines = []
        all_helpful_rows_of_nums = []
        for row1 in range(3):
            line = []
            for square1 in range(3):
                line += sudoku[Row1][square1][row1]
            lines.append(line)
        for square1 in range(3):
            rows_of_nums = {}
            helpful_rows_of_nums = {}
            for num in range(1, 10):
                helpful = True
                for row2 in range(3):
                    for element in sudoku[Row1][square1][row2]:
                        if isinstance(element, list) and helpful:
                            if num in element:
                                if num in rows_of_nums.keys():
                                    if rows_of_nums[num] != row2:
                                        helpful = False
                                        break
                                rows_of_nums[num] = row2
                if helpful and num in rows_of_nums.keys():
                    helpful_rows_of_nums[num] = rows_of_nums[num]
            all_helpful_rows_of_nums.append(helpful_rows_of_nums)
        for L in range(3):
            for element in range(9):
                if isinstance(lines[L][element], list):
                    for each in lines[L][element]:
                        for r in range(3):
                            if each in all_helpful_rows_of_nums[r].keys():
                                if all_helpful_rows_of_nums[r][each] == L:
                                    for El in range(9):
                                        if El < r * 3 or El >= 3 * (r + 1):
                                            if isinstance(lines[L][El], list):
                                                if each in lines[L][El]:
                                                    lines[L][El].remove(each)
                                                    if len(lines[L][El]) == 1:
                                                        lines[L][El] = lines[L][El][0]
                                                    again = True
                                            elif lines[L][El] == each:
                                                raise ValueError
    if again:
        cleaning_els_met_on_the_same_row_in_a_square_from_the_rest_of_the_line()


def limiting_els_in_third_square_if_number_is_met_only_within_the_same_2_rows_in_the_first_2_squares():
    for Row1 in range(3):
        lines = []
        all_helpful_rows_of_nums = []
        for row1 in range(3):
            line = []
            for square1 in range(3):
                line += sudoku[Row1][square1][row1]
            lines.append(line)
        for square1 in range(3):
            for square2 in range(square1 + 1, 3):
                rows_of_nums1 = {}
                rows_of_nums2 = {}
                helpful_rows_of_nums = {}
                for num in range(1, 10):
                    helpful = True
                    for row2 in range(3):
                        for element in sudoku[Row1][square1][row2]:
                            if isinstance(element, list) and helpful:
                                if num in element:
                                    if num in rows_of_nums1.keys():
                                        rows_of_nums1[num].add(row2)
                                        if len(rows_of_nums1[num]) == 3:
                                            helpful = False
                                            break
                                    else:
                                        rows_of_nums1[num] = {row2}
                    for row2 in range(3):
                        for element in sudoku[Row1][square2][row2]:
                            if isinstance(element, list) and helpful:
                                if num in element:
                                    if num in rows_of_nums2.keys():
                                        rows_of_nums2[num].add(row2)
                                        if len(rows_of_nums2[num]) == 3:
                                            helpful = False
                                            break
                                    else:
                                        rows_of_nums2[num] = {row2}
                    if num in rows_of_nums1.keys() and num in rows_of_nums2.keys():
                        if rows_of_nums1[num] != rows_of_nums2[num] and not (
                                rows_of_nums1[num].issubset(rows_of_nums2[num]) or rows_of_nums2[num].issubset(rows_of_nums1[num])):
                            helpful = False
                    if helpful and num in rows_of_nums1.keys() and num in rows_of_nums2.keys():
                        helpful_rows_of_nums[num] = rows_of_nums1[num]
                all_helpful_rows_of_nums.append(helpful_rows_of_nums)
        for square1 in range(3):
            for num in range(1, 10):
                if num in all_helpful_rows_of_nums[2 - square1].keys():
                    for row1 in range(3):
                        if row1 in all_helpful_rows_of_nums[2 - square1][num]:
                            for El in sudoku[Row1][square1][row1]:
                                if isinstance(El, list):
                                    if num in El:
                                        El.remove(num)


def set_of_nums_met_within_the_same_places_at_most_squares():
    for Row1 in sudoku:
        for square1 in Row1:
            not_found_yet = [i for i in range(1, 10)]
            for row1 in square1:
                for element in row1:
                    if isinstance(element, int):
                        not_found_yet.remove(element)
            nums_positions = {}
            for num in not_found_yet:
                nums_positions[num] = []
                for row1 in range(3):
                    for col1 in range(3):
                        if isinstance(square1[row1][col1], list):
                            if num in square1[row1][col1]:
                                nums_positions[num].append((row1, col1))
            nums_positions = {k: v for k, v in sorted(nums_positions.items(), key=lambda T: len(T[1]))}
            for num, positions in nums_positions.items():
                if list(nums_positions.keys()).index(num) + 1 >= len(nums_positions[num]):
                    full = False
                    so_far = {num}
                    checked = [num]
                    for pair in range(len(positions)):
                        for each in square1[positions[pair][0]][positions[pair][1]]:
                            if each not in checked:
                                if set(nums_positions[each]) <= set(nums_positions[num]):
                                    if full:
                                        raise ValueError
                                    so_far.add(each)
                                    if len(so_far) == len(nums_positions[num]):
                                        full = True
                                checked.append(each)
                    if full:
                        for pair in range(len(positions)):
                            for each in square1[positions[pair][0]][positions[pair][1]]:
                                if each not in so_far:
                                    square1[positions[pair][0]][positions[pair][1]].remove(each)


def set_of_nums_met_within_the_same_places_at_most_lines():
    lines = []
    for Row1 in sudoku:
        for r in range(3):
            lines.append(Row1[0][r] + Row1[1][r] + Row1[2][r])
    for line in lines:
        not_found_yet = [i for i in range(1, 10) if i not in line]
        nums_positions = {}
        for num in not_found_yet:
            nums_positions[num] = []
            for el in range(9):
                if isinstance(line[el], list):
                    if num in line[el]:
                        nums_positions[num].append(el)
        nums_positions = {k: v for k, v in sorted(nums_positions.items(), key=lambda T: len(T[1]))}
        for num, positions in nums_positions.items():
            if list(nums_positions.keys()).index(num) + 1 >= len(nums_positions[num]):
                full = False
                so_far = {num}
                checked = [num]
                for position in positions:
                    for each in line[position]:
                        if each not in checked:
                            if set(nums_positions[each]) <= set(nums_positions[num]):
                                if full:
                                    raise ValueError
                                so_far.add(each)
                                if len(so_far) == len(nums_positions[num]):
                                    full = True
                            checked.append(each)
                if full:
                    for position in positions:
                        for each in line[position]:
                            if each not in so_far:
                                line[position].remove(each)


def solve():
    holder = True
    last_sudoku = [[[[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
                   [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]]],
                   [[[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0], [0, 0, 0]]]]
    while holder:
        holder = False
        make_equal(sudoku, last_sudoku)
        limiting_possibilities_for_nums_in_squares()
        filling_in_els_only_met_once_squares()
        limiting_possibilities_for_nums_in_lines()
        filling_in_els_only_met_once_lines()
        limiting_possibilities_for_nums_in_squares()
        filling_in_els_only_met_once_squares()
        cleaning_els_met_on_the_same_row_in_a_square_from_the_rest_of_the_line()
        filling_in_els_only_met_once_squares()
        limiting_possibilities_for_nums_in_squares()
        limiting_els_in_third_square_if_number_is_met_only_within_the_same_2_rows_in_the_first_2_squares()
        filling_in_els_only_met_once_squares()
        limiting_possibilities_for_nums_in_lines()
        set_of_nums_met_within_the_same_places_at_most_lines()
        filling_in_els_only_met_once_lines()
        TransposeSudoku()
        limiting_possibilities_for_nums_in_lines()
        filling_in_els_only_met_once_lines()
        limiting_possibilities_for_nums_in_squares()
        filling_in_els_only_met_once_squares()
        cleaning_els_met_on_the_same_row_in_a_square_from_the_rest_of_the_line()
        filling_in_els_only_met_once_squares()
        limiting_possibilities_for_nums_in_squares()
        limiting_els_in_third_square_if_number_is_met_only_within_the_same_2_rows_in_the_first_2_squares()
        filling_in_els_only_met_once_squares()
        limiting_possibilities_for_nums_in_lines()
        set_of_nums_met_within_the_same_places_at_most_lines()
        filling_in_els_only_met_once_lines()
        error_in_lines()
        TransposeSudoku()
        limiting_possibilities_for_nums_in_squares()
        set_of_nums_met_within_the_same_places_at_most_squares()
        filling_in_els_only_met_once_squares()
        error_in_lines()
        for Row1 in sudoku:
            for square1 in Row1:
                for row1 in square1:
                    for el in row1:
                        if isinstance(el, list):
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
        if sudoku == last_sudoku and holder:
            for Row1 in range(3):
                for square1 in range(3):
                    for row1 in range(3):
                        for col1 in range(3):
                            if isinstance(sudoku[Row1][square1][row1][col1], list):
                                possible = [i for i in sudoku[Row1][square1][row1][col1]]
                                last_attempt = [[[[[], [], []], [[], [], []], [[], [], []]],
                                                 [[[], [], []], [[], [], []], [[], [], []]],
                                                 [[[], [], []], [[], [], []], [[], [], []]]],
                                                [[[[], [], []], [[], [], []], [[], [], []]],
                                                 [[[], [], []], [[], [], []], [[], [], []]],
                                                 [[[], [], []], [[], [], []], [[], [], []]]],
                                                [[[[], [], []], [[], [], []], [[], [], []]],
                                                 [[[], [], []], [[], [], []], [[], [], []]],
                                                 [[[], [], []], [[], [], []], [[], [], []]]]]
                                make_equal(sudoku, last_attempt)
                                for el in possible:
                                    sudoku[Row1][square1][row1][col1] = el
                                    try:
                                        solve()
                                        if solved():
                                            return
                                    except ValueError:
                                        last_attempt[Row1][square1][row1][col1].remove(el), make_equal(last_attempt, sudoku)
                                if not solved():
                                    raise ValueError


for Row in range(3):
    row, current = 0, None
    while row < 3:
        try:
            current = list(map(int, input(f'{3 * Row + row + 1}: ').split(maxsplit=9)))
            for square in range(3):
                sudoku[Row][square][row] = current[3 * square: 3 * square + 3]
            for n in current:
                if n != n % 10:
                    print('This isn\'t valid, enter line again!')
                    row -= 1
        except TypeError:
            print('This isn\'t valid, enter line again!')
            row -= 1
        row += 1
t1 = time() * 1000
solve()
t2 = time() * 1000
if not solved():
    raise ValueError('This sudoku is incorrect!')
print_sudoku(), print('Milliseconds:', t2 - t1)
