import math
import os
import sys
import plotlib
from PIL import Image
from sys import stdout 

file_path = os.path.join(os.path.dirname(__file__), sys.argv[1])
filename = sys.argv[2]

im = Image.open(file_path)
im = im.convert('RGB')
pixel = im.load()
output_path = os.path.join(os.path.dirname(__file__), "output/")

show_przss1 = True
show_przss2 = True
show_przss3 = True

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

print "converting image to black&white..."

for j in range(size_y):
	for i in range(size_x): 
		pixelRGB = pixel[i,j]
		tmp = int((math.sqrt(math.pow(pixelRGB[0],2)+math.pow(pixelRGB[1],2)+math.pow(pixelRGB[2],2)))/precalc*255) 
		pixel[i,j] = (setPixel(tmp),setPixel(tmp),setPixel(tmp))
		if show_przss1:
			plotL(i,j,setPixel(tmp),setPixel(tmp),setPixel(tmp),False)
	print "converting: %.2f%s\r" %(100*(float(j+1))/size_y,"%      "),
	stdout.flush()
	plotter.show()

print "converting complete!"

im.save(output_path+filename+'_BW', format="png")

edge = (255,0,0)
edgeList = []
joined_pixel = (0,0,255)
white = (255,255,255)

print "searching for edges..." 
for j in range(size_y):
	for i in range(size_x): 
		if i < size_x-1:
			this_pixel = pixel[i,j]
			next_pixel = pixel[i+1,j]
			if not this_pixel[1] ==  next_pixel[1]: 
				if this_pixel==white and not next_pixel==edge:
					edgePos = (i+1,j)
					pixel[edgePos] = edge
					edgeList.append(edgePos) 
					if show_przss2:
						plotL(i+1,j,255,0,0,False)
				elif next_pixel==white and not this_pixel==edge:
					edgePos = (i,j)
					pixel[edgePos] = edge
					edgeList.append(edgePos) 
					if show_przss2:
						plotL(i,j,255,0,0,False)
	print "%s %.1f%s\r" %(len(edgeList),(float(j+1)/size_y)*50,"%             "),
	stdout.flush()
	plotter.show()

for j in range(size_x):
	for i in range(size_y): 
		if i < size_y-1:
			this_pixel = pixel[j,i]
			next_pixel = pixel[j,i+1]
			if not this_pixel[1] ==  next_pixel[1]: 
				if this_pixel==white and not next_pixel==edge:
					edgePos = (j,i+1)
					pixel[edgePos] = edge
					edgeList.append(edgePos)
					if show_przss2:
						plotL(j,i+1,255,0,0,False)
				elif next_pixel==white and not this_pixel==edge:
					edgePos = (j,i)
					pixel[edgePos] = edge
					edgeList.append(edgePos)
					if show_przss2:
						plotL(j,i,255,0,0,False)
	print "%s %.1f%s\r" %(len(edgeList),(float(j+1)/size_x)*50+50,"%          "),
	stdout.flush()
	plotter.show()

print "found edges: %s" %(len(edgeList))
print "creating path..."

stdout.flush()

def testIndex(x,y):
	if x == -1 or y == -1 or x == size_x or y == size_y:
		return False
	else:
	 	return True

def searchPath(x,y):
	pixel[x,y] = joined_pixel
	blubb = True
	while(1):
		edgeList.remove((x,y))
		if testIndex(x+1,y+1):
			px = pixel[x+1,y+1]
			if px == edge:
				pixel[x,y] = joined_pixel
				if show_przss3:
					plotL(x,y,0,0,255,False)
				x = x+1
				y = y+1
				continue
	
		if testIndex(x+1,y-1):	
			px = pixel[x+1,y-1]
			if px == edge:
				pixel[x,y] = joined_pixel
				if show_przss3:
					plotL(x,y,0,0,255,False)
				x = x+1
				y = y-1
				continue

		if testIndex(x-1,y+1):
			px = pixel[x-1,y+1]
			if px == edge:
				pixel[x,y] = joined_pixel
				if show_przss3:
					plotL(x,y,0,0,255,False)
				x = x-1
				y = y+1
				continue

		if testIndex(x-1,y-1):
			px = pixel[x-1,y-1]
			if px == edge:
				pixel[x,y] = joined_pixel

				if show_przss3:
					plotL(x,y,0,0,255,False)
				x = x-1
				y = y-1
				continue
	
		if testIndex(x+1,y):
			px = pixel[x+1,y]
			if px == edge:
				pixel[x,y] = joined_pixel
				if show_przss3:
					plotL(x,y,0,0,255,False)
				x = x+1
				y = y
				continue
	
		if testIndex(x-1,y):
			px = pixel[x-1,y]
			if px == edge:
				pixel[x,y] = joined_pixel
				if show_przss3:
					plotL(x,y,0,0,255,False)
				x = x-1
				y = y
				continue
	
		if testIndex(x,y+1):
			px = pixel[x,y+1]
			if px == edge:
				pixel[x,y] = joined_pixel
				if show_przss3:
					plotL(x,y,0,0,255,False)
				x = x
				y = y+1
				continue
	
		if testIndex(x,y-1):
			px = pixel[x,y-1]
			if px == edge:
				pixel[x,y] = joined_pixel
				if show_przss3:
					plotL(x,y,0,0,255,False)
				x = x
				y = y-1
				continue
		return x,y 

def seachNextEdge(x,y):
	nearestEdge = edgeList[0]
	distance = math.sqrt(math.pow(nearestEdge[0]-x,2)+math.pow(nearestEdge[0]-y,2)) 
	for i in edgeList:
		newDistance = math.sqrt(math.pow(i[0]-x,2)+math.pow(i[1]-y,2))
		if newDistance < distance:
			distance = newDistance
			nearestEdge = i
	return nearestEdge
		
lastPath = (0,0)
totalLen = len(edgeList)
while len(edgeList) > 0:
	nextPath = seachNextEdge(lastPath[0],lastPath[1])
	lastPath = searchPath(nextPath[0],nextPath[1])
	print "remaining edges: %s %.1f%s\r" %(len(edgeList),100-100*(len(edgeList)+0.001)/totalLen,"%    "),
	stdout.flush()
	if show_przss3:
		plotter.show()


print "remaining edges: %s 100%s" %(len(edgeList),"%   ") 
	
im.save(output_path+filename, format="png")

print "Done :3"
print "Press any key to exit."

raw_input()







