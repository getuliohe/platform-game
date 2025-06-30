# -*- coding: utf-8 -*-


import pgzrun
import random
from pygame import Rect


# --- CONFIGURAÇÕES DO JOGO ---
WIDTH = 800
HEIGHT = 600
TITLE = "Platformer Kodland"

# --- CONSTANTES ---
GRAVITY = 0.6
JUMP_FORCE = -16
PLAYER_SPEED = 4
TILE_SIZE = 70

# --- VARIÁVEIS GLOBAIS ---
game_state = 'menu'
background_music_on = True
sfx_on = True
score = 0
player = None
platforms = []
enemies = []
coins = []
goal = None
level_width = 0
level_height = 0
camera_x = 0
camera_y = 0

# --- MAPA DA FASE ---
LEVEL_MAP = [
    "                                ",
    "                                ",
    "          C F                   ",
    "         PPPPPP                 ",
    "                                ",
    "                      C C       ",
    "   C C               PPPPP      ",
    "  PPPPP             E           ",
    "              E    PPPPP        ",
    "             PPPP               ",
    " E       C   C   C              ",
    "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
]

# --- CLASSES ---
class AnimatedCharacter:
    """ Classe base para personagens animados. """
    def __init__(self, pos, animations, animation_speed=0.15):
        self.animations = animations
        self.current_animation = 'idle'
        self.actor = Actor(self.animations[self.current_animation][0], pos)
        self.animation_timer = 0.0
        self.animation_speed = animation_speed
        self.current_frame = 0

    def set_animation(self, name):
        if self.current_animation != name:
            self.current_animation = name
            self.current_frame = 0

    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            animation_list = self.animations[self.current_animation]
            self.current_frame = (self.current_frame + 1) % len(animation_list)
            self.actor.image = animation_list[self.current_frame]

class Player(AnimatedCharacter):
    """ Classe do jogador, com física e controle. """
    def __init__(self, pos):
        animations = {
            'idle': ['player_stand'],
            'run': ['player_walk_1', 'player_walk_2'],
            'jump': ['player_jump']
        }
        super().__init__(pos, animations)
        self.velocity_y = 0
        self.is_on_ground = False
        self.facing_left = False

    def update(self, dt):
        is_moving = False
        if keyboard.left:
            self.actor.x -= PLAYER_SPEED
            self.facing_left = True
            is_moving = True
        if keyboard.right:
            self.actor.x += PLAYER_SPEED
            self.facing_left = False
            is_moving = True
        self.velocity_y += GRAVITY
        self.actor.y += self.velocity_y
        self.is_on_ground = False
        for platform in platforms:
            if self.actor.colliderect(platform.rect) and self.velocity_y > 0:
                self.actor.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_on_ground = True
                break
        if self.actor.left < 0: self.actor.left = 0
        if self.actor.right > level_width: self.actor.right = level_width
        if not self.is_on_ground: self.set_animation('jump')
        elif is_moving: self.set_animation('run')
        else: self.set_animation('idle')
        self.update_animation(dt)
        self.actor._flip_x = self.facing_left

class Enemy(AnimatedCharacter):
    """ Classe para os inimigos. """
    def __init__(self, pos):
        animations = {'idle': ['frog_idle', 'frog_rest'], 'jump': ['frog_jump']}
        super().__init__(pos, animations, animation_speed=0.4)
        self.actor.bottom = pos[1]

class Platform:
    """ Classe para as plataformas estáticas. """
    def __init__(self, pos, image):
        self.rect = Rect(pos, (TILE_SIZE, TILE_SIZE))
        self.image = image

# --- FUNÇÕES DE SETUP E JOGO ---
def setup_level():
    """ Constrói o nível a partir do LEVEL_MAP. """
    global platforms, enemies, coins, goal, score, level_width, level_height
    platforms, enemies, coins = [], [], []
    goal = None
    score = 0
    level_width = len(LEVEL_MAP[0]) * TILE_SIZE
    level_height = len(LEVEL_MAP) * TILE_SIZE
    for row_index, row in enumerate(LEVEL_MAP):
        for col_index, char in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if char == 'P':
                platform = Platform((x, y), 'terrain_grass_horizontal_middle')
                platforms.append(platform)
            elif char == 'C':
                coin = Actor('gem_yellow', center=(x + TILE_SIZE/2, y + TILE_SIZE/2))
                coins.append(coin)
            elif char == 'E':
                enemy = Enemy(pos=(x + TILE_SIZE/2, y + TILE_SIZE))
                enemies.append(enemy)
            elif char == 'F':
                goal = Actor('flag_yellow_a', center=(x + TILE_SIZE/2, y + TILE_SIZE/2))
                goal = goal

def setup_menu():
    """ Define os botões do menu. """
    global start_button, music_button, sfx_button, exit_button
    button_width, button_height = 240, 50
    start_button = Rect((WIDTH/2 - button_width/2, 220), (button_width, button_height))
    music_button = Rect((WIDTH/2 - button_width/2, 290), (button_width, button_height))
    sfx_button = Rect((WIDTH/2 - button_width/2, 360), (button_width, button_height))
    exit_button = Rect((WIDTH/2 - button_width/2, 430), (button_width, button_height))

