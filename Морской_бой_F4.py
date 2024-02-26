# C2.5. Итоговое практическое задание - ИГРА МОРСКОЙ БОЙ (by VZ)
import random
import copy

play_board = [[' ', 1, 2, 3, 4, 5, 6], [1, 0, 0, 0, 0, 0, 0], [2, 0, 0, 0, 0, 0, 0], [3, 0, 0, 0, 0, 0, 0],
              [4, 0, 0, 0, 0, 0, 0], [5, 0, 0, 0, 0, 0, 0], [6, 0, 0, 0, 0, 0, 0]]

fleet = [3, 2, 2, 1, 1, 1, 1]   # Список флота с количеством палуб

ship_sign = '■'                 # Маркер "палуба"
hit_sign = 'X'                  # Маркер "попал"
contour_sign = '·'              # Маркер "contour"
miss_sign = 'T'                 # Маркер "промах"
blank_sign = '0'                # Маркер "Пустое поле"
no_sign = [ship_sign, hit_sign, contour_sign]  # ['■', 'X', '·'] Варианты маркировки ячеек которое нельзя помечать '·'
no_shot = [contour_sign, miss_sign, hit_sign]  # ['·', 'T', 'X'] Варианты ячеек в которые "нет смысла" стрелять

vertical = 0                    # Вертикальная ориентация корабля
horizontal = 1                  # Горизонтальная ориентация корабля

# В начале имеет смысл написать классы исключений, которые будет использовать наша программа. Например, когда игрок
# пытается выстрелить в клетку за пределами поля, во внутренней логике должно выбрасываться соответствующее исключение
# BoardOutException, а потом отлавливаться во внешней логике, выводя сообщение об этой ошибке пользователю.

mode = True                     # Признак окончания игры if False - окончание игры
board_size = 6                  # Размер игровой доски (по факту, адресация к ячейкам от 1 до 6)


class BoardException(Exception):
    pass


class BoardOutException(BoardException):            # Exception если стреляет пользователь
    def __str__(self):
        return 'Вы пытаетесь выстрелить в клетку за пределами поля'


class BoardDoubleShotException(BoardException):     # Exсeption для пользователя (с выводом сообщения)
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardDoubleShotException4AI(BoardException):  # Exception для AI (без вывода сообщения)
    pass


class BoardShipIsOutException(BoardException):
    pass


# Далее нужно реализовать класс Dot — класс точек на поле. Каждая точка описывается параметрами:
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):                             # Нормализованное представление координат точки
        return f"({self.x}, {self.y})"

    # В программе мы будем часто обмениваться информацией о точках на поле, поэтому имеет смысл сделать отдельный тип
    # данных для них. Очень удобно будет реализовать в этом классе метод __eq__, чтобы точки можно было проверять на
    # равенство. Тогда, чтобы проверить, находится ли точка в списке, достаточно просто использовать оператор in,
    # как мы делали это с числами.
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# Следующим идёт класс Ship — корабль на игровом поле, который описывается параметрами:
class Ship:
    def __init__(self, ship_bow_xy, length, orientation):
        self.ship_bow_xy = ship_bow_xy              # Точка, где размещён нос корабля.
        self.length = length                        # Длина.
        self.orientation = orientation              # Ориентация корабля (вертикально/горизонтально).
        self.number_of_lives = length               # Количеством жизней (сколько точек корабля ещё не подбито).

    # И имеет метод dots, который возвращает список всех точек корабля.
    @property
    def dots(self):
        ship_coords = []

        # Наполнение списков (матрица)
        for n in range(self.length):
            if self.orientation:                                # if True
                ship_coords.append(Dot(self.ship_bow_xy.x + n,
                                       self.ship_bow_xy.y))     # ship_coords = ship_coords= [<__main__.Dot object ...
            else:
                ship_coords.append(Dot(self.ship_bow_xy.x, self.ship_bow_xy.y + n))  # ship_coords =
        return ship_coords


