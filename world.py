#TODO: improve efficiency for higher neuron count
#TODO: make tiles and brains selectable and show info
#TODO: limit population size and maintain between bounds
#TODO: balance systems
#TODO: change spawn points of brains
#TODO: make brains pass information when breeding
import sys
from time import time, sleep
import pygame
from random import random
import brain
pygame.init()

#Colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

screen = pygame.display.set_mode([800, 600])
pygame.display.set_caption("Genetics AI")
fontBig = pygame.font.Font(None, 40)
fontSmall = pygame.font.Font(None, 16)

foodSpawnChance = 0.0005
class World:
	def __init__(self):
		self.grid = []
		for y in range(16):
			row = []
			for x in range(16):
				row.append([])
			self.grid.append(row)
	
		self.brains = [None] * 64
		for i in range(1, 31):
			print("Creating brain " + str(i))
			self.brains[i] = brain.Brain((i-1) % 16, (i-1) // 16, self, i)
			self.brains[i].randomize(10)
			self.grid[self.brains[i].y][self.brains[i].x].append(self.brains[i])
		
		self.food = []
		for y in range(16):
			row = [0] * 16
			self.food.append(row)
			
	def tick(self):
		for y in range(16):
			for x in range(16):
				if (random() < foodSpawnChance):
					self.food[y][x] += 1
					
		for i in range(len(self.brains)):
			b = self.brains[i]
			if (b is not None):
				b.tick()
				if (b.toKill):
					self.brains[i] = None
					del b
					
	def foodOnCell(self, x, y):
		return self.food[y][x] >= 1
	
	def foodNearby(self, x, y):
		foodTotal = self.food[y][x]
		foodTotal += self.food[y-1 if y!=0 else 15][x-1 if x!=0 else 15]
		foodTotal += self.food[y-1 if y!=0 else 15][x]
		foodTotal += self.food[y-1 if y!=0 else 15][x+1 if x!=15 else 0]
		foodTotal += self.food[y][x-1 if x!=0 else 15]
		foodTotal += self.food[y][x+1 if x!=15 else 0]
		foodTotal += self.food[y+1 if y!=15 else 0][x-1 if x!=0 else 15]
		foodTotal += self.food[y+1 if y!=15 else 0][x]
		foodTotal += self.food[y+1 if y!=15 else 0][x+1 if x!=15 else 0]
		return foodTotal >= 1
		
	def eat(self, x, y):
		if (self.foodOnCell(x, y)):
			self.food[y][x] -= 1
			return True
		else:
			return False
			
	def speak(self, message, speaker, posX, posY):
		for i in range(len(self.brains)):
			if (self.brains[i] is not None and i != speaker):
				self.brains[i].hearSpeach(message, speaker, posX, posY)
				
		convertedMessage = ""
		for i in range(20):
			val = int(message[7*i:7*(i+1)], 2)
			if (val < 32):
				val = 32
			convertedMessage += chr(val)
		speakerStr = str(speaker)
		if (speaker < 10):
			speakerStr = '0' + speakerStr
		print(speakerStr + " says: " + str(convertedMessage))
				
	def move(self, ID, posX, posY, fromX, fromY):
		b = self.brains[ID]
		self.grid[fromY][fromX].remove(b)
		self.grid[posY][posX].append(b)
		
	def newBorn(self, b):
		nextValid = 0
		for i in range(1, len(self.brains)):
			if (self.brains[i] is None):
				nextValid = i
				break
		b.ID = nextValid
		self.brains[nextValid] = b
		self.grid[b.y][b.x].append(b)
		

def load(filename):
	pass
	
def save(filename):
	pass
	
if (len(sys.argv) < 2):
	print("Please indicate which world needs to be loaded.")
	exit()
else:
	print(sys.argv)
	load(sys.argv[1])

world = World()

offset = 10
gridSize = 20

done = False
pause = True
printTicks = False
def pygameLoop():
	global done
	global pause
	global printTicks
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		elif event.type == pygame.MOUSEBUTTONDOWN:
			pass
		elif event.type == pygame.KEYDOWN:
			#print(str(event.key))
			if (event.key == 27): #Esc
				done = True
			elif (event.key == 112): #P
				pause = not pause
			elif (event.key == 116): #T
				printTicks = not printTicks
			
	screen.fill(WHITE)
	# map grid
	for i in range(17):
		pygame.draw.line(screen, BLACK, [offset, offset + i * gridSize], [offset + 16 * gridSize, offset + i * gridSize])
		pygame.draw.line(screen, BLACK, [offset + i * gridSize, offset], [offset + i * gridSize, offset + 16 * gridSize])
	
	# food coloring
	for y in range(16):
		for x in range(16):
			val = min(30*world.food[y][x], 255)
			pygame.draw.rect(screen, (255, 255, 255-val), [offset + x*gridSize + 1, offset + y*gridSize + 1, gridSize - 1, gridSize - 1])
	
	for i in range(len(world.brains)):
		b = world.brains[i]
		if (b is not None):
			strID = fontSmall.render(str(i), True, BLUE)
			screen.blit(strID, (offset + b.x * gridSize + 3, offset + b.y * gridSize + 3))
			
	#strPoints = font.render("Number of points: " + str(len(points)), True, BLACK)
	#screen.blit(strPoints, (10, 10))
	#pygame.draw.rect(screen, RED, [x-2, y-2, 5, 5])
	#pygame.draw.circle(screen, RED, [x,y], int(worst), 1)
	
	pygame.display.flip()

FPS = 20
delay = 1 / FPS
lastTime = time()
tickCount = 0
while not done:
	if (not pause):
		world.tick()
	if (time() - lastTime > delay):
		tickCount += 1
		if (printTicks):
			print("Tick " + str(tickCount))
		pygameLoop()
		if (pause):
			sleep(delay)
	
save(sys.argv[1])
pygame.quit()