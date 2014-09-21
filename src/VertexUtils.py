import json

def getJsonData(filename):
	f = open(filename)
	data = json.load(f)
	f.close()
	return data

def getVertexByName(vertices, name):
	for c in range(len(vertices)):
		if vertices[c]["name"] == name:
			return c
	return None

def computeVertexValue(data, stepSize, animationPercent):
	x1 = stepSize
	x2 = animationPercent
	a, b, c, d, e = data["a"], data["b"], data["c"], data["d"], data["e"]
	return x1 * x1 * a + x1 * b + x2 * x2 * c + x2 * d + e	

def computeVertices(trainedData, stepSize, animationPercent):
	vertices = []

	for i in range(len(trainedData["x"])):
		x = computeVertexValue(trainedData["x"][i]["result"], stepSize, animationPercent)
		y = computeVertexValue(trainedData["y"][i]["result"], stepSize, animationPercent)
		vertices.append({"x":x, "y":y})

	return vertices

def scaleVertices(vertices, scale):
	return [{"x":v["x"]*scale, "y":v["y"]*scale} for v in vertices]

def translateVertices(vertices, x, y):
	return [{"x":v["x"] + x, "y":v["y"] + y} for v in vertices]


