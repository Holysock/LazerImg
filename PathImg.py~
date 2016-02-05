import math
import os
import sys
import plotlib
from PIL import Image

file_path = os.path.join(os.path.dirname(__file__), sys.argv[1])
filename = sys.argv[2]

im = Image.open(file_path)
im = im.convert('RGB')
pixel = im.load()
output_path = os.path.join(os.path.dirname(__file__), "output/")


size_x = int(im.size[0])
size_y = int(im.size[1])

renderScale = int(sys.argv[4])

plotter = plotlib.plot(size_x/renderScale,size_y/renderScale)
plotter.setBackground(0,0,0)

threshold = float(sys.argv[3]) # between 0 and 255

if(threshold >= 255):
	threshold = 255
elif(threshold <= 0):
	threshold = 0

def setPixel(value):
	if value >= threshold:
		return 255
	else:
		return 0

def plotL(x,y,r,g,b,s):
	plotter.setColor(r,g,b)
	plotter.plotdot(x/renderScale,y/renderScale)
	if(s):
		plotter.show()
		

precalc = math.sqrt(math.pow(255,2)+math.pow(255,2)+math.pow(255,2)) #precalculation of the length of an 3 dimensional RGB-color vector (255,255,255) - white

for j in range(size_y):
	for i in range(size_x): 
		pixelRGB = pixel[i,j]
		tmp = int((math.sqrt(math.pow(pixelRGB[0],2)+math.pow(pixelRGB[1],2)+math.pow(pixelRGB[2],2)))/precalc*255) 
		pixel[i,j] = (setPixel(tmp),setPixel(tmp),setPixel(tmp))
		plotL(i,j,setPixel(tmp),setPixel(tmp),setPixel(tmp),False)
	plotter.show()


edge = (255,0,0)
joined_pixel = (0,0,255)

for j in range(size_y):
	for i in range(size_x): 
		if i < size_x-1:
			this_pixel = pixel[i,j]
			next_pixel = pixel[i+1,j]
			if not (this_pixel[1] ==  next_pixel[1]): 
				if this_pixel[1] == 255:
					pixel[i+1,j]=(255,0,0)
					plotL(i+1,j,255,0,0,False)
				elif next_pixel[1] == 255:
					pixel[i,j]=(255,0,0)
					plotL(i,j,255,0,0,False)
	plotter.show()

for j in range(size_x):
	for i in range(size_y): 
		if i < size_y-1:
			this_pixel = pixel[j,i]
			next_pixel = pixel[j,i+1]
			if not (this_pixel[1] ==  next_pixel[1]): 
				if this_pixel[1] == 255:
					pixel[j,i+1]=(255,0,0)
					plotL(j,i+1,255,0,0,False)
				elif next_pixel[1] == 255:
					pixel[j,i]=(255,0,0)
					plotL(j,i,255,0,0,False)
	plotter.show()

def testIndex(x,y):
	if x == -1 or y == -1 or x == size_x or y == size_y:
		return False
	else:
	 	return True

def searchPath(x,y):
	pixel[x,y] = joined_pixel
	blubb = True
	while(blubb):
		if testIndex(x+1,y+1):
			px = pixel[x+1,y+1]
			if px == edge:
				print 'a'
				pixel[x,y] = joined_pixel
				plotL(x,y,0,0,255,True)
				x = x+1
				y = y+1
				continue
	
		if testIndex(x+1,y-1):	
			px = pixel[x+1,y-1]
			if px == edge:
				print 'b'
				pixel[x,y] = joined_pixel
				plotL(x,y,0,0,255,True)
				x = x+1
				y = y-1
				continue

		if testIndex(x-1,y+1):
			px = pixel[x-1,y+1]
			if px == edge:
				print 'c'
				pixel[x,y] = joined_pixel
				plotL(x,y,0,0,255,True)
				x = x-1
				y = y+1
				continue

		if testIndex(x-1,y-1):
			px = pixel[x-1,y-1]
			if px == edge:
				print 'd'
				pixel[x,y] = joined_pixel
				plotL(x,y,0,0,255,True)
				x = x-1
				y = y-1
				continue
	
		if testIndex(x+1,y):
			px = pixel[x+1,y]
			if px == edge:
				print 'e'
				pixel[x,y] = joined_pixel
				plotL(x,y,0,0,255,True)
				x = x+1
				y = y
				continue
	
		if testIndex(x-1,y):
			px = pixel[x-1,y]
			if px == edge:
				print 'f'
				pixel[x,y] = joined_pixel
				plotL(x,y,0,0,255,True)
				x = x-1
				y = y
				continue
	
		if testIndex(x,y+1):
			px = pixel[x,y+1]
			if px == edge:
				print 'g'
				pixel[x,y] = joined_pixel
				plotL(x,y,0,0,255,True)
				x = x
				y = y+1
				continue
	
		if testIndex(x,y-1):
			px = pixel[x,y-1]
			if px == edge:
				print 'h'
				pixel[x,y] = joined_pixel
				plotL(x,y,0,0,255,True)
				x = x
				y = y-1
				continue
		blubb = False

for j in range(size_y):
	for i in range(size_x): 
		if pixel[i,j] == edge:
			searchPath(i,j)

im.save(output_path+filename, format="png")

print 'done :3'

while(1):
	pass








