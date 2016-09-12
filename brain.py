import math
from random import random, randint
ticksBetweenPerception = 5
neuronsWeakeningRate = 0.95
signalStrengthToFire = 1
connectionsDecayRate = 0.99
connectionsStrengtheningRate = 1.2
newConnectionChance = 0.1
neuronsCount = 500
hungerRate = 0.001
foodEfficiency = 0.2
agingRate = 0.0001
hungerToBreed = 0.75

def formatID(ID):
	if (ID < 10):
		return '0' + str(ID)
	else:
		return str(ID)

class Neuron:
	def __init__(self, brain, index):
		self.connections = []
		self.signalLevel = 0
		self.state = 0
		self.toAdd = 0
		self.brain = brain
		self.index = index
		
	def fire(self):
		for c in self.connections:
			if (c.neuron.state == 0):
				c.neuron.toAdd += c.strength
			c.changeStrength(min(c.strength * connectionsStrengtheningRate, 1))
		if (random() < newConnectionChance):
			chosenNeuron = None
			while (chosenNeuron is None):
				chosenNeuron = self.brain.neurons[randint(0, len(self.brain.neurons)-1)]
				for c in self.connections:
					if (c.neuron is chosenNeuron):
						chosenNeuron = None
			self.connections.append(Connection(chosenNeuron, 0.5))
			
	def tick(self):
		for c in self.connections:
			c.tick()
			if (c.toKill):
				self.connections.remove(c)
				del c
		
class Connection:
	def __init__(self, neuron, strength):
		self.neuron = neuron
		self.changeStrength(strength)
		self.toKill = False
		
	def changeStrength(self, strength):
		self.strength = strength
		self.destructionChance = 0.1*math.exp(-30*self.strength)
		
	def tick(self):
		self.changeStrength(self.strength * connectionsDecayRate)
		if (random() < self.destructionChance):
			self.toKill = True
		
		
