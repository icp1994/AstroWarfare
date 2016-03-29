# -*- file-encoding: utf-8 -*-
"""
Created on March 22, 2016 at 21:45

@author: carl
"""

import sys
import pygame as pg
from random import randrange


class Block(pg.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = pg.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)


class Button(pg.font.Font):
    def __init__(self, text, state, font=None, font_size=30,
                 font_color=pg.Color("white"), xcoord=0, ycoord=0):
        super().__init__(font, font_size)
        self.text = text
        self.state = state
        self.info = {}
        self.font_size = font_size
        self.font_color = font_color
        self.label = self.render(self.text, True, self.font_color)
        self.label_rect = self.label.get_rect(center=(xcoord, ycoord))
        self.width = self.label_rect.width
        self.height = self.label_rect.height

    def set_position(self, pos):
        self.label_rect = self.label.get_rect(center=pos)

    def set_font_color(self, color):
        self.font_color = color
        self.label = self.render(self.text, True, self.font_color)

    def is_mouse_selection(self, pos):
        if self.label_rect.collidepoint(pos):
            return True
        return False


class Game:
    def __init__(self, screen, states, initial_state):
        self.screen = screen
        self.states = states
        self.current_state = initial_state
        self.state = self.states[self.current_state]
        self.fps = 60
        self.clock = pg.time.Clock()
        self.done = False

    def event_loop(self):
        for event in pg.event.get():
            self.state.get_event(event)

    def flip_state(self):
        next_state = self.state.next_state
        self.state.done = False
        self.current_state = next_state
        data = self.state.data
        self.state = self.states[self.current_state]
        self.state.startup(data)

    def update(self, delta):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(delta)

    def draw(self):
        self.state.draw(self.screen)

    def run(self):
        while not self.done:
            delta = self.clock.tick(self.fps)
            self.event_loop()
            self.update(delta)
            self.draw()
            pg.display.update()


class GameState:
    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state = None
        self.screen_rect = pg.display.get_surface().get_rect()
        self.screen_width = self.screen_rect.width
        self.screen_height = self.screen_rect.height
        self.time = 0
        self.data = {}
        self.font = pg.font.SysFont(None, 80)

    def startup(self, data):
        self.data = data

    def get_event(self, event):
        pass

    def update(self, delta):
        pass

    def draw(self, surface):
        pass


class SplashScreen(GameState):
    def __init__(self):
        super().__init__()
        self.title = self.font.render("Welcome to Astro Warfare", True, pg.Color("dodgerblue"))
        self.title_rect = self.title.get_rect(center=self.screen_rect.center)
        self.next_state = "MENU"
        self.flag = True

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            self.done = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.done = True

    def update(self, delta):
        self.time += delta
        if self.time >= 420:
            self.time = 0
            self.flag = not self.flag

    def draw(self, surface):
        surface.fill(pg.Color("navyblue"))
        surface.blit(self.title, self.title_rect)
        if self.flag:
            confirm = pg.font.SysFont(None, 25).render("PRESS ANY KEY TO CONTINUE", True, pg.Color("dodgerblue"))
            surface.blit(confirm, confirm.get_rect(centerx=self.screen_rect.centerx,
                                                   centery=self.screen_rect.centery + 60))


