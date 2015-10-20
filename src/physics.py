from pygame.math import Vector2
from pygame import Rect
import pygame
import math
import copy
import time

BODY_DYNAMIC = 1
BODY_STATIC = 2

ID_PLAYER = 0
ID_OBJ = 1
ID_MOVABLE_BLOCK = 2


class Platform(object):
	""" Simply holding some information about a platform in the game """

	def __init__(self, rect, layer):
		self.rect = rect
		self.layer = layer


class PhysicsObject(object):

	MAX_PENETRATION = 20.0
	FOOT_SIZE = 1
	PENETRATION_CORRECTION = 1.1

	def __init__(self, pos, vel, size=(0, 0), body_type=0):
		self.pos = Vector2(pos)
		self.vel = Vector2(vel)
		self.target_vel = Vector2((0, 0))
		self.type = body_type
		self.rect = Rect(pos, size)
		self.rect.left = self.pos.x - self.rect.width / 2
		self.rect.top = self.pos.y - self.rect.height / 2
		self.acceleration = 1500
		self.on_ground = False
		self.foot = None
		self.wants_to_move = False
		self.id = None

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
		return self.rect.left # + (self.rect.width * self.FOOT_SIZE / 2)

	def update_foot(self):
		if not self.foot is None:
			self.foot.left = self.get_foot_left()
			self.foot.top = self.rect.bottom - 2.5

	def update(self, dt):
		self.pos += self.vel * dt
		self.rect.left = self.pos.x - self.rect.width / 2
		self.rect.top = self.pos.y - self.rect.height / 2

		if self.id == ID_MOVABLE_BLOCK and self.on_ground:
			self.vel.x = self.move(self.vel.x, self.target_vel.x, self.acceleration, dt)
		elif self.id != ID_MOVABLE_BLOCK:
			self.vel.x = self.move(self.vel.x, self.target_vel.x, self.acceleration, dt)

		if not self.wants_to_move and self.type == BODY_DYNAMIC:
			self.target_vel.x = 0

		if self.vel.x == 0.0:
			self.wants_to_move = False

		self.update_foot()

	def debug_draw(self, screen, view_rect):

		draw_rect = None

		if self.type == BODY_DYNAMIC:
			draw_rect = self.rect
		else:
			draw_rect = copy.copy(self.rect)
			draw_rect.left -= view_rect.left
			draw_rect.top -= view_rect.top

		image = pygame.Surface((draw_rect.width, draw_rect.height))
		image.fill((207, 207, 0))
		screen.blit(image, (draw_rect.left, draw_rect.top))

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
		pass

	def on_collide_platform(self, tile=None):
		pass

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
			self.pos.y -= (self.rect.bottom - orect.top) * self.PENETRATION_CORRECTION

		elif overlapse_right and p_right < self.MAX_PENETRATION:
			self.pos.x -= (self.rect.right - orect.left) * self.PENETRATION_CORRECTION

		elif overlapse_bottom and p_top < self.MAX_PENETRATION:
			self.pos.y += (orect.bottom - self.rect.top) * self.PENETRATION_CORRECTION

		elif overlapse_left and p_left < self.MAX_PENETRATION:
			self.pos.x += (orect.right - self.rect.left) * self.PENETRATION_CORRECTION

		self.rect.left = self.pos.x - self.rect.width / 2
		self.rect.top = self.pos.y - self.rect.height / 2


