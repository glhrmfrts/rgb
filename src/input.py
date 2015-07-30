from pygame.locals import *

##
## responsable for input handling
##
class Input(object):

	def __init__(self, keys, mouse):
		self.keys = keys
		self.mouse = mouse
		self.keys_down = {}
		self.pos = (0, 0)
		self.mouse_down = False

	def update(self):
		# this clears all key states, and must be called before "handle_event"
		self.click = False
		for key in self.keys_down:
			self.keys_down[key] = False

	def handle_event(self, event):
		if event.type == KEYDOWN:
			self.handle_key_down(event.key)
		elif event.type == KEYUP:
			self.handle_key_up(event.key)
		elif event.type == MOUSEBUTTONDOWN:
			self.handle_mouse_down()
		elif event.type == MOUSEBUTTONUP:
			self.handle_mouse_up()
		elif event.type == MOUSEMOTION:
			self.handle_mouse_move()

	def handle_key_down(self, keycode):
		self.keys_down[keycode] = True

	def handle_key_up(self, keycode):
		self.keys_down[keycode] = False

	def handle_mouse_down(self):
		self.mouse_down = True
		self.click = False

	def handle_mouse_up(self):
		self.mouse_down = False
		self.click = True

	def handle_mouse_move(self):
		self.pos = self.mouse.get_pos()

	def is_down(self, key):
		try:
			return self.keys_down[key]
		except KeyError:
			return False

	def is_pressed(self, key):
		return self.keys.get_pressed()[key]