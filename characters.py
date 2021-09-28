import random

import pygame
"""
Collectibles:
Birds - 1:
Appear for a few seconds then disappear.
Player to collect these for points.
Appear randomly on platforms. <-- this might be a bit of a challenge. How to randomly choose platform?
disappear when player touches them.

Snake - 3:
If collected, hurts player.
Takes one heart.

Mouse - 2:
Runs along bottom of the screen when player is on a platform.
Gives additional points.
"""

# Player Class

gravity = 2


class Player(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y, windowWidth):
        super(Player, self).__init__()
        self.image = pygame.image.load("assets/images/SwartKat_Sprite_01.png")
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.size = self.image.get_size()
        self.img_left = self.image
        self.img_right = pygame.transform.flip(self.image, True, False)
        self.jump_snd = pygame.mixer.Sound("assets/sound/cartoon_jump.ogg")
        self.land = pygame.mixer.Sound("assets/sound/Balloon_Wall.ogg")
        self.land.set_volume(0.2)
        self.ouch = pygame.mixer.Sound("assets/sound/Cat_Ouch.ogg")
        self.ouch.set_volume(0.5)
        self.health = 3
        self.speed = 1
        self.vx = self.speed
        self.jump_height = 28
        self.vy = self.jump_height
        self.maxSpeed = 15
        self.windowWidth = windowWidth
        self.floor = self.rect.bottom
        self.ground = self.floor
        self.hasJumped = False
        self.landed = 0

    def update(self):
        keystate = pygame.key.get_pressed()

        # Leftward
        if keystate[pygame.K_LEFT]:
            self.image = self.img_left
            if self.rect.left > 0:
                if self.vx > 0:
                    self.vx = -self.speed
                if self.vx >= -self.maxSpeed:
                    self.vx *= 1.1
                self.rect.move_ip([self.vx, 0])
            else:
                self.rect.left = 0
        # Rightward
        if keystate[pygame.K_RIGHT]:
            self.image = self.img_right
            if self.rect.right < self.windowWidth:
                if self.vx < 0:
                    self.vx = self.speed
                if self.vx <= self.maxSpeed:
                    self.vx *= 1.1
                self.rect.move_ip([self.vx, 0])
            else:
                self.rect.right = self.windowWidth

        # Speed Reset
        if not keystate[pygame.K_LEFT] and not keystate[pygame.K_RIGHT]:
            self.vx = self.speed

        # Jump
        if keystate[pygame.K_SPACE]:
            self.hasJumped = True
            self.landed = 1
            if self.rect.bottom >= self.floor:
                self.jump_snd.play()

        if self.hasJumped is True:
            self.rect.move_ip([0, -self.vy])


        # Gravity
        if self.rect.bottom < self.floor:
            if not self.hasJumped:
                self.rect.move_ip(0, -self.vy)
            self.vy -= gravity

        else:
            self.vy = self.jump_height
            self.hasJumped = False
            self.rect.bottom = self.floor
            if self.landed == 1:
                self.land.play()
                self.landed = 0


class Platforms(pygame.sprite.Sprite):

    def __init__(self, plat_x, plat_y, width, colour):
        super(Platforms, self).__init__()
        self.tile = pygame.image.load("assets/images/50x30-platform-tile.png")
        self.image = pygame.Surface([width, 30])
        for x in range(0, int(width/50)):
            self.image.blit(self.tile, [(50 * x), 0])
        self.rect = self.image.get_rect()
        self.rect.topleft = [plat_x, plat_y]


class Collectibles(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y, variant):
        super(Collectibles, self).__init__()
        self.variant = variant
        self.speeds = [5, 8, 10, 15, 20]
        self.vx = 8
        self.rnd_speed = self.speeds[random.randrange(0, 5)]
        # Bird
        if self.variant == 1:
            self.image = pygame.image.load("assets/images/Bird01.png")
            self.score = 10
            self.eaten = pygame.mixer.Sound("assets/sound/Eat_Bird-01.ogg")
            self.eaten.set_volume(0.5)
        # Mouse
        elif self.variant == 3:
            self.raw = pygame.image.load("assets/images/Mouse01.png")
            self.image = pygame.transform.scale(self.raw, [70, 30])
            # the faster the mouse, the higher the score:
            self.score = 5 * self.rnd_speed
            self.eaten = pygame.mixer.Sound("assets/sound/Eat_Mouse-01.ogg")
            self.eaten.set_volume(0.5)
        # Snake
        elif self.variant == 2:
            self.image = pygame.image.load("assets/images/Snake01.png")
            self.damage = 1
            self.score = 20
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [pos_x, pos_y]
        self.spawntime = pygame.time.get_ticks()
        self.time_alive = 0

    def update(self):

        # Bird
        if self.variant == 1:
            self.time_alive = pygame.time.get_ticks()
            if self.time_alive - self.spawntime > 4000:
                self.kill()

        # Snake
        if self.variant == 2:
            self.time_alive = pygame.time.get_ticks()
            if self.time_alive - self.spawntime > 3000:
                self.kill()

        # for mouse
        if self.variant == 3:
            if self.rect.center[0] < 1024:
                self.rect.move_ip([self.rnd_speed, 0])
            else:
                self.kill()


class Indicators(pygame.sprite.Sprite):

    def __init__(self, pos_x, pos_y):
        super(Indicators, self).__init__()
        self.image = pygame.image.load("assets/images/Heart01.png")
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.state = False

    def update(self):
        if self.state is True:
            self.image = pygame.image.load("assets/images/Heart02.png")
        else:
            self.image = pygame.image.load("assets/images/Heart01.png")













