import copy
import json
import numpy
from scipy.optimize import curve_fit

from Utils import getJsonData, getVertexByName

verbose = False

def fitSingleF(x1, x2, a, b, c, d, e):
	return x1 * x1 * a + x1 * b + x2 * x2 * c + x2 * d + e

def fitF(x, a, b, c, d, e):
	ret = [fitSingleF(x[0], x[1], a, b, c, d, e) for x in x]
	return ret

def linearRegression(x, y):
	x = numpy.array(x)
	y = numpy.array(y)

	res, cov = curve_fit(fitF, x, y)
	return res

def splitIntoTrainingAndTest(frames):
	trainingProportion = .75
	trainingSize = int(trainingProportion * len(frames))
	frames2 = copy.deepcopy(frames)
	return frames2[:trainingSize], frames2[trainingSize:]

def framesToDataset(frames, vertexIdx, vertexCoordinate):
	x = [[frame["stepWidth"], frame["animationPercent"]] for frame in frames]
	y = [frame["vertices"][vertexIdx][vertexCoordinate] for frame in frames]

	return x, y

def getFitError(x, y, a, b, c, d, e):
	err = [abs(z) for z in (numpy.array(fitF(x, a, b, c, d, e)) - numpy.array(y))]
	minerr = min(err)
	maxerr = max(err)
	meanerr = numpy.mean(err)
	return minerr, maxerr, meanerr

def learnVertex(vertexIdx, vertexCoordinate):
	frameSel = [frame for frame in data["frames"] if frame["vertices"][vertexIdx][vertexCoordinate] != None]

	framesTraining, framesTesting = splitIntoTrainingAndTest(frameSel)

	xTrain, yTrain = framesToDataset(framesTraining, vertexIdx, vertexCoordinate)
	xTest, yTest = framesToDataset(framesTesting, vertexIdx, vertexCoordinate)

	ret = linearRegression(xTrain, yTrain)

	a, b, c, d, e = ret

	trainMinErr, trainMaxErr, trainMeanErr = getFitError(xTrain, yTrain, a, b, c, d, e)
	testMinErr, testMaxErr, testMeanErr = getFitError(xTest, yTest, a, b, c, d, e)

	return {
		"a" : ret[0], "b" : ret[1], "c" : ret[2], "d" : ret[3], "e" : ret[4],
		"trainingError" : {"minerr" : trainMinErr, "maxerr" : trainMaxErr, "meanerr" : trainMeanErr},
		"testingError" : {"minerr" : testMinErr, "maxerr" : testMaxErr, "meanerr" : testMeanErr}
		}


data = getJsonData("../data/results/normalized.json")

result = {"x":[], "y":[]}
allMeans = {"testing":[], "training":[]}

for i in range(len(data["vertices"])):
	for coordinate in ["x", "y"]:
		name = data["vertices"][i]["name"]
		ret = learnVertex(i, coordinate)
		result[coordinate].append({"vertex" : name, "result" : ret})

		if verbose: print name + ":"
		for t in ["testing", "training"]:
			err = ret[t + "Error"]
			allMeans[t].append(err["meanerr"])
			if verbose:
				print "\t" + t + " minerr: " + str(err["minerr"])
				print "\t" + t + " maxerr: " + str(err["maxerr"])
				print "\t" + t + " meanerr: " + str(err["meanerr"])

for t in ["testing", "training"]:
	print
	print "all " + t + " means:"
	print allMeans[t]
	print "min mean:"
	print min(allMeans[t])
	print "max mean:"
	print max(allMeans[t])

finalData = {"lines":data["lines"], "trained":result}

f = open("../data/results/learned.json", "w")
json.dump(finalData, f)
f.close()

