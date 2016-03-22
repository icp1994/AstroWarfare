# -*- file-encoding: utf-8 -*-
"""
Created on March 20, 2016 at 13:13

@author: carl
"""


import pygame
from random import randrange
from sys import exit

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

SCREEN_SIZE = (620, 680)


class Block(pygame.sprite.Sprite):
    # the building blocks for every object in the game
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()


class Button:
    # to display menu-buttons to give user choices
    def __init__(self, msg, font, color, position, size):
        self.position = position
        self.size = size
        self.text = font.render(msg, True, GREEN)
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.image.blit(self.text, (5, 5))

    def render(self, surface):
        # to decide where to put the button on a given screen
        surface.blit(self.image, self.position)

    def is_over(self, point):
        # to decide which button, if any, the user clicks
        # TODO: implement keyboard support
        x, y = self.position
        w, h = self.size
        if x < point[0] < x + w:
            if y < point[1] < y + h:
                return True
        return False


def menu(screen, font):
    # displaying the menu on the screen
    pygame.mouse.set_visible(True)
    screen.fill(BLACK)
    text = font.render('Welcome to the Space Invader!', True, GREEN)
    screen.blit(text, (100, 20))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill(BLACK)
        text = font.render('Welcome to the Space Invader!', True, GREEN)
        screen.blit(text, (100, 20))
        # create all the menu buttons and store them in a dictionary
        buttons = {}
        button = Button('HELP', font, BLACK, (120, 420), (120, 40))
        buttons['h'] = button
        button.render(screen)  # all the instructions to need
        for i in range(5):
            # 5 levels of difficulty
            msg = 'LEVEL ' + str(i)
            button = Button(msg, font, BLACK, (250, 300 + i * 60), (120, 40))
            buttons[i] = button
            button.render(screen)
        button = Button('QUIT', font, BLACK, (420, 420), (120, 40))
        buttons['q'] = button
        button.render(screen)  # quit button
        pygame.display.flip()
        # this is ugly. need to refactor
        while True:
            for new_event in pygame.event.get():
                if new_event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif new_event.type == pygame.MOUSEBUTTONDOWN:
                    # check the option user chooses
                    for button_name, button in buttons.items():
                        if button.is_over(new_event.pos):
                            if button_name == 'h':
                                while True:  # show help
                                    screen.fill(BLACK)
                                    help_font = pygame.font.SysFont(None, 24)
                                    msg = 'Press left and right arrow keys to move your launcher sideways.'
                                    text = help_font.render(msg, True, GREEN)
                                    screen.blit(text, (10, 20))
                                    msg = 'Use SPACE to shoot. Score 20 points on each level to pass it.'
                                    text = help_font.render(msg, True, GREEN)
                                    screen.blit(text, (10, 50))
                                    button = Button('OK', font, BLACK, (250, 300), (120, 40))
                                    button.render(screen)
                                    pygame.display.flip()
                                    for another_event in pygame.event.get():
                                        if another_event.type == pygame.QUIT:
                                            pygame.quit()
                                            exit()
                                        elif another_event.type == pygame.MOUSEBUTTONDOWN:
                                            # go back to main menu
                                            if button.is_over(another_event.pos):
                                                return menu(screen, font)
                            elif button_name == 'q':  # quit game
                                pygame.quit()
                                exit()
                            else:
                                return button_name  # return the level(an int)


