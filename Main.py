import pygame
import sys
import random
import sqlite3

Name = ""


def terminate():
    pygame.quit()
    sys.exit()


def game():
    global Name
    global last_bonus
    global score
    global lvl
    score = 0
    life = 3
    last_bonus = ""

    def load_lvl(txt=None):  # Загрузка уровня
        Border(5, 60, width - 5, 30)
        Lose_Border(5, height - 5, width - 5, height - 5)
        Border(5, 60, 5, height - 5)
        Border(width - 5, 60, width - 5, height - 5)
        global p
        p = Player_Brick(1010 // 2, 655)
        Ball(10, 600, 500)
        try:
            f = open("File/" + str(txt) + "_lvl.txt")
            t = f.readlines()
            f.close()
            for j in range(len(t)):
                for i in range(10):
                    Brick(10 + i * 100, 70 + j * 50, int(t[j][i]))
        except Exception:
            if txt is None:  # Если нет написаного уровня
                for j in range(5):
                    for i in range(10):
                        Brick(10 + i * 100, 70 + j * 50, random.randint(1, 6))

    class Ball(pygame.sprite.Sprite):  # Мяч
        def __init__(self, radius, x, y):
            self.catched = True
            super().__init__(all_sprites)
            self.add(balls)
            self.radius = radius
            self.image = pygame.Surface((2 * radius, 2 * radius),
                                        pygame.SRCALPHA, 32)
            pygame.draw.circle(self.image, pygame.Color("white"),
                               (radius, radius), radius)
            self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
            self.vx = random.choice([random.randint(-4, -4), random.randint(-4, -2)])
            self.vy = random.randrange(2, 4)

        def update(self):  # Обновление шара
            if self.catched:
                self.rect.center = p.rect.center[0], p.rect.center[1] - 30
            else:
                self.rect = self.rect.move(self.vx, self.vy)
            if pygame.sprite.spritecollideany(self, horizontal_borders):
                self.vy = -self.vy
            elif pygame.sprite.spritecollideany(self, vertical_borders):
                self.vx = -self.vx
            elif pygame.sprite.spritecollideany(self, lose_borders):
                self.kill()
            elif pygame.sprite.spritecollideany(self, bricks):
                i = pygame.sprite.spritecollideany(self, bricks)
                if i.rect.right - self.rect.left < self.rect.right - i.rect.left:
                    dx = i.rect.right - self.rect.left
                else:
                    dx = self.rect.right - i.rect.left
                if self.rect.bottom - i.rect.top < i.rect.bottom - self.rect.top:
                    dy = self.rect.bottom - i.rect.top
                else:
                    dy = i.rect.bottom - self.rect.top
                if dx < dy:
                    self.vx = -self.vx
                elif dx == dy:
                    self.vx = -self.vx
                    self.vy = -self.vy
                else:
                    self.vy = -self.vy
            elif pygame.sprite.spritecollideany(self, player_bricks):
                i = pygame.sprite.spritecollideany(self, player_bricks)
                if i.rect.right - self.rect.left < self.rect.right - i.rect.left:
                    dx = i.rect.right - self.rect.left
                else:
                    dx = self.rect.right - i.rect.left
                if self.rect.bottom - i.rect.top < i.rect.bottom - self.rect.top:
                    dy = self.rect.bottom - i.rect.top
                else:
                    dy = i.rect.bottom - self.rect.top
                if dx < dy:
                    self.vx = -self.vx
                elif dx == dy:
                    self.vx = -self.vx
                    self.vy = -self.vy
                else:
                    self.vy = -self.vy

    class Bonus(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__(all_sprites)
            self.add(bonuses)
            self.radius = 12
            self.image = pygame.Surface((2 * self.radius, 2 * self.radius),
                                        pygame.SRCALPHA, 32)
            pygame.draw.circle(self.image, pygame.Color("yellow"),
                               (self.radius, self.radius), self.radius)
            self.rect = pygame.Rect(x, y, 2 * self.radius, 2 * self.radius)
            self.vy = random.randint(1, 4)

        def update(self):
            self.rect = self.rect.move(0, self.vy)
            if pygame.sprite.spritecollideany(self, lose_borders):
                self.kill()
            if pygame.sprite.spritecollideany(self, player_bricks):
                self.activate()
                self.kill()

        def activate(self):
            global last_bonus
            global life
            chance = random.randint(0, 100)
            if chance <= 5:
                life += 1
                last_bonus = "Дополнительная Жизнь"
            elif chance <= 35:
                for i in balls:
                    if i.vx > 1:
                        i.vx += 1
                    elif i.vx < -1:
                        i.vx -= 1
                    if i.vy > 1:
                        i.vy += 1
                    elif i.vy < -1:
                        i.vy -= 1
                last_bonus = "Ускорить Мяч"
            elif chance <= 65:
                for i in balls:
                    if i.vx > 1:
                        i.vx -= 1
                    elif i.vx < -1:
                        i.vx += 1
                    if i.vy > 1:
                        i.vy -= 1
                    elif i.vy < -1:
                        i.vy += 1
                last_bonus = "Замедлить Мяч"
            elif chance <= 85:
                for i in balls:
                    i.catched = True
                last_bonus = "Поймать Мяч"
            elif chance <= 100:
                for i in balls:
                    Ball(i.radius, i.rect.x, i.rect.y)
                last_bonus = "Дополнительный Шар"

    class Lose_Border(pygame.sprite.Sprite):  # Граница проигрыша
        # строго вертикальный или строго горизонтальный отрезок
        def __init__(self, x1, y1, x2, y2):
            super().__init__(all_sprites)
            if x1 == x2:  # вертикальная стенка
                self.add(lose_borders)
                self.image = pygame.Surface([1, y2 - y1])
                self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
                pygame.draw.rect(self.image, (225, 0, 0), (0, 0, 1, y2 - y1))
            else:  # горизонтальная стенка
                self.add(lose_borders)
                self.image = pygame.Surface([x2 - x1, 1])
                self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
                pygame.draw.rect(self.image, (225, 0, 0), (0, 0, x2 - x1, 1))

    class Border(pygame.sprite.Sprite):  # Обычная граница
        # строго вертикальный или строго горизонтальный отрезок
        def __init__(self, x1, y1, x2, y2):
            super().__init__(all_sprites)
            if x1 == x2:  # вертикальная стенка
                self.add(vertical_borders)
                self.image = pygame.Surface([1, y2 - y1])
                self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
                pygame.draw.rect(self.image, (225, 255, 255), (0, 0, 1, y2 - y1))
            else:  # горизонтальная стенка
                self.add(horizontal_borders)
                self.image = pygame.Surface([x2 - x1, 1])
                self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
                pygame.draw.rect(self.image, (225, 255, 255), (0, 0, x2 - x1, 1))

    class Player_Brick(pygame.sprite.Sprite):  # Ракетка
        def __init__(self, x, y):
            super().__init__(all_sprites)
            self.add(player_bricks)
            self.v = 5
            self.image = pygame.Surface([120, 40])
            self.rect = pygame.Rect(x, y, 120, 40)
            pygame.draw.rect(self.image, (255, 255, 255), (0, 0, 120, 40), border_radius=80)

        def update(self):
            pass

        def left_moution(self):
            if self.rect.left > 10:
                self.rect = self.rect.move(-self.v, 0)

        def right_moution(self):
            if self.rect.right < size[0] - 10:
                self.rect = self.rect.move(self.v, 0)

    class Brick(pygame.sprite.Sprite):  # Кирпич
        def __init__(self, x, y, h):
            super().__init__(all_sprites)
            self.add(bricks)
            self.hp = h
            self.image = pygame.Surface([90, 40])
            self.rect = pygame.Rect(x, y, 90, 40)
            pygame.draw.rect(self.image, (255, 255, 0), (0, 0, 90, 40), border_radius=6)

        def update(self):  # Обновление информации
            global score
            if pygame.sprite.spritecollideany(self, balls):  # Обработка столкновений с шаром
                self.hp -= 1
                score += 5
            if self.hp == 0:
                score += 10
                chance = random.randint(0, 100)
                if chance <= 20:
                    Bonus(self.rect.center[0], self.rect.center[1])
                self.kill()
            elif self.hp == 1:
                pygame.draw.rect(self.image, color_1hp, (0, 0, 90, 40), border_radius=6)
            elif self.hp == 2:
                pygame.draw.rect(self.image, color_2hp, (0, 0, 90, 40), border_radius=6)
            elif self.hp == 3:
                pygame.draw.rect(self.image, color_3hp, (0, 0, 90, 40), border_radius=6)
            elif self.hp == 4:
                pygame.draw.rect(self.image, color_4hp, (0, 0, 90, 40), border_radius=6)
            elif self.hp == 5:
                pygame.draw.rect(self.image, color_5hp, (0, 0, 90, 40), border_radius=6)
            elif self.hp == 6:
                pygame.draw.rect(self.image, color_6hp, (0, 0, 90, 40), border_radius=6)

    def chek_loose_win():  # Проверка победы/поражения
        global life
        global lvl
        global score
        if len(bricks) == 0:
            lvl += 1
            for sprite in all_sprites:
                sprite.kill()
            load_lvl(lvl)
        elif len(balls) == 0:
            if life <= 0:
                game_over(score)
            else:
                life = life - 1
                Ball(10, 600, 500)

    # Группы спрайтов
    player_bricks = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    bricks = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    lose_borders = pygame.sprite.Group()

    # Цвета жизней кирпичей
    color_1hp = pygame.Color(200, 10, 10)
    color_2hp = pygame.Color(0, 255, 0)
    color_3hp = pygame.Color(0, 0, 255)
    color_4hp = pygame.Color(255, 255, 0)
    color_5hp = pygame.Color(0, 255, 255)
    color_6hp = pygame.Color(255, 0, 255)

    # стартовая информация окна
    size = 1010, 700
    width = size[0]
    height = size[1]
    screen = pygame.display.set_mode(size)
    pygame.init()
    lvl = 1

    def new_game():
        # стартовая информация
        global score
        global life
        global lvl
        life = 3
        score = 0
        fps = 80
        clock = pygame.time.Clock()
        left_mout = False
        right_mout = False
        running = True
        # Удаление спрайтов если они были
        for sprite in all_sprites:
            sprite.kill()
        # Загрузка уровня
        load_lvl(lvl)

        while running:
            # Считывание информации с клавиатуры
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN and event.key == 1073741904:
                    left_mout = True
                elif event.type == pygame.KEYUP and event.key == 1073741904:
                    left_mout = False
                elif event.type == pygame.KEYDOWN and event.key == 1073741903:
                    right_mout = True
                elif event.type == pygame.KEYUP and event.key == 1073741903:
                    right_mout = False
                elif event.type == pygame.KEYDOWN and event.key == 114:
                    new_game()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    for i in balls:
                        i.catched = False
            # Движение ракетки
            if left_mout and right_mout:
                pass
            elif left_mout:
                p.left_moution()
            elif right_mout:
                p.right_moution()
            # Обновление фона
            screen.fill((0, 0, 0))
            # Обновление спрайтов
            all_sprites.update()
            f = pygame.font.SysFont("Comic Sans", 40)
            t_sc = f.render(str(score), True, (250, 0, 0))
            t_bon = f.render(f"Последний бонус: {last_bonus}", True, (250, 0, 0))
            t_hp = f.render(str(life), True, (250, 0, 0))
            t = t_hp.get_rect()
            t2 = t_sc.get_rect()
            t3 = t_hp.get_rect()
            t.center = size[0] - 25, 30
            t2.center = 70, 30
            t3.center = size[0] // 5, 30
            clock.tick(fps)
            all_sprites.draw(screen)
            screen.blit(t_hp, t)
            screen.blit(t_sc, t2)
            screen.blit(t_bon, t3)
            chek_loose_win()
            pygame.display.flip()

    new_game()


def main():  # Меню
    class Input_text:  # Окно ввода текста
        def __init__(self, x_pos, y_pos, width, hight, image_path):
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (width, hight))
            self.x_pos = x_pos
            self.y_pos = y_pos
            self.width = width
            self.hight = hight
            self.rect = self.image.get_rect(center=(x_pos, y_pos))
            self.font = pygame.font.SysFont("Comic Sans", 75)
            self.text = self.font.render(text, True, "white")
            self.text_rect = self.text.get_rect(center=(x_pos, y_pos))
            self.need_inp = True

        def update(self):
            if need_inp:
                self.text = self.font.render(text, True, "black")
            else:
                self.text = self.font.render(text, True, "white")
            self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
            screen.blit(self.image, self.rect)
            screen.blit(self.text, self.text_rect)

    class Title:
        def __init__(self, x_pos, y_pos, width, hight, image_path):
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (width, hight))
            self.x_pos = x_pos
            self.y_pos = y_pos
            self.width = width
            self.hight = hight
            self.rect = self.image.get_rect(center=(x_pos, y_pos))

        def update(self):
            screen.blit(self.image, self.rect)

    class Button:
        def __init__(self, x_pos, y_pos, width, hight, text_input, image_path):
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (width, hight))
            self.x_pos = x_pos
            self.y_pos = y_pos
            self.width = width
            self.hight = hight
            self.rect = self.image.get_rect(center=(x_pos, y_pos))
            self.text_input = text_input
            self.font = pygame.font.SysFont("Comic Sans", 75)
            self.text = self.font.render(self.text_input, True, "white")
            self.text_rect = self.text.get_rect(center=(x_pos, y_pos))

        def update(self):
            self.changeColor()
            screen.blit(self.image, self.rect)
            screen.blit(self.text, self.text_rect)

        def chekForInput(self):
            if pygame.mouse.get_pos()[0] in range(self.rect.left, self.rect.right) and pygame.mouse.get_pos()[1] \
                    in range(self.rect.top, self.rect.bottom):
                return True
            else:
                return False

        def changeColor(self):
            if self.chekForInput():
                self.text = self.font.render(self.text_input, True, "black")
            else:
                self.text = self.font.render(self.text_input, True, "white")

    size = 1010, 700
    screen = pygame.display.set_mode(size)
    pygame.init()
    running = True
    fps = 80
    clock = pygame.time.Clock()
    global Name

    text = ""
    text_inp = Input_text(500, 350, 600, 200, "File/board.png")
    button_play = Button(500, 550, 600, 200, "Играть!", "File/board.png")
    t = Title(500, 125, 700, 250, "File/log.png")

    need_inp = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif not need_inp and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and button_play.chekForInput():
                game()
            if need_inp:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    Name = str(text)
                    text_inp.need_inp = False
                    need_inp = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.type == pygame.KEYDOWN and len(text) <= 10:
                    text += str(event.unicode)
        screen.fill((0, 0, 0))
        text_inp.update()
        button_play.update()
        t.update()
        clock.tick(fps)
        pygame.display.flip()