class PhysicsWorld(object):
	""" Handles (hopefully) all collisions and interactions in the "world" """

	def __init__(self, tilemap, bounds, gravity=(0, 0)):
		self.map = tilemap
		self.bounds = bounds
		self.gravity = Vector2(gravity)
		self.velocity_threshold = 3
		self.static_objects = []
		self.dynamic_objects = []
		self.platforms = []
		self.create_platforms()

	def add_obj(self, obj):
		if obj.type == BODY_DYNAMIC:
			self.dynamic_objects.append(obj)
		elif obj.type == BODY_STATIC:
			self.static_objects.append(obj)

	def create_platforms(self):		
		for layer in self.map.collidable_tile_layers:
			tiles = list(self.map.get_nonempty_tiles_coord(layer))
			self.create_platforms_rect(tiles, layer)

	def create_platforms_rect(self, tiles, layer):
		""" Create a collision rect for each non-empty tile segment, that is, one or more tiles together """
		if len(tiles) < 1:
			return False

		x, y = tiles.pop(0)
		width = self.map.content['tilewidth']
		height = self.map.content['tileheight']
		rect = Rect((0, 0, 0, 0))
		rect.left = x * width
		rect.top = y * height
		rect.width = width
		rect.height = height
		# self.platforms.append(Platform(rect, layer))
		n_tiles_x, n_tiles_y = 0, 0

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
		return a.colliderect(b)

	def set_view(self, view_rect):
		self.map.set_view(view_rect)

	def has_velocity_influence(self, obj):
		return type(obj).__name__ in ['MovingBlock', 'ImpulseBlock']

	def update(self, dt):
		bounds = self.bounds
		view_rect = self.map.view_rect
		previous_active_color = None

		for obj in self.static_objects:
			obj.update(dt)

		for i, obj in enumerate(self.dynamic_objects):

			if previous_active_color is None:
				try:
					previous_active_color = obj.active_color
				except:
					pass

			obj.update(dt)

			# adjust viewport offsets
			obj.rect.left -= view_rect.left
			obj.rect.top -= view_rect.top

			if not obj.foot is None:
				obj.foot.left = obj.get_foot_left()
				obj.foot.top -= view_rect.top
			
				# TODO: adjust y-axis viewport also

			foot_collisions = 0

			# check left and right bounds
			if obj.pos.x < (obj.rect.width / 2):
				obj.vel.x = 0
				obj.pos.x = (obj.rect.width / 2)
			elif obj.pos.x > bounds.width:
				obj.vel.x = 0
				obj.pos.x = bounds.width - (obj.rect.width / 2)

			for p in (self.platforms + self.static_objects):

				p_rect = copy.copy(p.rect)
				p_rect.left -= view_rect.left
				p_rect.top -= view_rect.top

				if not obj.foot is None:
					if self.is_colliding(obj.foot, p_rect) and obj.foot.y < p_rect.y:
						foot_collisions += 1

						changed_active_color = False
						try:
							changed_active_color_static = False
							if type(p).__name__ in ['ColorChangingBlock', 'TrickyBlock']:
								changed_active_color_static = p.active_color != p.previous_active_color
								if changed_active_color_static: 
									p.previous_active_color = p.active_color

							changed_active_color = obj.active_color != previous_active_color or \
													changed_active_color_static

							previous_active_color = obj.active_color

							if changed_active_color:
								# print 'changed active color'
								foot_collisions = 0
								obj.on_ground = False
						except AttributeError:
							pass

						if self.has_velocity_influence(p):
							p.change_obj_velocity(obj)
				
				is_colliding = False
				if obj.vel.y > 0:
					is_colliding = self.is_colliding(obj.rect, p_rect) and foot_collisions < 2
				else:
					is_colliding = self.is_colliding(obj.rect, p_rect)

				if is_colliding:

					should_handle_collision = False

					if isinstance(p, Platform):
						should_handle_collision = obj.on_collide_platform(p)
					else:
						should_handle_collision = obj.on_collide_obj(p)
						p.on_collide_obj(obj)
						
					if should_handle_collision:
						print(foot_collisions)
						obj.correct_penetration(p_rect)

						obj.rect.left -= view_rect.left
						obj.rect.top -= view_rect.top

						if not obj.foot is None:
							obj.foot.left = obj.get_foot_left()

						if obj.rect.bottom < p_rect.top:
							obj.vel.y = 0
							obj.on_ground = True
						elif obj.rect.top > p_rect.bottom:
							obj.vel.y = 0

						if obj.rect.right < p_rect.left or obj.rect.left > p_rect.right:
							obj.vel.x = 0

			for o in self.dynamic_objects[(i + 1):]:

				if not obj.foot is None:
					if self.is_colliding(obj.foot, o.rect) and obj.foot.y < o.rect.y:
						foot_collisions += 1

				if self.is_colliding(obj.rect, o.rect):
					should_handle_collision = obj.on_collide_obj(o)
					if not should_handle_collision: 
						continue

					obj_rect_copy = copy.copy(obj.rect)

					obj.correct_penetration(o.rect)
					o.correct_penetration(obj_rect_copy)

					del obj_rect_copy

					obj.rect.left -= view_rect.left
					obj.rect.top -= view_rect.top

					o.rect.left -= view_rect.left
					o.rect.top -= view_rect.top

					if not obj.foot is None:
						obj.foot.left = obj.get_foot_left()
						obj.foot.top -= view_rect.top

					if not o.foot is None:
						o.foot.left = o.get_foot_left()
						o.foot.top -= view_rect.top

					if obj.rect.bottom < o.rect.top:
						obj.vel.y = 0
						obj.on_ground = True
					elif obj.rect.top > o.rect.bottom:
						obj.vel.y = 0

					if obj.rect.right < o.rect.left or obj.rect.left > o.rect.right:
						o.vel.x = obj.vel.x * 0.75
						obj.vel.x *= 0.25

			if not (obj.foot is None) and foot_collisions < 1:
				obj.on_ground = False

			if not obj.on_ground and obj.type == BODY_DYNAMIC:
				obj.vel += self.gravity * dt

	def rect_adjust(self, rect):
		result = copy.copy(rect)
		result.left -= self.map.view_rect.left
		result.top -= self.map.view_rect.top
		return result

	def debug_draw(self, screen):
		view_rect = self.map.view_rect

		for p in self.platforms:
			image = pygame.Surface((p.rect.width, p.rect.height))
			image.fill((205, 0, 205))
			screen.blit(image, (p.rect.left - view_rect.left, p.rect.top - view_rect.top))

		for obj in (self.dynamic_objects + self.static_objects):
			obj.debug_draw(screen, view_rect)