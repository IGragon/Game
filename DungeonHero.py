import os
import sys
import pygame
import random
import time

pygame.init()
pygame.key.set_repeat(200, 70)
pygame.mixer.music.load('data/music.mp3')
pygame.mixer.music.play(-1)

# константы
FPS = 50
WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
door = None

# создание всех групп спрайтов
start_settings = {'level': '',
                  'player_stats': []}
all_sprites = pygame.sprite.Group()
hud_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
magic_group = pygame.sprite.Group()
passive_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
particles = pygame.sprite.Group()
buttons = pygame.sprite.Group()
speed_up = []
damage_up = []


def load_image(name, color_key=None):
    # загрузка изображения(спрайтов)
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def load_level(filename):
    # загрузка уровня из файла
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    # генерация уровня по схеме
    new_player, x, y = None, None, None
    for sprite in all_sprites:
        sprite.kill()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == 'H':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'T':
                Tile('lava', x, y)
            elif level[y][x] == 'C':
                Tile('empty', x, y)
                if random.randint(0, 2) != 0:
                    Coin(x, y)
            elif level[y][x] == 'F':
                Tile('empty', x, y)
                Fire(x, y)
            elif level[y][x] == 'M':
                Tile('empty', x, y)
                HealMagic(x, y)
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                door_created = Exit(x, y)
            elif level[y][x] == 'L':
                Tile('empty', x, y)
                Wizard(1, 100, x, y)
            elif level[y][x] == 'D':
                Tile('empty', x, y)
                Wizard(2, 250, x, y)
            elif level[y][x] == 'B':
                Tile('empty', x, y)
                Wizard(3, 20, x, y)
            elif level[y][x] == 'Z':
                Tile('empty', x, y)
                Potion(x, y, 1)
            elif level[y][x] == 'S':
                Tile('empty', x, y)
                Potion(x, y, 2)
            elif level[y][x] == 'X':
                Tile('empty', x, y)
                Potion(x, y, 3)
    return new_player, x, y, door_created


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    # меню игры
    speed_up.clear()
    pygame.mouse.set_visible(True)
    for button in buttons:
        button.kill()
    background = load_image('fon.png')
    screen.blit(background, (0, 0))
    NewGame(HEIGHT / 2 - 40)
    Continue(HEIGHT / 2, 1)
    Rules(HEIGHT / 2 + 40)
    Back(HEIGHT / 2 + 80, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # проверка нажатия на кнопки
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        button.action()
                        return

        for button in buttons:
            button.update()

        screen.blit(background, (0, 0))
        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def game_screen(mode):
    # основой экран игры, где происходит всё действие

    global player, camera, level_x, level_y, door
    # загрузка новой игры
    if mode == 0:
        f = open('data/default_load.txt')
        save = open('data/save_load.txt', mode='w')
        save.writelines(f.readlines())
        f.seek(0)
        f = list(map(lambda x: x.strip(), f.readlines()))
        start_settings['level'] = f[0]
        start_settings['player_stats'] = [int(f[1]),
                                          int(f[2]),
                                          int(f[3]),
                                          int(f[4]),
                                          int(f[5]),
                                          int(f[6])]
        player, level_x, level_y, door = generate_level(load_level
                                                        (start_settings
                                                         ['level']))
        camera = Camera((level_x, level_y))
        save.close()
    # загрузка сохранения
    elif mode == 1:
        f = open('data/save_load.txt')
        f = list(map(lambda x: x.strip(), f.readlines()))
        start_settings['level'] = f[0]
        start_settings['player_stats'] = [int(f[1]),
                                          int(f[2]),
                                          int(f[3]),
                                          int(f[4]),
                                          int(f[5]),
                                          int(f[6])]
        player, level_x, level_y, door = generate_level(load_level
                                                        (start_settings
                                                         ['level']))
        camera = Camera((level_x, level_y))

    pygame.mouse.set_visible(False)

    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == 27 or event.key == 112:
                    # пауза
                    pause_screen()
                elif event.key == 118:
                    # проверка на удар
                    player.action = 'hit'
                    for enemy in enemy_group:
                        if pygame.sprite.collide_mask(enemy,
                                                      player):
                            enemy.hp -= player.damage
                            for _ in range(7):
                                Particle((enemy.rect[0] + 50,
                                          enemy.rect[1] + 50),
                                         random.randint(-5, 6),
                                         random.randint(-5, 6))
                # использование зелий
                # 1.Восстановление жизней
                elif event.key == 122:
                    if player.heal_potion:
                        player.heal_potion -= 1
                        player.hp += 10
                        PotionEffect('heal')
                # 2.Увеличение скорости
                elif event.key == 120:
                    if player.speed_potion:
                        player.speed_potion -= 1
                        speed_up.append(DoubleSpeed())
                        PotionEffect('speed')
                # 3.Увеличение урона
                elif event.key == 99:
                    if player.damage_increasing:
                        player.damage_increasing -= 1
                        damage_up.append(IncreaseDamage())
                        PotionEffect('damage')
                # показ миникарты
                elif event.key == 109:
                    show_minimap()
        # описание движений персонажа и поворотов его спрайта
        if player.hp > 0:
            player.action = 'move' if player.action != \
                                      'hit' else player.action
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                player.turn = True
                player.rect.x -= player.speed / FPS
                if pygame.sprite.spritecollideany(player,
                                                  wall_group):
                    player.rect.x += player.speed / FPS
                player.update()
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                player.turn = False
                player.rect.x += player.speed / FPS
                if pygame.sprite.spritecollideany(player,
                                                  wall_group):
                    player.rect.x -= player.speed / FPS
                player.update()
            if pygame.key.get_pressed()[pygame.K_UP]:
                player.rect.y -= player.speed / FPS
                if pygame.sprite.spritecollideany(player,
                                                  wall_group):
                    player.rect.y += player.speed / FPS
                player.update()
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                player.rect.y += player.speed / FPS
                if pygame.sprite.spritecollideany(player,
                                                  wall_group):
                    player.rect.y -= player.speed / FPS
                player.update()
            if not (pygame.key.get_pressed()[pygame.K_DOWN] or
                    pygame.key.get_pressed()[pygame.K_UP] or
                    pygame.key.get_pressed()[pygame.K_RIGHT] or
                    pygame.key.get_pressed()[pygame.K_LEFT]):
                player.action = 'stand' if player.action != \
                                           'hit' else player.action
                player.update()
        else:
            # смерть
            player.action = 'dead'
            player.update()

        camera.update(player)

        # обновление всех групп спрайтов

        for sprite in passive_group:
            sprite.update()

        for sprite in all_sprites:
            camera.apply(sprite)

        for enemy in enemy_group:
            enemy.update()

        for particle in particles:
            particle.update()

        for magic in magic_group:
            magic.rect.x += (magic.speed / FPS) * magic.vector_x
            magic.rect.y += (magic.speed / FPS) * magic.vector_y
            magic.update()

        for speed in speed_up:
            if not speed.update():
                speed_up.remove(speed)

        # "рисование" всех спрайтов и картинок

        wall_group.draw(screen)
        tiles_group.draw(screen)
        passive_group.draw(screen)
        enemy_group.draw(screen)
        player_group.draw(screen)
        magic_group.draw(screen)
        particles.draw(screen)
        hud_sprites.draw(screen)

        draw_hud_text()

        pygame.display.flip()

        clock.tick(FPS)


def pause_screen():
    # окно паузы
    pygame.mouse.set_visible(True)
    for button in buttons:
        button.kill()
    background = load_image('pause.jpg')
    screen.blit(background, (0, 0))
    Continue(HEIGHT / 2 - 40, 0)
    Back(HEIGHT / 2 + 40, 1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # выход по esc или по "Р"
            elif event.type == pygame.KEYDOWN:
                if event.key == 27 or event.key == 112:
                    return
            # проверка на нажитие по кнопкам
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        button.action()
                        return

        for button in buttons:
            button.update()

        screen.blit(background, (0, 0))
        buttons.draw(screen)
        pygame.display.flip()


def congratulation_screen():
    # конечное окно, поздравляющее игрока с прохождением игры
    f = open('data/save_load.txt',
             encoding='UTF8',
             mode='w')
    default = open('data/default_load.txt',
                   encoding='UTF8',
                   mode='r')
    default_s = default.read()
    f.write(default_s)
    f.close()
    default.close()
    pygame.mouse.set_visible(True)
    for button in buttons:
        button.kill()
    background = load_image('end.jpg')
    screen.blit(background, (0, 0))
    Back(HEIGHT - 40, 1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # выход по назатию esc
            elif event.type == pygame.KEYDOWN:
                if event.key == 27:
                    return
            # проверка нажатия на кнопку
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        button.action()
                        return

        for button in buttons:
            button.update()

        screen.blit(background, (0, 0))

        # отрисовка очков игрока
        score = pygame.font.Font(None, 60)
        score = score.render('ОЧКИ: {}'.format(player.score +
                                               100 * player.coins +
                                               200 * player.hp),
                             1,
                             pygame.Color('red'))
        screen.blit(score, (WIDTH // 2 - (score.get_rect()[2] // 2),
                            HEIGHT // 2,
                            score.get_rect()[0],
                            score.get_rect()[1]))

        buttons.draw(screen)
        pygame.display.flip()


def rules_screen():
    # окно с правилами и условиями игры
    pygame.mouse.set_visible(True)
    for button in buttons:
        button.kill()
    background = load_image('rules.jpg')
    screen.blit(background, (0, 0))
    Back(HEIGHT - 40, 1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # выход по назатию esc
            elif event.type == pygame.KEYDOWN:
                if event.key == 27:
                    return
            # проверка нажатия на кнопку
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        button.action()
                        return

        for button in buttons:
            button.update()

        screen.blit(background, (0, 0))
        buttons.draw(screen)
        pygame.display.flip()


def show_minimap():
    # показ миникарты уровня
    pygame.mouse.set_visible(True)
    for button in buttons:
        button.kill()
    background = load_image('{}_map.jpg'.format
                            (start_settings['level'][:-4]))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # выход по назатию esc или "М"
            elif event.type == pygame.KEYDOWN:
                if event.key == 109 or event.key == 27:
                    return
        screen.blit(background, (0, 0))
        pygame.display.flip()


def draw_hud_text():
    # текст игрового интерфейса
    # монетки
    coins = pygame.font.Font(None, 75)
    coins = coins.render(str(player.coins),
                         1,
                         pygame.Color('gold'))
    screen.blit(coins, (WIDTH - 60, 15, 100, 100))
    # здоровье
    hp = pygame.font.Font(None, 75)
    hp = hp.render(str(player.hp),
                   1,
                   pygame.Color('red'))
    screen.blit(hp, (65, 10, 100, 100))
    # очки
    score = pygame.font.Font(None, 75)
    score = score.render(str(player.score),
                         1,
                         pygame.Color('white'))
    screen.blit(score, (WIDTH // 2 - (score.get_rect()[2] // 2),
                        10,
                        score.get_rect()[0],
                        score.get_rect()[1]))
    # кол-во зелей здоровья
    hp_potion = pygame.font.Font(None, 75)
    hp_potion = hp_potion.render(str(player.heal_potion),
                                 1,
                                 pygame.Color('white'))
    screen.blit(hp_potion, (70,
                            HEIGHT - 60,
                            hp_potion.get_rect()[0],
                            hp_potion.get_rect()[1]))
    # кол-во зелей скорости
    speed = pygame.font.Font(None, 75)
    speed = speed.render(str(player.speed_potion),
                         1,
                         pygame.Color('white'))
    screen.blit(speed, (WIDTH // 6 + 60,
                        HEIGHT - 60,
                        speed.get_rect()[0],
                        speed.get_rect()[1]))
    # кол-во зелей урона
    damage = pygame.font.Font(None, 75)
    damage = damage.render(str(player.damage_increasing),
                           1,
                           pygame.Color('white'))
    screen.blit(damage, (WIDTH // 6 * 2 + 60,
                         HEIGHT - 60,
                         damage.get_rect()[0],
                         damage.get_rect()[1]))
    # информация об уровне(кол-во очков и номер уровня)
    level_info = pygame.font.Font(None, 40)
    level_info = level_info.render('СЧЁТ: {} УРОВЕНЬ {}'.format
                                   (door.current_score,
                                    start_settings['level'][0]),
                                   1,
                                   pygame.Color('white'))
    screen.blit(level_info, (WIDTH - level_info.get_rect()[2] - 10,
                             HEIGHT - level_info.get_rect()[3] - 10,
                             level_info.get_rect()[0],
                             level_info.get_rect()[1]))


def cut_sheet(self, sheet, columns, rows):
    # функция разрезания спрайт шитов вынесена во внешнее поле
    self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                            sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (self.rect.w * i, self.rect.h * j)
            self.frames.append(sheet.subsurface(pygame.Rect(
                frame_location, self.rect.size)))


def restart_level():
    # перезагрузка уровня на новый или тот же
    global player, level_x, level_y, camera, door
    f = open('data/save_load.txt', encoding='UTF8', mode='r')
    f = f.read().split('\n')
    if f[0] == '5level.txt':
        congratulation_screen()
        return
    start_settings['level'] = f[0]
    start_settings['player_stats'] = [int(f[1]),
                                      int(f[2]),
                                      int(f[3]),
                                      int(f[4]),
                                      int(f[5]),
                                      int(f[6])]
    player, level_x, level_y, door = generate_level(load_level
                                                    (start_settings['level']))
    camera = Camera((level_x, level_y))


# изображения пола
tile_images = {'wall': load_image('wall.jpg'),
               'empty': load_image('floor.jpg'),
               'lava': load_image('lava.png')}
# изображения зелей
potion_images = {1: load_image('heal_potion.png'),
                 2: load_image('speed_potion.png'),
                 3: load_image('fist.png')}
# изображения МАААГИИ
magic_images = {1: load_image('magic_ball1.png'),
                2: load_image('magic_ball2.png'),
                3: load_image('magic_ball3.png')}
# изображения эффектов частиц
effect_settings = {'heal': [load_image('heal_effect.png'), 50],
                   'speed': [load_image('speed_effect.png'), 500],
                   'damage': [load_image('damage_effect.png'), 300]}
# изображения игрового интерфейса
hud_images = {'coin': load_image('coin_hud.png'),
              'hp': load_image('HPHud.png'),
              'hp_potion': load_image('heal_potion_hud.png'),
              'speed': load_image('speed_hud.png'),
              'damage': load_image('damage_hud.png')}
# изображения магов
wizard_frames = {1: [load_image('WizardEasy1.png'),
                     load_image('WizardEasy2.png'),
                     load_image('WizardEasy3.png'),
                     load_image('WizardEasy4.png')],
                 2: [load_image('WizardHard1.png'),
                     load_image('WizardHard2.png'),
                     load_image('WizardHard3.png'),
                     load_image('WizardHard4.png')],
                 3: [load_image('WizardBoss1.png'),
                     load_image('WizardBoss2.png'),
                     load_image('WizardBoss3.png'),
                     load_image('WizardBoss4.png')]}
# размер "плитки"
tile_width = tile_height = 100


class DoubleSpeed:
    # увеличение скорости

    def __init__(self):
        self.start_time = time.time()
        player.speed *= 2
        self.updater = 0

    def update(self):
        # таймер на выключение бафа
        self.updater += 1
        if self.updater > 500:
            player.speed //= 2
            return False
        return True


class IncreaseDamage:
    # увеличение урона

    def __init__(self):
        self.start_time = time.time()
        player.damage += 2
        self.updater = 0

    def update(self):
        # таймер на выключение бафа
        self.updater += 1
        if self.updater > 300:
            player.damage -= 2
            return False
        return True


class Back(pygame.sprite.Sprite):
    # кнопка назад

    image = load_image('exit.png')
    active = load_image('exit_active.png')

    def __init__(self, pos_y, code):
        super().__init__(buttons)
        self.code = code
        self.image = Back.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(WIDTH // 2 - (self.rect[2] / 2), pos_y)

    def update(self):
        # загорается красным при наведении мышки
        xm, ym = pygame.mouse.get_pos()
        x, y = self.rect[0], self.rect[1]
        delta_x, delta_y = self.rect[2], self.rect[3]
        if x < xm < x + delta_x and y < ym < y + delta_y:
            self.image = Back.active
        else:
            self.image = Back.image

    def action(self):
        # выходит из игры
        if self.code == 0:
            terminate()
        # или запускает начальный экран
        elif self.code == 1:
            start_screen()


class NewGame(pygame.sprite.Sprite):
    # кнопка новой игры

    image = load_image('new_game.png')
    active = load_image('new_game_active.png')

    def __init__(self, pos_y):
        super().__init__(buttons)
        self.image = NewGame.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(WIDTH // 2 - (self.rect[2] / 2), pos_y)

    def update(self):
        # загорается красным при наведении мышки
        xm, ym = pygame.mouse.get_pos()
        x, y = self.rect[0], self.rect[1]
        delta_x, delta_y = self.rect[2], self.rect[3]
        if x < xm < x + delta_x and y < ym < y + delta_y:
            self.image = NewGame.active
        else:
            self.image = NewGame.image

    def action(self):
        # запускает игру с начальными настройками
        game_screen(0)


class Rules(pygame.sprite.Sprite):
    # кнопка правил

    image = load_image('rules.png')
    active = load_image('rules_active.png')

    def __init__(self, pos_y):
        super().__init__(buttons)
        self.image = Rules.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(WIDTH // 2 - (self.rect[2] / 2), pos_y)

    def update(self):
        # загорается красным при наведении мышки
        xm, ym = pygame.mouse.get_pos()
        x, y = self.rect[0], self.rect[1]
        delta_x, delta_y = self.rect[2], self.rect[3]
        if x < xm < x + delta_x and y < ym < y + delta_y:
            self.image = Rules.active
        else:
            self.image = Rules.image

    def action(self):
        rules_screen()


class Continue(pygame.sprite.Sprite):
    # кнопка продолжить

    image = load_image('save.png')
    active = load_image('save_active.png')

    def __init__(self, pos_y, code):
        super().__init__(buttons)
        self.code = code
        self.image = Continue.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(WIDTH // 2 - (self.rect[2] / 2), pos_y)

    def update(self):
        # загорается красным при наведении мышки
        xm, ym = pygame.mouse.get_pos()
        x, y = self.rect[0], self.rect[1]
        delta_x, delta_y = self.rect[2], self.rect[3]
        if x < xm < x + delta_x and y < ym < y + delta_y:
            self.image = Continue.active
        else:
            self.image = Continue.image

    def action(self):
        # просто возвращет ничего для продолжения
        if self.code == 0:
            return
        # запускает игру из сохранения
        elif self.code == 1:
            game_screen(1)


class Tile(pygame.sprite.Sprite):
    # пол

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)


class Wall(pygame.sprite.Sprite):
    # стены

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wall_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)


class Coin(pygame.sprite.Sprite):
    # монетка

    def __init__(self, pos_x, pos_y):
        super().__init__(passive_group, all_sprites)
        self.frames = []
        cut_sheet(self, load_image('coin.png'), 6, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.update_counter = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        # анимация монетки и обработка сбора
        self.update_counter += 1
        if pygame.sprite.collide_mask(self, player):
            player.coins += 1
            player.score += 10
            door.current_score += 10
            self.kill()
        if self.update_counter % 2 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class Potion(pygame.sprite.Sprite):
    # зелье здоровья, скорости или урона

    def __init__(self, pos_x, pos_y, code):
        super().__init__(passive_group, all_sprites)
        self.code = code
        self.image = potion_images[code]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.update_counter = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        # обработка сбора зелья
        self.update_counter += 1
        if pygame.sprite.collide_mask(self, player):
            if self.code == 1:
                player.heal_potion += 1
                self.kill()
            elif self.code == 2:
                player.speed_potion += 1
                self.kill()
            else:
                player.damage_increasing += 1
                self.kill()


class PotionEffect(pygame.sprite.Sprite):
    # эффекты при и использовании зелей и лечения

    def __init__(self, eff_type):
        super().__init__(particles)
        self.frames = []
        cut_sheet(self, effect_settings[eff_type][0], 8, 4)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(player.rect[0] + 50,
                                               player.rect[1] + 60)
        self.living_time = effect_settings[eff_type][1]
        self.update_counter = 0

    def update(self):
        # анимация эффекта
        self.update_counter += 1
        self.rect = self.image.get_rect().move(player.rect[0] + 0,
                                               player.rect[1] + 40)
        if self.update_counter % 4 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        if self.update_counter >= self.living_time:
            self.kill()


class Magic(pygame.sprite.Sprite):
    # МАААААГИЯЯЯ плохая

    def __init__(self, power, pos_x, pos_y, speed, vector, damage):
        super().__init__(magic_group, all_sprites)
        self.image = magic_images[power]
        self.speed = speed
        self.damage = damage
        self.vector_x = vector[0]
        self.vector_y = vector[1]
        self.rect = self.image.get_rect().move(pos_x,
                                               pos_y)
        self.update_counter = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        # движение и обработка столкновения с игроком и стеной
        self.update_counter += 1
        if pygame.sprite.collide_mask(self, player):
            for _ in range(self.damage * 2):
                Particle((player.rect[0] + 50,
                          player.rect[1] + 60),
                         random.randint(-5, 6),
                         random.randint(0, 6),
                         dmg=True)
            player.hp -= self.damage
            if player.hp < 0:
                player.hp = 0
            self.kill()
        elif pygame.sprite.spritecollideany(self, wall_group):
            self.kill()


class Exit(pygame.sprite.Sprite):
    # дверь с собственным счётчиком очков

    def __init__(self, pos_x, pos_y):
        super().__init__(passive_group, all_sprites)
        self.image = load_image('door.png')
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.current_score = 0
        self.opened = False

    def update(self):
        # переход на следуюций уровень и подсчёт очков за текущий
        if (pygame.sprite.spritecollideany(self, player_group) and
                self.current_score >= 5000):
            f = open('data/save_load.txt', mode='w')
            data = ['{}level.txt'.format(str(int
                                             (start_settings
                                              ['level'][0]) + 1)),
                    str(player.coins),
                    str(player.hp),
                    str(player.score),
                    str(player.heal_potion),
                    str(player.speed_potion),
                    str(player.damage_increasing)]
            f.writelines('\n'.join(data))
            f.close()
            for sprite in all_sprites:
                sprite.kill()
            speed_up.clear()
            damage_up.clear()
            restart_level()
        if self.current_score >= 5000 and not self.opened:
            self.image = load_image('door_opened.png')
            self.opened = True


class Fire(pygame.sprite.Sprite):
    # огонь

    def __init__(self, pos_x, pos_y):
        super().__init__(passive_group, all_sprites)
        self.frames = []
        cut_sheet(self, load_image('fire_sheet.png'), 8, 4)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.update_counter = 0

    def update(self, *args):
        # анимация огня
        self.update_counter += 1
        if pygame.sprite.collide_mask(self, player) and \
                self.update_counter % 50 == 0:
            player.hp -= 1
        else:
            if self.update_counter % 2 == 0:
                self.cur_frame = (self.cur_frame + 1) % \
                                 len(self.frames)
                self.image = self.frames[self.cur_frame]
                self.mask = pygame.mask.from_surface(self.image)


class HealMagic(pygame.sprite.Sprite):
    # МАААГИЯЯЯ лечебная

    def __init__(self, pos_x, pos_y):
        super().__init__(passive_group, all_sprites)
        self.frames = []
        cut_sheet(self, load_image('heal_magic.png'), 5, 5)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.update_counter = 0
        self.heal_counter = 0

    def update(self, *args):
        # анимация и обработка сбора
        self.update_counter += 1
        if pygame.sprite.spritecollideany(self, player_group) and \
                self.update_counter % 35 == 0:
            player.hp += 1
            self.heal_counter += 1
            PotionEffect('heal')
            if self.heal_counter == 3:
                self.kill()
        else:
            if self.update_counter % 3 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]


class Particle(pygame.sprite.Sprite):
    # частички

    def __init__(self, pos, dx, dy, dmg=False):
        piece = [load_image("spark.png" if not dmg else "blood.png")]
        for scale in (5, 10, 15):
            piece.append(pygame.transform.scale(piece[0], (scale, scale)))
        super().__init__(particles, all_sprites)
        self.image = random.choice(piece)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.blood = dmg
        self.update_counter = 0

    def update(self):
        # обработка двух типов частиц
        self.update_counter += 1
        if self.blood:
            if self.update_counter % 3 == 0:
                self.rect.x += self.velocity[0]
                self.rect.y += self.velocity[1]
            if self.update_counter >= 25:
                self.velocity = 0, 0
            if self.update_counter >= 50:
                self.kill()
        else:
            if self.update_counter % 3 == 0:
                self.rect.x += self.velocity[0]
                self.rect.y += self.velocity[1]
            if self.update_counter >= 25:
                self.kill()


class Hud(pygame.sprite.Sprite):
    # элементы игрового интерфейса

    def __init__(self, pos_x, pos_y, image):
        super().__init__(hud_sprites)
        self.image = hud_images[image]
        self.rect = self.image.get_rect().move(pos_x,
                                               pos_y)


class Wizard(pygame.sprite.Sprite):
    # плохие маги

    def __init__(self, power, frequency, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.frames = wizard_frames[power]
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.power = power
        self.damage = power * 2
        self.frequency = frequency
        self.update_counter = 0
        self.f = True
        self.hp = power * 20 if power < 3 else 50 * power
        self.score = power * 1000 if self.power < 3 else 5600

    def update(self):
        self.update_counter += 1
        # анимация
        if self.update_counter % 8 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        # смерть
        if self.hp <= 0:
            self.kill()
            player.score += self.score
            door.current_score += self.score
        # стрельба МАААГИЕЙ
        if abs(player.rect.x - self.rect.x) < 400 and \
                abs(player.rect.y - self.rect.y) < 400 and \
                self.update_counter % (self.frequency // 2) == 0:
            if self.power == 1:
                if self.f:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          200,
                          (0, -1),
                          self.damage)
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          200,
                          (0, 1),
                          self.damage)
                    self.f = not self.f
                else:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          200,
                          (1, 0),
                          self.damage)
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          200,
                          (-1, 0),
                          self.damage)
                    self.f = not self.f
            elif self.power == 2:
                if self.f:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          100,
                          (0, -1),
                          self.damage)
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          100,
                          (0, 1),
                          self.damage)
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          100,
                          (1, 0),
                          self.damage)
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          100,
                          (-1, 0),
                          self.damage)
                    self.f = not self.f
                else:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          100,
                          (1, -1),
                          self.damage)
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          100,
                          (1, 1),
                          self.damage)
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          100,
                          (-1, 1),
                          self.damage)
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          100,
                          (-1, -1),
                          self.damage)
                    self.f = not self.f
            elif self.power == 3:
                if self.f == 0:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          random.randint(250, 350),
                          (0, -1),
                          self.damage)
                elif self.f == 1:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          random.randint(250, 350),
                          (1, 0),
                          self.damage)
                elif self.f == 2:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          random.randint(250, 350),
                          (0, 1),
                          self.damage)
                elif self.f == 3:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          random.randint(250, 350),
                          (-1, 0),
                          self.damage)
                elif self.f == 4:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          random.randint(250, 350),
                          (1, -1),
                          self.damage)
                elif self.f == 5:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          random.randint(250, 350),
                          (1, 1),
                          self.damage)
                elif self.f == 6:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          random.randint(250, 350),
                          (-1, 1),
                          self.damage)
                elif self.f == 7:
                    Magic(self.power,
                          self.rect.x,
                          self.rect.y,
                          random.randint(250, 350),
                          (-1, -1),
                          self.damage)
                    self.f = -1
                self.f += 1


