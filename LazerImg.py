#Author: Nick Sidney Lemberger
#Last edit: 17:24 2/2/2016

#Simple tool to generate G-Code from images / bitmaps
# Z-axis is used for direct TTL control of the laser (8-bit PWM or 8-bit Digital-Analog-Converter)  

#Usage (on linux): python LazerImg.py [path-to-image.file-extension] [name-of-resulting-gcode-file(without file extension)] [scale-factor][offset-x][offset-y][feedrate][laser-scale-factor]

#NEW: Optimized paths
#next step: friends to friends analysis 

import math 
import sys  
import os
from PIL import Image
from sys import stdout 
print "parameters: path, filename, px_scale, offset_x, offset_y, feedrate_max, laser_scale"

file_path = os.path.join(os.path.dirname(__file__), sys.argv[1])
filename = sys.argv[2]
pixelScale = float(sys.argv[3]) # to scale the pixels of the image in mm. 1.0 -> 1 pixel/mm

im = Image.open(file_path)
im = im.convert('RGB')
pixel = im.load()

output_path = os.path.join(os.path.dirname(__file__), "output/")

size_x = int(im.size[0])
size_y = int(im.size[1])

print "pixel: %spx x %spx" %(size_x,size_y)
print "size: %smm x %smm" %(size_x*pixelScale,size_y*pixelScale)

target = open(output_path+filename+'.nc','w')
target.seek(0)

offset_x = float(sys.argv[4]) #in mm
offset_y = float(sys.argv[5])
feedrate = float(sys.argv[6]) #in mm/s. note: change to dynamic feedrate variation later 

laserScale = float(sys.argv[7]) # Value between 0 and 1

if laserScale > 1:
	laserScale = 1
elif laserScale < 0:
	laserScale = 0

def setFr(value):
	if(value <= 10):
		return feedrate*2
	elif(value <= 127):
		return feedrate
	else:
		return feedrate - feedrate*((float(value)-128)/127)*0.5

	#Head of Gcode
target.write('#############################################################\n')
target.write('###########Gcode generated with LazerImg.py V0.1#############\n')
target.write('######written by Nick Sidney Lemberger aka Holysocks#########\n')
target.write('#############################################################\n\n')
target.write('%s\n' %(filename))
target.write('laser_engraver(diode, 445nm)\n')
target.write('X%s Y%s \n' %(offset_x,offset_y))
target.write('\n\n\n')
target.write('F%s \n\n\n' %(feedrate*2)) #redundant

#preprocessing:
lengthOfPath2 = 0

precalc = math.sqrt(math.pow(255,2)+math.pow(255,2)+math.pow(255,2)) #precalculation of the length of an 3 dimensional RGB-color vector (255,255,255) - white 
for j in range(size_y): # iterates through y-axis of the image
	for i in range(size_x): # iterates through x-axis of the image
		pixelRGB = pixel[i,j] # get the RGB-vector of current pixel
		tmp = int((255-int((math.sqrt(math.pow(pixelRGB[0],2)+math.pow(pixelRGB[1],2)+math.pow(pixelRGB[2],2)))/precalc*255))*laserScale) # calculate the length of the vector, normalize it and map it between 0 and 255 (part of the HSV-transformation, to get the greyscale value) 
		pixel[i,j] = (tmp,tmp,tmp)
	lengthOfPath2 += (size_x+1)*pixelScale
	print 'Preprocessing: %.2f%s%s\r' %((float(j)/(size_y-1))*100,'%','       '),
	stdout.flush()

print 'Preprocessing done.    '
					
#main loop

flag = 0
lengthOfPath = 0
lastPos = [0.0,0.0]

target.write('G00 X%s Y%s Z%s F%.2f\n ' %(offset_x,offset_y,0,setFr(0)))

for j in range(size_y): 
	notWhiteFrom = 0
	notWhiteTo = size_x-1
	cFlag = 0
	k = 0	

	for c in range(size_x):
		pixelRGB = pixel[c,j]
		newPX = pixelRGB[1] # [0] [1] and [2] are the same cause grayscale

		if cFlag == 0 and newPX < 10: 
			notWhiteFrom = c
			pixel[c,j]=(255,0,0)			
		elif cFlag == 0 and newPX >= 10:
			cFlag = 1
		if cFlag == 1 and  newPX >=10:
			notWhiteTo = c

	for c in range(notWhiteTo,size_x-1):
		pixel[c,j]=(255,0,0)
	
	for i in range(notWhiteFrom,notWhiteTo+1):
		edge = 0 # is current position left or right edge of the image? 
		if flag == 0: # determinates the direction of the path (left to right or right to left)
			k = i
			if i == notWhiteTo:
				flag = 1
				edge = 1
		else:
			k = (notWhiteTo) - (i-notWhiteFrom)
			if i == notWhiteTo:
				flag = 0
				edge = 1
			
		pixelRGB = pixel[k,j]
		thisPX = pixelRGB[1] # [0] [1] and [2] are the same cause grayscale 
		nextPX = thisPX
		if(flag == 0 and k != notWhiteTo):
			tmpPX = pixel[k+1,j]
			nextPX = tmpPX[1]
		elif(flag == 1 and k != notWhiteFrom):
			tmpPX = pixel[k-1,j]
			nextPX = tmpPX[1]

		if thisPX != nextPX or (edge == 1 and cFlag == 1): # simple compression. Pixels with the same greyscale value are compressed into one path 

			if edge == 1:
				target.write('G01 X%s Y%s Z%s F%.2f \n' %((k*pixelScale)+offset_x,(j*pixelScale)+offset_y,thisPX,setFr(thisPX))) # writes a simple G1 path with Z as modulation value
			if(k != notWhiteTo and flag == 0 and edge == 0):
				target.write('G01 X%s Y%s Z%s F%.2f \n' %(((k+0.5)*pixelScale)+offset_x,(j*pixelScale)+offset_y,thisPX,setFr(thisPX)))
			elif(k != notWhiteFrom and flag == 1 and edge == 0):
				target.write('G01 X%s Y%s Z%s F%.2f \n' %(((k-0.5)*pixelScale)+offset_x,(j*pixelScale)+offset_y,thisPX,setFr(thisPX)))
			lengthOfPath += math.sqrt(math.pow((k-lastPos[0])*pixelScale,2)+math.pow((j-lastPos[1])*pixelScale,2))
			lastPos[0:2] = k,j

	if cFlag == 1:
		target.write('G00 X%s Y%s Z%s F%.2f \n' %((k*pixelScale)+offset_x,((j+1)*pixelScale)+offset_y,0,setFr(0)))
		
		lengthOfPath += math.sqrt(math.pow((k-lastPos[0])*pixelScale,2)+math.pow(((j+1)-lastPos[1])*pixelScale,2))
		lastPos[0:2] = k,j+1

	print 'Calculation of path: %.2f%s%s\r' %((float(j)/(size_y-1))*100,'%','       '),
	stdout.flush()	

print 'Calculation of path done.    '

target.write('\n\nG00 X%s Y%s Z%s \n' %(0,0,0))  # home
target.write('M0 ')
target.close

print 'Total length of path: %.2fm. Estimated time: %.2fh' %(lengthOfPath2/1000,lengthOfPath2/(feedrate*math.pow(60,2)))
print 'Total length of optimized path: %.2fm. Estimated time: %.2fh' %(lengthOfPath/1000,lengthOfPath/(feedrate*math.pow(60,2)))

print 'Done :3'

#im.show()
im.save(output_path+filename, format="png")



