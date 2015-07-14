from physics import *
from pygame import Surface
import copy


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