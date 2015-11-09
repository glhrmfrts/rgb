from pygame.locals import *
from pygame import Surface
from pygame import Rect
from pygame.math import Vector2
from pygame.mixer import Sound
from pygame.font import Font
from color import *
from physics import *
from scene import Scene
from camera import Camera
from sprite import Sprite
from text import Text
from map import Map
import resource
import random
import os
import math

SOUND_ENABLED = True
COLORS = ['red', 'green', 'blue']
PLAYER_JUMP_FORCE = -400

def PLAY_SOUND(sound):
	if SOUND_ENABLED: sound.play()


class ColorChangingBlock(PhysicsObject):

	PATTERN_SIZE = 3

	def __init__(self, pos, interval, exclude_color):
		PhysicsObject.__init__(self, (pos[0] + 16, pos[1] + 16), (0, 0), (32, 32), BODY_STATIC)
		self.sprite = Sprite('./assets/img/blocks.png', (32, 32), 0.1)

		self.id = ID_OBJ

		self.timer = 0.0
		self.interval = float(interval)

		self.colors = ['red', 'green', 'blue']
		self.exclude_color = self.colors.index(exclude_color)

		# create a pattern for changing colors
		self.pattern = []

		while len(self.pattern) < self.PATTERN_SIZE:
			color = random.randint(0, 2)
			if not color == self.exclude_color and self.pattern.count(color) < 2:
				self.pattern.append(color)

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
		self.sprite = Sprite('./assets/img/blocks.png', (32, 32), 0.1)
		self.sprite.use_frames([0, 1, 2])
		self.id = ID_OBJ

	def update(self, dt):
		self.sprite.update(dt)

	def draw(self, screen, view_rect):
		rect = Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
		rect.left -= view_rect.left - rect.width / 2
		rect.top -= view_rect.top
		self.sprite.draw(screen, rect)


class MovingBlock(PhysicsObject):

	def __init__(self, pos, end_pos, size, tile_width, tile):
		left, top = pos
		x = left
		y = top + tile_width / 2
		scale = size[0] / tile_width
		PhysicsObject.__init__(self, (x + size[0] / 2, y), (0, 0), size, BODY_STATIC)
		self.img_rect = Surface(size)

		self.id = ID_OBJ

		self.start_point = Vector2( (x + size[0] / 2, y) )
		self.end_point = Vector2( (end_pos[0] + size[0] / 2, end_pos[1]) )
		self.target_point = self.end_point

		self.colors = ['red', 'green', 'blue', 'gray']
		self.colors_values = [RED, GREEN, BLUE, GRAY]
		self.color_index = self.colors.index(tile['properties']['color'])

		self.active_color = self.colors[ self.colors.index(tile['properties']['color']) ]
		self.previous_active_color = 0

		self.img_rect.fill(self.colors_values[self.color_index])

		self.target_vel.x = 20 * math.copysign(1.0, self.target_point.x - self.pos.x)

	def on_collide_obj(self, obj):
		return True

	def change_obj_velocity(self, obj):
		if not obj.wants_to_move:
			obj.target_vel.x = self.target_vel.x

	def update(self, dt):
		PhysicsObject.update(self, dt)
		if abs(self.pos.x - self.target_point.x) < 10:
			self.target_point = self.start_point \
								if self.target_point is self.end_point \
								else self.end_point
			self.target_vel.x = 20 * math.copysign(1.0, self.target_point.x - self.pos.x)

	def draw(self, screen, view_rect):
		left = self.rect.left - view_rect.left
		top = self.rect.top - view_rect.top

		screen.blit(self.img_rect, (left, top))


