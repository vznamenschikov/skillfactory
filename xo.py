# Крестики-нолики https://ru.wikipedia.org/wiki/Крестики-нолики

# Нумерация игрового поля
xo_board = [1, 2, 3,
            4, 5, 6,
            7, 8, 9]

all_board = [1,2,3,4,5,6,7,8,9] # Все возможные варианты

# Варианты выигрышных комбинаций
winner = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

x_step1val = None  # Адрес клетки на первом ходе для игрока Х
x_step2val = None  # Адрес клетки на втором ходе для игрока Х
x_step = None  # Номер хода игрока Х
o_step_val = None  # Адрес клетки для игрока O

o_step_next_val = []  # Адреса клеток для игрока O для следующих шагов


# Печать игрового поля на экран
def print_xo_board():
    print(xo_board[0], "", xo_board[1], "", xo_board[2])
    print(xo_board[3], "", xo_board[4], "", xo_board[5])
    print(xo_board[6], "", xo_board[7], "", xo_board[8])
    print()


# Проверка победителя
def check_winner():
    who_win = ""
    for i in winner:
        if xo_board[i[0]] == "X" and xo_board[i[1]] == "X" and xo_board[i[2]] == "X":
            who_win = "X"
        if xo_board[i[0]] == "O" and xo_board[i[1]] == "O" and xo_board[i[2]] == "O":
            who_win = "O"

    if step == None:
        who_win = "ничья"
        game_end = True
    return who_win


# Добавление символа в ячейку
def put_to_xo_board(cell_, mark):

    global xo_board
    global o_step_val



    if cell_is_empty(cell_):
        xo_board[cell_ - 1] = mark
        return True
    else:
        # print("Ячейка уже заполнена.")
        return False


def cell_is_empty(cell_):

    if cell_ in range(1, 10):
        if xo_board[cell_ - 1] in range(1, 10):
            return True
        else:
            return False



def o_step_forward(force_ = None):
    global o_step_val

    if len(o_step_next_val) > 0:

        while len(o_step_next_val) > 0:
            if cell_is_empty(o_step_next_val[0]):
                o_step_val = o_step_next_val[0]
                o_step_next_val.pop(0)
                return o_step_val
            else:
                o_step_next_val.pop(0)


    elif o_step_val == None or force_ == True:
        while len(all_board) > 0:
            if cell_is_empty(all_board[0]):
                o_step_val = all_board[0]
                all_board.pop(0)
                return o_step_val
            else:
                all_board.pop(0)




# Обработка ИИ ==========================================
def gpt_step():

    # Проверяем, был ли заказан следующий ход для игрока O заранее. Если да - выполняем его
    global o_step_next_val
    global o_step_val


    if len(o_step_next_val) > 0:
        o_step_val = o_step_forward()
        return o_step_val

    # | | | |       |O| |O|      | |O| |
    # | |X| |  -->  | |X| |  or  |O| |O|
    # | | | |       |O| |O|      | |O| |
# Если крестики сделали первый ход в центр, до конца игры ходить в любой угол, а если это невозможно — в любую клетку.
    if x_step == 1 and x_step1val == 5:  # if cell5: Если Х пошел на 5-ю клетку на первом ходу
        o_step_val = 1
        o_step_next_val = [3, 7, 9, 2, 4, 6, 8]


    # |X| |X|       |X| |X|       |X| | |      | |O| |
    # | | | |  -->  | |O| |  -->  | | | |  or  |O|-|O|
    # |X| |X|       |X| |X|       | | |O|      | |O| |
