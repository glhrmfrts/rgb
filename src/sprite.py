import pygame
import resource
from color import *

##
## this is nothing more than a spritesheet manager to be used by the game entities,
## NOT to be extended
##
class Sprite(object):

	def __init__(self, texture, dimensions, delay, scale=(1, 1)):
		self.width, self.height = dimensions
		self.delay = delay
		self.timer = 0.0	
		self.image = resource.load_image(texture)
		self.rect = self.image.get_rect()

		nframes_x = int(self.rect.width / self.width)
		nframes_y = int(self.rect.height / self.height)

		self.width *= scale[0]
		self.height *= scale[1]
		self.image = pygame.transform.scale(self.image, (self.width * nframes_x, self.height * nframes_y))
		self.rect = self.image.get_rect()
		
		self.frames = [self.image.subsurface(rect) for rect in self.get_frames_rect()]
		self.using_frames = range(len(self.frames))
		self.current_frame = 0

		# 1 (right) or -1 (left)
		self.direction_x = 1
		self.direction_y = -1
		self.offset = 0

	def get_rect(self):
		return self.rect

	def get_frames_rect(self):
		for y in range(int(self.rect.height / self.height)):
			for x in range(int(self.rect.width / self.width)):
				frame_left = x * self.width
				frame_top = y * self.height
				yield (frame_left, frame_top, self.width, self.height)

	def use_frames(self, frames):
		self.using_frames = frames

	def set_offset(self, offset):
		self.offset = offset

	def set_direction(self, direction_x, direction_y=0):
		direction_x = direction_x or self.direction_x
		direction_y = direction_y or self.direction_y
		for i in range(len(self.frames)):
			self.frames[i] = pygame.transform.flip(
				self.frames[i], 
				direction_x != self.direction_x, 
				direction_y != self.direction_y
			)
		self.direction_x = direction_x
		self.direction_y = direction_y

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
		image = self.frames[self.offset + self.current_frame]

		# TODO: fix this bug
		left = dst_rect.left - dst_rect.width / 2
		
		top = dst_rect.top
		screen.blit(image, (left, top))