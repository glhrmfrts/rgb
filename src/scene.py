class Scene(object):

	def __init__(self, game):
		self.game = game

	def update(self, dt):
		raise NotImplementedError('Implement update method')

	def draw(self):
		raise NotImplementedError('Implement draw method')