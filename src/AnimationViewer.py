import json, glob
import sys
import Tkinter as tk

import VertexUtils
sys.path.insert(0, "../editor")
import Utils

canvas = None
Lines = None
Trained = None
AnimationPercent = None
StepSize = None
lblAnimationPercent, lblStepSize = None, None
canvasSize = 400
step = 0.03
minStepSize = None
maxStepSize = None

def fillEditorWindow(window):
	global canvas, canvasSize, lblAnimationPercent, lblStepSize

	window.title("Animation Viewer")

	window.bind("<Left>", btnPrevAnimationPercentClick)
	window.bind("<Right>", btnNextAnimationPercentClick)
	window.bind("<Up>", btnNextStepSizeClick)
	window.bind("<Down>", btnPrevStepSizeClick)

	canvas = tk.Canvas(window)
	canvas.grid(row=0, column=0, columnspan=7)
	canvas.config(width=canvasSize, height=canvasSize)

	tk.Label(window, text="AnimationPercent:").grid(row=1, column=0)
	lblAnimationPercent = Utils.MakeArrowButtons(window, 1, 1, btnPrevAnimationPercentClick, btnNextAnimationPercentClick)

	tk.Label(window, text="Step size:").grid(row=2, column=0)
	lblStepSize = Utils.MakeArrowButtons(window, 2, 1, btnPrevStepSizeClick, btnNextStepSizeClick)

	window.update()

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

def updateImage():
	global canvas, Lines
	global Trained, canvasSize, StepSize, AnimationPercent

	noSelection = -1
	currentImage = None
	vertices = VertexUtils.computeVertices(Trained, StepSize, AnimationPercent)
	vertices = VertexUtils.translateVertices(VertexUtils.scaleVertices(vertices, canvasSize / 4), canvasSize * 2. / 3, canvasSize * 2. / 3)

	Utils.UpdateImage(canvas, 0, 0, vertices, Lines, currentImage, noSelection, noSelection)

def OpenFromFile(window, filename):
	global Lines, Trained, AnimationPercent, StepSize, minStepSize, maxStepSize

	AnimationPercent = 0

	data = VertexUtils.getJsonData(filename)
	stepWidth = VertexUtils.getJsonData("data/stepWidth.json")

	minStepSize = stepWidth["minStepWidth"]
	maxStepSize = stepWidth["maxStepWidth"]
	StepSize = minStepSize

	Lines = data["lines"]
	Trained = data["trained"]

	fillEditorWindow(window)

if __name__ == "__main__":
	OpenFromFile(tk.Tk(), "data/learned.json")



