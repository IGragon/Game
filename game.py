import os
import sys
import pygame
import random

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 50
WIDTH = 1000
HEIGHT = 700
SPEED = 300

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
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
buttons = pygame.sprite.Group()


def load_image(name, color_key=None):
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
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
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
                if random.randint(0, 1) == 0:
                    Coin(x, y)
            elif level[y][x] == 'F':
                Tile('empty', x, y)
                Fire(x, y)
            elif level[y][x] == 'M':
                Tile('empty', x, y)
                HealMagic(x, y)
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                Exit(x, y)
            elif level[y][x] == 'L':
                Tile('empty', x, y)
                Wizard(1, 100, x, y)
            elif level[y][x] == 'D':
                Tile('empty', x, y)
                Wizard(2, 250, x, y)
            elif level[y][x] == 'B':
                Tile('empty', x, y)
                Wizard(3, 40, x, y)
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
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
    global player, camera, level_x, level_y

    if mode == 0:
        f = open('data/default_load.txt')
        save = open('data/save_load.txt', mode='w')
        save.writelines(f.readlines())
        f.seek(0)
        f = list(map(lambda x: x.strip(), f.readlines()))
        start_settings['level'] = f[0]
        start_settings['player_stats'] = [int(f[1]), int(f[2]), int(f[3])]
        player, level_x, level_y = generate_level(load_level(start_settings['level']))
        camera = Camera((level_x, level_y))
        save.close()
    elif mode == 1:
        f = open('data/save_load.txt')
        f = list(map(lambda x: x.strip(), f.readlines()))
        start_settings['level'] = f[0]
        start_settings['player_stats'] = [int(f[1]), int(f[2]), int(f[3])]
        player, level_x, level_y = generate_level(load_level(start_settings['level']))
        camera = Camera((level_x, level_y))

    pygame.mouse.set_visible(False)

    running = True
    turn = False

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == 27:
                    pause_screen()
        if player.hp > 0:
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                turn = True
                player.rect.x -= SPEED / FPS
                if pygame.sprite.spritecollideany(player, wall_group):
                    player.rect.x += SPEED / FPS
                player.update('move', turn)
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                turn = False
                player.rect.x += SPEED / FPS
                if pygame.sprite.spritecollideany(player, wall_group):
                    player.rect.x -= SPEED / FPS
                player.update('move', turn)
            if pygame.key.get_pressed()[pygame.K_UP]:
                player.rect.y -= SPEED / FPS
                if pygame.sprite.spritecollideany(player, wall_group):
                    player.rect.y += SPEED / FPS
                player.update('move', turn)
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                player.rect.y += SPEED / FPS
                if pygame.sprite.spritecollideany(player, wall_group):
                    player.rect.y -= SPEED / FPS
                player.update('move', turn)
            if not (pygame.key.get_pressed()[pygame.K_DOWN] or
                    pygame.key.get_pressed()[pygame.K_UP] or
                    pygame.key.get_pressed()[pygame.K_RIGHT] or
                    pygame.key.get_pressed()[pygame.K_LEFT]):
                player.update('stand')
        else:
            player.update('dead')

        camera.update(player)

        for sprite in passive_group:
            sprite.update()

        for sprite in all_sprites:
            camera.apply(sprite)

        for enemy in enemy_group:
            enemy.update()

        for magic in magic_group:
            magic.rect.x += (magic.speed / FPS) * magic.vector_x
            magic.rect.y += (magic.speed / FPS) * magic.vector_y
            magic.update()

        screen.fill(pygame.Color(0, 0, 0))
        wall_group.draw(screen)
        tiles_group.draw(screen)
        passive_group.draw(screen)
        enemy_group.draw(screen)
        player_group.draw(screen)
        magic_group.draw(screen)
        hud_sprites.draw(screen)

        draw_hud_text()

        pygame.display.flip()

        clock.tick(FPS)


def pause_screen():
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


def rules_screen():
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