class GameMenu(GameState):
    def __init__(self, items=None, bg_color=pg.Color("black"), font=None,
                 font_size=60, font_color=pg.Color("green")):
        super().__init__()
        self.title = self.font.render("Astro Warfare", True, pg.Color("orange"))
        self.title_rect = self.title.get_rect(centerx=self.screen_rect.centerx, centery=40)
        self.bg_color = bg_color
        if items is not None:
            self.items = items
        self.font = font
        self.font_size = font_size
        self.font_color = font_color

    def startup(self, data):
        self.data = data
        self.buttons = []
        total_items = len(self.items)
        for index, item in enumerate(self.items):
            text, state, info = item
            button = Button(text, state, self.font, self.font_size, self.font_color)
            button.info = info
            xcoord = self.screen_width // 2
            if total_items % 2 == 0:
                ycoord = (self.screen_height // 2) - (total_items - 2 * index - 1) * (button.height // 2)
            else:
                ycoord = (self.screen_height // 2) - ((total_items - 1) // 2 - index) * button.height
            button.set_position((xcoord, ycoord))
            self.buttons.append(button)

        self.mouse_visibility = False
        self.current_button = None

    def set_mouse_visiblity(self):
        if self.mouse_visibility:
            pg.mouse.set_visible(True)
        else:
            pg.mouse.set_visible(False)

    def set_mouse_selection(self, pos, mouse_button=None, menu_button=None):
        if mouse_button == 1:
            for index, button in enumerate(self.buttons):
                if button.is_mouse_selection(pos):
                    self.next_state = button.state
                    self.data.update(button.info)
                    self.done = True
                    return
        if menu_button is not None:
            if menu_button.is_mouse_selection(pos):
                menu_button.set_font_color(pg.Color("gold"))
                menu_button.set_bold(True)
            else:
                menu_button.set_font_color(pg.Color("green"))
                menu_button.set_bold(False)

    def set_keyboard_selection(self, key):
        for button in self.buttons:
            button.set_bold(False)
            button.set_font_color(pg.Color("green"))

        if self.current_button is None:
            self.current_button = 0
        else:
            if key == pg.K_UP:
                if self.current_button > 0:
                    self.current_button -= 1
                else:
                    self.current_button = len(self.buttons) - 1
            elif key == pg.K_DOWN:
                if self.current_button < len(self.buttons) - 1:
                    self.current_button += 1
                else:
                    self.current_button = 0
            elif key == pg.K_RETURN:
                self.next_state = self.buttons[self.current_button].state
                self.data.update(self.buttons[self.current_button].info)
                self.done = True

        self.buttons[self.current_button].set_bold(True)
        self.buttons[self.current_button].set_font_color(pg.Color("gold"))

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key in (pg.K_UP, pg.K_DOWN, pg.K_RETURN):
                self.mouse_visibility = False
                self.set_keyboard_selection(event.key)
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.mouse_visibility = True
            self.set_mouse_selection(pos=event.pos, mouse_button=event.button)

    def update(self, delta):
        if pg.mouse.get_rel() != (0, 0):
            self.mouse_visibility = True
            self.current_button = None
        self.set_mouse_visiblity()
        for button in self.buttons:
            if self.mouse_visibility:
                self.set_mouse_selection(pos=pg.mouse.get_pos(), menu_button=button)

    def draw(self, surface):
        surface.fill(pg.Color("purple"))
        surface.blit(self.title, self.title_rect)
        for button in self.buttons:
            surface.blit(button.label, button.label_rect)


class GameHelp(GameMenu):
    def startup(self, data):
        self.help_texts = ["Astro Warfare is a classic space-shooter. Don't let the enemies fly pass you.",
                           "Use directioanal keys to move your ship and SPACEBAR to shoot.",
                           "You are given certain amount of ammunition and enemy allowance based on the difficulty.",
                           "Shoot down 25 enemies on each level to clear the level.", "Good Luck, Have Fun!"]
        self.items = (("OK", "MENU", {}),)
        super().startup(data)

    def draw(self, surface):
        super().draw(surface)
        for index, text in enumerate(self.help_texts):
            message = pg.font.Font(None, 30).render(text, True, pg.Color("greenyellow"))
            surface.blit(message, message.get_rect(centerx=self.screen_rect.centerx,
                                                   centery=100 + 25 * index))


class GameDifficulty(GameMenu):
    def startup(self, data):
        self.items = (("LEVEL 0", "PLAY", {"level": 0}), ("LEVEL 1", "PLAY", {"level": 1}),
                      ("LEVEL 2", "PLAY", {"level": 2}), ("LEVEL 3", "PLAY", {"level": 3}),
                      ("LEVEL 4", "PLAY", {"level": 4}), ("LEVEL 5", "PLAY", {"level": 5}))
        super().startup(data)


class GamePlay(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "OVER"

    def startup(self, data):
        self.data = data
        self.time = 1000
        self.enemy_list, self.shooter_list, self.all_sprite_list = \
            pg.sprite.Group(), pg.sprite.Group(), pg.sprite.Group()

        self.player = Block("player.png")
        self.player.rect.centerx = self.screen_width // 2
        self.player.rect.centery = self.screen_height - self.player.rect.height // 2
        self.all_sprite_list.add(self.player)

        pg.mouse.set_visible(False)

        self.level = data["level"]
        self.speed = 1 + self.level
        self.lives = 7 - self.level
        self.ammo = 55 - 5 * self.level
        self.score = 0

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                if self.score == 25 or self.ammo == 0 or self.lives == 0:
                    self.data.update({"score": self.score, "ammo": self.ammo, "lives": self.lives})
                    self.done = True
                else:
                    self.ammo -= 1
                    shooter = Block("laser.png")
                    shooter.rect.centerx = self.player.rect.centerx
                    shooter.rect.centery = self.player.rect.y - shooter.rect.height // 2
                    self.shooter_list.add(shooter)
                    self.all_sprite_list.add(shooter)

    def update(self, delta):
        pressed_keys = pg.key.get_pressed()
        if pressed_keys[pg.K_LEFT]:
            self.player.rect.x -= 10
        elif pressed_keys[pg.K_RIGHT]:
            self.player.rect.x += 10

        if self.player.rect.x + self.player.rect.width > self.screen_width:
            self.player.rect.x = 0
        if self.player.rect.x < 0:
            self.player.rect.x = self.screen_width - self.player.rect.width

        self.time += delta
        if self.time >= 1000:
            self.time = 0
            enemy = Block("enemy.png")
            enemy.rect.centerx = randrange(enemy.rect.width // 2, self.screen_width - enemy.rect.width // 2)
            enemy.rect.centery = - randrange(enemy.rect.height, 2 * enemy.rect.height)
            self.enemy_list.add(enemy)
            self.all_sprite_list.add(enemy)

        for enemy in self.enemy_list:
            enemy.rect.y += self.speed
            if enemy.rect.y > self.screen_height:
                enemy.kill()
                if self.lives > 0:
                    self.lives -= 1

        for shooter in self.shooter_list:
            shooter.rect.y -= 5
            if shooter.rect.y < 0:
                shooter.kill()

        enemy_hit_dict = pg.sprite.groupcollide(self.enemy_list, self.shooter_list, True, True, pg.sprite.collide_mask)
        for _ in enemy_hit_dict:
            self.score += 1

        if self.score == 25 or self.ammo == 0 or self.lives == 0:
            self.data.update({"score": self.score, "ammo": self.ammo, "lives": self.lives})
            self.done = True

    def draw(self, surface):
        surface.set_clip(0, 0, self.screen_width, 40)
        surface.fill(pg.Color("black"))
        text = pg.font.SysFont(None, 30).render('LEVEL: ' + str(self.level), True, pg.Color("blue"))
        surface.blit(text, text.get_rect(centerx=self.screen_width // 5, centery=25))
        text = pg.font.SysFont(None, 30).render('AMMO: ' + str(self.ammo), True, pg.Color("blue"))
        surface.blit(text, text.get_rect(centerx=2 * self.screen_width // 5, centery=25))
        text = pg.font.SysFont(None, 30).render('LIVES: ' + str(self.lives), True, pg.Color("blue"))
        surface.blit(text, text.get_rect(centerx=3 * self.screen_width // 5, centery=25))
        text = pg.font.SysFont(None, 30).render('SCORE: ' + str(self.score), True, pg.Color("blue"))
        surface.blit(text, text.get_rect(centerx=4 * self.screen_width // 5, centery=25))
        pg.draw.aaline(surface, pg.Color("white"), (0, 35), (self.screen_width, 35), 5)
        surface.set_clip(0, 40, self.screen_width, self.screen_height - 40)
        surface.fill(pg.Color("black"))
        self.all_sprite_list.draw(surface)
        surface.set_clip(0, 0, self.screen_width, self.screen_height)


class GameOver(GameMenu):
    def startup(self, data):
        self.data = data
        level = data["level"]
        if data["score"] == 25:
            message = "Congratulations! You have completed this level."
            color = pg.Color("green")
            if level < 5:
                self.items = (("NEXT LEVEL", "PLAY", {"level": 1 + level}), ("PLAY AGAIN", "PLAY", {"level": level}),
                              ("MAIN MENU", "MENU", {}), ("QUIT", "QUIT", {}))
            else:
                self.items = (("PLAY AGAIN", "PLAY", {"level": level}), ("MAIN MENU", "MENU", {}), ("QUIT", "QUIT", {}))
        else:
            color = pg.Color("red")
            self.items = (("RETRY", "PLAY", {"level": level}), ("MAIN MENU", "MENU", {}), ("QUIT", "QUIT", {}))
            if data["ammo"] == 0:
                message = "Oops! You are out of ammo."
            else:
                message = "Sorry! You have lost all available lives"
        self.title = pg.font.SysFont(None, 50).render(message, True, color)
        self.title_rect = self.title.get_rect(centerx=self.screen_rect.centerx, centery=80)
        super().startup(data)


class GameExit(GameState):
    def __init__(self):
        super().__init__()
        self.quit = True


if __name__ == "__main__":
    pg.init()
    game_screen = pg.display.set_mode((1366, 768), pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF)
    menu = (("DIFFICULTY", "DIFFICULTY", {}), ("HELP", "HELP", {}), ("QUIT", "QUIT", {}))
    game_states = {"SPLASH": SplashScreen(), "MENU": GameMenu(menu), "HELP": GameHelp(),
                   "DIFFICULTY": GameDifficulty(), "PLAY": GamePlay(), "OVER": GameOver(), "QUIT": GameExit()}
    game = Game(game_screen, game_states, "SPLASH")
    game.run()
    pg.quit()
    sys.exit()
