import copy
import json
import Tkinter as tk
from PIL import Image, ImageDraw, ImageTk

def MakeArrowButtons(window, row, col, leftHandler, rightHandler):
	btnLeft = tk.Button(window, text="<")
	btnLeft.grid(row=row, column=col)
	btnLeft.bind("<ButtonRelease-1>", leftHandler)

	lblVertex = tk.Label(window)
	lblVertex.grid(row=row, column=col+1)

	btnRight = tk.Button(window, text=">")
	btnRight.grid(row=row, column=col+2)
	btnRight.bind("<ButtonRelease-1>", rightHandler)

	return lblVertex

def DrawFrame(currentImage, width, height, originX, originY, vertices, lines, currentVertex, currentLine, skipVertex):

	if currentImage == None:
		im = Image.new('RGBA', (width, height), (150, 150, 150, 0)) 
	else:
		im = Image.open(currentImage)

	draw = ImageDraw.Draw(im) 

	radius = 3
	for c in range(len(vertices)):
		v = vertices[c]
		color = "black"
		if c == currentVertex:
			color = "red"

		if skipVertex != c:
			draw.ellipse((
				v["x"] - radius + originX,
				v["y"] - radius + originY,
				v["x"] + radius + originX,
				v["y"] + radius + originY), fill=color)

	for c in range(len(lines)):
		l = lines[c]
		color = l["color"]
		width = 1
		if c == currentLine:
			width = 2

		draw.line((
			vertices[lines[c]["from"]]["x"] + originX,
			vertices[lines[c]["from"]]["y"] + originY,
			vertices[lines[c]["to"]]["x"] + originX,
			vertices[lines[c]["to"]]["y"] + originY,
			), fill=color, width=width)

	return im


def UpdateImage(canvas, originX, originY, vertices, lines, currentImage, currentVertex, currentLine):
	canvas.delete(tk.ALL)
	canvas.image = ImageTk.PhotoImage(
		DrawFrame(currentImage, canvas.winfo_width(), canvas.winfo_height(), originX, originY, vertices, lines, currentVertex, currentLine, None))
	canvas.create_image(0, 0, image=canvas.image, anchor=tk.NW)

def Save(fileName, imageGlob, vertices, lines, frames):
	data = {"imageGlob" : imageGlob, "vertices" : vertices, "lines" : lines, "frames" : frames}
	f = open(fileName, "w")
	json.dump(data, f, indent=4)
	f.close()

def NewVertex():
	return {"x" : 0, "y" : 0, "name" : ""}

def NewLine(vertices):
	toVertex = 0
	if len(vertices) > 1:
		toVertex = 1
	return {"from" : 0, "to" : toVertex, "color" : "black"}

def NewFrame(frames):
	if len(frames) == 0:
		# by default, any vertex not in the list of vertices has coordinates 
		# that are equal to the base vertex at the same index
		return {"vertices" : [], "name" : ""}
	return copy.deepcopy(frames[-1])



