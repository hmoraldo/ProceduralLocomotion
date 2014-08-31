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