# Самый важный класс во внутренней логике — класс Board — игровая доска. Доска описывается параметрами:
class Board:
    def __init__(self, play_board=[], ships_list=[], hid=False, ships_alive=7, player_name=''):

        self.play_board = play_board    # Двумерный список, в котором хранятся состояния каждой из клеток.
        self.ships_list = ships_list    # Список кораблей доски.
        self.hid = hid                  # Параметр hid типа bool — информация о том, нужно ли скрывать корабли на доске
                                        # (для вывода доски врага) или нет (для своей доски).
        self.ships_alive = ships_alive  # Количество живых кораблей на доске.
        self.player_name = player_name  # Имя пользователя (для определения дочернего класса внутри родительского)
                                        # Есть другие методы определения???

    # ПОДСКАЗКА:
    # my_board - доска игрока
    # ai_board - доска AI

    # Метод out, который для точки (объекта класса Dot) возвращает True, если точка выходит за пределы поля,
    # и False, если не выходит.
    def out(self, dot):                                             # от (Boards)
        return not (1 <= dot.x <= board_size) or not (1 <= dot.y <= board_size)  # Если не в пределах поля

    # И имеет методы:
    # Метод add_ship, который ставит корабль на доску (если ставить не получается, выбрасываем исключения).
    def add_ship(self, ship):                                       # от (Boards)

        for d in ship.dots:
            if self.out(d) or self.no_contour(d):  # одна из координат корабля за пределами игрового поля / не разрешена
                raise BoardShipIsOutException()

        for d in ship.dots:                                         # Установка корабля на доску
            self.play_board[d.x][d.y] = "■"

        self.ships_list.append(ship)    # Добавляем корабль к общему списку кораблей ships_list
        self.contour(ship)                                          # Обводка contour '·'

        return False

    def find_blank_cell(self):   # Найти подходящую свободную клетку для установки корабля Dot(x,y) (от Board)
        d = Dot(0, 0)
        for x in range(1, board_size + 1):                          # Перебор всех клеток игрового поля
            for y in range(1, board_size + 1):
                if self.play_board[x][y] == blank_sign:             # Если в клетке символ '·'
                    d = Dot(x, y)                                   # То заменить на '0'
                    print(x, y, self.play_board[x][y])
        return d

    def no_contour(self, dot):  # Проверка на зоны, где маркер контура не ставится (координаты за пределами доски)
        if not (1 <= dot.x <= board_size) or not (1 <= dot.y <= board_size):
            return True

        if self.play_board[dot.x][dot.y] in no_sign:  # Запрещенная зона/Не помечать '·' если no_sign = ['■', 'X', '·']
            return True
        return False

    def clear_contour(self):  # Очистка игрового поля от символа '·' после расстановки кораблей
        for x in range(1, board_size + 1):                          # Перебор всех клеток игрового поля
            for y in range(1, board_size + 1):
                if self.play_board[x][y] == contour_sign:           # Если в клетке символ '·'
                    self.play_board[x][y] = blank_sign              # То заменить на '0'

    def clear_all_cells(self):  # "Обнуление" доски. Замена содержимого всех клеток на '0' + Очистка списка кораблей
        for x in range(1, board_size + 1):                          # Перебор всех клеток игрового поля
            for y in range(1, board_size + 1):
                self.play_board[x][y] = blank_sign                  # Заменить все на '0'
        self.ships_list = []

    # Метод contour, который обводит корабль по контуру. Он будет полезен и в ходе самой игры, и при расстановке
    # кораблей (помечает соседние точки, где корабля по правилам быть не может).
    def contour(self, ship):                                        # от (Boards)

        # 3 | · | · | · | · | 0 | 0 |
        # 4 | ■ | ■ | ■ | · | 0 | 0 |
        # 5 | · | · | · | · | 0 | 0 |

        for d in ship.dots:
            contour_d = [Dot(d.x - 1, d.y - 1), Dot(d.x - 1, d.y), Dot(d.x - 1, d.y + 1), Dot(d.x, d.y - 1),
                         Dot(d.x + 1, d.y - 1), Dot(d.x + 1, d.y), Dot(d.x + 1, d.y + 1), Dot(d.x, d.y + 1)]

            # Оптимизация кода
            # contour_d = []
            # contour_d.append(Dot(d.x - 1, d.y - 1))  # Описание всех координат вокруг указанной точки d
            # contour_d.append(Dot(d.x - 1, d.y))
            # contour_d.append(Dot(d.x - 1, d.y + 1))
            # contour_d.append(Dot(d.x, d.y - 1))
            # contour_d.append(Dot(d.x + 1, d.y - 1))
            # contour_d.append(Dot(d.x + 1, d.y))
            # contour_d.append(Dot(d.x + 1, d.y + 1))
            # contour_d.append(Dot(d.x, d.y + 1))

            for sd in contour_d:                                    # Проверка всех точек вокруг d
                if not self.out(sd) and not self.no_contour(sd):    # Если точка не за пределами доски и не '·'
                    self.play_board[sd.x][sd.y] = contour_sign      # Пометить ячейку как '·'; contour_sign = '·'

    # Метод, который выводит доску в консоль в зависимости от параметра hid.
    def print_board(self, *args):                                   # от (Boards)

        if len(args):
            self.hid = args[0]

        for y in range(0, 7):
            for x in range(0, 7):
                # Код заменён на более компактный ниже
                # if self.hid:                                            # Проверка нужно ли скрывать корабли на доске
                #     if self.play_board[x][y] != ship_sign:              # Если в клетке доски AI не "■",
                #         print(f' {self.play_board[x][y]} |', end='')    # то показать содержимое
                #     else:
                #         print(f' {blank_sign} |', end='')               # иначе скрыть корабль и показать "0"
                # else:
                #     print(f' {self.play_board[x][y]} |', end='')        # Показать всё

                if not self.hid or self.play_board[x][y] != ship_sign:    # Если не нужно скрывать корабли / или не "■"
                    print(f' {self.play_board[x][y]} |', end='')
                else:
                    print(f' {blank_sign} |', end='')
            print()

    # Метод shot, который делает выстрел по доске (если есть попытка выстрелить за пределы и в использованную точку,
    # нужно выбрасывать исключения).
    def shot(self, d):                                  # (от Boards)

        # ПРОВЕРКА КОРРЕКТНОСТИ ВВОДА
        if self.out(d):                                 # Если ячейка за пределами доски
            raise BoardOutException()                   # Выбрасываем исключение

        # (Если координаты в пределах доски, то можем обращаться к ячейке)
        cell_content = str(self.play_board[d.x][d.y])   # Получение содержания ячейки в которую стреляем

        # ПРОВЕРКА ПОВТОРА ВЫСТРЕЛА В ТУ-ЖЕ КЛЕТКУ
        if cell_content in no_shot:                     # Если ячейка содержит ['·', 'T', 'X']
            if self.hid:
                raise BoardDoubleShotException()        # Exception для пользователя "Вы уже стреляли в эту клетку"
            else:
                raise BoardDoubleShotException4AI()     # Exception для AI (без вывода сообщения)

        # ПОПАДАНИЕ
        if cell_content == ship_sign:                               # Если попадание '■'
            self.play_board[d.x][d.y] = hit_sign                    # То маркируем как 'X'

            for n in range(len(self.ships_list)):                   # Перебор списка кораблей
                if d in self.ships_list[n].dots:                    # Поиск в какую палубу попадание
                    self.ships_list[n].number_of_lives -= 1         # Уменьшение количество жизней на -1

                    if self.ships_list[n].number_of_lives == 0:     # Если УБИТ,
                        self.contour(self.ships_list[n])            # то обводка контуром
                        print('<< УБИЛ >> Ещё ход.')
                    else:
                        print('<< РАНИЛ >> Ещё ход.')

        # ПРОМАХ
        if cell_content == blank_sign:                              # Если пустая ячейка '0'
            self.play_board[d.x][d.y] = miss_sign                   # То "промах" 'T'
            print('<< ПРОМАХ >> Переход хода.')
            return False                                            # и переход хода

        game.print_all_boards()                                     # Печать всех досок
        return True                                                 # True - Повторный выстрел / False - Переход хода

    def check_alive(self):                                          # Проверка количества живых кораблей на доске
        ships_alive = 0                                             # ships_alive - кол-во живых кораблей
        for n in range(len(self.ships_list)):                       # Перебор списка кораблей
            if self.ships_list[n].number_of_lives != 0:
                ships_alive += 1

        if self.hid:
            print('Кол-во живых кораблей AI:', ships_alive)
            if ships_alive == 0:
                print('< КОНЕЦ ИГРЫ > ПОЗДРАВЛЕНИЯ! ВЫ ВЫИГРАЛИ!)')
                exit()
        else:
            print('Кол-во ваших живых кораблей:', ships_alive)
            if ships_alive == 0:
                print('< КОНЕЦ ИГРЫ > Выиграл AI!')
                exit()
        return False