# Если крестики сделали первый ход в угол, ответить ходом в центр. Следующим ходом занять угол, противоположный первому
# ходу крестиков, а если это невозможно — пойти на сторону.
    elif x_step == 1 and (
            x_step1val == 1 or x_step1val == 3 or x_step1val == 7 or x_step1val == 9):  # if cell1 or 3 or 7 or 9:
        o_step_val = 5  # step to cell5
        if x_step1val == 1:
            o_step_next_val = [9, 2, 4, 6, 8, 3, 7]  # затем в противоположный угол
        elif x_step1val == 3:
            o_step_next_val = [7, 2, 4, 6, 8, 9, 1]
        elif x_step1val == 7:
            o_step_next_val = [3, 2, 4, 6, 8, 1, 9]
        elif x_step1val == 9:
            o_step_next_val = [1, 2, 4, 6, 8, 7, 3]



    # 1. Если крестики сделали первый ход на сторону (не в центр и не в угол), ответить ходом в центр.
    # 2. Далее отвечать в зависимости от второго хода крестиков:
    #    Если следующий ход крестиков — в угол, занять противоположный угол.
    # 3. Если следующий ход крестиков — на противоположную сторону, пойти в любой угол.
    # 4. Если следующий ход крестиков — на сторону рядом с их первым ходом, пойти в угол рядом с обоими крестиками.
    #    Возможные позиции после двух ходов показаны на диаграммах.
    # | |X| |       | |X| |       |X| | |      | |X| |       | |X| |       |O| |O|      | |X| |       | |X|X|       |O|X|X|
    # |X| |X| -1->  |X|O|X| -2->  | | | |  or  | |O| |       | |O| | -3->  | | | |  or  | | | | -4->  | | | | --->  | | | |
    # | |X| |       | |X| |       | | |O|      | | | |       | |X| |       |O| |O|      | | | |       | | | |       | | | |

    # Если крестики сделали первый ход на сторону
    elif x_step == 1 and (x_step1val == 2 or x_step1val == 4 or x_step1val == 6 or x_step1val == 8):
        o_step_val = 5  # ответить ходом в центр

    # Обработка второго хода Х предыдущей комбинации
    # Если следующий ход крестиков — в угол, занять противоположный угол.?????????????????
    #????????????? ЛОГИКА СТРАННАЯ ????????????
#    elif x_step == 2 and (x_step1val == 2 or x_step1val == 4 or x_step1val == 6 or x_step1val == 8):
#        if x_step2val == 1 or x_step2val == 3 or x_step2val == 7 or x_step2val == 9:
#            if x_step2val == 1:
#                o_step_val = 9
#                o_step_next_val = [2, 3, 4, 5, 6, 7, 8]
#
#            elif x_step2val == 3:
#                o_step_val = 7
#                o_step_next_val = [1, 2, 4, 5, 6, 8, 9]
#
#            if x_step2val == 7:
#                o_step_val = 3
#                o_step_next_val = [1, 2, 4, 5, 6, 8, 9]
#
#            if x_step2val == 9:
#                o_step_val = 1
#                o_step_next_val = [2, 3, 4, 5, 6, 7, 8]

    # Если следующий ход крестиков — на противоположную сторону, пойти в любой угол.
    elif x_step == 2 and \
            ((x_step1val == 2 and x_step2val == 8) or \
             (x_step1val == 4 and x_step2val == 6) or \
             (x_step1val == 6 and x_step2val == 4) or \
             (x_step1val == 8 and x_step2val == 2)):
        o_step_val = 1
        o_step_next_val = [3, 7, 9, 2, 4, 5, 6, 8]  # углы - это 1,3,7,9

    # Если следующий ход крестиков — на сторону рядом с их первым ходом, пойти в угол рядом с обоими крестиками.
    elif x_step == 2 and \
            ((x_step1val == 2 and (x_step2val == 1 or x_step2val == 3)) or \
             (x_step1val == 4 and (x_step2val == 1 or x_step2val == 7)) or \
             (x_step1val == 6 and (x_step2val == 3 or x_step2val == 9)) or \
             (x_step1val == 8 and (x_step2val == 7 or x_step2val == 9))):
        if x_step1val == 2 and x_step2val == 1:
            o_step_val = 3
        elif x_step1val == 2 and x_step2val == 3:
            o_step_val = 1
        elif x_step1val == 4 and x_step2val == 1:
            o_step_val = 7
        elif x_step1val == 4 and x_step2val == 7:
            o_step_val = 1
        elif x_step1val == 6 and x_step2val == 3:
            o_step_val = 9
        elif x_step1val == 6 and x_step2val == 9:
            o_step_val = 3
        elif x_step1val == 8 and x_step2val == 7:
            o_step_val = 9
        elif x_step1val == 8 and x_step2val == 9:
            o_step_val = 7

    if x_step > 2:
        o_step_val = o_step_forward()

    print("Ход ИИ:")
    return o_step_val


# Основной модуль ========================
game_end = False
player = True
x_step = 0


while game_end == False:

    print_xo_board()  # Показать игровое поле

    # Ввод значений Человек/ИИ
    if player:  # Если человек
        symbol = "X"
        step = int(input("Ваш ход: "))

        x_step += 1

        if x_step == 1:
            x_step1val = step
        elif x_step == 2:
            x_step2val = step

    else:  # Если ИИ
        symbol = "O"
        # step = int(input("Xод ИИ: "))
        step = gpt_step()
        if step == None:
            step = o_step_forward(True)


    put_to_xo_board(step, symbol)  # Добавление символа в ячейку

    who_win = check_winner()  # кто выиграл?
    if who_win != "":
        game_end = True
    else:
        game_end = False

    player = not player

# Конец игры
print_xo_board()
print("Победил(а)", who_win)