def game_over(score):
    print(score)
    global Name
    size = 1010, 700
    screen = pygame.display.set_mode(size)
    pygame.init()
    running = True
    fps = 80
    clock = pygame.time.Clock()
    con = sqlite3.connect("File/Score_base.sqlite3")
    cur = con.cursor()
    score_board = list(map(list, cur.execute("""SELECT Plase, Name, Score  FROM Score_board""")))
    for i in range(len(score_board)):
        if Name == score_board[i][1]:
            if score > score_board[i][2]:
                score_board[i][2] = score
            break
    else:
        score_board.append([11, Name, score])
    score_board.sort(key=lambda x: x[2], reverse=True)
    for i in range(len(score_board)):
        score_board[i][0] = i + 1
    if len(score_board) > 10:
        score_board = score_board[:10]
    font = pygame.font.SysFont("Comic Sans", 70)
    # Отрисовка
    t_lw = font.render("Игра окончена", True, (250, 0, 0))
    t = t_lw.get_rect()
    t.center = size[0] // 2, 30
    screen.blit(t_lw, t)
    font = pygame.font.SysFont("Comic Sans", 40)
    t_lw = font.render("Место", True, (250, 0, 0))
    t = t_lw.get_rect()
    t.center = size[0] // 4, 75
    screen.blit(t_lw, t)
    t_lw = font.render("Имя", True, (250, 0, 0))
    t = t_lw.get_rect()
    t.center = 2 * size[0] // 4, 75
    screen.blit(t_lw, t)
    t_lw = font.render("Очки", True, (250, 0, 0))
    t = t_lw.get_rect()
    t.center = 3 * size[0] // 4, 75
    screen.blit(t_lw, t)
    cur.execute("""DELETE from Score_board""")
    con.commit()
    for i in range(len(score_board)):
        cur.execute(f"""INSERT INTO Score_board(Plase, Score, Name) 
            VALUES ({score_board[i][0]}, {score_board[i][2]}, '{score_board[i][1]}')""")
        con.commit()
        if score_board[i][1] != Name:
            font = pygame.font.SysFont("Comic Sans", 40)
            t_lw = font.render(str(score_board[i][0]), True, (250, 0, 0))
            t = t_lw.get_rect()
            t.center = size[0] // 4, 120 + i * 40
            screen.blit(t_lw, t)
            t_lw = font.render(score_board[i][1], True, (250, 0, 0))
            t = t_lw.get_rect()
            t.center = 2 * size[0] // 4, 120 + i * 40
            screen.blit(t_lw, t)
            t_lw = font.render(str(score_board[i][2]), True, (250, 0, 0))
            t = t_lw.get_rect()
            t.center = 3 * size[0] // 4, 120 + i * 40
            screen.blit(t_lw, t)
        else:
            font = pygame.font.SysFont("Comic Sans", 40)
            t_lw = font.render(str(score_board[i][0]), True, (250, 250, 0))
            t = t_lw.get_rect()
            t.center = size[0] // 4, 120 + i * 40
            screen.blit(t_lw, t)
            t_lw = font.render(score_board[i][1], True, (250, 250, 0))
            t = t_lw.get_rect()
            t.center = 2 * size[0] // 4, 120 + i * 40
            screen.blit(t_lw, t)
            t_lw = font.render(str(score_board[i][2]), True, (250, 250, 0))
            t = t_lw.get_rect()
            t.center = 3 * size[0] // 4, 120 + i * 40
            screen.blit(t_lw, t)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == 114:
                game()
        clock.tick(fps)
        pygame.display.flip()


if __name__ == '__main__':
    main()
