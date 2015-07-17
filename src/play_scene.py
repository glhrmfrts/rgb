from pygame.locals import *
from pygame import Surface
from pygame import Rect
from pygame.math import Vector2
from color import *
from physics import *
from scene import Scene
from camera import Camera
from background import Background
from sprite import Sprite
from text import Text
from map import Map
import random


class ColorChangingBlock(PhysicsObject):

	PATTERN_SIZE = 5

	def __init__(self, pos, interval):
		PhysicsObject.__init__(self, pos, (0, 0), (32, 32), BODY_STATIC)
		self.sprite = Sprite('../assets/img/blocks.png', (32, 32), 0.1)

		self.timer = 0.0
		self.interval = float(interval)

		self.colors = ['red', 'green', 'blue']

		# create a pattern for changing colors
		self.pattern = [random.randint(0, 2) for i in range(self.PATTERN_SIZE)]

		self.pattern_color_pointer = 0
		self.previous_active_color = 0
		self.active_color = self.colors[self.pattern_color_pointer]
		self.sprite.use_frames([self.pattern_color_pointer])

	def on_collide_obj(self, obj):
		return True

	def on_collide_platform(self, plat):
		return True

	def update(self, dt):
		self.sprite.update(dt)
		self.timer += dt

		self.previous_active_color = self.active_color
		
		if self.timer >= self.interval:
			self.timer = 0
			self.previous_pointer = self.pattern_color_pointer
			self.pattern_color_pointer += 1

			if self.pattern_color_pointer >= self.PATTERN_SIZE:
				self.pattern_color_pointer = 0

			next_color = self.pattern[self.pattern_color_pointer]
			self.sprite.use_frames([next_color])
			self.active_color = self.colors[next_color]

	def draw(self, screen, view_rect):
		rect = Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
		rect.left -= view_rect.left - rect.width / 2
		rect.top -= view_rect.top

		self.sprite.draw(screen, rect)


class LavaBlock(PhysicsObject):

	def __init__(self, pos):
		PhysicsObject.__init__(self, pos, (0, 0), (32, 64), BODY_STATIC)
		self.sprite = Sprite('../assets/img/blocks.png', (32, 32), 0.1)
		self.sprite.use_frames([0, 1, 2])

	def update(self, dt):
		self.sprite.update(dt)

	def draw(self, screen, view_rect):
		rect = Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
		rect.left -= view_rect.left - rect.width / 2
		rect.top -= view_rect.top
		self.sprite.draw(screen, rect)


class Player(PhysicsObject):

	def __init__(self, pos, input):
		PhysicsObject.__init__(self, pos, (0, 0), (32, 64), BODY_DYNAMIC)
		self.input = input
		self.sprite = Sprite("../assets/img/new_guy.png", (64, 64), (1.0 / 12.0))
		self.set_foot(True)
		self.active_color = 'red'
		self.dead = False

	def handle_input(self, dt):
		
		self.target_vel.x = 0
		if self.input.is_pressed(K_RIGHT):
			self.target_vel.x = 300
			self.sprite.set_direction(1)
			self.sprite.use_frames([1, 2])
		elif self.input.is_pressed(K_LEFT):
			self.target_vel.x = -300
			self.sprite.set_direction(-1)
			self.sprite.use_frames([1, 2])

		if self.input.is_down(K_UP) and True: # self.on_ground:
			print 'jump'
			self.vel.y = -425
			
		if self.input.is_down(K_1):
			self.active_color = 'red'
			self.sprite.set_offset(0)

		elif self.input.is_down(K_2):
			self.active_color = 'green'
			self.sprite.set_offset(4)

		elif self.input.is_down(K_3):
			self.active_color = 'blue'
			self.sprite.set_offset(8)

	def on_collide_obj(self, obj):
		# print "player obj collisoin"
		if isinstance(obj, ColorChangingBlock):
			return obj.active_color != self.active_color
		elif isinstance(obj, LavaBlock):
			self.dead = True
		return True

	def on_collide_platform(self, platform):
		return platform.layer != self.active_color

	def update(self, dt):
		PhysicsObject.update(self, dt)
		self.handle_input(dt)
		self.sprite.update(dt)

		if self.vel.y > 1.0 and not self.on_ground:
			print 'flying'
			self.sprite.use_frames([3])
		else:
			self.sprite.use_frames([0])

	def draw(self, screen):
		self.sprite.draw(screen, self.rect)


class PlayScene(Scene):

	def __init__(self, game):
		Scene.__init__(self, game)
		self.timer = 0.0
		self.timer_freq = 5.0
		self.x = 50.0
		self.drawable_objects = []
		self.map = Map('../assets/maps/test.json', '../assets/img/ground.png')

		self.drawable_objects.append(Text(game.font, 'hello world', (200, 100)))

		screen_rect = game.screen.get_rect()
		world_bounds = Rect(0, 0, self.map.get_rect().width, game.height)

		self.bg = Surface((game.width, game.height))

		self.world = PhysicsWorld(self.map, world_bounds, (0, 900))

		player_spawn = self.map.get_obj_layer('player_spawn')['objects'][0]
		player_x = player_spawn['x']
		player_y = player_spawn['y']

		self.player = Player((player_x, player_y), game.input)

		# create dynamic color blocks
		color_changing_blocks = self.map.get_obj_layer('color_changing_blocks')['objects']
		lava_blocks = self.map.get_obj_layer('lava_blocks')['objects']

		for tile_block in color_changing_blocks:
			map_x, map_y = self.map.get_map_coord((tile_block['x'], tile_block['y']))
			real_coord = (map_x * self.map.content['tilewidth'], map_y * self.map.content['tileheight'])

			block = ColorChangingBlock(real_coord, 2)
			self.world.add_obj(block)
			self.drawable_objects.append(block)

		for block in lava_blocks:
			map_x, map_y = self.map.get_map_coord((block['x'], block['y']))
			real_coord = (map_x * self.map.content['tilewidth'], map_y * self.map.content['tileheight'])

			lava_block = LavaBlock(real_coord)
			self.world.add_obj(lava_block)
			self.drawable_objects.append(lava_block)
		
		self.camera = Camera(self.world, screen_rect, world_bounds)
		self.camera.set_target(self.player)

		self.world.add_obj(self.player)

	def update(self, dt):
		game = self.game

		self.camera.update()
		self.world.update(dt)

		if self.player.rect.top > game.screen.get_rect().height or self.player.dead:
			game.restart()

	def draw(self):
		game = self.game
		# self.background.draw(game.screen, self.camera.rect)
		game.screen.blit(self.bg, (0, 0))

		self.map.draw(game.screen)

		for obj in self.drawable_objects:
			obj.draw(game.screen, self.camera.rect)

		self.player.draw(game.screen)
		# self.world.debug_draw(game.screen)