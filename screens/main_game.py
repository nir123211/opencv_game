import random
import time
from copy import copy
import math

import cv2 as cv
import keyboard as kb
from scripts.init_values import initialize_image_and_aim, init_enemies
from scripts.enemies import Enemies
from scripts.game_mechanics import move_aim, shoot_missile, scope_zoom_animation, \
     toggle_night_vision, shoot_bullet, create_sniper_scope_image, move_aim_breath, draw_launcher_scope
from scripts import sounds
from scripts.utils import waste_time, kill_with_mouse


def main_game(image, ammo_amount):
    # setting up initial variables
    original_image, aim = initialize_image_and_aim(image)
    mode = 'launcher'
    night_vision = False
    breath = 50
    scope_y_movement = 1
    do_animation = True
    enemies = Enemies()
    zoom = False
    ammo = ammo_amount
    starting_time = time.time()
    # cheat for killing with mouse
    cv.setMouseCallback('game', kill_with_mouse, enemies)
    # game music
    sounds.game_music.play()

    while True:
        if random.randrange(0, 40) == 20:
            enemies.add_soldier((random.randrange(50, 400), random.randrange(350, 450)))
        # creating temp image to not draw on the original
        frame = copy(original_image)
        # exit the game
        if kb.is_pressed("c"):
            quit()
        # scope movement
        aim = move_aim(aim, mode)

        if kb.is_pressed("r"):
            cv.waitKey(100)
            sounds.reloading.play()
            if zoom:
                scope_zoom_animation('out', frame, aim, enemies)
            ammo_to_reload = 5 - ammo
            for i in range(ammo_to_reload):
                waste_time(frame, enemies, 0.7)
                sounds.click1.play()
            if mode == 'sniper':
                do_animation = True
            ammo = ammo_amount

        if mode == 'launcher':
            # shoot missile
            if kb.is_pressed("space"):
                shoot_missile(frame, aim, enemies)
            if kb.is_pressed("q"):
                mode = 'sniper'
                do_animation = True
            # scope
            enemies.display_all_soldiers(frame)
            draw_launcher_scope(frame, aim)

        elif mode == 'sniper':
            if do_animation:
                scope_zoom_animation('in', frame, aim, enemies)
                zoom = True
                do_animation = False

            if kb.is_pressed("space"):
                if ammo > 0:
                    shoot_bullet(frame, aim, enemies)
                    ammo -= 1
                else:
                    sounds.no_ammo.play()
                    cv.waitKey(100)

            if kb.is_pressed("e"):
                night_vision = toggle_night_vision(night_vision)
                cv.waitKey(100)

            if kb.is_pressed("q"):
                scope_zoom_animation('out', frame, aim, enemies)
                zoom = False
                mode = 'launcher'
                continue

            enemies.display_all_soldiers(frame)
            frame = create_sniper_scope_image(frame, aim, 2)
            aim, breath, scope_y_movement = move_aim_breath(aim, breath, scope_y_movement)

        cv.imshow("game", frame)
        cv.waitKey(20)


if __name__ == '__main__':
    main_game('artworks-ulR2yrpsx0S6d5Ra-nXZ09Q-t500x500.jpg', 5)
