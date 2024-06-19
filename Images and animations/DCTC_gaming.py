import tkinter as tk
import random
import keyboard
import winsound
import threading
from PIL import Image, ImageTk
import os
from tkinter import Frame

abspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

# Фоновая музыка
background_music_thread = None

# Функция фоновой музыки
def play_background_music():
    global background_music_thread, sound_enabled
    if sound_enabled:
        filename = f"{abspath}DCTC.wav"
        if background_music_thread is None or not background_music_thread.is_alive():
            background_music_thread = threading.Thread(target=winsound.PlaySound,
                                                       args=(filename, winsound.SND_ASYNC | winsound.SND_LOOP))
            background_music_thread.start()

# Глобальная переменная для отслеживания состояния звука
sound_enabled = True

# Функция для включения/выключения звука
def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    if sound_enabled:
        play_background_music()  # Если звук включен, воспроизвести музыку
    else:
        winsound.PlaySound(None, winsound.SND_PURGE)  # Если звук выключен, остановить музыку


# Создание игрового холста
root = tk.Tk()
root.title("Don't Crash The Car")
root.attributes('-fullscreen', True)
canvas = tk.Canvas(root)
canvas.pack()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
canvas_width = int(width * 0.7)
canvas_height = int(height * 0.7)
canvas.place(relx=0.5, rely=0.525, anchor='center', width=canvas_width, height=canvas_height)
root.config(width=canvas_width, height=canvas_height, bg="black")

# Загрузка изображений машин
player_car_image = tk.PhotoImage(file=f"{abspath}carmain.png")

enemy_list = ['police',
              'taxi',
              'sport',
              'car1',
              'car4',
              'car2',
              'car3',
              'car5',
              'car6']

enemy_car_images = [
    tk.PhotoImage(file=f"{abspath}{enemy}.png")
    for enemy in enemy_list
]

# Загрузка изображений для фона (дороги)
pil_image = Image.open(f"{abspath}road1.png")

# Растягивание изображений
width, height = pil_image.size
zoom_x, zoom_y = [round(canvas_width / width, 3),
                  round(canvas_height / height, 3) * 4]
pil_image = pil_image.resize((int(width * zoom_x), int(height * zoom_y)))

road = ImageTk.PhotoImage(pil_image)
road_images = [road]

# Анимация взрыва
poco_x3_path = f'{abspath}explosion.gif'
poco_x3_frames = Image.open(poco_x3_path).n_frames
image_frames_pack_poco_x3 = [tk.PhotoImage(file=poco_x3_path, format=f'gif -index {i}')
                             for i in range(poco_x3_frames)]

# Размеры машин
car_width = 42
car_height = 57

# Отступы для учета крайней части машины игрока
player_margin_x = 45  # Ширина машинки игрока
player_margin_y = 60  # Высота машинки игрока

# Позиция игрока
player_x = canvas_width // 2
player_y = canvas_height - player_margin_y - 10  # Оставляем небольшой отступ от нижней границы

# Скорость игрока
player_speed = 3