# Теперь нужно заняться внешней логикой: класс Player — класс игрока в игру (и AI, и пользователь).
# Этот класс будет родителем для классов с AI и с пользователем.
class Player:
    def __init__(self, board):
        # Игрок описывается параметрами:
        # self.my_board = my_board  # Собственная доска (объект класса Board).
        # self.ai_board = ai_board  # Доска врага.
        self.board = board

    # И имеет следующие методы:
    #
    # ask — метод, который «спрашивает» игрока, в какую клетку он делает выстрел. Пока мы делаем общий для AI
    # и пользователя класс, этот метод мы описать не можем. Оставим этот метод пустым.
    def ask(self):
        pass

    # Тем самым обозначим, что потомки должны реализовать этот метод.
    # move — метод, который делает ход в игре. Тут мы вызываем метод ask, делаем выстрел по вражеской доске
    # (метод Board.shot), отлавливаем исключения, и если они есть, пытаемся повторить ход. Метод должен возвращать True,
    # если этому игроку нужен повторный ход (например, если он выстрелом подбил корабль).
    def move(self):
        move_again = True
        while move_again:
            try:
                shot_to = self.ask()                   # Получение координат выстрела user/ai
                move_again = self.board.shot(shot_to)  # shot возвращает True - Повторный выстрел / False - Переход хода

            except BoardException as e:                # Если что-то пошло не так
                print(e)


