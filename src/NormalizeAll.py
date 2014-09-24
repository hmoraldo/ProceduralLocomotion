import copy
import csv
import glob
import json
import math
import numpy
import os.path
from scipy.optimize import curve_fit

from Utils import getJsonData, getVertexByName

allowInterpolatedData = True
alwaysUseArmData = True # it is too sparse otherwise

def parseBoolean(value):
	if value == "1": return True
	if value == "0": return False
	return value

def getCsvProperties(filename):
	f = open(filename)
	reader = csv.reader(f)
	data = [r for r in reader]

	header = data[0]
	data = data[1:]
	data = [{header[i]:parseBoolean(d[i]) for i in range(len(d))} for d in data]
	data = {d["File"]:d for d in data}

	f.close()
	return data


files = glob.glob("../editor/data/*/*.json")
properties = getCsvProperties("../editor/data/properties.csv")

def distance(x, y, x2, y2):
	return math.sqrt(float((x - x2)**2 + (y - y2)**2))

def vertexDistance(v1, v2):
	return distance(v1["x"], v1["y"], v2["x"], v2["y"])

def fitF(x, a, b):
	return a * x + b

def linearRegressionSimple(points):
	x = numpy.array([p["x"] for p in points])
	y = numpy.array([p["y"] for p in points])

	[a, b], cov = curve_fit(fitF, x, y)
	return a, b

# normalizes and prepares all animation data (in place)
def normalizeAnimation(animation, fileProperties):

	vertices, frames = animation["vertices"], animation["frames"]

	# compute vertices to skip
	verticesToSkip = []
	frontArmVertices = ["elbow-front", "wrist-front"]
	backArmVertices = ["elbow-back", "wrist-back"]
	if not fileProperties["Head-vertex-useful"]:
		verticesToSkip.append("head-ear")

	if not alwaysUseArmData:
		if fileProperties["Arms-useful"]:
			if not fileProperties["Both-arms-visible"]:
				if fileProperties["Front-leg-closest-to-camera"]:
					verticesToSkip.extend(backArmVertices)
				else:
					verticesToSkip.extend(frontArmVertices)
		else:
			verticesToSkip.extend(frontArmVertices)
			verticesToSkip.extend(backArmVertices)

	# normalize coordinates using leg - neck size
	legSizes = []
	for frame in frames:
		neck = frame["vertices"][getVertexByName(vertices, "neck")]
		shoulder = frame["vertices"][getVertexByName(vertices, "shoulder")]
		waist = frame["vertices"][getVertexByName(vertices, "waist")]
		kneefront = frame["vertices"][getVertexByName(vertices, "knee-front")]
		kneeback = frame["vertices"][getVertexByName(vertices, "knee-back")]
		footfront = frame["vertices"][getVertexByName(vertices, "foot-front")]
		footback = frame["vertices"][getVertexByName(vertices, "foot-back")]
		footendfront = frame["vertices"][getVertexByName(vertices, "footend-front")]
		footendback = frame["vertices"][getVertexByName(vertices, "footend-back")]
		neckToWaist = vertexDistance(neck, shoulder) + vertexDistance(shoulder, waist)

		legSizes.append(neckToWaist + vertexDistance(waist, kneefront) + vertexDistance(kneefront, footfront) + vertexDistance(footfront, footendfront))
		legSizes.append(neckToWaist + vertexDistance(waist, kneeback) + vertexDistance(kneeback, footback) + vertexDistance(footback, footendback))

	meanLegSize = numpy.mean(legSizes)
	refVertex = getVertexByName(vertices, "reference-floor")

	# rotate by angle of ref vertex
	refFramePoints = []
	for frame in frames:
		refFramePoints.append(frame["vertices"][refVertex])
	a, b = linearRegressionSimple(refFramePoints)	
	angle = -math.atan(a) # angle to rotate backwards

	if abs(refFramePoints[0]["x"] - refFramePoints[-1]["x"]) < 50:
		angle = 0

	rotMat = numpy.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])

	# invert if needed, such that in first frame, front leg x > back leg x
	inverter = 1
	footfrontX = frames[0]["vertices"][getVertexByName(vertices, "foot-front")]["x"]
	footbackX = frames[0]["vertices"][getVertexByName(vertices, "foot-back")]["x"]
	if footbackX > footfrontX:
		inverter = -1


	# final normalization
	animationPercent = 0.

	for frame in frames:
		refX = frame["vertices"][refVertex]["x"]
		refY = frame["vertices"][refVertex]["y"]

		frame["animationPercent"] = animationPercent
		animationPercent += 1. / (len(frames) - 1)

		for vi in range(len(frame["vertices"])):
			vertex = frame["vertices"][vi]

			x = (vertex["x"] - refX) / meanLegSize
			y = (vertex["y"] - refY) / meanLegSize

			p = numpy.array([[x, y]]).T
			[[x], [y]] = numpy.dot(rotMat, p)

			if vertices[vi]["name"] in verticesToSkip:
				vertex["x"] = None
				vertex["y"] = None
			else:
				vertex["x"] = inverter * x
				vertex["y"] = y

	# calculate step distance parameter on normalized values
	backFootEnd = getVertexByName(vertices, "footend-back")
	animation["stepWidth"] = abs(frames[0]["vertices"][backFootEnd]["x"] - frames[-1]["vertices"][backFootEnd]["x"])

# our training data may be too sparse... if allowInterpolatedData is True, we interpolate between frames to provide the training algorithm
# with more data of how the animations work
def addInterpolatedData(animation):
	newFrames = []
	frames = animation["frames"]

	for i in range(len(frames) - 1):
		frame1 = frames[i]
		frame2 = frames[i + 1]

		newf = {
			"animationPercent" : numpy.mean([frame1["animationPercent"], frame2["animationPercent"]]),
			"vertices" : []
		}

		for vidx in range(len(frame1["vertices"])):
			newf["vertices"].append(copy.deepcopy(frame1["vertices"][vidx]))
			for coordinate in ["x", "y"]:
				meanValue = None
				if frame1["vertices"][vidx][coordinate] != None:
					meanValue = numpy.mean([frame1["vertices"][vidx][coordinate], frame2["vertices"][vidx][coordinate]])

				newf["vertices"][vidx][coordinate] = meanValue

		newFrames.append(newf)

	frames.extend(newFrames)

initialData = getJsonData(files[0])
finalData = {"vertices" : initialData["vertices"], "lines" : initialData["lines"], "frames" : []}

minStepWidth = 10000
maxStepWidth = 0

for filename in files:
	data = getJsonData(filename)

	fileProperties = properties[os.path.basename(os.path.splitext(filename)[0])]

	normalizeAnimation(data, fileProperties)
	if allowInterpolatedData: addInterpolatedData(data)

	minStepWidth = min(data["stepWidth"], minStepWidth)
	maxStepWidth = max(data["stepWidth"], maxStepWidth)

	for frame in data["frames"]:
		newFrame = {"animationPercent":frame["animationPercent"], "stepWidth":data["stepWidth"]}
		newFrame["vertices"] = frame["vertices"]
		finalData["frames"].append(newFrame)


f = open("data/normalized.json", "w")
json.dump(finalData, f)
f.close()

f = open("data/stepWidth.json", "w")
json.dump({"minStepWidth":minStepWidth, "maxStepWidth":maxStepWidth}, f)
f.close()


print "minStepWidth: " + str(minStepWidth)
print "maxStepWidth: " + str(maxStepWidth)
