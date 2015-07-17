import pygame
from color import *
from play_scene import PlayScene
from input import Input
import time

class Game(object):

	def __init__(self, screen, width, height):
		self.target_fps = 60
		self.clock = pygame.time.Clock()
		self.running = False
		self.test_text = "Hello world"
		self.font = pygame.font.Font('../assets/font/vcr.ttf', 28)
		self.screen = screen
		self.width = width
		self.height = height
		self.current_scene = None
		self.restarting = False
		self.input = Input(pygame.key, pygame.mouse)
		# self.background = Background((800, 600), 'assets/img/bgs.png')

	def run(self):
		self.running = True
		self.current_scene = PlayScene(self)
		current_time = 0
		previous_time = time.time()
		while self.running:
			self.clock.tick( self.target_fps )
			self.screen.fill( WHITE )
			self.input.update()

			for event in pygame.event.get():
				self.input.handle_event(event)

			if game.input.is_down(pygame.K_ESCAPE):
				self.running = False
				self.restarting = False

			current_time = time.time()
			delta_time = (current_time - previous_time)
			
			self.update(delta_time)
			self.draw()

			fps = round(1.0 / delta_time)
			fps_text = 'FPS: {0}'.format(fps)
			fps_w, fps_h = self.font.size(fps_text)
			fps_text_pos = (self.width - fps_w - 40, 20)
			
			self.screen.blit(self.font.render(fps_text, 1, WHITE), fps_text_pos)

			pygame.display.update()
			previous_time = current_time

		if self.restarting:
			game.run()
		else:
			game.quit()

	def restart(self):
		self.running = False
		self.restarting = True

	def quit(self):
		pygame.quit()

	def update(self, dt):
		self.current_scene.update(dt)

	def draw(self):
		self.current_scene.draw()

width = 800
height = 600
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.flip()

# initialize the game with the screen
game = Game(screen, width, height)
game.run()