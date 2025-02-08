import pygame as pg

mt_bg = 'C:\\Users\\Daniyal\\Python\\Kinematics Lab\\mt_bg.jpg'
geom_bg = 'C:\\Users\\Daniyal\\Python\\Kinematics Lab\\geom_bg.jpg'

bg_image = pg.image.load(mt_bg)
image_w, image_h = bg_image.get_size()

def background(screen, w , h):
    x = w - image_w + 200
    y = 0
    screen.blit(bg_image, (x, y))
