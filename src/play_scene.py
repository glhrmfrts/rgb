from pygame.locals import *
from pygame import Surface
from color import *
from physics import *
from scene import Scene
from player import Player
from camera import Camera
from background import Background
from sprite import Sprite
from map import Map
import random


class ColorChangingBlock(PhysicsObject):

	def __init__(self, pos, interval):
		PhysicsObject.__init__(self, pos, (0, 0), (32, 32), BODY_STATIC)
		self.sprite = Sprite('../assets/img/ground.png', (32, 32), 0.1)
		self.sprite.use_frames([8])
		self.timer = 0.0
		self.interval = float(interval)
		self.colors = []

	def on_collide_obj(self, obj):
		return True

	def on_collide_platform(self, plat):
		return True

	def update(self, dt):
		self.timer += dt
		if self.timer >= self.interval:
			self.timer = 0
			self.sprite.use_frames([9])

	def draw(self, screen, view_rect):
		rect = Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
		rect.left -= view_rect.left
		rect.top -= view_rect.top

		self.sprite.draw(screen, rect)


class PlayScene(Scene):

	def __init__(self, game):
		Scene.__init__(self, game)
		self.timer = 0.0
		self.timer_freq = 5.0
		self.x = 50.0
		self.color_changing_blocks = []
		self.map = Map('../assets/maps/test.json', '../assets/img/ground.png')

		screen_rect = game.screen.get_rect()
		world_bounds = Rect(0, 0, self.map.get_rect().width, game.height)

		self.background = Background((game.width, game.height), world_bounds.width, '../assets/img/bg.png')

		self.world = PhysicsWorld(self.map, world_bounds, (0, 900))

		player_spawn = self.map.get_obj_layer('player_spawn')['objects'][0]
		player_x = player_spawn['x']
		player_y = player_spawn['y']

		self.player = Player((player_x, player_y), game.input)

		# create dynamic color blocks
		color_changing_blocks = self.map.get_obj_layer('color_changing_blocks')['objects']

		print color_changing_blocks

		for tile_block in color_changing_blocks:
			map_x, map_y = self.map.get_map_coord((tile_block['x'], tile_block['y']))
			real_coord = (map_x * self.map.content['tilewidth'], map_y * self.map.content['tileheight'])

			block = ColorChangingBlock(real_coord, random.randint(1, 5))
			self.world.add_obj(block)
			self.color_changing_blocks.append(block)
		
		self.camera = Camera(self.world, screen_rect, world_bounds)
		self.camera.set_target(self.player)

		self.world.add_obj(self.player)

	def update(self, dt):
		game = self.game

		self.camera.update()
		self.world.update(dt)

		if self.player.rect.top > game.screen.get_rect().height:
			game.restart()

	def draw(self):
		game = self.game
		self.background.draw(game.screen, self.camera.rect)
		self.map.draw(game.screen)

		for block in self.color_changing_blocks:
			block.draw(game.screen, self.camera.rect)

		self.player.draw(game.screen)
		self.world.debug_draw(game.screen)