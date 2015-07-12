import pygame.image
import pygame.font
import copy

__image_cache = {}

def load_image(filename):
	if not filename in __image_cache:
		__image_cache[filename] = pygame.image.load(filename)
	return copy.copy(__image_cache[filename])