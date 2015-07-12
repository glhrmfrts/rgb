from pygame.math import Vector2
from pygame import Rect
from platform import Platform
import pygame
import math
import copy

BODY_DYNAMIC = 1
BODY_STATIC = 2

class PhysicsWorld(object):

	def __init__(self, tilemap, bounds, gravity=(0, 0)):
		self.map = tilemap
		self.bounds = bounds
		self.gravity = Vector2(gravity)
		self.velocity_threshold = 3
		self.objects = []
		self.platforms = []
		self.create_platforms()

	def add_object(self, game_object):
		self.objects.append(game_object)

	def create_platforms(self):		
		for layer in self.map.collidable_layers:
			tiles = list(self.map.get_nonempty_tiles_coord(layer))
			self.create_platforms_rect(tiles, layer)


	def create_platforms_rect(self, tiles, layer):
		""" Create a collision rect for each non-empty tile segment, that is, one or more tiles together """
		if len(tiles) < 1:
			return False

		x, y = tiles.pop(0)
		n_tiles_x = n_tiles_y = 1
		width = self.map.content['tilewidth']
		height = self.map.content['tileheight']
		rect = Rect((0, 0, 0, 0))
		rect.left = x * width
		rect.top = y * height
		rect.width = width
		rect.height = height

		# exclude the tiles we're about to create a platform for
		excluded_tiles = []
		for (n_x, n_y) in tiles:
			if abs(n_x - x) == n_tiles_x and n_y == y:
				rect.width += width
				n_tiles_x += 1
				excluded_tiles.append((n_x, n_y))
			if abs(n_y - y) == n_tiles_y and n_x == x:
				rect.height += height
				n_tiles_y += 1
				excluded_tiles.append((n_x, n_y))

		self.platforms.append(Platform(rect, layer))
		self.create_platforms_rect([t for t in tiles if not t in excluded_tiles], layer)

	def is_colliding(self, a, b):
		types = [type(a).__name__, type(b).__name__]
		if not types.count('Rect') == len(types):
			raise TypeError('should be Rect')
		return a.colliderect(b)

	def set_view(self, view_rect):
		self.map.set_view(view_rect)

	def update(self, dt):
		bounds = self.bounds
		view_rect = self.map.view_rect
		for layer in self.map.content['layers']:
			for i, obj in enumerate(self.objects):

				obj.update(dt)

				# correct viewport offsets
				obj.rect.left -= view_rect.left
				obj.foot.left = obj.get_foot_left()
				
				# TODO: correct y-axis viewport also

				foot_collisions = 0

				# check left and right bounds
				if obj.pos.x < (obj.rect.width / 2):
					obj.vel.x = 0
					obj.pos.x = (obj.rect.width / 2)
				elif obj.pos.x > bounds.width:
					obj.vel.x = 0
					obj.pos.x = bounds.width - (obj.rect.width / 2)

				# check top and bottom bounds
				"""if obj.pos.y < obj.rect.height / 2:
					obj.vel.y = 0
					obj.pos.y = obj.rect.height / 2
				elif obj.pos.y > bounds.height - (obj.rect.height / 2):
					obj.vel.y = 0
					obj.pos.y = bounds.height - (obj.rect.height / 2)
					obj.on_ground = True
					foot_collisions = 1"""
				
				for p in self.platforms:

					p_rect = copy.copy(p.rect)
					p_rect.left -= view_rect.left

					if not obj.foot is None:
						if self.is_colliding(obj.foot, p_rect):
							foot_collisions += 1

					if self.is_colliding(obj.rect, p_rect):

						# print obj.vel

						if obj.on_collide_platform(p):

							obj.correct_penetration(p_rect)

							if obj.rect.bottom < p_rect.top:
								obj.vel.y = 0
								obj.on_ground = True
							elif obj.rect.top > p_rect.bottom:
								obj.vel.y = 0

							if obj.rect.right < p_rect.left or obj.rect.left > p_rect.right:
								print 'left or right'
								obj.vel.x = 0

				if not obj.foot is None and foot_collisions < 1:
					obj.on_ground = False

				if not obj.on_ground and obj.type == BODY_DYNAMIC:
					obj.vel += self.gravity * dt

	def debug_draw(self, screen):
		view_rect = self.map.view_rect

		for p in self.platforms:
			image = pygame.Surface((p.rect.width, p.rect.height))
			screen.blit(image, (p.rect.left - view_rect.left, p.rect.top - view_rect.top))

		for obj in self.objects:
			obj.debug_draw(screen)


