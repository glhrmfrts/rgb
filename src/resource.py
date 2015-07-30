import pygame.image
import pygame.font
import copy

__image_cache = {}
SAVE_FILE_PATH = 'save.rgb'

def find_save_file():
	try:
		return open(SAVE_FILE_PATH, 'r')
	except IOError:
		return None

def write_save_file(content):
	save_file = open(SAVE_FILE_PATH, 'w')
	save_file.write(content)
	save_file.close()

def load_image(filename):
	if not filename in __image_cache:
		__image_cache[filename] = pygame.image.load(filename)
	return copy.copy(__image_cache[filename])