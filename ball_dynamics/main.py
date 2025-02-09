import pygame as pg


# if screen.get_flags() & pg.FULLSCREEN:

pg.init()
screen_width = pg.display.Info().current_w - 100
screen_height = pg.display.Info().current_h - 100
window_size = (screen_width, screen_height)
screen = pg.display.set_mode(window_size)
pg.display.set_caption('Ball Dynamics')