def draw_hud_text():
    coins = pygame.font.Font(None, 75)
    coins = coins.render(str(player.coins),
                         1,
                         pygame.Color('gold'))
    screen.blit(coins, (WIDTH - 60, 15, 100, 100))
    hp = pygame.font.Font(None, 75)
    hp = hp.render(str(player.hp),
                   1,
                   pygame.Color('red'))
    screen.blit(hp, (65, 10, 100, 100))
    score = pygame.font.Font(None, 75)
    score = score.render(str(player.score),
                         1,
                         pygame.Color('white'))
    screen.blit(score, (WIDTH // 2 - (score.get_rect()[2] // 2),
                        10,
                        score.get_rect()[0],
                        score.get_rect()[1]))


def restart_level():
    global player, level_x, level_y, camera
    f = open('data/save_load.txt', encoding='UTF8', mode='r')
    f = f.read().split('\n')
    start_settings['level'] = f[0]
    start_settings['player_stats'] = [int(f[1]), int(f[2]), int(f[3])]
    player, level_x, level_y = generate_level(load_level(start_settings['level']))
    camera = Camera((level_x, level_y))


tile_images = {'wall': load_image('wall.jpg'),
               'empty': load_image('floor.jpg'),
               'lava': load_image('lava.png')}

magic_images = {1: load_image('magic_ball1.png'),
                2: load_image('magic_ball2.png'),
                3: load_image('magic_ball3.png')}

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

tile_width = tile_height = 100


