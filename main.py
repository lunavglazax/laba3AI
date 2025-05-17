import tkinter as tk
from tkinter import messagebox
import time

class SixPawnsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Игра: Шесть пешек (игрок = W, ИИ = B)")

        self.board = ['W'] * 6 + ['.'] + ['B'] * 6
        self.buttons = []
        self.selected_index = None

        self.status_label = tk.Label(root, text="Выберите белую фигуру (W)", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.board_frame = tk.Frame(root)
        self.board_frame.pack()

        self.draw_board()

    def draw_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        for i, cell in enumerate(self.board):
            btn = tk.Button(
                self.board_frame,
                text=cell,
                width=4,
                height=2,
                font=("Arial", 16),
                bg='white',
                command=lambda i=i: self.on_cell_click(i)
            )
            btn.grid(row=0, column=i, padx=2, pady=2)
            self.buttons.append(btn)

    def on_cell_click(self, index):
        if self.selected_index is None:
            if self.board[index] == 'W':
                self.selected_index = index
                self.buttons[index].config(bg='lightblue')
                self.status_label.config(text=f"Выбрана фигура W на позиции {index}")
        else:
            if self.try_move(self.selected_index, index):
                self.draw_board()
                if self.check_win():
                    messagebox.showinfo("Победа", "🎉 Вы победили!")
                    self.root.quit()
                else:
                    self.root.after(500, self.ai_move)  # AI ходит через 0.5 секунды
            else:
                self.status_label.config(text="❌ Неверный ход!")
            self.selected_index = None
            self.reset_button_colors()

    def reset_button_colors(self):
        for btn in self.buttons:
            btn.config(bg='white')

    def try_move(self, from_index, to_index):
        piece = self.board[from_index]
        if self.board[to_index] != '.':
            return False

        direction = 1 if piece == 'W' else -1

        # шаг
        if to_index == from_index + direction:
            self.make_move(from_index, to_index)
            return True

        # прыжок через одну
        if to_index == from_index + 2 * direction and self.board[from_index + direction] in ['W', 'B']:
            self.make_move(from_index, to_index)
            return True

        return False

    def make_move(self, from_index, to_index):
        self.board[to_index] = self.board[from_index]
        self.board[from_index] = '.'

    def check_win(self):
        return self.board == ['B'] * 6 + ['.'] + ['W'] * 6

    def ai_move(self):
        # AI ходит за 'B'
        for i, piece in enumerate(self.board):
            if piece == 'B':
                direction = -1
                one_step = i + direction
                jump_step = i + 2 * direction

                # шаг
                if 0 <= one_step < len(self.board) and self.board[one_step] == '.':
                    self.make_move(i, one_step)
                    self.status_label.config(text=f"ИИ сдвинул B с {i} на {one_step}")
                    self.draw_board()
                    if self.check_win():
                        messagebox.showinfo("Поражение", "ИИ победил!")
                        self.root.quit()
                    return

                # прыжок
                if (
                    0 <= jump_step < len(self.board)
                    and self.board[i + direction] in ['W', 'B']
                    and self.board[jump_step] == '.'
                ):
                    self.make_move(i, jump_step)
                    self.status_label.config(text=f"ИИ прыгнул B с {i} на {jump_step}")
                    self.draw_board()
                    if self.check_win():
                        messagebox.showinfo("Поражение", "ИИ победил!")
                        self.root.quit()
                    return

        self.status_label.config(text="ИИ: нет доступных ходов.")

# Запуск игры
if __name__ == "__main__":
    root = tk.Tk()
    game = SixPawnsGame(root)
    root.mainloop()
