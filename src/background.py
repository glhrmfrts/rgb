from sprite import *
import pygame.image
import pygame.transform
import copy

########### NOTE: not used yet

class Background(object):

	def __init__(self, (dimensions), parallax):
		self.width, self.height = dimensions
		self.image = None
		self.parallax = parallax
		self.fst_rect = Rect(0, 0, self.width, self.height)
		self.snd_rect = copy.copy(self.fst_rect)

	def set_image(self, filename):
		self.image = pygame.image.load(filename)
		self.image = pygame.transform.scale(self.first_image, (self.width, self.height))

	def update(self, view_rect):
		self.fst_rect.left -= view_rect.left * parallax
		self.snd_rect.left = self.fst_rect.right

	def draw(self, screen):
		screen.blit(self.image, (self.rect.left, 0))
		screen.blit(self.image, (self.snd_rect.left, 0))