import pygame as pg

mt_bg = 'assets/mt_bg.jpg'
geom_bg = 'assets/geom_bg.jpg'

bg_image = pg.image.load(mt_bg)
image_w, image_h = bg_image.get_size()

def background(screen, w , h):
    x = w - image_w + 200
    y = 0
    screen.blit(bg_image, (x, y))
