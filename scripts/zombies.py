import math
import os
import random

import cv2 as cv
import numpy as np

from scripts import sounds
from scripts.utils import rotate_vector, probability

soldiers_death_sounds = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sounds',
                                                     'death_sounds'))


class Zombie:
    def __init__(self, location):
        self.death_sound = sounds.death_sounds[random.randrange(0, 8)]
        self.frames_lived = 1
        self.location = location
        self.color = [random.randrange(0, 50), random.randrange(0, 255), random.randrange(0, 50)]
        self.size = (self.frames_lived ** 2) * 0.00001

    def location_to_relative(self, aim):
        return [600 - aim.x + self.location[0], 400 - aim.y + self.location[1]]

    def kill(self, enemies_list: list):
        self.death_sound.play()
        enemies_list.remove(self)
        del self

    def draw_arrow(self, frame, aim):
        arrow_color = (0, int(255 * (1600 - self.frames_lived) / 1600), int(255 * self.frames_lived / 1600))
        direction_vector = np.array([self.location[0] - aim.x, self.location[1] - aim.y])
        vector_size = np.linalg.norm(direction_vector)
        normalized_vector = (direction_vector / vector_size)
        arrow_point = [int((normalized_vector[0] * 550) + 600), int((normalized_vector[1] * 350) + 400)]
        rotated_vector1 = rotate_vector(normalized_vector, 135) * (1 / math.sqrt(vector_size)) * 2000
        rotated_vector2 = rotate_vector(normalized_vector, -135) * (1 / math.sqrt(vector_size)) * 2000
        cv.line(frame, arrow_point, [int(arrow_point[0]) + int(rotated_vector1[0]),
                                     int(arrow_point[1]) + int(rotated_vector1[1])],
                arrow_color, 10)
        cv.line(frame, arrow_point, [int(arrow_point[0]) + int(rotated_vector2[0]),
                                     int(arrow_point[1]) + int(rotated_vector2[1])],
                arrow_color, 10)

    def update(self):
        if random.randrange(0, 5) == 4:
            self.location[0] += random.randrange(-1, 2)
            self.location[1] += random.randrange(-1, 2)
            self.location[1] += 1
        self.frames_lived += 1
        self.size = (self.frames_lived ** 2) * 0.00001

    def draw_on_image(self, photo: np.ndarray, aim):
        relative_location = self.location_to_relative(aim)
        self.draw_body(photo, relative_location)
        self.draw_face(photo, relative_location)
        # angry face when close
        if self.frames_lived > 1400:
            self.draw_angry_face(photo, relative_location)
        if not (600 > self.location[0] - aim.x > -600 and 400 > self.location[1] - aim.y > -400):
            self.draw_arrow(photo, aim)

    def draw_angry_face(self, photo, relative_location):
        # eyebrows
        cv.line(photo, [relative_location[0] - math.ceil(6 * self.size),
                        relative_location[1] - math.ceil(12.5 * self.size)],
                [relative_location[0] - math.ceil(3.5 * self.size),
                 relative_location[1] - math.ceil(11.5 * self.size)], [0, 0, 0], math.ceil(0.5 * self.size))
        cv.line(photo, [relative_location[0] + math.ceil(6 * self.size),
                        relative_location[1] - math.ceil(12.5 * self.size)],
                [relative_location[0] + math.ceil(3.5 * self.size),
                 relative_location[1] - math.ceil(11.5 * self.size)], [0, 0, 0], math.ceil(0.5 * self.size))
        # mouth
        cv.circle(photo, [relative_location[0], relative_location[1] - math.ceil(5 * self.size)],
                  math.ceil(2.5 * self.size), [0, 0, 0], -1)

    def draw_body(self, photo, relative_location):
        cv.circle(photo, [int(relative_location[0]), int(relative_location[1] - math.ceil(10 * self.size))],
                  math.ceil(10 * self.size), self.color, -1)
        cv.line(photo, [relative_location[0], relative_location[1]],
                [relative_location[0], relative_location[1] + math.ceil(10 * self.size)], self.color,
                math.ceil(1 + 1 * self.size))
        cv.line(photo, [relative_location[0], relative_location[1] + math.ceil(3 * self.size)],
                [relative_location[0] + math.ceil(10 * self.size), relative_location[1]],
                self.color, math.ceil(1 + 1 * self.size))
        cv.line(photo, [relative_location[0], relative_location[1] + math.ceil(3 * self.size)],
                [relative_location[0] - math.ceil(10 * self.size), relative_location[1]], self.color,
                math.ceil(1 + 1 * self.size))
        cv.line(photo, [relative_location[0], relative_location[1] + math.ceil(10 * self.size)],
                [relative_location[0] + math.ceil(7 * self.size),
                 relative_location[1] + math.ceil(20 * self.size)],
                self.color, math.ceil(1 + 1 * self.size))
        cv.line(photo, [relative_location[0], relative_location[1] + math.ceil(10 * self.size)],
                [relative_location[0] - math.ceil(7 * self.size),
                 relative_location[1] + math.ceil(20 * self.size)],
                self.color, math.ceil(1 + 1 * self.size))

    def draw_face(self, photo, relative_location):
        # eyes
        cv.circle(photo,
                  [relative_location[0] + math.ceil(5 * self.size), relative_location[1] - math.ceil(10 * self.size)],
                  math.ceil(0.2 * self.size), [0, 0, 0], -1)
        cv.circle(photo,
                  [relative_location[0] - math.ceil(5 * self.size), relative_location[1] - math.ceil(10 * self.size)],
                  math.ceil(0.2 * self.size), [0, 0, 0], -1)


class Zombies:
    def __init__(self, aim, spawn_chance, image_shape, horizon_line):
        self.enemies_list = []
        self.spawn_chance = spawn_chance
        self.image_shape = image_shape
        self.aim = aim
        self.horizon_line = horizon_line

    def maybe_add_soldier(self):
        if probability(self.spawn_chance):
            location = [random.randrange(600, self.image_shape[1] - 600),
                        random.randrange(self.horizon_line - 100, self.horizon_line + 100)]
            self.enemies_list.append(Zombie(location))

    def update_frame(self, frame):
        health_down = False
        for enemy in self.enemies_list[::-1]:
            enemy.draw_on_image(frame, self.aim)
            enemy.update()
            if isinstance(enemy, Zombie) and enemy.frames_lived == 1400:
                sounds.screaming.play()
            if isinstance(enemy, Zombie) and enemy.frames_lived > 1700:
                if enemy.frames_lived % 300 == 0:
                    health_down = True
        return health_down
