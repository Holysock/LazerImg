#Pygame-Wrapper by OleL

import pygame

class plot:
	width = 800
	height = 600
	r = 255
	g = 255
	b = 255
	screen = pygame.display.set_mode((width,height))
	autoflipping = False
	def __init__(self, width, height, autof = False):
		self.screen = pygame.display.set_mode((width, height))
		self.width = width
		self.height = height
		self.autoflipping = autof
		self.clock = pygame.time.Clock()
	def setColor(self,r,g,b):
		self.r = r
		self.g = g
		self.b = b
	def setBackground(self,r,g,b):
		self.screen.fill((r,g,b))
	def plot(self, x, y, t = 2):
		pygame.draw.rect(self.screen, (self.r,self.g,self.b), (x,y,t,t))
		if self.autoflipping: pygame.display.flip()
	def plotdot(self,x,y):
		self.plotline(x,y,x,y)
		if self.autoflipping: pygame.display.flip()
	def plotline(self, x1, y1, x2, y2):
		pygame.draw.line(self.screen, (self.r,self.g,self.b), (x1,y1),(x2,y2),1)
		if self.autoflipping: pygame.display.flip()
		
	def show(self):
		pygame.display.flip()
	def plotimage(self,path_to_image):
		image = pygame.image.load(path_to_image)
		self.screen.blit(image, image.get_rect())
		if self.autoflipping: pygame.display.flip()
		
	def getcolor(self, x,y):
		rgb = self.screen.get_at((x,y))	
		r = rgb[0]
		g = rgb[1]
		b = rgb[2]
		return (r,g,b)
	def tick(self,frate):
		self.clock.tick(frate)
	def doMagic(self):
		pass
