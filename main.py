import tkinter as tk
from tkinter import messagebox
import copy

class SixPawnsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("6 Пешек: Игрок (W) vs AI (B) - Minimax")

        self.board = ['W'] * 6 + ['.'] + ['B'] * 6
        self.buttons = []
        self.selected_index = None
        self.player_first = True
        self.is_player_turn = True

        self.board_frame = tk.Frame(root)
        self.status_label = tk.Label(root, text="Выберите белую фигуру (W)", font=("Arial", 14))

        self.create_menu()

    def start_game(self):
        self.status_label.pack(pady=10)
        self.board_frame.pack()
        self.draw_board()
        self.is_player_turn = self.player_first
        self.update_status()
        if not self.player_first:
            self.root.after(500, self.ai_move_minimax)

    def create_menu(self):
        top = tk.Toplevel(self.root)
        top.title("Выбор игрока")
        tk.Label(top, text="Кто ходит первым?", font=("Arial", 14)).pack(pady=10)
        tk.Button(top, text="Игрок (W)", font=("Arial", 12), command=lambda: self.set_first_player(True, top)).pack(pady=5)
        tk.Button(top, text="ИИ (B)", font=("Arial", 12), command=lambda: self.set_first_player(False, top)).pack(pady=5)

    def set_first_player(self, is_player, window):
        self.player_first = is_player
        window.destroy()
        self.start_game()

    def draw_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        possible_moves = self.get_possible_moves('W') if self.is_player_turn else []
        for i, cell in enumerate(self.board):
            color = 'white'
            if self.selected_index is not None:
                # Подсветка выбранной фигуры
                if i == self.selected_index:
                    color = 'lightblue'
                # Подсветка возможных ходов
                elif (self.selected_index, i) in possible_moves:
                    color = 'lightgreen'

            btn = tk.Button(
                self.board_frame,
                text=cell,
                width=4,
                height=2,
                font=("Arial", 16),
                bg=color,
                command=lambda i=i: self.on_cell_click(i)
            )
            btn.grid(row=0, column=i, padx=2, pady=2)
            self.buttons.append(btn)

    def update_status(self, message=None):
        if message:
            self.status_label.config(text=message)
            return
        if self.is_player_turn:
            self.status_label.config(text="Ваш ход (W). Выберите фигуру.")
        else:
            self.status_label.config(text="Ход ИИ (B)...")

    def on_cell_click(self, index):
        if not self.is_player_turn:
            return

        # Если ничего не выбрано и нажали на свою фигуру — выбрать её
        if self.selected_index is None:
            if self.board[index] == 'W':
                self.selected_index = index
                self.status_label.config(text=f"Выбрана фигура W на позиции {index}")
                self.draw_board()
        else:
            # Если кликнули по той же фигуре — отмена выбора
            if index == self.selected_index:
                self.selected_index = None
                self.update_status()
                self.draw_board()
                return

            # Попытка сделать ход
            if self.try_move(self.board, self.selected_index, index, 'W'):
                self.draw_board()
                if self.check_win(self.board):
                    messagebox.showinfo("Победа", "🎉 Вы победили!")
                    self.root.quit()
                else:
                    self.is_player_turn = False
                    self.selected_index = None
                    self.update_status()
                    self.root.after(500, self.ai_move_minimax)
            else:
                self.status_label.config(text="❌ Неверный ход!")
                self.draw_board()
                self.selected_index = None
                self.update_status()

    def try_move(self, board, from_index, to_index, player):
        if board[to_index] != '.':
            return False

        direction = 1 if player == 'W' else -1

        # Простой ход на 1 клетку вперед
        if to_index == from_index + direction:
            self.make_move(board, from_index, to_index)
            return True

        # Прыжок через фигуру соперника
        if to_index == from_index + 2 * direction:
            mid_index = from_index + direction
            # Прыжок возможен только через фигуру противника
            opponent = 'B' if player == 'W' else 'W'
            if board[mid_index] == opponent and board[to_index] == '.':
                self.make_move(board, from_index, to_index)
                return True

        return False

    def make_move(self, board, from_index, to_index):
        board[to_index] = board[from_index]
        board[from_index] = '.'

    def check_win(self, board):
        # Проверка, что фигуры поменялись местами полностью
        return board == ['B'] * 6 + ['.'] + ['W'] * 6

    def ai_move_minimax(self):
        moves = self.get_possible_moves('B')
        if not moves:
            messagebox.showinfo("Победа", "🎉 Вы победили! (ИИ сдался)")
            self.root.quit()
            return

        _, move = self.minimax(self.board, 4, True)
        if move:
            self.try_move(self.board, move[0], move[1], 'B')
            self.draw_board()
            if self.check_win(self.board):
                messagebox.showinfo("Поражение", "ИИ победил!")
                self.root.quit()
            else:
                self.is_player_turn = True
                self.update_status()
        else:
            # Нет ходов — игрок выигрывает
            messagebox.showinfo("Победа", "🎉 Вы победили! (ИИ не нашёл ходов)")
            self.root.quit()

    def evaluate(self, board):
        # Если выиграл ИИ — максимальная оценка
        if board == ['B'] * 6 + ['.'] + ['W'] * 6:
            return 9999
        # Если выиграл игрок — минимальная оценка
        if board == ['W'] * 6 + ['.'] + ['B'] * 6:
            return -9999
        # Считаем сумму позиций для B и W (чем ближе к своей цели — тем лучше)
        b_score = sum((12 - i) for i, p in enumerate(board) if p == 'B')
        w_score = sum(i for i, p in enumerate(board) if p == 'W')
        return b_score - w_score

    def get_possible_moves(self, player):
        moves = []
        direction = 1 if player == 'W' else -1
        for i, piece in enumerate(self.board):
            if piece != player:
                continue
            one_step = i + direction
            if 0 <= one_step < len(self.board) and self.board[one_step] == '.' and one_step - i == direction:
                moves.append((i, one_step))
            jump_step = i + 2 * direction
            opponent = 'B' if player == 'W' else 'W'
            if (
                0 <= jump_step < len(self.board)
                and self.board[i + direction] == opponent
                and self.board[jump_step] == '.'
                and jump_step - i == 2 * direction
            ):
                moves.append((i, jump_step))
        return moves

    def generate_moves(self, board, player):
        moves = []
        direction = 1 if player == 'W' else -1
        for i, piece in enumerate(board):
            if piece != player:
                continue
            one_step = i + direction
            if 0 <= one_step < len(board) and board[one_step] == '.' and one_step - i == direction:
                new_board = copy.deepcopy(board)
                self.make_move(new_board, i, one_step)
                moves.append((new_board, (i, one_step), 1))  # 1 — простой шаг
            jump_step = i + 2 * direction
            opponent = 'B' if player == 'W' else 'W'
            if (
                0 <= jump_step < len(board)
                and board[i + direction] == opponent
                and board[jump_step] == '.'
                and jump_step - i == 2 * direction
            ):
                new_board = copy.deepcopy(board)
                self.make_move(new_board, i, jump_step)
                moves.append((new_board, (i, jump_step), 2))  # 2 — прыжок
        return moves

    def minimax(self, board, depth, maximizing_player):
        if depth == 0 or self.check_win(board):
            return self.evaluate(board), None

        player = 'B' if maximizing_player else 'W'
        best_move = None

        if maximizing_player:
            max_eval = float('-inf')
            for new_board, move, move_type in self.generate_moves(board, player):
                eval, _ = self.minimax(new_board, depth - 1, False)
                # Штраф за прыжок (чтобы ИИ предпочитал простые ходы)
                if move_type == 2:
                    eval -= 5
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for new_board, move, move_type in self.generate_moves(board, player):
                eval, _ = self.minimax(new_board, depth - 1, True)
                if move_type == 2:
                    eval += 5
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

if __name__ == "__main__":
    root = tk.Tk()
    game = SixPawnsGame(root)
    root.mainloop()
