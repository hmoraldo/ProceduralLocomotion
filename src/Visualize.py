import csv
import glob
import json
import math
import numpy
import os.path
from scipy.optimize import curve_fit

from Utils import getJsonData

import Image, ImageDraw

normalized = getJsonData("../data/results/normalized.json")

imgsize = 500
img = Image.new("RGB", (imgsize, imgsize), "black")
draw = ImageDraw.Draw(img)

for frame in normalized["frames"]:
	# show a single frame
	if frame["animationPercent"] < 1:
		continue

	for vertex in frame["vertices"]:
		color = "blue"
		if vertex["name"] == "knee-front":
			color = "green"
		if vertex["name"] == "foot-front":
			color = "yellow"
		if vertex["name"] == "waist":
			color = "red"
		if vertex["name"] == "shoulder":
			color = "brown"
		if vertex["name"] == "foot-back":
			color = "white"

		if vertex["x"] != None and vertex["y"] != None:
			draw.point((vertex["x"] * imgsize / 3. + imgsize / 2, vertex["y"] * imgsize / 3. + imgsize / 1.5), fill=color)


img.show()