def setup_game():
    """ Configura ou reinicia o estado do jogo. """
    global player, camera_x, camera_y
    setup_level()
    player = Player(pos=(100, 700))
    camera_x, camera_y = 0, 0

# --- FUNÇÕES PRINCIPAIS DO PYGAME ZERO ---
def draw_hud():
    """ Desenha a pontuação na tela. """
    screen.draw.text(f"SCORE: {score}", (20, 20), fontsize=40, color="white", owidth=1, ocolor="black")

def draw():
    """ Função principal de desenho. """
    screen.clear()
    screen.blit('background', (0,0))
    if game_state == 'menu':
        screen.draw.text("Kodland Adventure", center=(WIDTH/2, 150), fontsize=70, color="white", owidth=1)
        screen.draw.filled_rect(start_button, "green"); screen.draw.text("Start Game", center=start_button.center, fontsize=40)
        screen.draw.filled_rect(music_button, "orange"); music_text = "Music: ON" if background_music_on else "Music: OFF"; screen.draw.text(music_text, center=music_button.center, fontsize=40)
        screen.draw.filled_rect(sfx_button, "cyan"); sfx_text = "SFX: ON" if sfx_on else "SFX: OFF"; screen.draw.text(sfx_text, center=sfx_button.center, fontsize=40)
        screen.draw.filled_rect(exit_button, "red"); screen.draw.text("Exit", center=exit_button.center, fontsize=40)
    elif game_state == 'playing':
        for p in platforms: screen.blit(p.image, (p.rect.x - camera_x, p.rect.y - camera_y))
        for c in coins: screen.blit(c.image, (c.x - c.width/2 - camera_x, c.y - c.height/2 - camera_y))
        for e in enemies: screen.blit(e.actor.image, (e.actor.x - e.actor.width/2 - camera_x, e.actor.y - e.actor.height/2 - camera_y))
        if goal: screen.blit(goal.image, (goal.x - goal.width/2 - camera_x, goal.y - goal.height/2 - camera_y))
        screen.blit(player.actor.image, (player.actor.x - player.actor.width/2 - camera_x, player.actor.y - player.actor.height/2 - camera_y))
        draw_hud()
    elif game_state == 'game_over' or game_state == 'win':
        message = "GAME OVER" if game_state == 'game_over' else "YOU WIN!"
        screen.draw.text(message, center=(WIDTH/2, HEIGHT/2), fontsize=100)
        if game_state == 'win': screen.draw.text(f"Final Score: {score}", center=(WIDTH/2, HEIGHT/2 + 70), fontsize=50)
        screen.draw.text("Click to return to menu", center=(WIDTH/2, HEIGHT/2 + 120), fontsize=40)

def update(dt):
    """ Função principal de lógica. """
    global game_state, score, camera_x, camera_y
    if game_state != 'playing': return
    player.update(dt)
    for coin in list(coins):
        if player.actor.colliderect(coin):
            coins.remove(coin); score += 10
            if sfx_on: sounds.sfx_coin.play()
    for enemy in list(enemies):
        enemy.update_animation(dt)
        if player.actor.colliderect(enemy.actor):
            if player.velocity_y > 0 and abs(player.actor.bottom - enemy.actor.top) < 15:
                enemies.remove(enemy); score += 50; player.velocity_y = -7
                if sfx_on: sounds.sfx_disappear.play()
            else:
                game_state = 'game_over'
                if sfx_on: sounds.sfx_hurt.play()
                music.stop()
    if goal and player.actor.colliderect(goal): game_state = 'win'; music.stop()
    if player.actor.top > level_height: game_state = 'game_over'; music.stop()
    target_camera_x = player.actor.x - WIDTH / 2
    target_camera_y = player.actor.y - HEIGHT / 2
    camera_x += (target_camera_x - camera_x) * 0.1
    camera_y += (target_camera_y - camera_y) * 0.1
    if camera_x < 0: camera_x = 0
    if camera_x > level_width - WIDTH: camera_x = level_width - WIDTH
    if camera_y < 0: camera_y = 0
    if camera_y > level_height - HEIGHT: camera_y = level_height - HEIGHT

def on_key_down(key):
    if game_state == 'playing' and key == keys.SPACE and player.is_on_ground:
        player.velocity_y = JUMP_FORCE

def on_mouse_down(pos):
    global game_state, background_music_on, sfx_on
    if game_state == 'menu':
        if start_button.collidepoint(pos):
            setup_game()
            game_state = 'playing'
            if background_music_on:
                music.play('background_music')
                music.set_volume(0.3)
        elif music_button.collidepoint(pos):
            background_music_on = not background_music_on
            if sfx_on: sounds.button_click.play()
        elif sfx_button.collidepoint(pos):
            sfx_on = not sfx_on
            if sfx_on: sounds.button_click.play()
        elif exit_button.collidepoint(pos):
            exit()
    elif game_state in ['game_over', 'win']:
        game_state = 'menu'

# --- INICIALIZAÇÃO ---
setup_menu()
pgzrun.go()