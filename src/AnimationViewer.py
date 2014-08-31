import json, glob
from PIL import Image, ImageTk
import sys
import Tkinter as tk

sys.path.insert(0, "../editor")
import Utils

canvas = None
Lines = None
Trained = None
AnimationPercent = None
StepSize = None
lblAnimationPercent, lblStepSize = None, None
canvasSize = 400
step = 0.1
minStepSize = 1.
maxStepSize = 2.

def fillEditorWindow(window):
	global canvas, canvasSize, lblAnimationPercent, lblStepSize

	window.title("Animation Viewer")

	canvas = tk.Canvas(window)
	canvas.grid(row=0, column=0, columnspan=7)
	canvas.config(width=canvasSize, height=canvasSize)

	tk.Label(window, text="AnimationPercent:").grid(row=1, column=0)
	lblAnimationPercent = Utils.MakeArrowButtons(window, 1, 1, btnPrevAnimationPercentClick, btnNextAnimationPercentClick)

	tk.Label(window, text="Step size:").grid(row=2, column=0)
	lblStepSize = Utils.MakeArrowButtons(window, 2, 1, btnPrevStepSizeClick, btnNextStepSizeClick)

	updateData()
	updateImage()

	window.mainloop()

def btnPrevAnimationPercentClick(event):
	global AnimationPercent, step
	if AnimationPercent > step:
		AnimationPercent -= step

	updateData()
	updateImage()

def btnNextAnimationPercentClick(event):
	global AnimationPercent, step
	if AnimationPercent < 1 - step:
		AnimationPercent += step

	updateData()
	updateImage()

def btnPrevStepSizeClick(event):
	global StepSize, step, minStepSize
	epsilon = 0.01

	if StepSize > minStepSize + step - epsilon:
		StepSize -= step

	updateData()
	updateImage()

def btnNextStepSizeClick(event):
	global StepSize, step, maxStepSize
	epsilon = 0.01

	if StepSize < maxStepSize - step + epsilon:
		StepSize += step

	updateData()
	updateImage()

def updateData():
	global lblStepSize, lblAnimationPercent, StepSize, AnimationPercent
	lblStepSize["text"] = "{0:.1f}".format(StepSize)
	lblAnimationPercent["text"] = "{0:.1f}".format(AnimationPercent)

def computeVertexValue(data):
	global StepSize, AnimationPercent
	x1 = StepSize
	x2 = AnimationPercent
	a, b, c, d, e = data["a"], data["b"], data["c"], data["d"], data["e"]
	return x1 * x1 * a + x1 * b + x2 * x2 * c + x2 * d + e	

def computeVertices():
	global Trained, canvasSize
	vertices = []

	for i in range(len(Trained["x"])):
		x = computeVertexValue(Trained["x"][i]["result"]) * canvasSize / 6 + canvasSize * 2. / 3
		y = computeVertexValue(Trained["y"][i]["result"]) * canvasSize / 6 + canvasSize * 2. / 3
		vertices.append({"x":x, "y":y})

	return vertices

def updateImage():
	global canvas, Lines

	noSelection = -1
	currentImage = None
	vertices = computeVertices()

	Utils.UpdateImage(canvas, 0, 0, vertices, Lines, currentImage, noSelection, noSelection)

def OpenFromFile(window, filename):
	global Lines, Trained, AnimationPercent, StepSize, minStepSize

	AnimationPercent = 0
	StepSize = minStepSize

	f = open(filename)
	data = json.load(f)
	f.close()	

	Lines = data["lines"]
	Trained = data["trained"]

	fillEditorWindow(window)

if __name__ == "__main__":
	OpenFromFile(tk.Tk(), "data/learned.json")



