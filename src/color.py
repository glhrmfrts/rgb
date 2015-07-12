class Color(object):

	def __init__(self, r=0, g=0, b=0, a=255):
		self.r = r
		self.g = g
		self.b = b
		self.a = a

	def tuple(self, mode='RGB'):
		if mode == 'RGB':
			return (self.r, self.g, self.b)
		elif mode == 'RGBA':
			return (self.r, self.g, self.b, self.a)

WHITE = Color(255, 255, 255).tuple()
BLACK = Color(0, 0, 0).tuple()
RED = Color(255, 0, 0).tuple()
GREEN = Color(0, 255, 0).tuple()
BLUE = Color(0, 0, 255).tuple()