class Brain:
	indexInputSpeech = 0
	sizeInputSpeech = 140
	indexInputRecognition = indexInputSpeech + sizeInputSpeech
	sizeInputRecognition = 6
	indexInputDistance = indexInputRecognition + sizeInputRecognition
	sizeInputDistance = 3
	indexInputPosition = indexInputDistance + sizeInputDistance
	sizeInputPosition = 8	
	indexInputHunger = indexInputPosition + sizeInputPosition
	sizeInputHunger = 1
	indexInputFoodCell = indexInputHunger + sizeInputHunger
	sizeInputFoodCell = 1
	indexInputFoodNearby = indexInputFoodCell + sizeInputFoodCell
	sizeInputFoodNearby = 1
	indexInputPain = indexInputFoodNearby + sizeInputFoodNearby
	sizeInputPain = 1
	numberOfInputNeurons = indexInputPain + sizeInputPain
	
	indexOutputSpeech = 0
	sizeOutputSpeech = 140
	indexOutputSpeechFlush = indexOutputSpeech + sizeOutputSpeech
	sizeOutputSpeechFlush = 1
	indexOutputMoving = indexOutputSpeechFlush + sizeOutputSpeechFlush
	sizeOutputMoving = 4 #UP - DOWN - LEFT - RIGHT
	indexOutputEating = indexOutputMoving + sizeOutputMoving
	sizeOutputEating = 1
	indexOutputBreeding = indexOutputEating + sizeOutputEating
	sizeOutputBreeding = 1
	numberOfOutputNeurons = indexOutputBreeding + sizeOutputBreeding
	
	def outputInfo(self):
		totalNeurons = 0
		totalConnections = 0
		for n in self.inputNeurons:
			totalNeurons += 1
			totalConnections += len(n.connections[0].neuron.connections)
		print(str(totalNeurons) + " neurons with " + str(totalConnections) + " connections")
	
	def __init__(self, posX, posY, world, ID):
		self.tickCount = 0
		self.tickAge = 0
		self.x = posX
		self.y = posY
		self.hunger = 0.5
		self.age = 0
		self.toKill = False
		self.world = world
		self.ID = ID
		
		self.neurons = []
		for i in range(neuronsCount):
			self.neurons.append(Neuron(self, i))
		
		self.inputNeurons = []
		for i in range(Brain.numberOfInputNeurons):
			self.inputNeurons.append(Neuron(self, i))
			self.inputNeurons[i].connections.append(Connection(self.neurons[i], 1))
			
		self.outputNeurons = []
		for i in range(Brain.numberOfOutputNeurons):
			self.outputNeurons.append(Neuron(self, neuronsCount + i))
			self.neurons[Brain.numberOfInputNeurons + i].connections.append(Connection(self.outputNeurons[i], 1))
			
	def randomize(self, intensity):
		for i in range(int(neuronsCount * intensity)):
			start = int(random() * neuronsCount)
			end = start
			while (start == end):
				end = int(random() * neuronsCount)
				
			alreadyThere = False
			for c in self.neurons[start].connections:
				if (c.neuron is self.neurons[end]):
					alreadyThere = True
			if (alreadyThere):
				continue
			
			self.neurons[start].connections.append(Connection(self.neurons[end], 0.5))
		
	def tick(self):
		self.tickAge += 1
		self.hunger += hungerRate
		if (self.hunger >= 1):
			self.toKill = True
			print(formatID(self.ID) + " has died of hunger")
			return
		self.age += agingRate * (3 if self.hunger >= 0.7 else 1)
		if (self.age >= 1):
			self.toKill = True
			print(formatID(self.ID) + " has died of old age")
			return
		if (self.tickCount == 0):
			#world inputs
			#position input
			posX = bin(self.x)[2:]
			while (len(posX) < 4):
				posX = "0" + posX
			posY = bin(self.y)[2:]
			while (len(posY) < 4):
				posY = "0" + posY
			posInput = posX + posY
			for i in range(len(posInput)):
				if (posInput[i] == '1'):
					self.inputNeurons[Brain.indexInputPosition + i].fire()
			#other inputs
			if (self.hunger >= 0.6):
				self.inputNeurons[Brain.indexInputHunger].fire()
			if (self.world.foodOnCell(self.x, self.y)):
				self.inputNeurons[Brain.indexInputFoodCell].fire()
			if (self.world.foodNearby(self.x, self.y)):
				self.inputNeurons[Brain.indexInputFoodNearby].fire()
			if (self.hunger >= 0.9 or self.age >= 0.9):
				self.inputNeurons[Brain.indexInputPain].fire()
				
		self.tickCount = (self.tickCount + 1) % ticksBetweenPerception
		
		for n in self.neurons:
			n.tick()
			if (n.state == 0):
				if (n.signalLevel >= signalStrengthToFire):
					n.fire()
					n.state = 1
					n.signalLevel = 0
				else:
					n.signalLevel *= neuronsWeakeningRate
					
		for n in self.neurons:
			if (n.state == 0):
				n.signalLevel += n.toAdd
				n.toAdd = 0
			else:
				n.state = (n.state + 1) % 3
				
		#world outputs
		for n in self.outputNeurons:
			n.signalLevel += n.toAdd
			n.toAdd = 0
		n = self.outputNeurons[Brain.indexOutputSpeechFlush]
		if (n.signalLevel >= signalStrengthToFire):
			n.signalLevel = 0
			msg = ""
			for i in range(Brain.indexOutputSpeech, Brain.indexOutputSpeech + Brain.sizeOutputSpeech):
				if (self.outputNeurons[i].signalLevel >= signalStrengthToFire):
					msg += '1'
					self.outputNeurons[i].signalLevel = 0
				else:
					msg += '0'
				
			self.world.speak(msg, self.ID, self.x, self.y)
			
		for i in range(4):
			n = self.outputNeurons[Brain.indexOutputMoving + i]
			if (n.signalLevel >= signalStrengthToFire):
				n.signalLevel = 0
				fromX = self.x
				fromY = self.y
				if (i == 0): #UP
					self.y = self.y - 1 if self.y > 0 else 15
				elif (i == 1): #DOWN
					self.y = self.y + 1 if self.y < 15 else 0
				elif (i == 2): #LEFT
					self.x = self.x - 1 if self.x > 0 else 15
				elif (i == 3): #RIGHT
					self.x = self.x + 1 if self.x < 15 else 0
				self.world.move(self.ID, self.x, self.y, fromX, fromY)
				
		n = self.outputNeurons[Brain.indexOutputEating]
		if (n.signalLevel >= signalStrengthToFire):
			n.signalLevel = 0
			if (self.world.eat, self.x, self.y):
				self.hunger -= foodEfficiency
				if (self.hunger < 0):
					self.hunger = 0
			
		n = self.outputNeurons[Brain.indexOutputBreeding]
		if (n.signalLevel >= signalStrengthToFire):
			n.signalLevel = 0
			if (self.hunger < 1 - hungerToBreed):
				self.breed()

	def clearConnections(self):
		for n in self.neurons:
			del n.connections[:]

	def breed(self):
		self.hunger += hungerToBreed
		b = Brain(self.x, self.y, self.world, 0)
		b.clearConnections()
		print(formatID(self.ID) + " had a baby")
		self.world.newBorn(b)
		for i in range(len(self.neurons)):
			for c in self.neurons[i].connections:
				target = None
				if (c.neuron.index < neuronsCount):
					target = b.neurons[c.neuron.index]
				else:
					target = b.outputNeurons[c.neuron.index - neuronsCount]
				b.neurons[i].connections.append(Connection(target, c.strength))
		b.randomize(1)
	
	def hearSpeach(self, message, speaker, posX, posY):
		for i in range(len(message)):
			if (message[i] == '1'):
				self.inputNeurons[Brain.indexInputSpeech + i].fire()
		speaker = bin(speaker)[2:]
		while (len(speaker) < Brain.sizeInputRecognition):
			speaker = '0' + speaker
		for i in range(Brain.sizeInputRecognition):
			if (speaker[i] == '1'):
				self.inputNeurons[Brain.indexInputRecognition + i].fire()
		dx = abs(posX - self.x)
		dx = min(dx, 16 - dx)
		dy = abs(posY - self.y)
		dy = min(dy, 16 - dy)
		dist = dx + dy
		dist = bin(dist)[2:]
		while (len(dist) < Brain.sizeInputDistance):
			dist = '0' + dist
		for i in range(Brain.sizeInputDistance):
			if (dist[i] == '1'):
				self.inputNeurons[Brain.indexInputDistance + i].fire()