class PhysicsObject(object):

	MAX_PENETRATION = 10.0
	FOOT_SIZE = 0.25
	PENETRATION_CORRECTION = 1.5

	def __init__(self, pos, vel, size=(0, 0), body_type=0):
		self.pos = Vector2(pos)
		self.vel = Vector2(vel)
		self.target_vel = Vector2((0, 0))
		self.type = body_type
		self.rect = Rect(pos, size)
		self.rect.left = self.pos.x - self.rect.width / 2
		self.rect.top = self.pos.y - self.rect.height / 2
		self.acceleration = 500
		self.on_ground = False
		self.foot = None

	def set_foot(self, use_foot=False):
		if use_foot:
			foot_left = self.get_foot_left()
			foot_top = self.rect.bottom - 2.5
			foot_width = self.rect.width * self.FOOT_SIZE
			foot_height = 5
			self.foot = Rect(foot_left, foot_top, foot_width, foot_height)
		else:
			self.foot = None

	def get_foot_left(self):
		return (self.rect.left + self.rect.width / 2) - self.rect.width * self.FOOT_SIZE

	def update_foot(self):
		if not self.foot is None:
			self.foot.left = self.get_foot_left()
			self.foot.top = self.rect.bottom - 2.5

	def update(self, dt):
		self.pos += self.vel * dt
		self.rect.left = self.pos.x - self.rect.width / 2
		self.rect.top = self.pos.y - self.rect.height / 2
		self.vel.x = self.move(self.vel.x, self.target_vel.x, self.acceleration, dt)
		self.update_foot()

	def debug_draw(self, screen):
		image = pygame.Surface((self.rect.width, self.rect.height))
		screen.blit(image, (self.rect.left, self.rect.top))

		if not self.foot is None:
			foot_image = pygame.Surface((self.foot.width, self.foot.height))
			foot_image.fill( (255, 20, 0) )
			screen.blit(foot_image, (self.foot.left, self.foot.top))

	def move(self, current, target, acceleration, dt):
		if (target == current):
			return target
		direction = math.copysign(1.0, target - current)
		current += direction * acceleration * dt
		return current if (direction == math.copysign(1.0, target - current)) else target

	def on_collide_obj(self, obj=None):
		raise NotImplementedError('implement on_collide_obj')

	def on_collide_platform(self, tile=None):
		raise NotImplementedError('implement on_collide_platform')

	def correct_penetration(self, orect):
		overlapse_right = self.vel.x > 0 and self.rect.right > orect.left and self.rect.left < orect.left
		overlapse_left = self.vel.x < 0 and self.rect.left < orect.right and self.rect.right > orect.right
		overlapse_top = self.vel.y > 0 and self.rect.bottom > orect.top and self.rect.top < orect.top
		overlapse_bottom = self.vel.y < 0 and self.rect.top < orect.bottom and self.rect.bottom > orect.bottom

		p_bottom = abs(self.rect.bottom - orect.top)
		p_right = abs(self.rect.right - orect.left)
		p_top = abs(self.rect.top - orect.bottom)
		p_left = abs(self.rect.left - orect.right)

		if overlapse_top and p_bottom < self.MAX_PENETRATION:
			self.rect.y -= (self.rect.bottom - orect.top) * self.PENETRATION_CORRECTION

		elif overlapse_right and p_right < self.MAX_PENETRATION:
			self.rect.x -= (self.rect.right - orect.left) * self.PENETRATION_CORRECTION

		elif overlapse_bottom and p_top < self.MAX_PENETRATION:
			self.rect.y += (orect.bottom - self.rect.top) * self.PENETRATION_CORRECTION

		elif overlapse_left and p_left < self.MAX_PENETRATION:
			self.rect.x += (orect.right - self.rect.left) * self.PENETRATION_CORRECTION