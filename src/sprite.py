import pygame
import resource
from color import *

##
## this is nothing more than a spritesheet manager to be used by the game entities,
## NOT to be extended
##
class Sprite(object):

	def __init__(self, texture, dimensions, delay, scale=1):
		self.width, self.height = dimensions
		self.delay = delay
		self.timer = 0.0	
		self.image = resource.load_image(texture)
		self.rect = self.image.get_rect()

		nframes_x = self.rect.width / self.width
		nframes_y = self.rect.height / self.height

		self.width *= scale
		self.height *= scale
		self.image = pygame.transform.scale(self.image, (self.width * nframes_x, self.height * nframes_y))
		self.rect = self.image.get_rect()
		
		self.frames = [self.image.subsurface(rect) for rect in self.get_frames_rect()]
		self.using_frames = range(len(self.frames))
		self.current_frame = 0

		# 1 (right) or -1 (left)
		self.direction = 1

	def get_rect(self):
		return self.rect

	def get_frames_rect(self):
		for y in range(self.rect.height / self.height):
			for x in range(self.rect.width / self.width):
				frame_left = x * self.width
				frame_top = y * self.height
				yield (frame_left, frame_top, self.width, self.height)

	def use_frames(self, frames):
		self.using_frames = frames

	def set_direction(self, direction):
		if self.direction != direction:
			for i in range(len(self.frames)):
				self.frames[i] = pygame.transform.flip(self.frames[i], True, False)
			self.direction = direction

	def get_next_frame(self):
		self.current_frame += 1
		if self.current_frame >= len(self.frames):
			return self.using_frames[0]
		if not self.current_frame in self.using_frames:
			return self.get_next_frame()
		return self.current_frame

	def update(self, dt):
		self.timer += dt
		if self.timer >= self.delay:
			self.timer = 0.0
			self.current_frame = self.get_next_frame()

	def draw(self, screen, dst_rect):
		image = self.frames[self.current_frame]

		# TODO: correct this bug
		left = dst_rect.left - dst_rect.width / 2
		
		top = dst_rect.top
		screen.blit(image, (left, top))