class MovableBlock(PhysicsObject):

	def __init__(self, pos, color):
		PhysicsObject.__init__(self, (pos[0] + 16, pos[1] + 16), (0, 0), (32, 32), BODY_DYNAMIC)
		self.set_foot(True)
		self.sprite = Sprite('./assets/img/ground.png', (32, 32), 0.1)
		self.bounce_timer = 0.0

		self.id = ID_MOVABLE_BLOCK
		self.acceleration = 300

		self.colors = COLORS + ['gray']
		self.colors_values = [RED, GREEN, BLUE, GRAY]
		self.color_index = self.colors.index(color)

		self.active_color = self.colors[ self.colors.index(color) ]
		self.previous_active_color = 0

		self.sprite.use_frames([ 12 + self.color_index ])
		self.sprite.update(5)

	def on_collide_obj(self, obj):
		return True

	def on_collide_platform(self, p):
		return p.layer != self.active_color

	def update(self, dt):
		PhysicsObject.update(self, dt)
		self.sprite.update(dt)

		if self.bounce_timer > 0.0:
			self.bounce_timer -= dt

	def draw(self, screen, view_rect):
		rect = copy.copy(self.rect)
		rect.left += rect.width / 2
		self.sprite.draw(screen, rect)


class ImpulseBlock(PhysicsObject):

	BOUNCE_FACTOR = 1.35
	BOUNCE_MIN_INTERVAL = 0.5

	def __init__(self, pos, color, direction):
		PhysicsObject.__init__(self, (pos[0] + 16, pos[1] + 16), (0, 0), (32, 32), BODY_STATIC)
		self.sprite = Sprite('./assets/img/arrow_blocks.png', (32, 32), 0.1)
		self.id = ID_OBJ
		self.colors = COLORS + ['gray']
		color_index = self.colors.index(color)
		self.active_color = self.colors[ color_index ]
		self.sprite.use_frames([color_index])
		self.sprite.update(5)
		self.direction = direction # 1(down) or -1(up)
		self.sprite.set_direction(False, direction)

	def change_obj_velocity(self, obj):
		if obj.active_color != self.active_color:
			if obj.bounce_timer <= 0.0:
				if obj.id == ID_PLAYER:
					PLAY_SOUND(obj.sound_jump)
				obj.bounce_timer = self.BOUNCE_MIN_INTERVAL
				if obj.vel.y < 50:
					obj.vel.y = PLAYER_JUMP_FORCE
				else:
					obj.vel.y = (obj.vel.y * self.BOUNCE_FACTOR) * self.direction
			return True
		return False

	def update(self, dt):
		pass

	def draw(self, screen, view_rect):
		rect = copy.copy(self.rect)
		rect.left -= view_rect.left - rect.width / 2
		rect.top -= view_rect.top
		self.sprite.draw(screen, rect)


class ExitBlock(PhysicsObject):

	def __init__(self, pos):
		PhysicsObject.__init__(self, (pos[0] + 16, pos[1] + 16), (0, 0), (32, 32), BODY_STATIC)
		self.img = pygame.image.load('./assets/img/exit.png')
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


