from pygame import Rect


class Text(object):

	def __init__(self, font, text, pos, color=(255,255,255), use_rect=False):
		self.text = text
		self.color = color
		self.font = font
		x, y = pos
		width, height = font.size(text)
		self.rect = Rect(x - width / 2, y, width, height)
		self.rendered = None
		self.update = False

	def draw(self, screen, view_rect = None):
		left = self.rect.left
		top = self.rect.top
		if not view_rect is None:
			left -= view_rect.left
			top -= view_rect.top

		if self.rendered is None or self.update:
			self.rendered = self.font.render(self.text, 1, self.color)

		screen.blit(self.rendered, (left, top))