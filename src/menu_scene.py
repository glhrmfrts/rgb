from pygame.locals import *
from pygame import Surface
from scene import Scene
from play_scene import PlayScene
from text import Text
from color import *
import pygame.font
import pygame.image
import pygame.transform
import inspect
import resource


class Menu(object):

	def __init__(self, input, size):
		self.input = input
		self.texts = []
		self.padding = 0
		self.current_menu = None
		self.width, self.height = size
		self.arrow = pygame.image.load('../assets/img/arrow.png')
		self.arrow = pygame.transform.scale(self.arrow, (64, 32))
		self.arrow.set_colorkey((0,0,0))
		self.arrow.convert()
		self.arrow_x = size[0] / 2
		self.arrow_y = 200
		self.debug_mouse_img = Surface((20, 20))
		self.debug_mouse_img.fill( RED )

	def generate(self, menu_tree, parent=None):
		font = None
		for k in menu_tree:
			val = menu_tree[k]
			x, y, size = 0, 0, 25
			callback = None
			if isinstance(val, tuple):
				x, y, size = val
			elif inspect.isfunction(val):
				callback = val
			if y == 0:
				y = (self.height / 2) + (self.padding * len(self.texts))
			x += self.width / 2
			font = pygame.font.Font('../assets/font/vcr.ttf', size)
			text_id = len(self.texts)
			text = Text(font, k, (x, y))
			info = {
				'id': text_id,
				'text': text,
				'callback': callback,
				'parent': parent,
				'has_children': False,
			}
			if isinstance(val, dict):
				info['has_children'] = True
				self.generate(val, text_id)
			self.texts.append(info)

	def update(self, dt):
		if self.input.click:
			mouse_rect = Rect(self.input.pos[0] - 5, self.input.pos[1] - 5, 10, 10)
			arrow_rect = Rect(self.arrow_x - 32, self.arrow_y - 16, 64, 32)
			if mouse_rect.colliderect(arrow_rect):
				self.current_menu = None
				return
			for text in self.texts:
				if not self.current_menu == text['parent']:
					continue
				if mouse_rect.colliderect(text['text'].rect):
					if not text['callback'] is None:
						cb = text['callback']
						cb()
					else:
						if text['has_children']:
							self.current_menu = text['id']
					break

	def draw(self, screen):
		# screen.blit(self.debug_mouse_img, self.input.pos)
		if not self.current_menu is None:
			screen.blit(self.arrow, (self.arrow_x - 32, self.arrow_y - 16))
		for text in self.texts:
			if self.current_menu == text['parent']:
				text['text'].draw(screen)


class MenuScene(Scene):

	def __init__(self, game, start_level):
		Scene.__init__(self, game)
		self.texts = []
		self.texts.append(Text(game.font, "RGB", (game.width / 2, 100)))
		self.view_rect = Rect(0,0,0,0)
		self.start_level = start_level
		self.bg = Surface((game.width, game.height))
		self.bg.fill((0,0,0))
		menu_tree = {
			'Play': {
				'New Game': (lambda: self.new_game()),
				'Continue Game': (lambda: self.continue_game())
			},
			'Controls': {
				'1 - Turn Red': (0, 300, 18),
				'2 - Turn Blue': (0, 325, 18),
				'3 - Turn Green': (0, 350, 18),
				'Arrows - Movement': (0, 375, 18),
				'R - Restart level': (0, 400, 18),
				'S - Enable/Disable sounds': (0, 425, 18)
			},
			'Help': {
				'You don\'t collide with anything': (0, 300, 18),
				'that has the same color as you': (0, 325, 18)
			},
			'Credits': {
				'Guilherme Nemeth': (0, 300, 25),
				'programming, and (pseudo) graphics': (0, 325, 18),
				'sounds mainly from bfxr and the web': (0, 375, 18),
				'Source on github.com/habboi/rgb': (0, 500, 16)
			}
		}
		self.menu = Menu(game.input, (game.width, game.height))
		self.menu.padding = 15
		self.menu.generate(menu_tree)

	def new_game(self):
		self.game.next_scene = PlayScene(self.game, self.start_level)

	def continue_game(self):
		save_file = resource.find_save_file()
		if save_file is None:
			return self.new_game()
		last_save = save_file.read()
		self.game.next_scene = PlayScene(self.game, int(last_save))
		save_file.close()

	def update(self, dt):	
		self.menu.update(dt)
		if self.game.input.is_down(K_SPACE):
			self.game.next_scene = PlayScene(self.game, self.start_level)

	def draw(self):
		self.game.screen.blit(self.bg, (0, 0))
		self.menu.draw(self.game.screen)
		for text in self.texts:
			text.draw(self.game.screen, self.view_rect)