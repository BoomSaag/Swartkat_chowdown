import pygame, sys, random
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import characters

"""
To do:
-----
Add new Game Over menu
Animate sprites
add sounds
add music
compile .exe file

Done:
----
Fix snake issue - sprites get confused as to their type. - fixed
Fix Swartkat falling though platforms - fixed!
Add game reset method to restart game - Done
Add new title menu - Done
Optimize platform interaction
Add graphics to all sprites - Platforms outstanding
"""

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
fps = 75

# Window Details
windowWidth = 1024
windowHeight = 768

surface = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption("-----  SwartKat ChowDown  -----")
BackGround = pygame.image.load("assets/images/BackGround_01.png")
ts_background = pygame.image.load("assets/images/SwartKatTitle_bkg.png")
ts_text = pygame.image.load("assets/images/SwartKatTitle_Text.png")
pygame.mixer.music.load("assets/music/Juhani Junkala [Chiptune Adventures] 1. Stage 1.ogg")
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1)


# Title Animation
title_frames = []
title_frames.append(ts_text)
# reverse range
for frame in range(1, 9):
    title_frames.append(pygame.transform.scale(ts_text, [int(windowWidth - (windowWidth * (frame/400))), int(windowHeight - (windowHeight * (frame/400)))]))
index = 0
cycle_complete = False


# Colours
khaki = [150, 150, 100]

# Fonts
score_font = pygame.font.SysFont(None, 80)
smaller_font = pygame.font.SysFont(None, 50)
tiny_font = pygame.font.SysFont(None, 20)

# Game Variables
gameState = 0
# 0 = Start Screen
# 1 = Game started
# 2 = Game Over
lastMouse = 0
lastSnake = 0
is_on_platform = False
player_score = 0

# Player Group:
Player_group = pygame.sprite.Group()
player = characters.Player(windowWidth / 2, windowHeight - 80, windowWidth)
Player_group.add(player)

# Health bar:
hearts = pygame.sprite.Group()
heart1 = characters.Indicators(windowWidth - 160, 40)
heart2 = characters.Indicators(windowWidth - 100, 40)
heart3 = characters.Indicators(windowWidth - 40, 40)
hearts.add(heart3, heart2, heart1)

# Platforms

plat_group = pygame.sprite.Group()
plat = characters.Platforms
platform1 = plat(0, windowHeight - 230, 200, [255, 0 , 0])
platform2 = plat(windowWidth/2 - 75, windowHeight - 230, 150, khaki)
platform3 = plat(windowWidth - 200, windowHeight - 230, 200, [0, 255, 0])
platform4 = plat(0, windowHeight/2 - 40, 200, [0, 0, 255])
platform5 = plat(windowWidth - 200, windowHeight / 2 - 120, 200, khaki)
platform6 = plat(windowWidth / 2 - 50, windowHeight / 2 - 100, 100, khaki)
platform7 = plat(windowWidth/2, 100, 100, khaki)
platform8 = plat(0, 60, 100, khaki)
plat_group.add(platform1, platform2, platform3, platform4, platform5, platform6, platform7, platform8)


# Collectible Groups
col_group = pygame.sprite.Group()
mouse_group = pygame.sprite.Group()
collect = characters.Collectibles


# add collectible
def add_col():
    global player_score, lastMouse, lastSnake

    spawn_count = 3
    snake_delay = 2000
    mouse_delay = 16000

    if len(col_group) < spawn_count:
        timestamp = pygame.time.get_ticks()
        rand_platform = random.randint(0, len(plat_group) - 1)
        platform = plat_group.sprites()[rand_platform]
        collectible01 = collect(random.randint(platform.rect.left, platform.rect.right - 40), platform.rect.top + 1, random.randint(1, 2))
        if len(col_group) >= 1:
            if not pygame.sprite.spritecollide(platform, col_group, False) and timestamp - col_group.sprites()[0].spawntime > 1500:
                if not (player.rect.bottom - 1) == platform.rect.top:
                    if collectible01.variant == 2:
                        if timestamp - lastSnake > snake_delay:
                            col_group.add(collectible01)
                            lastSnake = pygame.time.get_ticks()
                        else:
                            pass
                    else:
                        col_group.add(collectible01)
            else:
                pass
        elif collectible01.variant == 2:
            if timestamp - lastSnake > snake_delay:
                col_group.add(collectible01)
                lastSnake = pygame.time.get_ticks()
            else:
                pass
        else:
            col_group.add(collectible01)

    # spawn mouse:
    # Checks that player is not on ground and then checks when the last mouse was spawned and if it can spawn again
    if is_on_platform is True and len(col_group) < spawn_count:
        mouse = collect(0, windowHeight - 80, 3)
        if lastMouse == 0:
            col_group.add(mouse)
            lastMouse = mouse.spawntime
        else:
            mouse_ticks = pygame.time.get_ticks()
            if mouse_ticks - lastMouse >= mouse_delay:
                col_group.add(mouse)
                lastMouse = mouse.spawntime

    # player collects collectible:
    for idx, i in enumerate(col_group):
        if pygame.sprite.collide_mask(player, i):
            if i.variant == 2:
                player.health -= i.damage
                player.ouch.play()
            else:
                player_score += i.score
                i.eaten.play()
            i.kill()


