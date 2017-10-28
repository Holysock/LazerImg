# Author: Nick Sidney Lemberger

import math
import os
import sys
from sys import stdout
from PIL import Image

if len(sys.argv) < 8:
    print "parameters: path_to_file, outputName, DPI, offset_x, offset_y, feedrate_max, feedrate_laser, laser_scale"
    exit()

inch = 25.4  # mm
file_path = os.path.join(os.path.dirname(__file__), sys.argv[1])
filename = sys.argv[2]
pxScale = inch / float(sys.argv[3])  # scale pixel depending on DPI

im = Image.open(file_path).rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
im = im.convert('RGB')
pixel = im.load()

output_path = os.path.join(os.path.dirname(__file__), "output/")

size_x = int(im.size[0])
size_y = int(im.size[1])

print "pixel: %spx x %spx" % (size_x, size_y)
print "size: %smm x %smm" % (size_x * pxScale, size_y * pxScale)

target = open(output_path + filename + '.nc', 'w+')
target.seek(0)

offset_x = float(sys.argv[4])  # in mm
offset_y = float(sys.argv[5])
feedrate_max = float(sys.argv[6])  # in mm/min. note: change to dynamic feedrate variation later
feedrate_laser = float(sys.argv[7])
laserScale = float(sys.argv[8])  # 0 < value <= 1

if laserScale > 1:
    laserScale = 1
elif laserScale < 0:
    laserScale = 0


#def setFr(value):
#    if (value <= 10):
#        return feedrate * 2
#    elif (value <= 127):
#        return feedrate
#    else:
#        return feedrate - feedrate * ((float(value) - 128) / 127) * 0.5

def setFr(value):
    if(value <= 10):
        return feedrate_max
    else:
        return feedrate_laser

# Head of Gcode
target.write('/#############################################################/ \n')
target.write('/########## Gcode generated with LazerImg.py V0.1 ############/ \n')
target.write('/##### written by Nick Sidney Lemberger aka Holysocks ########/ \n')
target.write('/#############################################################/ \n\n')
target.write('/%s/ \n' % (filename))
target.write('\n\n\n')
target.write('G90\n')
target.write('S0\n')
target.write('M03\n')

# preprocessing:
lengthOfPath2 = 0

precalc = math.sqrt(3) * 255

for j in range(size_y):  # iterates through y-axis of the image
    for i in range(size_x):  # iterates through x-axis of the image
        pixelRGB = pixel[i, j]  # get the RGB-vector of current pixel
        tmp = int((255 - int((math.sqrt(math.pow(pixelRGB[0], 2) + math.pow(pixelRGB[1], 2) + math.pow(pixelRGB[2],
                                                                                                       2))) / precalc * 255)) * laserScale)
        pixel[i, j] = (tmp, tmp, tmp)
    lengthOfPath2 += (size_x + 1) * pxScale
    print 'Preprocessing: %.2f%s%s\r' % ((float(j) / (size_y - 1)) * 100, '%', '       '),
    stdout.flush()

print 'Preprocessing done.    '

# main loop

flag = 0
lengthOfPath = 0
lastPos = [0.0, 0.0]

# target.write('G00 X%s Y%s Z%s\n ' % (offset_x, offset_y, 0))

for j in range(size_y):
    notWhiteFrom = 0
    notWhiteTo = size_x - 1
    cFlag = 0
    k = 0

    for c in range(size_x):
        pixelRGB = pixel[c, j]
        newPX = pixelRGB[0]  # [0] [1] and [2] are the same value

        if cFlag == 0 and newPX < 10:
            notWhiteFrom = c
            pixel[c, j] = (255, 0, 0)
        elif cFlag == 0 and newPX >= 10:
            cFlag = 1
        if cFlag == 1 and newPX >= 10:
            notWhiteTo = c

    for c in range(notWhiteTo, size_x - 1):
        pixel[c, j] = (255, 0, 0)

    for i in range(notWhiteFrom, notWhiteTo + 1):
        edge = 0  # is current position left or right edge of the image?
        if flag == 0:  # determinates the direction of the path (left to right or right to left)
            k = i
            if i == notWhiteTo:
                flag = 1
                edge = 1
        else:
            k = (notWhiteTo) - (i - notWhiteFrom)
            if i == notWhiteTo:
                flag = 0
                edge = 1

        pixelRGB = pixel[k, j]
        thisPX = pixelRGB[1]  # [0] [1] and [2] are the same
        nextPX = thisPX
        if flag == 0 and k != notWhiteTo:
            tmpPX = pixel[k + 1, j]
            nextPX = tmpPX[1]
        elif flag == 1 and k != notWhiteFrom:
            tmpPX = pixel[k - 1, j]
            nextPX = tmpPX[1]

        if thisPX != nextPX or (
                        edge == 1 and cFlag == 1):  # simple compression. Pixels with the same greyscale value are compressed into one path

            if edge == 1:
                target.write('G01 X%s Y%s S%s F%.2f \n' % (
                    (k * pxScale) + offset_x, (j * pxScale) + offset_y, int(thisPX * 1000 / 255),
                    setFr(thisPX)))  # writes a simple G1 path with S to control laser PWM
            if k != notWhiteTo and flag == 0 and edge == 0:
                target.write('G01 X%s Y%s S%s F%.2f \n' % (
                    ((k + 0.5) * pxScale) + offset_x, (j * pxScale) + offset_y, int(thisPX * 1000 / 255),
                    setFr(thisPX)))
            elif k != notWhiteFrom and flag == 1 and edge == 0:
                target.write('G01 X%s Y%s S%s F%.2f \n' % (
                    ((k - 0.5) * pxScale) + offset_x, (j * pxScale) + offset_y, int(thisPX * 1000 / 255),
                    setFr(thisPX)))
            lengthOfPath += math.sqrt(
                math.pow((k - lastPos[0]) * pxScale, 2) + math.pow((j - lastPos[1]) * pxScale, 2))
            lastPos[0:2] = k, j

    if cFlag == 1:
        target.write(
            'G00 X%s Y%s S%s\n' % ((k * pxScale) + offset_x, ((j + 1) * pxScale) + offset_y, 0))

        lengthOfPath += math.sqrt(
            math.pow((k - lastPos[0]) * pxScale, 2) + math.pow(((j + 1) - lastPos[1]) * pxScale, 2))
        lastPos[0:2] = k, j + 1

    print 'Calculation of path: %.2f%s%s\r' % ((float(j) / (size_y - 1)) * 100, '%', '       '),
    stdout.flush()

print 'Calculation of path done.    '

target.write('S0 \n')
target.write('M05 \n')
target.write('G00 X0 Y0\n')
target.close

print 'Total length of path: %.2fm.' % (lengthOfPath / 1000)

print 'Done :3'

im.rotate(180).transpose(Image.FLIP_LEFT_RIGHT).show()
