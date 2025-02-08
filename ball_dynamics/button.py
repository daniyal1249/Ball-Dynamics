import pygame as pg

class Button:
    def __init__(self, x, y, width, height, radius, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.text = text
        self.rect = pg.Rect(x - width/2, y - height/2, width, height)
        
    def draw(self):
        pass