def run(level, screen, font):
    pygame.mouse.set_visible(False)
    # starts game with a particular level
    block_list = pygame.sprite.Group()
    shooter_list = pygame.sprite.Group()
    all_sprites_list = pygame.sprite.Group()

    for _ in range(5):
        # create random enemy blocks on the top half of the screen
        block = Block(WHITE, 15, 15)
        block.rect.x = randrange(25, SCREEN_SIZE[0] - 40)
        block.rect.y = randrange(40, SCREEN_SIZE[1]//4)

        block_list.add(block)
        all_sprites_list.add(block)

    player = Block(RED, 30, 10)  # the player block
    player.rect.x = SCREEN_SIZE[0] // 2 - 15
    player.rect.y = SCREEN_SIZE[1] - 10
    all_sprites_list.add(player)

    clock = pygame.time.Clock()

    # adjusting difficulty according to the level
    speed = 1 + level / 4
    lives = 5 - level
    ammo = 85 - 15 * level
    score = 0
    while True:
        for main_event in pygame.event.get():
            if main_event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif main_event.type == pygame.KEYDOWN:
                if main_event.key == pygame.K_SPACE:
                    if score == 20 or ammo == 0 or lives == 0:
                        # if the taget score is reached or the player fails, finish the game
                        return
                    else:
                        ammo -= 1
                        shooter = Block(GREEN, 10, 10)  # create the shooter block
                        shooter.rect.x = player.rect.x + 5
                        shooter.rect.y = player.rect.y - 5
                        shooter_list.add(shooter)
                        all_sprites_list.add(shooter)

        if score == 20:
            # target score is reached
            screen.set_clip(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])
            screen.fill(BLACK)
            text = font.render('Congratulations, You have passed the level!', True, RED)
            screen.blit(text, (30, 200))
            text = font.render('Press SPACE to continue', True, RED)
            screen.blit(text, (30, 300))
            pygame.display.flip()
            continue

        if ammo == 0:
            # no ammo
            if not shooter_list:  # no more shooter block left in the screen
                screen.set_clip(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])
                screen.fill(BLACK)
                text = font.render('Out of Ammo!', True, RED)
                screen.blit(text, (30, 200))
                text = font.render('Final score: ' + str(score), True, RED)
                screen.blit(text, (30, 300))
                text = font.render('Press SPACE to continue', True, RED)
                screen.blit(text, (30, 400))
                pygame.display.flip()
                continue

        if lives == 0:
            # no more chances left
            screen.set_clip(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])
            screen.fill(BLACK)
            text = font.render('Lost all your lives!', True, RED)
            screen.blit(text, (30, 200))
            text = font.render('Final score: ' + str(score), True, RED)
            screen.blit(text, (30, 300))
            text = font.render('Press SPACE to continue', True, RED)
            screen.blit(text, (30, 400))
            pygame.display.flip()
            continue

        pressed_keys = pygame.key.get_pressed()
        # basic movement of the player pad
        if pressed_keys[pygame.K_LEFT]:
            player.rect.x -= 5
        elif pressed_keys[pygame.K_RIGHT]:
            player.rect.x += 5

        if player.rect.x + 20 > SCREEN_SIZE[0]:
            player.rect.x = 0
        if player.rect.x < 0:
            player.rect.x = SCREEN_SIZE[0] - 20

        for block in block_list:
            # the approach of the enemy blocks depending on the level; if they cross the player, player loses one life
            block.rect.y += speed
            if block.rect.y > SCREEN_SIZE[1]:
                if lives > 0:
                    lives -= 1
                block.rect.x = randrange(25, SCREEN_SIZE[0] - 40)
                block.rect.y = 0

        tmp = pygame.sprite.Group()
        # the upward-movement of the shooter block
        for shooter in shooter_list:
            shooter.rect.y -= 5
            if shooter.rect.y < 0:  # shooter is out of screen
                tmp.add(shooter)
            block_hit_list = pygame.sprite.spritecollide(shooter, block_list, False)
            if block_hit_list:  # this list contains max. one enemy block as one shooter can destroy only one block
                tmp.add(shooter)
            for block in block_hit_list:  # re-deploy destroyed enemy blocks; meanwhile the score increases
                block.rect.x = randrange(25, SCREEN_SIZE[0] - 40)
                block.rect.y = 0
                score += 1

        for shooter in tmp:  # shooters which are out of screen or killed an enemy are removed from screen
            shooter_list.remove(shooter)
            all_sprites_list.remove(shooter)

        screen.set_clip(0, 0, SCREEN_SIZE[0], 40)  # live stats
        screen.fill(BLACK)
        text = font.render('LEVEL: ' + str(level), True, BLUE)
        screen.blit(text, (10, 10))
        text = font.render('AMMO: ' + str(ammo), True, BLUE)
        screen.blit(text, (155, 10))
        text = font.render('LIVES: ' + str(lives), True, BLUE)
        screen.blit(text, (310, 10))
        text = font.render('SCORE: ' + str(score), True, BLUE)
        screen.blit(text, (465, 10))
        pygame.draw.aaline(screen, WHITE, (0, 35), (SCREEN_SIZE[0], 35), 5)
        screen.set_clip(0, 40, SCREEN_SIZE[0], SCREEN_SIZE[1] - 40)  # game screen
        screen.fill(BLACK)
        all_sprites_list.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def main():
    # manages the menu and the game
    pygame.init()

    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Space Invader")

    font = pygame.font.SysFont(None, 40)

    while True:  # hack!
        level = menu(screen, font)
        run(level, screen, font)


if __name__ == '__main__':
    main()