class Player(PhysicsObject):

	def __init__(self, pos, color_interval, input):
		PhysicsObject.__init__(self, pos, (0, 0), (28, 48), BODY_DYNAMIC)
		self.change_color_mode = False
		self.color_interval = 0
		self.color_timer_text = None
		if color_interval > 0:
			self.change_color_mode = True
			self.color_interval = color_interval
			font = Font('./assets/font/vcr.ttf', 18)
			self.color_timer_text = Text(font, str(color_interval), (740, 5))
			self.color_timer_text.update = True
		self.color_timer = 0.0
		self.input = input
		self.sprite = Sprite("./assets/img/new_guy.png", (64, 64), (1.0 / 12.0))
		self.set_foot(True)
		self.active_color = 'red'
		self.acceleration = 400
		self.dead = False
		self.sound_jump = Sound('./assets/audio/jump.wav')
		self.sound_land = Sound('./assets/audio/land.wav')
		self.sound_push = Sound('./assets/audio/push.wav')
		self.sound_timer = 0.0
		self.sound_min_interval = 0.5
		self.id = ID_PLAYER
		self.bounce_timer = 0.0

		# view rectangle for HUD stuff
		self.view_rect = Rect(0, 0, 0, 0)

	def handle_input(self, dt):
		
		self.target_vel.x = 0
		if self.input.is_pressed(K_RIGHT):
			if not self.wants_to_move:
				self.wants_to_move = True
			self.target_vel.x = 300
			self.sprite.set_direction(1)
			self.sprite.use_frames([1, 2])
		elif self.input.is_pressed(K_LEFT):
			if not self.wants_to_move:
				self.wants_to_move = True
			self.target_vel.x = -300
			self.sprite.set_direction(-1)
			self.sprite.use_frames([1, 2])

		if self.input.is_down(K_UP) and self.on_ground:
			self.vel.y = PLAYER_JUMP_FORCE
			PLAY_SOUND(self.sound_jump)
		
		# if we are in the automatic color changing mode
		# ignore the input from the user
		if self.change_color_mode:
			return

		if self.input.is_down(K_1):
			self.active_color = 'red'
			self.sprite.set_offset(0)

		elif self.input.is_down(K_2):
			self.active_color = 'green'
			self.sprite.set_offset(4)

		elif self.input.is_down(K_3):
			self.active_color = 'blue'
			self.sprite.set_offset(8)

	def play_land_sound(self):
		if self.sound_timer > self.sound_min_interval:
			PLAY_SOUND(self.sound_land.play())
			self.sound_timer = 0.0

	def on_collide_obj(self, obj):
		if isinstance(obj, ColorChangingBlock) or \
			isinstance(obj, MovingBlock) or \
			isinstance(obj, MovableBlock) or \
			isinstance(obj, ImpulseBlock):
			if obj.active_color != self.active_color:
				if self.vel.y > 1.0: 
					pass 
				return True
			return False
		elif isinstance(obj, LavaBlock):
			self.dead = True
		elif isinstance(obj, ExitBlock):
			return True if self.active_color != 'green' else False
		return True

	def on_collide_platform(self, platform):
		if platform.layer != self.active_color:
			if self.vel.y > 1.0: 
				pass
			return True
		return False

	def change_color(self):
		current_color_index = COLORS.index(self.active_color)
		next_color_index = (current_color_index + 1) % len(COLORS)
	
		self.active_color = COLORS[next_color_index]
		self.sprite.set_offset(4 * next_color_index)

	def update(self, dt):
		PhysicsObject.update(self, dt)
		self.handle_input(dt)
		self.sprite.update(dt)
		self.sound_timer += dt

		if self.bounce_timer > 0.0:
			self.bounce_timer -= dt

		if self.change_color_mode:
			self.color_timer_text.text = str(self.color_interval - self.color_timer)[:4]
			self.color_timer += dt
			if self.color_timer >= self.color_interval:
				self.color_timer = 0.0
				self.change_color()

		if self.vel.y > 1.0 and not self.on_ground:
			self.sprite.use_frames([3])
		else:
			self.sprite.use_frames([0])

	def draw(self, screen):
		rect = copy.copy(self.rect)

		# TODO: find the reason of this bug
		rect.bottom -= 16
		self.sprite.draw(screen, rect)
		if not self.color_timer_text is None:
			self.color_timer_text.draw(screen, self.view_rect)