class Back(pygame.sprite.Sprite):
    image = load_image('exit.png')
    active = load_image('exit_active.png')

    def __init__(self, pos_y, code):
        super().__init__(buttons)
        self.code = code
        self.image = Back.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(WIDTH // 2 - (self.rect[2] / 2), pos_y)

    def update(self):
        xm, ym = pygame.mouse.get_pos()
        x, y = self.rect[0], self.rect[1]
        delta_x, delta_y = self.rect[2], self.rect[3]
        if x < xm < x + delta_x and y < ym < y + delta_y:
            self.image = Back.active
        else:
            self.image = Back.image

    def action(self):
        if self.code == 0:
            terminate()
        elif self.code == 1:
            start_screen()


class NewGame(pygame.sprite.Sprite):
    image = load_image('new_game.png')
    active = load_image('new_game_active.png')

    def __init__(self, pos_y):
        super().__init__(buttons)
        self.image = NewGame.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(WIDTH // 2 - (self.rect[2] / 2), pos_y)

    def update(self):
        xm, ym = pygame.mouse.get_pos()
        x, y = self.rect[0], self.rect[1]
        delta_x, delta_y = self.rect[2], self.rect[3]
        if x < xm < x + delta_x and y < ym < y + delta_y:
            self.image = NewGame.active
        else:
            self.image = NewGame.image

    def action(self):
        game_screen(0)


class Rules(pygame.sprite.Sprite):
    image = load_image('rules.png')
    active = load_image('rules_active.png')

    def __init__(self, pos_y):
        super().__init__(buttons)
        self.image = Rules.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(WIDTH // 2 - (self.rect[2] / 2), pos_y)

    def update(self):
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
    image = load_image('save.png')
    active = load_image('save_active.png')

    def __init__(self, pos_y, code):
        super().__init__(buttons)
        self.code = code
        self.image = Continue.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(WIDTH // 2 - (self.rect[2] / 2), pos_y)

    def update(self):
        xm, ym = pygame.mouse.get_pos()
        x, y = self.rect[0], self.rect[1]
        delta_x, delta_y = self.rect[2], self.rect[3]
        if x < xm < x + delta_x and y < ym < y + delta_y:
            self.image = Continue.active
        else:
            self.image = Continue.image

    def action(self):
        if self.code == 0:
            return
        elif self.code == 1:
            game_screen(1)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wall_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(passive_group, all_sprites)
        self.frames = []
        self.cut_sheet(load_image('coin.png'), 6, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.update_counter = 0
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.update_counter += 1
        if pygame.sprite.collide_mask(self, player):
            player.coins += 1
            player.score += 10

            self.kill()
        else:
            if self.update_counter % 2 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]


class Magic(pygame.sprite.Sprite):
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
        self.update_counter += 1
        if pygame.sprite.collide_mask(self, player):
            player.hp -= self.damage
            if player.hp < 0:
                player.hp = 0
            self.kill()
        elif pygame.sprite.spritecollideany(self, wall_group):
            self.kill()


class Exit(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(passive_group, all_sprites)
        self.image = load_image('door.png')
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            f = open('data/save_load.txt', mode='w')
            data = ['{}level.txt'.format(str(int(start_settings['level'][0]) + 1)),
                    str(player.coins),
                    str(player.hp),
                    str(player.score),
                    str(player.heal_poison),
                    str(player.speed_poison),
                    str(player.damage_increase)]
            f.writelines('\n'.join(data))
            f.close()
            for sprite in all_sprites:
                sprite.kill()
            restart_level()


class Fire(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(passive_group, all_sprites)
        self.frames = []
        self.cut_sheet(load_image('fire_sheet.png'), 8, 4)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.update_counter = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        self.update_counter += 1
        if pygame.sprite.spritecollideany(self, player_group) and\
                self.update_counter % 50 == 0:
            player.hp -= 1
        else:
            if self.update_counter % 2 == 0:
                self.cur_frame = (self.cur_frame + 1) %\
                                 len(self.frames)
                self.image = self.frames[self.cur_frame]


class HealMagic(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(passive_group, all_sprites)
        self.frames = []
        self.cut_sheet(load_image('heal_magic.png'), 5, 5)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.update_counter = 0
        self.heal_counter = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        self.update_counter += 1
        if pygame.sprite.spritecollideany(self, player_group) and\
                self.update_counter % 70 == 0:
            player.hp += 1
            self.heal_counter += 1
            if self.heal_counter == 3:
                self.kill()
        else:
            if self.update_counter % 2 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]


class CoinHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(hud_sprites)
        self.image = load_image('coin_hud.png')
        self.rect = self.image.get_rect().move(WIDTH - 115,
                                               10)


class HPHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(hud_sprites)
        self.image = load_image('HPHud.png')
        self.rect = self.image.get_rect().move(10,
                                               10)


class Wizard(pygame.sprite.Sprite):
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

    def update(self):
        self.update_counter += 1
        if self.update_counter % 8 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        if abs(player.rect.x - self.rect.x) < 400 and\
                abs(player.rect.y - self.rect.y) < 400 and\
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
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames_walk = [load_image('HeroWalk1.png'),
                             load_image('HeroWalk2.png'),
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
        self.cur_frame = 0
        self.image = self.frames_stand[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.update_counter = 0
        self.coins = start_settings['player_stats'][0]
        CoinHud()
        self.hp = start_settings['player_stats'][1]
        HPHud()
        self.score = start_settings['player_stats'][2]
        self.heal_poison = 0
        self.speed_poison = 0
        self.damage_increase = 0
        self.dead_start = True
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, action, left=False):
        self.update_counter += 1
        if self.update_counter % 3 == 0:
            if action == 'move':
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_walk)
                self.image = self.frames_walk[self.cur_frame] if not left else pygame.transform.flip(self.frames_walk[self.cur_frame], True, False)
            if action == 'stand':
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_stand)
                self.image = self.frames_stand[self.cur_frame]
            if action == 'dead':
                if self.dead_start:
                    self.cur_frame = 0
                    self.dead_start = not self.dead_start
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_dead)
                self.image = self.frames_dead[self.cur_frame]
                if self.cur_frame == 9:
                    self.kill()
                    global player, level_x, level_y
                    start_settings['player_stats'][0] = 0
                    start_settings['player_stats'][1] = 20
                    player, level_x, level_y = generate_level(load_level(start_settings['level']))


class Camera:
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