def on_platform():

    global is_on_platform

    for idx, platform in enumerate(plat_group):
        # Checks if player has jumped onto platform
        if platform.rect.left < player.rect.center[0] < platform.rect.right:
            if pygame.sprite.collide_mask(player, platform) and player.rect.center[1] < platform.rect.center[1]:
                player.rect.bottom = platform.rect.top + 1
                player.floor = platform.rect.top + 1
                is_on_platform = True

        # Checks if player has left platform to drop to floor
        if is_on_platform is True and pygame.sprite.spritecollideany(player, plat_group):
            if (platform.rect.left - 10 > player.rect.center[0] > platform.rect.left - 50) or (
                    platform.rect.right + 10 < player.rect.center[0] < platform.rect.right + 50):
                if platform.rect.top - (player.rect.bottom - player.rect.top) < player.rect.center[1] < platform.rect.bottom:
                    player.floor = player.ground
                    if not player.hasJumped:
                        player.vy = 0
                    is_on_platform = False
        # Checks if player is not touching any platform
        if len(pygame.sprite.spritecollide(player, plat_group, False)) == 0:
            player.floor = player.ground


def Screen_indicators():

    score_text = score_font.render("SCORE: " + str(player_score), True, [0, 100, 150])
    surface.blit(score_text, (0, 0))

    for idx, heart in enumerate(hearts):
        if player.health <= idx:
            heart.state = True


def title_screen():
    global gameState, index, cycle_complete

    current_frame = title_frames[int(index)]
    frame_cycle = 0.7

    surface.blit(ts_background, (0, 0))
    title_size = current_frame.get_size()
    surface.blit(current_frame, ((windowWidth - title_size[0]) /2, (windowHeight - title_size[1])))
    start = smaller_font.render("Press 'SPACE' to Start!!!", True, [200, 200, 200])
    author = tiny_font.render("by Alexander Schweickerdt", True, [255, 255, 255])
    start_size = start.get_size()
    auth_size = author.get_size()
    surface.blit(start, (20, windowHeight - start_size[1] - 20))
    surface.blit(author, (windowWidth - auth_size[0] - 10, windowHeight - auth_size[1] - 10))

    if index <= 8 and cycle_complete is False:
        index += frame_cycle
    else:
        cycle_complete = True
    if index >= 2 and cycle_complete is True:
        index -= frame_cycle
    else:
        cycle_complete = False


def gameStarted():

    global gameState

    if player.health > 0:
        surface.blit(BackGround, (0, 0))
        Player_group.update()
        hearts.draw(surface)
        hearts.update()
        Screen_indicators()
        add_col()
        on_platform()
        plat_group.draw(surface)
        col_group.draw(surface)
        col_group.update()
        Player_group.draw(surface)
    else:
        gameState = 2


def GameOver():

    surface.fill([0, 0, 0])
    gameover = score_font.render("GAME OVER", True, [200, 50, 50])
    yourScore = smaller_font.render("Final Score: " + str(player_score), True, [255, 255, 0])
    restart = smaller_font.render("Press 'SPACE' to retry!", True, [200, 200, 200])
    size = gameover.get_size()
    size2 = yourScore.get_size()
    surface.blit(gameover, ((windowWidth / 2) - (size[0]/2), (windowHeight / 2) - (size[1] / 2)))
    surface.blit(yourScore, ((windowWidth / 2) - (size2[0] / 2), (windowHeight) - 300))
    surface.blit(restart, (20, windowHeight - 50))


def reset():

    global player_score, lastMouse, lastSnake, player

    col_group.empty()
    player.health = 3
    player.floor = player.ground
    player.rect.center = [windowWidth / 2, windowHeight - 80]
    player_score = 0
    for heart in hearts:
        heart.state = False
    lastMouse = 0
    lastSnake = 0


def quitGame():

    pygame.quit()
    sys.exit()

# Main Loop
while True:

    for event in GAME_EVENTS.get():

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                quitGame()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                if gameState == 0:
                    gameState = 1
                elif gameState == 2:
                    reset()
                    gameState = 1

        if event.type == GAME_GLOBALS.QUIT:
            quitGame()
    if gameState == 0:
        title_screen()
    elif gameState == 1:
        gameStarted()
    elif gameState == 2:
        GameOver()
    pygame.display.flip()
    clock.tick(fps)