class PlayScene(Scene):

	def __init__(self, game, level):
		Scene.__init__(self, game)
		self.timer = 0.0
		self.timer_freq = 5.0
		self.x = 50.0
		self.drawable_objects = []
		self.level = level
		level_map_path = './assets/maps/map'+ str(level) +'.json'
		self.map = Map(level_map_path, './assets/img/ground.png')

		screen_rect = game.screen.get_rect()
		world_bounds = Rect(0, 0, self.map.get_rect().width, self.map.get_rect().height)

		self.bg = Surface((game.width, game.height))

		self.world = PhysicsWorld(self.map, world_bounds, (0, 900))

		player_spawn = self.map.get_obj_layer('player_spawn')['objects'][0]
		player_x = player_spawn['x']
		player_y = player_spawn['y']
		player_color_interval = 0
		try:
			player_color_interval = int(player_spawn['properties']['color_interval'])
		except KeyError:
			pass

		self.player = Player((player_x, player_y), player_color_interval, game.input)
		self.world.add_obj(self.player)

		color_changing_blocks = self.map.get_obj_layer('color_changing_blocks')['objects']
		lava_blocks = self.map.get_obj_layer('lava_blocks')['objects']
		moving_blocks = self.map.get_obj_layer('moving_blocks')['objects']
		movable_blocks = self.map.get_obj_layer('movable_blocks')['objects']
		impulse_blocks = self.map.get_obj_layer('impulse_blocks')['objects']

		exit_block = self.map.get_obj_layer('exit')['objects'][0]
		texts = self.map.get_obj_layer('texts')['objects']

		exit_coord = self.obj_adjust_position((exit_block['x'], exit_block['y']))

		self.exit = ExitBlock(exit_coord)
		self.world.add_obj(self.exit)
		self.drawable_objects.append(self.exit)

		# create dynamic color blocks
		for block in color_changing_blocks:
			real_coord = self.obj_adjust_position( (block['x'], block['y']) )

			exclude_color = 'red'

			try:
				exclude_color = block['properties']['exclude_color']
			except KeyError:
				pass

			block = ColorChangingBlock(real_coord, 1, exclude_color)
			self.world.add_obj(block)
			self.drawable_objects.append(block)

		# create lava blocks
		for block in lava_blocks:
			real_coord = self.obj_adjust_position( (block['x'], block['y']) )

			lava_block = LavaBlock(real_coord)
			self.world.add_obj(lava_block)
			self.drawable_objects.append(lava_block)

		for block in moving_blocks:
			real_coord = self.obj_adjust_position( (block['x'], block['y']) )
			right, _ = self.obj_adjust_position(( block['x'] + block['width'], block['y'] ))

			right += self.map.content['tilewidth']

			map_x, _ = self.map.get_map_coord( (block['x'], block['y']) )
			end_pos_x = (map_x + int(block['properties']['end_pos_x'])) * self.map.content['tilewidth']
			end_pos = (end_pos_x, block['y'])

			moving_block = MovingBlock(real_coord, end_pos, (right - real_coord[0], self.map.content['tilewidth']), self.map.content['tilewidth'], block)
			self.world.add_obj(moving_block)
			self.drawable_objects.append(moving_block)

		for block in movable_blocks:
			real_coord = self.obj_adjust_position( (block['x'], block['y']) )

			movable_block = MovableBlock(real_coord, block['properties']['color'])
			self.world.add_obj(movable_block)
			self.drawable_objects.append(movable_block)

		for block in impulse_blocks:
			real_coord = self.obj_adjust_position( (block['x'], block['y']) )
			color = block['properties']['color']
			direction = int(block['properties']['direction'])
			impulse_block = ImpulseBlock(real_coord, color, direction)
			self.world.add_obj(impulse_block)
			self.drawable_objects.append(impulse_block)

		# create map texts
		for text in texts:
			real_coord = self.obj_adjust_position( (text['x'], text['y']) )
			size = 20
			try:
				size = int(text['properties']['size'])
			except KeyError:
				pass

			font = pygame.font.Font('./assets/font/vcr.ttf', size)
			game_text = Text(font, text['properties']['text'], real_coord)

			self.drawable_objects.append(game_text)
		
		self.camera = Camera(self.world, screen_rect, world_bounds)
		self.camera.set_target(self.player)

		self.sound_player_lose = Sound('./assets/audio/lose.wav')

	def obj_adjust_position(self, pos):
		map_x, map_y = self.map.get_map_coord((pos[0], pos[1]))
		return (map_x * self.map.content['tilewidth'], map_y * self.map.content['tileheight'])

	def save_game(self):
		resource.write_save_file(str(int(self.level) + 1))

	def update(self, dt):
		global SOUND_ENABLED
		game = self.game

		if game.input.is_down(K_s):
			SOUND_ENABLED = not SOUND_ENABLED

		self.camera.update()
		self.world.update(dt)

		lose = self.player.dead
		win = self.exit.exited
		restart = game.input.is_down(K_r)

		if lose:
			PLAY_SOUND(self.sound_player_lose)

		if lose or restart:
			game.next_scene = PlayScene(game, self.level)
		elif win:
			game.next_scene = PlayScene(game, int(self.level) + 1)
			self.save_game()

	def draw(self):
		game = self.game
		# self.background.draw(game.screen, self.camera.rect)
		game.screen.blit(self.bg, (0, 0))

		self.map.draw(game.screen)

		for obj in self.drawable_objects:
			obj.draw(game.screen, self.camera.rect)

		self.player.draw(game.screen)
		# self.world.debug_draw(game.screen)