class Player(pygame.sprite.Sprite):
    # игрок

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames_walk = [load_image('HeroWalk1.png'),  # куча изображений,
                            load_image('HeroWalk2.png'),  # тк отдельным шитом нет
                            load_image('HeroWalk3.png'),
                            load_image('HeroWalk4.png'),
                            load_image('HeroWalk5.png'),
                            load_image('HeroWalk6.png'),
                            load_image('HeroWalk7.png'),
                            load_image('HeroWalk8.png'),
                            load_image('HeroWalk9.png'),
                            load_image('HeroWalk10.png')]
        self.frames_stand = [load_image('HeroIdle1.png'),
                             load_image('HeroIdle2.png'),
                             load_image('HeroIdle3.png'),
                             load_image('HeroIdle4.png'),
                             load_image('HeroIdle5.png'),
                             load_image('HeroIdle6.png'),
                             load_image('HeroIdle7.png'),
                             load_image('HeroIdle8.png'),
                             load_image('HeroIdle9.png'),
                             load_image('HeroIdle10.png')]
        self.frames_dead = [load_image('HeroDead1.png'),
                            load_image('HeroDead2.png'),
                            load_image('HeroDead3.png'),
                            load_image('HeroDead4.png'),
                            load_image('HeroDead5.png'),
                            load_image('HeroDead6.png'),
                            load_image('HeroDead7.png'),
                            load_image('HeroDead8.png'),
                            load_image('HeroDead9.png'),
                            load_image('HeroDead10.png')]
        self.frames_hit = [load_image('HeroHit1.png'),
                           load_image('HeroHit2.png'),
                           load_image('HeroHit5.png'),
                           load_image('HeroHit6.png'),
                           load_image('HeroHit10.png')]
        self.cur_frame = 0
        self.image = self.frames_stand[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.update_counter = 0
        self.coins = start_settings['player_stats'][0]
        Hud(WIDTH - 115, 10, 'coin')
        self.hp = start_settings['player_stats'][1]
        Hud(10, 10, 'hp')
        self.score = start_settings['player_stats'][2]
        self.heal_potion = start_settings['player_stats'][3]
        Hud(10, HEIGHT - 60, 'hp_potion')
        self.speed = 300
        self.speed_potion = start_settings['player_stats'][4]
        Hud(WIDTH // 6, HEIGHT - 60, 'speed')
        self.damage = 4
        self.damage_increasing = start_settings['player_stats'][5]
        Hud(WIDTH // 6 * 2, HEIGHT - 60, 'damage')
        self.kill_counter = 0
        self.action = 'stand'
        self.dead_start = True
        self.turn = False
        self.hit_animation = False
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global door

        self.update_counter += 1
        # анимация
        if self.update_counter % 3 == 0:
            if self.action == 'move':
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_walk)
                self.image = self.frames_walk[self.cur_frame] if not self.turn else pygame.transform.flip(
                    self.frames_walk[self.cur_frame], True, False)
            elif self.action == 'stand':
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_stand)
                self.image = self.frames_stand[self.cur_frame] if not self.turn else pygame.transform.flip(
                    self.frames_stand[self.cur_frame], True, False)
            elif self.action == 'dead':
                if self.dead_start:
                    self.cur_frame = 0
                    self.dead_start = not self.dead_start
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_dead)
                self.image = self.frames_dead[self.cur_frame] if not self.turn else pygame.transform.flip(
                    self.frames_dead[self.cur_frame], True, False)
                if self.cur_frame == 9:
                    self.kill()
                    speed_up.clear()
                    damage_up.clear()
                    global player, level_x, level_y
                    start_settings['player_stats'][0] = 0
                    start_settings['player_stats'][1] = 20
                    settings = generate_level(load_level
                                              (start_settings['level']))
                    player, level_x, level_y, door = settings
            elif self.action == 'hit':
                if not self.hit_animation:
                    self.cur_frame = 0
                    self.hit_animation = not self.hit_animation
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_hit)
                self.image = self.frames_hit[self.cur_frame] if not self.turn else pygame.transform.flip(
                    self.frames_hit[self.cur_frame], True, False)
                if self.cur_frame == 4:
                    self.action = 'stand'
                    self.hit_animation = not self.hit_animation


class Camera:
    # камера для перемещения по карте
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


start_screen()

terminate()
