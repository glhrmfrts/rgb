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
import os


class ColorChangingBlock(PhysicsObject):

	PATTERN_SIZE = 5

	def __init__(self, pos, interval):
		PhysicsObject.__init__(self, (pos[0] + 16, pos[1] + 16), (0, 0), (32, 32), BODY_STATIC)
		self.sprite = Sprite('../assets/img/blocks.png', (32, 32), 0.1)

		self.timer = 0.0
		self.interval = float(interval)

		self.colors = ['red', 'green', 'blue']

		# create a pattern for changing colors
		self.pattern = [random.randint(0, 2) for i in range(self.PATTERN_SIZE)]

		self.pattern_color_pointer = random.randint(0, self.PATTERN_SIZE - 1)
		self.previous_active_color = 0
		self.active_color = self.colors[ self.pattern[self.pattern_color_pointer] ]
		self.sprite.use_frames([ self.pattern[self.pattern_color_pointer] ])

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
		PhysicsObject.__init__(self, (pos[0] + 16, pos[1] + 16), (0, 0), (32, 32), BODY_STATIC)
		self.sprite = Sprite('../assets/img/blocks.png', (32, 32), 0.1)
		self.sprite.use_frames([0, 1, 2])

	def update(self, dt):
		self.sprite.update(dt)

	def draw(self, screen, view_rect):
		rect = Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
		rect.left -= view_rect.left - rect.width / 2
		rect.top -= view_rect.top - rect.height / 2
		self.sprite.draw(screen, rect)


class TrickyBlock(PhysicsObject):

	def __init__(self, pos, size, tile_width, properties):
		left, top = pos
		x = left
		y = top + tile_width / 2
		scale = size[0] / tile_width
		PhysicsObject.__init__(self, (x + size[0] / 2, y), (0, 0), size, BODY_STATIC)
		self.img_rect = Surface(size)

		self.colors = ['red', 'green', 'blue', 'gray']
		self.colors_values = [RED, GREEN, BLUE, GRAY]

		self.shown_color_frame = self.colors.index(properties['initial_color'])

		self.active_color = self.colors[self.shown_color_frame]
		self.previous_active_color = 0

		self.img_rect.fill(self.colors_values[self.shown_color_frame])

		self.inverse = True if 'inverse' in properties else False

	def gen_color(self, color_frame):
		new_color = random.randint(0, 2)
		if new_color == color_frame:
			return self.gen_color(color_frame)
		return new_color

	def on_collide_obj(self, obj):
		if isinstance(obj, Player):
			next_color = 0
			if not self.inverse:
				self.active_color = obj.active_color
				next_color = self.colors.index(self.active_color)
			else:
				rand = self.gen_color(self.colors.index(self.active_color))
				self.active_color = self.colors[rand]
				next_color = rand

			self.img_rect.fill(self.colors_values[next_color])

	def update(self, dt):
		pass

	def draw(self, screen, view_rect):
		left = self.rect.left - view_rect.left
		top = self.rect.top - view_rect.top

		screen.blit(self.img_rect, (left, top))


class ExitBlock(PhysicsObject):

	def __init__(self, pos):
		PhysicsObject.__init__(self, (pos[0] + 16, pos[1] + 16), (0, 0), (32, 32), BODY_STATIC)
		self.img = pygame.image.load('../assets/img/exit.png')
		self.exited = False

	def on_collide_obj(self, obj):
		if isinstance(obj, Player):
			if obj.active_color != 'green':
				self.exited = True
				return True
		return False

	def draw(self, screen, view_rect):
		left = self.rect.left - view_rect.left
		top = self.rect.top - view_rect.top

		screen.blit(self.img, (left, top))


# NOTE: not currently used
class Monster(PhysicsObject):

	def __init__(self, pos):
		PhysicsObject.__init__(self, pos, (0, 0), (32, 64), BODY_DYNAMIC)
		self.start_point = Vector2(450, 400)
		self.end_point = Vector2(350, 400)
		self.pos.x, self.pos.y = self.start_point.x, self.start_point.y
		self.turn_direction(self.start_point)

	def turn_direction(self, last_point):
		self.target_vel.x = 20 * math.copysign(1.0, last_point.x - self.start_point.x)
		self.last_point = last_point

	def update(self, dt):
		PhysicsObject.update(self, dt)
		if abs(self.pos.x - self.end_point.x) < 10 and not self.last_point is self.end_point:
			print "turn to start"
			self.turn_direction(self.end_point)

		elif abs(self.pos.x - self.start_point.x) < 10 and not self.last_point is self.start_point:
			print "turn to end"
			self.turn_direction(self.start_point)

	def on_collide_platform(self, plat):
		return True

	def on_collide_obj(self, obj):
		return True

	def draw(self, screen):
		debug_image = pygame.Surface((32, 64))
		debug_image.fill( (0, 0, 255) )
		screen.blit(debug_image, (self.rect.left, self.rect.top))