# Теперь нам остаётся унаследовать классы AI и User от Player и переопределить в них метод ask.
# Для AI это будет выбор случайной точки, а для User этот метод будет спрашивать координаты точки из консоли.
class User(Player):
    def ask(self):

        self.board.check_alive()                        # Проверка количества живых кораблей

        while True:
            my_shot_xy = input("Ваш ход (x y): ").split()
            try:
                int(my_shot_xy[0])
                int(my_shot_xy[1])
            except:
                print('Ошибка ввода: Введите два целых числа через пробел')
                continue

            my_shot_x, my_shot_y = int(my_shot_xy[0]), int(my_shot_xy[1])

            if len(my_shot_xy) != 2:                    # Если параметров не 2
                print('Ошибка ввода! Пожалуйста введите два параметра X и Y через пробел')
                continue
            elif not (0 < my_shot_x < board_size + 1) or not (0 < my_shot_y < board_size + 1):
                print('Ошибка ввода! Параметры X и Y должны быть в диапазоне от 1 до 6')
                continue

            return Dot(my_shot_x, my_shot_y)            # Возвращаем введённые координаты


class AI(Player):
    def ask(self):

        self.board.check_alive()

        ai_shot_xy = Dot(random.randint(1, 6), random.randint(1, 6))
        print('Выстрел AI:', ai_shot_xy)
        return ai_shot_xy


