from sprite import *
from pygame import Rect
import pygame.image
import pygame.transform
import copy
import resource
import random

class Cloud(object):

	def __init__(self, image, rect, parallax=1, scale=1):
		self.image = resource.load_image(image)
		self.rect = rect
		self.parallax = parallax
		self.scale = scale
		self.resize()

	def resize(self):
		image_rect = self.image.get_rect()
		width = int(image_rect.width * self.scale)
		height = int(image_rect.height * self.scale)
		self.image = pygame.transform.scale(self.image, (width, height))

	def draw(self, screen, view_rect):
		left_offset = view_rect.left * self.parallax
		screen.blit(self.image, (self.rect.left - left_offset, self.rect.top))


class Background(object):

	# TODO: discover why this slows down the framerate

	MIN_CLOUD_DISTANCE = 100
	MAX_CLOUD_DISTANCE = 500

	def __init__(self, (dimensions), total_width, filename=''):
		self.width, self.height = dimensions
		self.image = None
		self.clouds = []
		self.set_image(filename)
		self.add_clouds(total_width)

	def set_image(self, filename):
		self.image = pygame.image.load(filename)
		self.image = pygame.transform.scale(self.image, (self.width, self.height))

	def add_clouds(self, total_width):
		i = 0
		while i < total_width:
			rect = Rect(i, 200, 320, 320)
			parallax = random.random()
			scale = random.random()
			self.clouds.append(Cloud('../assets/img/clouds.png', rect, parallax, scale))
			i += rect.width + random.randint(self.MIN_CLOUD_DISTANCE, self.MAX_CLOUD_DISTANCE)

	def draw(self, screen, view_rect):
		screen.blit(self.image, (0, 0))
		for c in self.clouds:
			c.draw(screen, view_rect)
		