from pygame.locals import *
from color import *
from player import Player
from physics import PhysicsWorld
from camera import Camera
from map import Map

##
## represents a game scene that can be changed
##
class GameScene(object):

	def __init__(self, game):
		self.game = game

	def update(self, dt):
		raise NotImplementedError('Implement update method')

	def draw(self):
		raise NotImplementedError('Implement draw method')

##
## the main scene where the player plays
##
class PlayableScene(GameScene):

	def __init__(self, game):
		GameScene.__init__(self, game)
		self.timer = 0.0
		self.timer_freq = 5.0
		self.x = 50.0
		self.map = Map('../assets/maps/test.json', '../assets/img/ground.png')

		screen_rect = game.screen.get_rect()
		world_bounds = Rect(0, 0, self.map.get_rect().width, screen_rect.height)

		self.world = PhysicsWorld(self.map, world_bounds, (0, 90))
		self.player = Player((50, 50), game.input)
		
		self.camera = Camera(self.world, screen_rect, world_bounds)
		self.camera.set_target(self.player)

		self.world.add_object(self.player)

	def update(self, dt):
		game = self.game
		self.camera.update()
		self.world.update(dt)

		if self.player.rect.top > game.screen.get_rect().height:
			game.restart()

	def draw(self):
		game = self.game
		self.player.draw(game.screen)
		self.map.draw(game.screen)
		# self.world.debug_draw(game.screen)

"""
class OtherScene(GameScene):
	def __init__(self, game):
		GameScene.__init__(self, game)

	def update(self, dt):
		pass

	def draw(self):
		game = self.game
		game.screen.blit(game.font.render("Hello world other scene", 1, color.WHITE), (200, 200) )
"""