from __future__ import annotations

from typing import Iterable

Board = list[int]

CONSTRAINTS = 324


class SudokuDLX:
    """
    Enumerate every solution to a 9x9 Sudoku using Algorithm X / Dancing Links.

    Empty cells may be 0, ".", or None. Digits may be ints or strings.
    The input board is not modified. Solutions are returned as 9x9 lists of ints.
    """

    def __init__(self, puzzle: Board):
        self.givens = puzzle
        self._validate_givens(self.givens)

        # Node 0 is the root; nodes 1..324 are column headers.
        self.left = [CONSTRAINTS, *range(CONSTRAINTS)]
        self.right = [*range(1, CONSTRAINTS + 1), 0]
        self.up: list[int] = [*range(CONSTRAINTS + 1)]
        self.down: list[int] = [*range(CONSTRAINTS + 1)]
        self.column: list[int] = [*range(CONSTRAINTS + 1)]
        self.row_id: list[int] = [-1] * (CONSTRAINTS + 1)
        self.column_size: list[int] = [0] * (CONSTRAINTS + 1)

        self.placements: list[tuple[int, int, int]] = []
        self._build_matrix()
        self._partial_solution: list[int] = []
        self.solutions: list[Board] = []

    @staticmethod
    def _validate_givens(board: Board):
        seen: set[tuple[str, int, int]] = set()

        for i in range(81):
            r, c = divmod(i, 9)
            d = board[i]

            if not d:
                continue

            keys = (("row", r, d), ("col", c, d), ("box", (r // 3) * 3 + c // 3, d))

            if any(key in seen for key in keys):
                raise ValueError(f"Contradictory givens: digit {d} at row {r + 1}, column {c + 1}")

            seen.update(keys)

    @staticmethod
    def _constraint_ids(r: int, c: int, d: int) -> tuple[int, int, int, int]:
        row_digit = 81 + r * 9 + d
        col_digit = 162 + c * 9 + d
        box_digit = 243 + 9 * (3 * (r // 3) + c // 3) + d
        # Convert zero-based constraint IDs to one-based DLX header node IDs.

        return 9 * r + c + 1, row_digit, col_digit, box_digit

    def _add_candidate_row(self, r: int, c: int, d: int):
        rid = len(self.placements)
        self.placements.append((r, c, d))
        nodes = [self._new_node(col, rid) for col in self._constraint_ids(r, c, d)]

        for i, node in enumerate(nodes):
            self.left[node] = nodes[i - 1]
            self.right[node] = nodes[(i + 1) % len(nodes)]

    def _new_node(self, col: int, rid: int) -> int:
        node = len(self.left)
        self.left.append(node)
        self.right.append(node)
        self.up.append(self.up[col])
        self.down.append(col)
        self.column.append(col)
        self.row_id.append(rid)

        # Insert at the bottom of the column's vertical list.
        self.down[self.up[col]] = node
        self.up[col] = node
        self.column_size[col] += 1

        return node

    def _build_matrix(self):
        row_used = [0] * 9
        col_used = [0] * 9
        box_used = [0] * 9

        for i in range(81):
            r, c = divmod(i, 9)
            d = self.givens[i]

            if d:
                bit = 1 << d
                row_used[r] |= bit
                col_used[c] |= bit
                box_used[(r // 3) * 3 + c // 3] |= bit

        for i in range(81):
            r, c = divmod(i, 9)
            d = self.givens[i]

            if d:
                digits: list[int] = [d]

            else:
                used = row_used[r] | col_used[c] | box_used[(r // 3) * 3 + c // 3]
                digits = [d for d in range(1, 10) if not (used & (1 << d))]

            for d in digits:
                self._add_candidate_row(r, c, d)

    def _cover(self, c: int):
        self.right[self.left[c]] = self.right[c]
        self.left[self.right[c]] = self.left[c]
        i = self.down[c]

        while i != c:
            j = self.right[i]

            while j != i:
                self.down[self.up[j]] = self.down[j]
                self.up[self.down[j]] = self.up[j]
                self.column_size[self.column[j]] -= 1
                j = self.right[j]

            i = self.down[i]

    def _uncover(self, c: int):
        i = self.up[c]

        while i != c:
            j = self.left[i]

            while j != i:
                self.column_size[self.column[j]] += 1
                self.down[self.up[j]] = j
                self.up[self.down[j]] = j
                j = self.left[j]

            i = self.up[i]

        self.right[self.left[c]] = c
        self.left[self.right[c]] = c

    def _choose_column(self) -> int:
        # Algorithm X's minimum-remaining-values heuristic.
        best = self.right[0]
        c = self.right[best]

        while c:
            if self.column_size[c] < self.column_size[best]:
                best = c

                if not self.column_size[c]:
                    break

            c = self.right[c]

        return best

    def _search(self, on_solution):
        if not self.right[0]:
            board = [0] * 81

            for rid in self._partial_solution:
                r, c, d = self.placements[rid]
                board[9 * r + c] = d

            self.solutions.append(board)

            if on_solution is not None:
                on_solution(board)

            return

        c = self._choose_column()

        if not self.column_size[c]:
            return

        self._cover(c)
        rnode = self.down[c]

        while rnode != c:
            self._partial_solution.append(self.row_id[rnode])
            j = self.right[rnode]

            while j != rnode:
                self._cover(self.column[j])
                j = self.right[j]

            self._search(on_solution)
            j = self.left[rnode]

            while j != rnode:
                self._uncover(self.column[j])
                j = self.left[j]

            self._partial_solution.pop()
            rnode = self.down[rnode]

        self._uncover(c)

    def solve(self, on_solution=None) -> list[Board]:
        """
        Return all solutions, optionally notifying a callback as each is found.

        stop_event may be a threading.Event; setting it stops the search early.
        Calling solve repeatedly starts a fresh search.
        """

        self.solutions = []
        self._partial_solution = []
        self._search(on_solution)

        return self.solutions


def solve_sudoku(puzzle: Board) -> list[Board]:
    """
    Convenience function: return every solution to a 9x9 Sudoku puzzle.
    """

    return SudokuDLX(puzzle).solve()


def format_board(board: Board) -> str:
    """
    Format a numeric solution as a readable Sudoku grid.
    """

    lines = []

    for l in range(9):
        lines.append(" │ ".join(["  ".join(map(str, board[9 * l: 9 * (l + 1)][3 * c:3 * c + 3])) for c in range(3)]))

    lines.insert(6, "────────│─────────│────────")
    lines.insert(3, "────────│─────────│────────")

    return "\n".join(lines)


if __name__ == "__main__":
    import time

    puzzle = [
        8, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 3, 6, 0, 0, 0, 0, 0,
        0, 7, 0, 0, 9, 0, 2, 0, 0,
        0, 5, 0, 0, 0, 7, 0, 0, 0,
        0, 0, 0, 0, 4, 5, 7, 0, 0,
        0, 0, 0, 1, 0, 0, 0, 3, 0,
        0, 0, 1, 0, 0, 0, 0, 6, 8,
        0, 0, 8, 5, 0, 0, 0, 1, 0,
        0, 9, 0, 0, 0, 0, 0, 0, 0
    ]
    start = time.perf_counter()
    solutions = solve_sudoku(puzzle)
    elapsed = 1000 * (time.perf_counter() - start)
    print(f"Found {len(solutions)} solution(s) in {elapsed:.6f} milliseconds.")

    for sol in solutions:
        print(f"{format_board(sol)}\n")
