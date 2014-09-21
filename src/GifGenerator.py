import json, glob, math, sys
from PIL import Image, ImageDraw
import subprocess

import VertexUtils
sys.path.insert(0, "dep")
import Utils

def loadData(datafile, stepfile):
	data = VertexUtils.getJsonData(datafile)
	stepWidth = VertexUtils.getJsonData(stepfile)
	
	MinStepArgument = stepWidth["minStepWidth"]
	MaxStepArgument = stepWidth["maxStepWidth"]

	Lines = data["lines"]
	Trained = data["trained"]

	return MinStepArgument, MaxStepArgument, Lines, Trained

def getVertexIndex(trained, name):
	tx = trained["x"]
	for idx in range(len(tx)):
		if tx[idx]["vertex"] == name:
			return idx

	return None

class SimpleWalker:
	trained = None # trained model
	StepArgument = None # this is the step size value (from 0 - 1) that is used to train the data
	stepLength = None # this is the actual length of a step in pixels

	refVertexX = 0 # pos of reference vertex
	currentFrame = 0 # current frame from 0 - 1
	frontLeftFirst = True # if false, leg and arm vertices need to be swapped

	def __init__(self, trained, StepArgument):
		self.trained = trained
		self.StepArgument = StepArgument
		self.setStepLength()

	def setStepLength(self):
		indexFootFront = getVertexIndex(self.trained, "foot-front")
		indexFootBack = getVertexIndex(self.trained, "foot-back")

		vertices0 = VertexUtils.computeVertices(self.trained, self.StepArgument, 0)
		vertices1 = VertexUtils.computeVertices(self.trained, self.StepArgument, 1)

		# reference vertex is the closest to the front foot; we estimate that the next place to put such
		# vertex is near the back foot after a full step was completed (which is when the back foot becomes
		# front foot again)
		self.stepLength = vertices1[indexFootBack]["x"] - vertices0[indexFootFront]["x"]

	def moveForward(self, percent):
		lastIntFrame = math.floor(self.currentFrame)
		self.currentFrame += percent
		self.refVertexX += (math.floor(self.currentFrame) - lastIntFrame) * self.stepLength

	def getVertices(self):
		vertices = VertexUtils.computeVertices(self.trained, self.StepArgument, self.currentFrame % 1)
		return VertexUtils.translateVertices(vertices, self.refVertexX, 0)



StepArgument = 0.6
width, height = 800, 300

MinStepArgument, MaxStepArgument, Lines, Trained = loadData("../data/results/learned.json", "../data/results/stepWidth.json")

walker = SimpleWalker(Trained, StepArgument)

for i in range(40):
	walker.moveForward(0.1)
	vertices = walker.getVertices()
	vertices = VertexUtils.translateVertices(
		VertexUtils.scaleVertices(vertices, height / 4),
		width * 2. / 3,
		height * 2. / 3)

	im = Utils.DrawFrame(None, width, height, 0, 0, vertices, Lines, None, None)
	im.save("../img/frame" + format(i, "03") + ".jpg")


subprocess.call(["convert", "-delay", "5", "-loop", "0", "../img/frame*.jpg", "../img/animation.gif"])


"""
next:
- agregar metodos en simple walker
- simple walker deberia tener un init que prepara las variables, y recibir enre otros, al trained model


funciones:
- increment frame
	- pertenece a sig frame?
		- si si, pasar al otro objeto
		- si no, calcular pos de todos los vertices, calcular next ref if needed, hacer blend
- compute next ref frame
- blend
- compute single frame

main
- compute varios frames a distintas velocidades o mezclandolos
- hacer gif con resultado
- agregar que la camara tenga un foco central

todo:
- agregar link a video del que saque el screenshot, o cambiarlo por otro

"""



