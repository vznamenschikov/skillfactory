# МОРСКОЙ БОЙ
from random import randint

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Координаты введены не верно!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Повторный выстрел в то-же поле!"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, ship_bow, length, orientation):
        self.length = length
        self.ship_bow = ship_bow
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            current_x = self.ship_bow.x
            current_y = self.ship_bow.y

            if self.orientation == 0:
                current_x = current_x + i

            elif self.orientation == 1:
                current_y = current_y + i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["0", "0", "0", "0", "0", "0"] for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "   | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1}  | " + " | ".join(row) + " |"
            #print("res=",res,"!")
        if self.hid:
            res = res.replace("■", "0")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1) # координаты контура
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Попадание. Корабль уничтожен!")
                    return False
                else:
                    print("Попадание. Корабль повреждён!")
                    return True

        self.field[d.x][d.y] = "Т"
        print("Промах!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as exception_:
                print(exception_)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход AI: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            coordinates = input("Ваш ход: ").split()

            if len(coordinates) != 2:
                print("Введите 2 координаты! ")
                continue

            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        player1 = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player1)
        self.pl = User(player1, computer)

    def try_board(self):
        length = [3, 2, 2, 1, 1, 1, 1]  # 1 - трехпалубный, 2 - двухпалубных, 4 - однопалубных 
        board = Board(size=self.size)
        attempts = 0

        # Пробуем заполнить доску флотом
        for l in length:
            while True:
                attempts += 1
                if attempts > 1000: # Максимальное количество попыток 1000
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("┌─────────────────────────────────────┐")
        print("│ Добро пожаловать в игру МОРСКОЙ БОЙ │")
        print("└─────────────────────────────────────┘")
        print("Формат ввода данных: (номер_строки) (номер_столбца)\n")


    def loop(self):
        num = 0
        while True:
            # Отрисовка досок
            print("=" * 28,"\nВаша доска:")
            print(self.pl.board)
            print("-" * 28,"\nДоска AI:")
            print(self.ai.board)
            print("-" * 28)
            if num % 2 == 0:
                repeat = self.pl.move() # Ваш ход
            else:
                repeat = self.ai.move() # Ход AI
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print("-" * 28,"\nВы выиграли!")
                break # Выход

            if self.pl.board.defeat():
                print("-" * 28,"\nВыиграл компьютер!")
                break # Выход
            num += 1

    def start(self):
        self.greet()
        self.loop()

game = Game()
game.start()