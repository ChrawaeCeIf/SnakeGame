import time
import threading
import random
from gameKeyboardControl import gameKeyboardControl, KeyboardControl
from pynput import keyboard
import os


class SnakeGame:
    def __init__(self):
        self.rows, self.cols = 20, 85  # Под размер 85x20
        self.score = 0
        self.game_zone = self.init_game_zone()
        self.current_direction = 'w'  # Начальное направление: вверх
        self.last_direction = 'w'
        self.running = True
        self.game_over = False
        self.lock = threading.Lock()

    def init_game_zone(self):
        zone = [[0] * self.cols for _ in range(self.rows)]

        # Инициализация змейки из 5 клеток
        start_row, start_col = self.rows // 2, self.cols // 2
        snake_positions = [
            (start_row, start_col),
            (start_row, start_col - 1),
            (start_row, start_col - 2),
            (start_row, start_col - 3),
            (start_row, start_col - 4),
        ]

        # Размещаю змейку (голова = 5, хвост = 1)
        for i, (r, c) in enumerate(snake_positions):
            zone[r][c] = len(snake_positions) - i

        # Размещаю начальную еду
        self.spawn_food(zone, 10)
        return zone

    def spawn_food(self, zone, food_count):
        filled_cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if zone[r][c] != 0:
                    filled_cells.append((r, c))

        free_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)
                      if (r, c) not in filled_cells and zone[r][c] != -1]

        # Не более 10 единиц еды на поле
        existing_food = sum(1 for r in range(self.rows) for c in range(self.cols) if zone[r][c] == -1)
        food_to_spawn = min(food_count, 10 - existing_food, len(free_cells))

        if food_to_spawn > 0 and free_cells:
            food_positions = random.sample(free_cells, food_to_spawn)
            for r, c in food_positions:
                zone[r][c] = -1

    def update_game_zone(self, zone):
        for r in range(self.rows):
            for c in range(self.cols):
                if zone[r][c] > 0:
                    zone[r][c] -= 1
        return zone

    def find_head_position(self, zone):
        max_val = 0
        head_pos = (0, 0)
        for r in range(self.rows):
            for c in range(self.cols):
                if zone[r][c] > max_val:
                    max_val = zone[r][c]
                    head_pos = (r, c)
        return head_pos

    def calculate_speed(self):
        snake_length = self.score + 5  # Начальная длина + съеденная еда

        if snake_length <= 10:
            return 600  # 600 мс
        elif snake_length >= 30:
            return 300  # 300 мс
        else:
            progress = (snake_length - 10) / 20
            return 600 - (300 * progress)

    def get_next_position(self, head_row, head_col, direction):
        if direction == 'w':  # вверх
            next_row = (head_row - 1) % self.rows
            next_col = head_col
        elif direction == 's':  # вниз
            next_row = (head_row + 1) % self.rows
            next_col = head_col
        elif direction == 'a':  # влево
            next_row = head_row
            next_col = (head_col - 1) % self.cols
        elif direction == 'd':  # вправо
            next_row = head_row
            next_col = (head_col + 1) % self.cols
        else:
            next_row, next_col = head_row, head_col

        return next_row, next_col

    def is_opposite_direction(self, dir1, dir2):
        # Проверяю, являются ли направления противоположными
        opposites = {'w': 's', 's': 'w', 'a': 'd', 'd': 'a'}
        return dir2 == opposites.get(dir1, '')


    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')


    def game_driver(self):
        with self.lock:
            if self.game_over:
                return

            # Нахожу текущую голову
            head_row, head_col = self.find_head_position(self.game_zone)

            # Проверяю противоположное направление
            if not self.is_opposite_direction(self.last_direction, self.current_direction):
                self.last_direction = self.current_direction

            # Вычисляю следующую позицию
            next_row, next_col = self.get_next_position(head_row, head_col, self.last_direction)

            # Проверка столкновения с собой
            if self.game_zone[next_row][next_col] > 0:
                self.game_over = True
                return

            # Обработка движения
            if self.game_zone[next_row][next_col] == -1:  # Еда
                self.score += 1
                self.game_zone[next_row][next_col] = self.score + 5  # Новая голова
                self.spawn_food(self.game_zone, 1)
            else:  # Пустая клетка
                self.game_zone = self.update_game_zone(self.game_zone)
                self.game_zone[next_row][next_col] = self.score + 5  # Новая голова

    def print_game_zone(self):
        # print(f"\033[HSCORE: {self.score} | LENGTH: {self.score + 5} | SPEED: {self.calculate_speed()}ms")
        self.clear()
        print(f"SCORE: {self.score} | LENGTH: {self.score + 5} | SPEED: {self.calculate_speed()}ms")
        print("Use WASD to control, ESC to exit")
        print("=" * 85)

        for row in self.game_zone:
            line = ""
            for cell in row:
                if cell > 0:  # Часть тела змеи
                    line += "🟩"
                elif cell == -1:  # Еда
                    line += "🟥"
                else:  # Пустота
                    line += "⬛"
            print(line)

    def input_thread(self):
        listener = KeyboardControl()
        while self.running:
            key = gameKeyboardControl()

            if key == keyboard.Key.esc:
                self.running = False
                break
            elif hasattr(key, 'char'):
                with self.lock:
                    if key.char in ['w', 'a', 's', 'd']:
                        self.current_direction = key.char

            time.sleep(0.05)

    def game_thread(self):
        print("\033[2J")  # Очистка консоли один раз

        while self.running and not self.game_over:
            start_time = time.time()

            self.game_driver()

            if self.game_over:
                print("\nGAME OVER! Final score:", self.score)
                self.running = False
                break


            print("\033[2J")
            self.print_game_zone()

            # Динамическая задержка
            sleep_time = self.calculate_speed() / 1000.0  # мс в секунды
            elapsed = time.time() - start_time
            remaining = max(0, sleep_time - elapsed)
            time.sleep(remaining)

    def run(self):
        print("Starting Snake Game...")

        # Запускаем поток ввода
        input_thread = threading.Thread(target=self.input_thread)
        input_thread.daemon = True
        input_thread.start()

        # Запускаем игровой поток
        self.game_thread()

        input_thread.join(timeout=1.0)
        print("Game finished!")


def main():
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()