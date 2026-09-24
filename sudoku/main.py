import tkinter as tk

from tkinter import ttk

from threading import Thread, Event

from queue import Queue, Empty

from solver import solve, format_sudoku

from time import time


class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")

        self.entries = [[None] * 9 for _ in range(9)]
        self.solution_queue = Queue()
        self.stop_event = Event()
        self.worker = None
        self.solution_count = 0

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        sudoku_frame = ttk.Frame(main)
        sudoku_frame.grid(row=0, column=0, padx=(0, 15), sticky="n")

        solutions_frame = ttk.Frame(main)
        solutions_frame.grid(row=0, column=1, sticky="nsew")
        solutions_frame.columnconfigure(0, weight=1)
        solutions_frame.rowconfigure(1, weight=1)

        main.columnconfigure(1, weight=1, minsize=400)
        main.rowconfigure(0, weight=1)

        for box_row in range(3):
            for box_col in range(3):
                box_frame = ttk.Frame(
                    sudoku_frame,
                    borderwidth=2,
                    relief="solid"
                )

                box_frame.grid(
                    row=box_row,
                    column=box_col,
                    padx=1,
                    pady=1
                )

                for row in range(3):
                    for col in range(3):
                        global_row = box_row * 3 + row
                        global_col = box_col * 3 + col

                        entry = ttk.Entry(
                            box_frame,
                            width=3,
                            justify="center"
                        )

                        entry.grid(
                            row=row,
                            column=col,
                            padx=1,
                            pady=1
                        )

                        entry.bind(
                            "<KeyRelease>",
                            lambda event, e=entry: self.normalize_entry(e)
                        )

                        self.entries[global_row][global_col] = entry

        buttons_frame = ttk.Frame(sudoku_frame)
        buttons_frame.grid(
            row=9,
            column=0,
            columnspan=9,
            pady=(12, 0),
            sticky="ew"
        )

        self.solve_button = ttk.Button(
            buttons_frame,
            text="Solve",
            command=self.start_solving
        )
        self.solve_button.grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="ew"
        )

        self.clear_button = ttk.Button(
            buttons_frame,
            text="Clear",
            command=self.clear
        )
        self.clear_button.grid(
            row=0,
            column=1,
            padx=(5, 0),
            sticky="ew"
        )

        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        ttk.Label(
            solutions_frame,
            text="Solutions"
        ).grid(row=0, column=0, sticky="w")

        self.solution_text = tk.Text(
            solutions_frame,
            width=45,
            height=35,
            state="disabled",
            font=("Courier New", 10)
        )
        self.solution_text.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            solutions_frame,
            orient="vertical",
            command=self.solution_text.yview
        )
        scrollbar.grid(row=1, column=1, sticky="ns")

        self.solution_text.configure(
            yscrollcommand=scrollbar.set
        )

    @staticmethod
    def normalize_entry(entry):
        if not entry.get():
            return

        try:
            value = int(entry.get())
        except ValueError:
            value = 0

        value %= 10

        entry.delete(0, tk.END)
        entry.insert(0, str(value))

    def get_sudoku(self):
        return [
            [
                [
                    [
                        int(self.entries[3 * band + row][3 * box + col].get() or 0) for col in range(3)
                    ]
                    for row in range(3)
                ]
                for box in range(3)
            ]
            for band in range(3)
        ]

    def start_solving(self):
        if self.worker is not None and self.worker.is_alive():
            return

        self.solution_count = 0
        self.stop_event.clear()

        self.clear_solution_text()

        sudoku = self.get_sudoku()

        self.worker = Thread(
            target=self.solve_worker,
            args=(sudoku,),
            daemon=True
        )
        self.worker.start()

        self.root.after(50, self.process_solution_queue)

    def solve_worker(self, sudoku):
        try:
            t = time()
            solve(sudoku,
                  on_solution=lambda solution:
                  self.solution_queue.put(
                      ("solution", solution, 1000 * (time() - t))
                  ),
                  stop_event=self.stop_event
                  )
            t = time() - t

            self.solution_queue.put(
                ("time", t)
            )

        except Exception as e:
            self.solution_queue.put(
                ("error", e)
            )

        finally:
            self.solution_queue.put(
                ("finished", None)
            )

    def process_solution_queue(self):
        try:
            while True:
                message = self.solution_queue.get_nowait()

                if message[0] == "solution":
                    solution, t = message[1:]
                    self.solution_count += 1

                    self.append_solution(
                        self.solution_count,
                        solution, t
                    )

                elif message[0] == "time":
                    self.append_text(
                        f"Finished in {message[1]:.3f} seconds.\n"
                    )

                elif message[0] == "error":
                    self.append_text(
                        f"Error: {message[1]}\n"
                    )

                elif message[0] == "finished":
                    self.worker = None

        except Empty:
            ...

        if self.worker is not None:
            self.root.after(50, self.process_solution_queue)

    def append_solution(self, number, solution, t):
        text = (
            f"Solution {number}\n"
            f"{format_sudoku(solution)}\n"
            f"Time: {t:.3f} miliseconds\n\n"
        )

        self.append_text(text)

    def append_text(self, text):
        self.solution_text.configure(state="normal")
        self.solution_text.insert(tk.END, text)
        self.solution_text.configure(state="disabled")
        self.solution_text.see(tk.END)

    def clear_solution_text(self):
        self.solution_text.configure(state="normal")
        self.solution_text.delete("1.0", tk.END)
        self.solution_text.configure(state="disabled")

    def clear(self):
        self.stop_event.set()

        self.clear_solution_text()

        for row in self.entries:
            for entry in row:
                entry.delete(0, tk.END)

        while True:
            try:
                self.solution_queue.get_nowait()

            except Empty:
                break


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
