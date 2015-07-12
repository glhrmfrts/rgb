import pygame
import json
import copy

class Map(object):
	""" Reads a json Tiled Map """

	def __init__(self, filename, texture=None):
		self.content = json.load(open(filename, 'r'))
		if texture is None:
			texture = self.content['tilesets'][0]['image']
		image = pygame.image.load(texture)
		image_rect = image.get_rect()
		self.tileset = [image.subsurface(rect) for rect in self.get_tileset_frames(image_rect)]
		self.rect = pygame.Rect(0, 0, self.content['width'] * self.content['tilewidth'], \
			self.content['height'] * self.content['tileheight'])

		# divide layers into tiles and objects and free the original array
		self.tile_layers = self.get_layers_of_type('tilelayer')
		self.obj_layers = self.get_layers_of_type('objectgroup')
		del self.content['layers']

		self.visible_tile_layers = map(lambda l: l['name'], self.tile_layers)
		self.collidable_tile_layers = copy.copy(self.visible_tile_layers)
		self.view_rect = None

	def get_tileset_frames(self, image_rect):
		""" get each individual frame of the tileset """
		nframes_x = image_rect.width / self.content['tilewidth']
		nframes_y = image_rect.height / self.content['tileheight']
		for y in range(nframes_y):
			for x in range(nframes_x):
				frame_left = x * self.content['tilewidth']
				frame_top = y * self.content['tileheight']
				yield (frame_left, frame_top, self.content['tilewidth'], self.content['tileheight'])

	def get_rect(self):
		return copy.copy(self.rect)

	def get_tile_layer(self, name):
		return filter(lambda l: (l['name'] == name), self.tile_layers)[0]

	def get_obj_layer(self, name):
		return filter(lambda l: (l['name'] == name), self.obj_layers)[0]

	def get_layers_of_type(self, type_name):
		return filter(lambda l: (l['type'] == type_name), self.content['layers'])

	def coord_to_index(self, x, y, width=0):
		width = width if width > 0 else self.content['width'] 
		return int(y * width + x)
	
	def get_map_coord(self, pos):
		""" takes a screen coordinate and maps to the tiled map """
		x, y = pos
		return (\
			int(float(x) / self.content['tilewidth']),
			int(float(y) / self.content['tileheight'])
		)

	def get_nonempty_tiles_coord(self, layer_name):
		layer = self.get_tile_layer(layer_name)
		for y in range(layer['height']):
			for x in range(layer['width']):
				if layer['data'][self.coord_to_index(x, y, layer['width'])] != 0:
					yield (x, y)

	def set_view(self, view_rect):
		self.view_rect = view_rect

	def draw(self, screen):
		for layer in self.tile_layers:
			if not layer['name'] in self.visible_tile_layers:
				continue
			for y in range(layer['height']):
				for x in range(layer['width']):
					tile_x = x * self.content['tilewidth']
					tile_y = y * self.content['tileheight']
					tile_to_use = layer['data'][self.coord_to_index(x, y, layer['width'])]
					if tile_to_use <= 0:
						continue
					image = self.tileset[tile_to_use - 1]
					screen.blit(image, (tile_x - self.view_rect.left, tile_y - self.view_rect.top))