# После создаём наш главный класс — класс Game. Игра описывается параметрами:
class Game:
    def __init__(self):
        # Игрок-пользователь, объект класса User.
        # Доска пользователя.
        # Игрок-компьютер, объект класса AI.
        # Доска компьютера.

        my_play_board = play_board                  # Назначаем пустую доску для my_play_board
        ai_play_board = copy.deepcopy(play_board)   # Копируем доску
        my_ships_list = []                          # Список кораблей пользователя
        ai_ships_list = []                          # Список кораблей AI

        # Создаём доску user
        self.my_board = Board(my_play_board, ships_list=my_ships_list, ships_alive=7, player_name='user')
        # Создаём доску AI
        self.ai_board = Board(ai_play_board, ships_list=ai_ships_list, hid=True, ships_alive=7, player_name='AI')

        self.user = User(self.ai_board)
        self.ai = AI(self.my_board)

    # И имеет методы:
    #
    # random_board — метод генерирует случайную доску. Для этого мы просто пытаемся в случайные клетки изначально пустой
    # доски расставлять корабли (в бесконечном цикле пытаемся поставить корабль в случайную доску, пока наша попытка не
    # окажется успешной). Лучше расставлять сначала длинные корабли, а потом короткие.
    # Если было сделано много (несколько тысяч) попыток установить корабль, но это не получилось, значит доска неудачная
    # и на неё корабль уже не добавить. В таком случае нужно начать генерировать новую доску.

    def random_board_part(self, board):                     # (от Game)

        for f in fleet:                                     # Расстановка кораблей из списка: fleet = [3, 2, 1, 1, 1, 1]
            cnt = 0
            while True:
                cnt += 1
                if cnt > 4000:                              # Проверка неудачной расстановки (пересоздать доску)
                    return False

                try:
                    board.add_ship(Ship(Dot(random.randint(1, board_size), random.randint(1, board_size)), f, \
                                                                                            random.randint(0, 1)))
                    break
                except BoardShipIsOutException:             # Исключение при неудачной установке корабля
                    continue
        return True

    def random_board(self, board):                          # (от Game)
        result = self.random_board_part(board)              # True - Всё поместилось, False - нужна новая доска
        while not result:
            board.clear_all_cells()                         # Очистка доски
            result = self.random_board_part(board)          # Расстановка кораблей на доске

    # greet — метод, который в консоли приветствует пользователя и рассказывает о формате ввода.
    def greet(self):                # (от Game)
        print('╔══════════════════════════════╗')
        print('║       ИГРА МОРСКОЙ БОЙ       ║')
        print('╚══════════════════════════════╝')
        print('Формат ввода координат (через пробел): x y <enter>')

    def print_all_boards(self):     # (от Game)
        print('\nМоя доска')
        self.my_board.print_board()
        print('\nДоска AI')
        self.ai_board.print_board(True)
        print()

    # MAIN LOOP
    # loop — метод с самим игровым циклом. Там мы просто последовательно вызываем метод mode для игроков и делаем
    # проверку, сколько живых кораблей осталось на досках, чтобы определить победу.
    def loop(self):

        self.random_board(self.my_board)        # Расстановка моих кораблей
        self.my_board.clear_contour()           # Очистка "контура"

        self.random_board(self.ai_board)        # Расстановка кораблей на доске противника
        self.ai_board.clear_contour()           # Очистка "контура"

        whose_move = 1                          # Триггер: Чей ход? 1-user, 0-AI

        mode = True
        while mode:

            # ПЕЧАТЬ ДОСКИ
            self.print_all_boards()
            # print('Моя доска')
            # self.my_board.print_board(False)
            # print('\nДоска AI')
            # self.ai_board.print_board(False)

            if whose_move:                      # Триггер: Чей ход? user=True
                self.user.move()                # Ход пользователя если whose_move = True
                whose_move = False
            else:
                self.ai.move()                  # Ход AI если whose_move = True
                whose_move = True

    # start — запуск игры. Сначала вызываем greet, а потом loop.
    def start(self):
        self.greet()
        self.loop()


# И останется просто создать экземпляр класса Game и вызвать метод start.
game = Game()
game.start()
