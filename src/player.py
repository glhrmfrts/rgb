from pygame.locals import *
from pygame import Rect
from sprite import Sprite
from physics import *


class Player(PhysicsObject):

	def __init__(self, pos, input):
		PhysicsObject.__init__(self, pos, (0, 0), (32, 64), BODY_DYNAMIC)
		self.input = input
		self.sprite = Sprite("../assets/img/guy.png", (32, 32), (1.0 / 12.0), 2)
		self.set_foot(True)
		self.active_color = 'red'

		# Provisory
		self.active_color_sprite = Sprite("../assets/img/ground.png", (32, 32), 1.0 / 12.0)
		self.active_color_sprite.use_frames([8])

	def handle_input(self, dt):
		self.sprite.use_frames([0])
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
			self.vel.y = -350
			
		if self.input.is_down(K_1):
			self.active_color = 'red'
			self.active_color_sprite.use_frames([8])
		elif self.input.is_down(K_2):
			self.active_color = 'green'
			self.active_color_sprite.use_frames([9])
		elif self.input.is_down(K_3):
			self.active_color = 'blue'
			self.active_color_sprite.use_frames([10])

	def on_collide_obj(self, obj):
		print "player obj collision"

	def on_collide_platform(self, platform):
		return platform.layer in [self.active_color, 'ground']

	def update(self, dt):
		PhysicsObject.update(self, dt)
		self.handle_input(dt)
		self.sprite.update(dt)
		self.active_color_sprite.update(dt)

	def draw(self, screen):
		self.sprite.draw(screen, self.rect)
		rect = Rect(20, 20, 32, 32)
		self.active_color_sprite.draw(screen, rect)