from pygame import Rect


class Text(object):

	def __init__(self, font, text, pos, color=(255,255,255)):
		self.text = text
		self.color = color
		self.font = font
		x, y = pos
		width, height = font.size(text)
		self.rect = Rect(x - width / 2, y, width, height)
		self.rendered = None

	def draw(self, screen, view_rect):
		left = self.rect.left - view_rect.left
		top = self.rect.top - view_rect.top

		if self.rendered is None:
			self.rendered = self.font.render(self.text, 1, self.color)

		screen.blit(self.rendered, (left, top))