class Player(PhysicsObject):

	def __init__(self, pos, input):
		PhysicsObject.__init__(self, pos, (0, 0), (28, 62), BODY_DYNAMIC)
		self.input = input
		self.sprite = Sprite("../assets/img/new_guy.png", (64, 64), (1.0 / 12.0))
		self.set_foot(True)
		self.active_color = 'red'
		self.acceleration = 400
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

		if self.input.is_down(K_UP) and self.on_ground:
			print 'jump'
			self.vel.y = -375
			
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
		if isinstance(obj, ColorChangingBlock) or isinstance(obj, TrickyBlock):
			return obj.active_color != self.active_color
		elif isinstance(obj, LavaBlock):
			self.dead = True
		elif isinstance(obj, ExitBlock):
			return True if self.active_color != 'green' else False
		return True

	def on_collide_platform(self, platform):
		return platform.layer != self.active_color

	def update(self, dt):
		PhysicsObject.update(self, dt)
		self.handle_input(dt)
		self.sprite.update(dt)

		if self.vel.y > 1.0 and not self.on_ground:
			self.sprite.use_frames([3])
		else:
			self.sprite.use_frames([0])

	def draw(self, screen):
		self.sprite.draw(screen, self.rect)


class PlayScene(Scene):

	def __init__(self, game, level):
		Scene.__init__(self, game)
		self.timer = 0.0
		self.timer_freq = 5.0
		self.x = 50.0
		self.drawable_objects = []
		self.level = level
		level_map_path = os.path.join('../assets/maps', 'map'+ str(level) +'.json')
		self.map = Map(level_map_path, '../assets/img/ground.png')

		screen_rect = game.screen.get_rect()
		world_bounds = Rect(0, 0, self.map.get_rect().width, game.height)

		self.bg = Surface((game.width, game.height))

		self.world = PhysicsWorld(self.map, world_bounds, (0, 900))

		player_spawn = self.map.get_obj_layer('player_spawn')['objects'][0]
		player_x = player_spawn['x']
		player_y = player_spawn['y']

		self.player = Player((player_x, player_y), game.input)

		color_changing_blocks = self.map.get_obj_layer('color_changing_blocks')['objects']
		lava_blocks = self.map.get_obj_layer('lava_blocks')['objects']
		tricky_blocks = self.map.get_obj_layer('tricky_blocks')['objects']
		exit_block = self.map.get_obj_layer('exit')['objects'][0]
		texts = self.map.get_obj_layer('texts')['objects']

		exit_coord = self.obj_adjust_position((exit_block['x'], exit_block['y']))

		self.exit = ExitBlock(exit_coord)
		self.world.add_obj(self.exit)
		self.drawable_objects.append(self.exit)

		# create dynamic color blocks
		for block in color_changing_blocks:
			real_coord = self.obj_adjust_position( (block['x'], block['y']) )

			block = ColorChangingBlock(real_coord, 2)
			self.world.add_obj(block)
			self.drawable_objects.append(block)

		# create lava blocks
		for block in lava_blocks:
			real_coord = self.obj_adjust_position( (block['x'], block['y']) )

			lava_block = LavaBlock(real_coord)
			self.world.add_obj(lava_block)
			self.drawable_objects.append(lava_block)

		# create tricky blocks
		for block in tricky_blocks:
			real_coord = self.obj_adjust_position( (block['x'], block['y']) )
			right, _ = self.obj_adjust_position(( block['x'] + block['width'], block['y']) )

			right += self.map.content['tilewidth']

			tricky_block = TrickyBlock(real_coord, (right - block['x'], self.map.content['tilewidth']), self.map.content['tilewidth'], block['properties'])
			self.world.add_obj(tricky_block)
			self.drawable_objects.append(tricky_block)

		# create map texts
		for text in texts:
			real_coord = self.obj_adjust_position( (text['x'], text['y']) )
			game_text = Text(game.font, text['properties']['text'], real_coord)

			self.drawable_objects.append(game_text)
		
		self.camera = Camera(self.world, screen_rect, world_bounds)
		self.camera.set_target(self.player)

		self.world.add_obj(self.player)

	def obj_adjust_position(self, pos):
		map_x, map_y = self.map.get_map_coord((pos[0], pos[1]))
		return (map_x * self.map.content['tilewidth'], map_y * self.map.content['tileheight'])

	def update(self, dt):
		game = self.game

		self.camera.update()
		self.world.update(dt)

		lose = self.player.rect.top > game.screen.get_rect().height or self.player.dead
		win = self.exit.exited

		if lose:
			game.next_scene = PlayScene(game, self.level)
		elif win:
			game.next_scene = PlayScene(game, self.level + 1)

	def draw(self):
		game = self.game
		# self.background.draw(game.screen, self.camera.rect)
		game.screen.blit(self.bg, (0, 0))

		self.map.draw(game.screen)

		for obj in self.drawable_objects:
			obj.draw(game.screen, self.camera.rect)

		self.player.draw(game.screen)
		# self.world.debug_draw(game.screen)