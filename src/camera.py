from pygame import Rect


class Camera(object):

	def __init__(self, world, screen_rect, map_rect):
		self.rect = Rect(0, 0, screen_rect.width, screen_rect.height)
		self.map_rect = map_rect
		self.world = world
		self.target = None

	def set_target(self, target):
		self.target = target

	def update(self):
		if not self.target is None:
			self.rect.left = 0
			self.rect.top = 0
			half_width = self.rect.width / 2
			half_height = self.rect.height / 2

			# x-axis
			if self.target.pos.x > self.map_rect.width - half_width:
				self.rect.left = self.map_rect.width - self.rect.width

			elif self.target.pos.x > half_width:
				self.rect.left = self.target.pos.x - half_width

			# y-axis
			if self.target.pos.y > self.map_rect.height - half_height:
				self.rect.top = self.map_rect.height - self.rect.height

			elif self.target.pos.y > half_height:
				self.rect.top = self.target.pos.y - half_height

			self.world.set_view(self.rect)