# Отображение фона на холсте
background_images = [canvas.create_image(canvas_width // 2, canvas_height, image=data[1])
                     for data in enumerate(road_images)]

# Смещение фона в начале игры
background_offset = 0

# Создание игрока
player = canvas.create_image(player_x, player_y, image=player_car_image, anchor=tk.CENTER)

# Флаг для отслеживания начала игры
game_started = False

# Флаг для отслеживания проигрыша
game_over_flag = False

# Счетчик очков
score = 0
score_label = tk.Label(canvas, text="Счёт: 0", bg="#BFBFBF", font=("Algerian", 12))
score_label.pack(pady=1.5)

# Создание списка вражеских машин
enemies = []

# Максимальное количество противников на экране
max_enemies = int(canvas_width / car_width * 0.315)

# Список координат всех активных машин противников
active_enemy_coordinates = []

# Функция создания противников
def create_enemy():
    if len(enemies) < max_enemies:
        x = random.randint(car_width // 2 + 15,
                           canvas_width - car_width // 2
                           if not canvas_width - car_width // 2 + car_width > canvas_width
                           else canvas_width - car_width - 5)
        y = 0
        enemy_image = random.choice(enemy_car_images)
        new_enemy_coords = (x, y)
        # Проверяем, чтобы новые координаты не пересекались с координатами других машин
        if all(
                abs(new_enemy_coords[0] - coord[0]) > car_width + 25
                or abs(new_enemy_coords[1] - coord[1]) > car_height + 25
                for coord in active_enemy_coordinates
        ):
            enemy = canvas.create_image(x, y, image=enemy_image, anchor=tk.CENTER)
            percentage = random.randint(1, 100)
            if percentage <= 20:
                speed = random.randint(1, 2)
            elif 20 < percentage <= 48:
                speed = random.randint(2, 3)
            elif 48 < percentage < 85:
                speed = 4
            else:
                speed = 5
            enemies.append({"id": enemy, "alive": True, "speed": speed})
            active_enemy_coordinates.append(new_enemy_coords)

# Функция движения игрока
def move_player():
    global player_x, player_y, game_started, canvas
    if game_started:
        if keyboard.is_pressed("a") and player_x > player_margin_x:  # Влево
            player_x -= player_speed
        if keyboard.is_pressed("d") and player_x < canvas_width - player_margin_x:  # Вправо
            player_x += player_speed
        if keyboard.is_pressed("w") and player_y > player_margin_y:  # Вперед
            player_y -= player_speed
        if keyboard.is_pressed("s") and player_y < canvas_height - player_margin_y:  # Назад
            player_y += player_speed
        canvas.coords(player, player_x, player_y)
    else:
        return
    root.after(10, move_player)  # Рекурсивный вызов функции для непрерывного отслеживания клавиш

# Функция движения вражеских машин
def move_enemies():
    global player_x, player_y, game_started, score, game_over_flag, canvas
    if game_started:
        create_enemy()
        enemies_to_remove = []

        for i, enemy in enumerate(enemies):
            if enemy["alive"]:
                try:
                    x, y = canvas.coords(enemy["id"])
                    if y > canvas_height:
                        enemy["alive"] = False
                        canvas.delete(enemy["id"])
                        enemies_to_remove.append(i)
                    else:
                        canvas.move(enemy["id"], 0, enemy["speed"])  # Двигаем машину вниз

                    # Проверяем столкновение с игроком
                    if (
                            player_x - player_margin_x < x + car_width / 2 and
                            player_x + player_margin_x > x - car_width / 2 and
                            player_y - player_margin_y < y + car_height / 2 and
                            player_y + player_margin_y > y - car_height / 2
                    ):
                        enemy["alive"] = False
                        game_over_flag = True  # Устанавливаем флаг проигрыша
                        winsound.PlaySound(None, winsound.SND_PURGE)  # Остановить фоновую музыку

                except tk.TclError:
                    pass

        for index in enemies_to_remove:
            if index < len(active_enemy_coordinates):
                active_enemy_coordinates.pop(index)

        enemies[:] = [enemy for enemy in enemies if enemy["alive"]]

        if game_over_flag:
            game_over()  # Вызываем функцию game_over, если игра окончена
        else:
            update_score(0.2)

        root.after(10, move_enemies)
    else:
        return

def show_poco_x3(count):
    global canvas, player_x, player_y, poco_x3_placeholder, image_frames_pack_poco_x3
    image = image_frames_pack_poco_x3[count]
    poco_x3_placeholder.configure(image=image)
    count += 1
    if count == poco_x3_frames:
        poco_x3_placeholder.destroy()
        return
    try:
        root.after(50, func=lambda: show_poco_x3(count))
    except tk.TclError:
        pass

# Добавьте глобальную переменную для хранения рекорда
high_score = 0

# Функция завершения игры
def game_over():
    global game_started, score_label, restart_button, canvas, poco_x3_placeholder, high_score
    game_started = False  # Останавливаем игру
    poco_x3_placeholder = tk.Label(canvas, image='')
    poco_x3_placeholder.place()
    poco_x3_placeholder.pack()
    show_poco_x3(0)
    restart_button = tk.Button(button_frame, text="Начать заново",
                               bg="#BFBFBF", width=16, height=2,
                               command=game_restart, font=("Arial", 12, "bold"))
    restart_button.pack(side=tk.LEFT, padx=10)  # Добавляем горизонтальный отступ между кнопками
    restart_button.pack(side=tk.LEFT)  # Используем side=tk.LEFT для расположения кнопок в линию
    canvas.delete("all")
     # Задаем цвет фона
    canvas.configure(bg='#fcfefc')
    canvas.create_text(canvas_width // 2, canvas_height // 2.7, text="ИГРА ОКОНЧЕНА", font=("Algerian", 24))
    canvas.create_text(canvas_width // 2, canvas_height // 2.2 + 40, text="Ваш счёт - " + str(int(score)),
                       font=("Algerian", 20))
    # Обновляем рекорд, если текущий счет больше рекорда
    if score > high_score:
        high_score = score
    # Отображаем рекорд
    canvas.create_text(canvas_width // 2, canvas_height // 2.2 + 80, text="Ваш личный рекорд - " + str(int(high_score)),
                       font=("Algerian", 20))
    score_label.pack_forget()

# Функция перезапуска игры
def game_restart():
    global game_started, player, restart_button, score, score_label, canvas, enemies, player_car_image, background_images, road_images, active_enemy_coordinates, player_x, player_y
    game_started = True
    enemies = []
    active_enemy_coordinates = []
    score = 0
    restart_button.destroy()
    canvas.delete("all")
    canvas.destroy()
    canvas = tk.Canvas(root)
    canvas.pack()
    canvas.place(relx=0.5, rely=0.525, anchor='center',
                 width=canvas_width, height=canvas_height)
    canvas.config(highlightbackground='white')
    background_images = [canvas.create_image(canvas_width // 2, canvas_height * i, image=image)
                         for i, image in enumerate(road_images)]
    player_x = canvas_width // 2
    player_y = canvas_height - player_margin_y - 10  # Оставляем небольшой отступ от нижней границы
    player = canvas.create_image(player_x, player_y, image=player_car_image, anchor=tk.CENTER)
    score_label = tk.Label(canvas, text="Счёт: 0", bg="#BFBFBF", font=("Algerian", 12))
    score_label.pack(pady=3)
    start_game()

# Функция для движения фона (дороги)
def move_background():
    global game_started, background_images, road_images, canvas
    if game_started:
        canvas.move(background_images[0], 0, 12)
        try:
            x, y = canvas.coords(background_images[0])
        except ValueError:
            background_images = [canvas.create_image(canvas_width // 2, canvas_height, image=image)
                                 for i, image in enumerate(road_images)]
            x, y = canvas.coords(background_images[0])
        if y >= canvas_height:
            prev_image_index = (0 - 1) % len(background_images)
            _, prev_y = canvas.coords(background_images[prev_image_index])
            canvas.coords(background_images[0], canvas_width // 2, prev_y - canvas_height)

        root.after(15, move_background)
    else:
        return

# Функция для обновления счета
def update_score(points):
    global score, score_label
    score += points
    if score_label is not None:
        score_label.config(text="Счёт: " + str(int(score)))

# Запуск игры
def start_game():
    global game_started, score_label, game_over_flag, restart_button
    canvas.itemconfig(title_text, state=tk.HIDDEN)
    game_started = True
    game_over_flag = False  # Сброс флага проигрыша
    move_enemies()  # Запускаем функцию для движения противников
    move_background()  # Запускаем функцию для движения фона
    move_player()  # Запускаем функцию для управления игроком
    sound_enabled = True  # Изначально звук включен
    background_music_thread = None  # Переменная для отслеживания фоновой музыки
    if start_button is not None:
        start_button.destroy()
    play_background_music()  # Вызываем функцию для проигрывания музыки при запуске игры

# Создаем рамку для размещения кнопок
button_frame = Frame(root, bg="black")
button_frame.pack(pady=40)  # pady для добавления вертикального отступа

title_text = canvas.create_text(canvas_width // 2, canvas_height // 3, text="Don't Crash The Car",
                                font=("Courier New", 40, "bold"),
                                fill="Black")

sound_enabled = True  # Изначально звук включен
background_music_thread = None  # Переменная для отслеживания фоновой музыки

sound_button = tk.Button(button_frame, text="Музыка вкл/выкл", bg="#BFBFBF", width=16, height=2, command=toggle_sound,
                         font=("Arial", 12, "bold"))
sound_button.pack(side=tk.LEFT, padx=10)  # Добавляем горизонтальный отступ между кнопками
sound_button.pack(side=tk.LEFT)  # Используем side=tk.LEFT для расположения кнопок в линию

start_button = tk.Button(button_frame, text="Играть", bg="#BFBFBF", width=16, height=2, command=start_game,
                         font=("Arial", 12, "bold"))
start_button.pack(side=tk.LEFT, padx=10)  # Добавляем горизонтальный отступ между кнопками
start_button.pack(side=tk.LEFT)  # Используем side=tk.LEFT для расположения кнопок в линию

exit_button = tk.Button(button_frame, text="Выход", bg="#BFBFBF", width=16, height=2, command=root.destroy,
                        font=("Arial", 12, "bold"))
exit_button.pack(side=tk.LEFT, padx=10)  # Добавляем горизонтальный отступ между кнопками
exit_button.pack(side=tk.LEFT)  # Используем side=tk.LEFT для расположения кнопок в линию
restart_button: tk.Button = None

root.mainloop()