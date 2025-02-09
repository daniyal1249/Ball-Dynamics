import pygame as pg

from utils import font


pg.init()
screen_width = pg.display.Info().current_w - 100
screen_height = pg.display.Info().current_h - 100


class ViewPort:
    dx, dy = 0, 0
    m_to_px = screen_height // 3

    @classmethod
    def pov(cls, x, y):
        x = (x * cls.m_to_px) - cls.dx
        y = (y * cls.m_to_px) - cls.dy
        return x, y

    @classmethod
    def move_by(cls, dx, dy):
        cls.dx += dx
        cls.dy += dy

    @classmethod
    def scale_by(cls, factor):
        cls.m_to_px = round(cls.m_to_px * factor)

    @classmethod
    def set_scale(cls, m_to_px):
        cls.m_to_px = m_to_px


class PhysicsObject(pg.sprite.Sprite):
    def __init__(self):
        pass


class Ball(pg.sprite.Sprite):
    def __init__(self, pos, radius, mass, cor, mu):
        super().__init__()
        self.image = pg.Surface((2 * radius, 2 * radius), pg.SRCALPHA)
        pg.draw.circle(self.image, 'black', (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)
        self.vel = pg.math.Vector2()

        self.radius = radius
        self.mass = mass
        self.cor = cor
        self.mu = mu

        self.highlighted = False
        self.selected = None

    def update(self, mouse_pos, borders, gravity, dt):
        pass



class Obstacle(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()


class Environment:
    ground_height = 0.4

    def __init__(self, borders):
        pass

    def update(self):
        pass
