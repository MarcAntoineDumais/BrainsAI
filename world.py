#TODO: improve efficiency for higher neuron count
#TODO: balance systems
#TODO: make brains pass information when breeding

import sys
from time import time, sleep
import pickle
import pygame
import os.path
from random import random, randint
import brain
pygame.init()
sys.setrecursionlimit(50000)
#Colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

screen = pygame.display.set_mode([800, 600])
pygame.display.set_caption("Genetics AI")
fontVeryBig = pygame.font.Font(None, 120)
fontBig = pygame.font.Font(None, 40)
fontMid = pygame.font.Font(None, 24)
fontSmall = pygame.font.Font(None, 16)

selectedTile = None
selectedBrain = None

def formatID(ID):
	if (ID < 10):
		return '0' + str(ID)
	else:
		return str(ID)

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
		for i in range(1, 33):
			print("Creating brain " + str(i))
			posX = 4 * ((i-1) % 4)
			posY = 4 * ((i-1) % 16 // 4)
			if (i > 16):
				posX += 2
				posY += 2
			self.brains[i] = brain.Brain(posX, posY, self, i)
			self.brains[i].randomize(10)
			self.grid[posY][posX].append(self.brains[i])
		
		self.food = []
		for y in range(16):
			row = [0] * 16
			self.food.append(row)
			
	def tick(self):
		global selectedBrain
		#Food generation
		for y in range(16):
			for x in range(16):
				if (random() < foodSpawnChance):
					self.food[y][x] += 1
		
		#Population limits
		popCount = 0
		for b in self.brains:
			if (b is not None):
				popCount += 1
		while (popCount > 50):
			oldest = -1
			oldestB = None
			for b in self.brains:
				if (b is not None and not b.toKill and b.age > oldest):
					oldest = b.age
					oldestB = b
			oldestB.toKill = True
			print(formatID(oldestB.ID) + " has passed away")
			popCount -= 1
		
		while (popCount < 10):
			b = brain.Brain(randint(0,15), randint(0,15), self, 0)
			b.randomize(10)
			self.newBorn(b)
			print(formatID(b.ID) + " was born from the void")
			popCount += 1
		
		#Updating brains
		for i in range(len(self.brains)):
			b = self.brains[i]
			if (b is not None):
				b.tick()
				if (b.toKill):
					if (b is selectedBrain):
						selectedBrain = None
					self.grid[b.y][b.x].remove(b)
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
		print(formatID(speaker) + " says: " + str(convertedMessage))
				
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
		print(formatID(nextValid) + " was born")

world = None

def load(filename):
	global world
	if (os.path.isfile(filename)):
		with open(filename, 'rb') as infile:
			print("Loading " + filename)
			world = pickle.load(infile)
	else:
		print("File not found. Creating file " + filename)
		world = World()
		with open(filename, 'wb') as outfile:
			pickle.dump(world, outfile, pickle.HIGHEST_PROTOCOL)
	
def save(filename):
	with open(filename, 'wb') as outfile:
			pickle.dump(world, outfile, pickle.HIGHEST_PROTOCOL)
	
if (len(sys.argv) < 2):
	print("Please indicate which world needs to be loaded.")
	print("Usage: python world.py filename")
	exit()
else:
	load(sys.argv[1])


offset = 10
gridSize = 20

done = False
pause = True
printTicks = False
def pygameLoop():
	global done
	global pause
	global printTicks
	global selectedTile
	global selectedBrain
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if (event.button == 1):
				gridX = (event.pos[0] - offset) // gridSize
				gridY = (event.pos[1] - offset) // gridSize
				if (gridX >= 0 and gridX < 16 and gridY >= 0 and gridY < 16):
					if (selectedTile is None or gridX != selectedTile[0] or gridY != selectedTile[1]):
						selectedTile = (gridX, gridY)
				else:
					unselect = True
					if (selectedTile is not None):
						for i in range(len(world.grid[selectedTile[1]][selectedTile[0]])):
							if (event.pos[0] >= offset + 5 and event.pos[0] < offset + 80 and
								event.pos[1] >= offset * 3 + gridSize * 16 + 26 * (i+1) + 19 and
								event.pos[1] < offset * 3 + gridSize * 16 + 26 * (i+1) + 43):
								selectedBrain = world.grid[selectedTile[1]][selectedTile[0]][i]
								unselect = False
							
					if (unselect):
						selectedTile = None
						selectedBrain = None
		elif event.type == pygame.KEYDOWN:
			#print(str(event.key))
			if (event.key == 27): #Esc
				selectedTile = None
				selectedBrain = None
			elif (event.key == 112): #P
				pause = not pause
			elif (event.key == 116): #T
				printTicks = not printTicks
			elif (event.key == 108): #L
				if (selectedTile is not None):
					for b in world.grid[selectedTile[1]][selectedTile[0]]:
						print(b.ID)
			elif (event.key == 111):
				if (selectedBrain is not None):
					selectedBrain.outputInfo()
			
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
			chosenColor = BLUE
			if (b is selectedBrain):
				chosenColor = RED
			strID = fontSmall.render(str(i), True, chosenColor)
			screen.blit(strID, (offset + b.x * gridSize + 4, offset + b.y * gridSize + 4))
			
	# selected cell
	if (selectedTile is not None):
		pygame.draw.rect(screen, RED, [offset + selectedTile[0] * gridSize + 2, offset + selectedTile[1] * gridSize + 2, gridSize - 3, gridSize - 3], 1)
		strFood = fontMid.render("Food on selected tile: " + str(world.food[selectedTile[1]][selectedTile[0]]), True, BLACK)
		screen.blit(strFood, (offset, offset * 2 + gridSize * 16))
		if (len(world.grid[selectedTile[1]][selectedTile[0]]) > 0):
			strBrainsOnTile = fontMid.render("Brains on selected tile:", True, BLACK)
			screen.blit(strBrainsOnTile, (offset, offset * 3 + gridSize * 16 + 24))
			
			for i in range(len(world.grid[selectedTile[1]][selectedTile[0]])):
				curID = world.grid[selectedTile[1]][selectedTile[0]][i].ID
				strSelected = fontMid.render("Brain " + formatID(curID), True, BLUE)
				screen.blit(strSelected, (offset + 10, offset * 3 + gridSize * 16 + 26 * (i+1) + 24))
				if (selectedBrain is not None and selectedBrain.ID == curID):
					pygame.draw.rect(screen, RED, [offset + 5, offset * 3 + gridSize * 16 + 26 * (i+1) + 19, 75, 24], 1)
	
	# population statistics
	totalFood = 0
	for y in range(16):
		for x in range(16):
			totalFood += world.food[y][x]
	
	strFood = fontMid.render("Total food in world: " + str(totalFood), True, BLACK)
	screen.blit(strFood, (offset * 2 + gridSize * 16, offset))
	totalBrains = 0
	for b in world.brains:
		if (b is not None):
			totalBrains += 1
	strBrains = fontMid.render("Amount of living brains: " + str(totalBrains), True, BLACK)
	screen.blit(strBrains, (offset * 2 + gridSize * 16, offset * 2 + 24))
	
	# selected brain
	if (selectedBrain is not None):
		strSelected = fontMid.render("Selected brain: " + formatID(selectedBrain.ID), True, BLUE)
		screen.blit(strSelected, (offset * 2 + gridSize * 16, offset * 3 + 48))
		strSelectedAge = fontMid.render("Age: " + str(round(selectedBrain.age, 4)), True, BLACK)
		screen.blit(strSelectedAge, (offset * 2 + gridSize * 16, offset * 4 + 72))
		strSelectedHunger = fontMid.render("Hunger: " + str(round(selectedBrain.hunger, 4)), True, BLACK)
		screen.blit(strSelectedHunger, (offset * 2 + gridSize * 16, offset * 5 + 96))
	
	# Pause indicator
	if (pause):
		strPause = fontVeryBig.render("Paused", True, (120, 120, 120))
		screen.blit(strPause, (offset + 10, offset + 120))
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