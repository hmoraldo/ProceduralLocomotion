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

	# invert front foot and back foot, etc.
	def invertFrontAndBack(self, vertices):
		def exchangeVertexData(name1, name2):
			index1 = getVertexIndex(self.trained, name1)
			index2 = getVertexIndex(self.trained, name2)

			for c in ["x", "y"]:
				vertices[index1][c], vertices[index2][c] = vertices[index2][c], vertices[index1][c]

		exchangeVertexData("foot-front", "foot-back")
		exchangeVertexData("footend-front", "footend-back")
		exchangeVertexData("knee-front", "knee-back")
		exchangeVertexData("elbow-front", "elbow-back")
		exchangeVertexData("wrist-front", "wrist-back")

	def getVerticesAtFrame(self, frame, refVertexX, invertFrontAndBack):
		vertices = VertexUtils.computeVertices(self.trained, self.StepArgument, frame % 1)
		vertices = VertexUtils.translateVertices(vertices, refVertexX, 0)
		if invertFrontAndBack:
			self.invertFrontAndBack(vertices)
		return vertices

	def getNextVertices(self, invertFrontAndBack):
		return self.getVerticesAtFrame(0, self.refVertexX + self.stepLength, invertFrontAndBack)

	def moveForward(self, percent):
		lastIntFrame = math.floor(self.currentFrame)
		self.currentFrame += percent

		self.refVertexX += (math.floor(self.currentFrame) - lastIntFrame) * self.stepLength

		for i in range(int(math.floor(self.currentFrame) - lastIntFrame)):
			self.frontLeftFirst = not self.frontLeftFirst

	def getVertices(self):
		vertices = self.getVerticesAtFrame(self.currentFrame, self.refVertexX, not self.frontLeftFirst)

		frameLerpStart = 0.6 # at what frame we start interpolating
		if self.currentFrame % 1 >= frameLerpStart:
			nextVertices = self.getNextVertices(self.frontLeftFirst)

			vertices = VertexUtils.lerpVertices(vertices, nextVertices, ((self.currentFrame % 1) - frameLerpStart) / (1 - frameLerpStart))

		return vertices



StepArgument = 0.55
StepArgument = 1.25
width, height = 800, 300

MinStepArgument, MaxStepArgument, Lines, Trained = loadData("../data/results/learned.json", "../data/results/stepWidth.json")

walker = SimpleWalker(Trained, StepArgument)
refVertexIndex = getVertexIndex(Trained, "reference-floor")

stepCount = 10
stepIncrement = 0.1

for i in range(int(math.ceil(stepCount / stepIncrement))):
	walker.moveForward(stepIncrement)
	vertices = walker.getVertices()
	vertices = VertexUtils.translateVertices(
		VertexUtils.scaleVertices(vertices, height / 4),
		width / 10,
		height * 2. / 3)

	im = Utils.DrawFrame(None, width, height, 0, 0, vertices, Lines, None, None, refVertexIndex)
	im.save("imgs/frame" + format(i, "03") + ".jpg")


subprocess.call(["convert", "-delay", "5", "-loop", "0", "../img/frame*.jpg", "../img/animation.gif"])


