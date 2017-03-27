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

def move(current, target, acceleration, dt):
	if (target == current):
		return target
	direction = math.copysign(1.0, target - current)
	current += direction * acceleration * dt
	return current if (direction == math.copysign(1.0, target - current)) else target

class Vector2(object):
        """2D vector"""

        def __init__(self, (x, y)):
                self.x = x
                self.y = y

        def __mul__(self, arg):
                if type(arg) == float or type(arg) == int:
                        return Vector2((self.x * arg, self.y * arg))
                elif isinstance(arg, Vector2):
                        return Vector2((self.x * arg.x, self.y * arg.y))
                else:
                        raise TypeError('Vector2 * (float|Vector2)')

        def __add__(self, arg):
                if type(arg) == float or type(arg) == int:
                        return Vector2((self.x + arg, self.y + arg))
                elif type(arg) == Vector2:
                        return Vector2((self.x + arg.x, self.y + arg.y))
                else:
                        raise TypeError('Vector2 + (float|Vector2)')

        def __sub__(self, arg):
                if type(arg) == float or type(arg) == int:
                        return Vector2((self.x - arg, self.y - arg))
                elif type(arg) == Vector2:
                        return Vector2((self.x - arg.x, self.y - arg.y))
                else:
                        raise TypeError('Vector2 - (float|Vector2)')

        def dot(self, arg):
                return self.x * arg.x + self.y * arg.y

class Collision(object):
        """ Describe a collision between two objects"""

        def __init__(self, first, second):
                self.first = first
                self.second = second
                self.normal = Vector2((0, 0))
                self.depth = 0

        def resolve(self):
                vel_normal = (self.second.vel - self.first.vel).dot(self.normal)
                if vel_normal > 0.0:
                        return

                j = -1 * vel_normal
                impulse = self.normal * j

                if self.first.type == BODY_DYNAMIC:
                        self.first.vel -= impulse

                if self.second.type == BODY_DYNAMIC:
                        self.second.vel += impulse

                s = max(self.depth - 0.05, 0.0)
                correction = self.normal * s
                if self.first.type == BODY_DYNAMIC:
                        self.first.pos -= correction

                if self.second.type == BODY_DYNAMIC:
                        self.second.pos += correction

class PhysicsObject(object):

	def __init__(self, pos, vel, size=(0, 0), body_type=0):
		self.pos = Vector2(pos)
		self.vel = Vector2(vel)
                self.half = Vector2((size[0] * 0.5, size[1] * 0.5))
		self.target_vel = Vector2((0, 0))
		self.type = body_type
		self.rect = Rect(pos, size)
		self.rect.left = self.pos.x - self.rect.width / 2
		self.rect.top = self.pos.y - self.rect.height / 2
		self.acceleration = 1500
		self.on_ground = False
		self.wants_to_move = False
		self.id = None

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

        def update(self, dt):
                pass

        def on_collision(self, col, obj):
                pass

class Platform(PhysicsObject):
	""" Simply holding some information about a platform in the game """

	def __init__(self, rect, layer):
                PhysicsObject.__init__(self, (rect.left + rect.width/2, rect.top + rect.height/2), (0, 0), (rect.width, rect.height), BODY_STATIC)
		self.layer = layer
                self.vel = Vector2((0, 0))

        def __mul__(self, arg):
                if type(arg) == 'float':
                        return Vector2((self.x * arg, self.y * arg))
                elif type(arg) == 'Vector2':
                        return Vector2((self.x * arg.x, self.y * arg.y))

        def on_collision(self, col, obj):
                return True

class World(object):
        def __init__(self, tilemap, bounds, gravity):
                self.map = tilemap
                self.bounds = bounds
                self.gravity = gravity
                self.velocity_threshold = 3
                self.static_objects = []
                self.dynamic_objects = []
                self.platforms = []
                self.collisions = []
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

        def set_view(self, view_rect):
		self.map.set_view(view_rect)

        def check_collision(self, a, b):
                dif = b.pos - a.pos

                dx = a.half.x + b.half.x - abs(dif.x)
                if dx <= 0.0:
                        return None

                dy = a.half.y + b.half.y - abs(dif.y)
                if dy <= 0.0:
                        return None

                col = Collision(a, b)
                if dx < dy:
                        col.normal.x = math.copysign(1.0, dif.x)
                        col.depth = dx
                else:
                        col.normal.y = math.copysign(1.0, dif.y)
                        col.depth = dy

                return col

        def check_collisions_against(self, obj, objs):
                for b in objs:
                        collision = self.check_collision(obj, b)
                        if collision is not None:
                                self.collisions.append(collision)

        def has_velocity_influence(self, obj):
		return type(obj).__name__ in ['MovingBlock', 'ImpulseBlock']

        def update(self, dt):
                del self.collisions[:]

                for i, obj in enumerate(self.dynamic_objects):
                        obj.vel.y += self.gravity[1]

                        self.check_collisions_against(obj, self.platforms)
                        self.check_collisions_against(obj, self.static_objects)

                        if i < len(self.dynamic_objects) - 2:
                                self.check_collisions_against(obj, self.dynamic_objects[i+1:])

                for col in self.collisions:
                        print((col.normal.x, col.normal.y), col.depth)
                        if col.first.on_collision(col, col.second) and col.second.on_collision(col, col.first):
                                col.resolve()

                for obj in self.dynamic_objects:
                        obj.update(dt)
                        obj.vel.x = move(obj.vel.x, obj.target_vel.x, obj.acceleration, dt)

                        obj.pos += obj.vel * dt
		        obj.rect.left = obj.pos.x - obj.rect.width / 2
		        obj.rect.top = obj.pos.y - obj.rect.height / 2

                        if not obj.wants_to_move:
                                pass#obj.target_vel.x = 0

                        if obj.vel.x == 0.0:
                                pass#obj.wants_to_move = False

                for obj in self.static_objects:
                        obj.update(dt)

                        if obj.id == ID_MOVABLE_BLOCK:
			        obj.vel.x = move(obj.vel.x, obj.target_vel.x, obj.acceleration, dt)
		        elif obj.id != ID_MOVABLE_BLOCK:
			        obj.vel.x = move(obj.vel.x, obj.target_vel.x, obj.acceleration, dt)

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
