from pygame.locals import *
from scene import Scene
from play_scene import PlayScene
from text import Text
from color import *
import pygame.font


class MenuScene(Scene):

	def __init__(self, game, start_level):
		Scene.__init__(self, game)
		self.texts = []
		self.texts.append(Text(game.font, "RGB", (game.width / 2, 100)))

		small_font = pygame.font.Font('../assets/font/vcr.ttf', 20)

		self.texts.append(Text(small_font, "You don't collide with anything", (game.width / 2, 200)))
		self.texts.append(Text(small_font, "that has the same color as you", (game.width / 2, 220)))

		self.texts.append(Text(small_font, "1 - Red", (game.width / 2, 300), RED))
		self.texts.append(Text(small_font, "2 - Green", (game.width / 2, 325), GREEN))
		self.texts.append(Text(small_font, "3 - Blue", (game.width / 2, 350), BLUE))
		self.texts.append(Text(small_font, "Arrows - Movement", (game.width / 2, 375)))
		self.texts.append(Text(small_font, "R - Restart level", (game.width / 2, 400)))
		self.texts.append(Text(small_font, "S - Enable/Disable sounds", (game.width / 2, 425)))

		self.texts.append(Text(game.font, "Press space to play", (game.width / 2, 500)))
		self.view_rect = Rect(0,0,0,0)
		self.start_level = start_level

	def update(self, dt):
		if self.game.input.is_down(K_SPACE):
			self.game.next_scene = PlayScene(self.game, self.start_level)

	def draw(self):
		for text in self.texts:
			text.draw(self.game.screen, self.view_rect)