# Author: Nick Sidney Lemberger
# rep ---> github.com/Holysocks/LazerImg

import math
import os
#import sys
import time
from sys import stdout
from PIL import Image
import plotlib
import argparse
import numpy as np

timeStart = float(time.time())

show_przss1 = True
show_przss2 = True
show_przss3 = True
show_connects = False
square = 10
deltamax = 1.5

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=True, help="Path to file to convert")
ap.add_argument("-n", "--name", required=True, help="Set name of output file without postfix ")
ap.add_argument("-d", "--dpi", required=True, help="Set DPI of input. Use this to scale the output")
ap.add_argument("-f", "--feedrate", required=True, help="Sets max feedrate.")
ap.add_argument("--hpgl", help="Set output protocol to HPGL instead of gcode", action="store_true")
ap.add_argument("-t", "--threshold", help="Set threshold for black/white conversion 0<t<255. Default: 128 ")
ap.add_argument("-off", "--offset", help="Set offset. x,y Default: 0,0 ")
ap.add_argument("--show", help="Usage: --show ""<allThingsToShow>"" things to show: bw, edges, paths")
ap.add_argument("--debugg", help="Shows various debugg-messages", action="store_true")
ap.add_argument("-s", "--scale", help="Scales windows. Default 1")
args = ap.parse_args()

hpgl = False

file_path = os.path.join(os.path.dirname(__file__), args.path)
filename = args.name
threshold = 128
if args.hpgl: hpgl = True
else: hpgl = False
gcode = not hpgl
if args.threshold:  threshold = int(args.threshold)
offset_x, offset_y = 0, 0
if args.offset: offset_x, offset_y = args.offset
feedrate = args.feedrate
renderScale = 1  # TODO implement auto scale
if args.scale: renderScale = float(args.scale)
inch = 25.4  # in mm
unit = 40  # 1mm = 40 hpgl base units
pxScale = inch / float(args.dpi)

im = Image.open(file_path).rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
im = im.convert('RGB')
pixel = im.load()
output_path = os.path.join(os.path.dirname(__file__), "output/")

size_x = int(im.size[0])
size_y = int(im.size[1])
totalPx = size_x * size_y

print "Pixel: %spx X %spx " %(size_x, size_y)
print "Size: %.2fmm X %.2fmm "%(size_x * pxScale, size_y * pxScale)

if hpgl: target = open(output_path + filename + '.hpgl', 'w')
if gcode: target = open(output_path + filename + '.nc', 'w')
target.seek(0)

plotter = plotlib.plot(int(size_x / renderScale), int(size_y / renderScale))  # just for visualization and debugging
plotter.setBackground(0, 0, 0)

precalc = math.sqrt(3) * 255

if (threshold >= 255):
    threshold = 255
elif (threshold <= 0):
    threshold = 0

# Header of Gcode
if gcode:
    target.write('/#############################################################/ \n')
    target.write('/########## Gcode generated with PathImg.py V0.6 #############/ \n')
    target.write('/##### written by Nick Sidney Lemberger aka Holysocks ########/ \n')
    target.write('/#############################################################/ \n\n')
    target.write('/%s/ \n' % (filename))
    target.write('\n\n\n')
    target.write('G90\n')
    target.write('S0\n')
    target.write('M03\n')
    # target.write('G28\n')
    # target.write('G00 X0 Y0 Z0 \n')
# Header of Gcode
if hpgl:
    target.write('IN;SP1;PU0,0')


def thresValue(value):  # returnes 0 or 255 for given value, depending on threshold
    if value >= threshold:
        return 255
    else:
        return 0


def plotL(x, y, r, g, b, s):  # simple visualisazion
    plotter.setColor(r, g, b)
    plotter.plotdot(x / renderScale, (size_y - y) / renderScale)
    if (s):
        plotter.show()


print "converting image to black&white..."

for j in xrange(size_y):  # First process: convert image to B&W
    for i in xrange(size_x):
        pixelRGB = pixel[i, j]
        tmp = int((math.sqrt(math.pow(pixelRGB[0], 2) + math.pow(pixelRGB[1], 2) + math.pow(pixelRGB[2],
                                                                                            2))) / precalc * 255)  # length of color-vector
        pixel[i, j] = (thresValue(tmp), thresValue(tmp), thresValue(tmp))  # replacing old pixels
        if show_przss1:
            plotL(i, j, thresValue(tmp), thresValue(tmp), thresValue(tmp), False)
    print "converting: %.2f%s\r" % (100 * (float(j + 1)) / size_y, "%      "),
    stdout.flush()
    plotter.show()

print "converting complete!"

im.save(output_path + filename + '_BW', format="png")

edge = (255, 0, 0)  # edges (black to white or white to black) are red
edgeList = []  # contains position of all edges as tupels (x,y)
joined_pixel = (0, 0, 255)  # pixel joined into a path, are blue
white = (255, 255, 255)

plotter.setBackground(0, 0, 0)
# Second process: searching edges
print "searching for edges..."
for j in xrange(size_y):  # Searching edges in x-diretion
    for i in xrange(size_x):
        if i < size_x - 1:
            this_pixel = pixel[i, j]
            next_pixel = pixel[i + 1, j]
            if not this_pixel[1] == next_pixel[1]:  # if theres a color change...
                if this_pixel == white and not next_pixel == edge:
                    edgePos = (i + 1, j)
                    pixel[edgePos] = edge
                    edgeList.append(edgePos)
                    if show_przss2:
                        plotL(i + 1, j, 255, 0, 0, False)
                elif next_pixel == white and not this_pixel == edge:
                    edgePos = (i, j)
                    pixel[edgePos] = edge
                    edgeList.append(edgePos)
                    if show_przss2:
                        plotL(i, j, 255, 0, 0, False)
    print "%s %.1f%s\r" % (len(edgeList), (float(j + 1) / size_y) * 50, "%             "),
    stdout.flush()
    plotter.show()

for j in xrange(size_x):  # Searching edges in y-diretion
    for i in xrange(size_y):
        if i < size_y - 1:
            this_pixel = pixel[j, i]
            next_pixel = pixel[j, i + 1]
            if not this_pixel[1] == next_pixel[1]:  # if theres a color change...
                if this_pixel == white and not next_pixel == edge:
                    edgePos = (j, i + 1)
                    pixel[edgePos] = edge
                    edgeList.append(edgePos)
                    if show_przss2:
                        plotL(j, i + 1, 255, 0, 0, False)
                elif next_pixel == white and not this_pixel == edge:
                    edgePos = (j, i)
                    pixel[edgePos] = edge
                    edgeList.append(edgePos)
                    if show_przss2:
                        plotL(j, i, 255, 0, 0, False)
    print "%s %.1f%s\r" % (len(edgeList), (float(j + 1) / size_x) * 50 + 50, "%          "),
    stdout.flush()
    plotter.show()

print "found edges: %s" % (len(edgeList))
print "creating path..."

stdout.flush()
plotter.setBackground(0, 0, 0)


def testIndex(x, y):  # prevents out of bounds exception
    if x <= -1 or y <= -1 or x >= size_x or y >= size_y:
        return False
    else:
        return True


def closeCircle(x, y, path):
    if len(path) <= 7: return (x, y, path)
    a = path[0][0]
    b = path[0][1]
    if x - 3 <= a <= x + 3 and y - 3 <= b <= y + 3:
        path.append((a, b, path[0][2]))
        return a, b, path
    else:
        return x, y, path


# Third process: creates a sub-path
def searchPath(x, y):
    subPath = []
    while (1):  # is there an edge next to current edge? ...
        dirct = 0
        edgeList.remove((x, y))  # processed edges are removed
        pixel[x, y] = joined_pixel

        # 1. possible position of next edge
        if testIndex(x + 1, y + 1) and pixel[x + 1, y + 1] == edge:  # ... yes? move to this edge, and continue to next
            if show_przss3:
                plotL(x, y, 0, 0, 255, False)
            x += 1
            y += 1
            dirct = 1

        # 2. possible position of next edge
        elif testIndex(x + 1, y - 1) and pixel[x + 1, y - 1] == edge:
            if show_przss3:
                plotL(x, y, 0, 0, 255, False)
            x += 1
            y -= 1
            dirct = 2

        # 3. possible position of next edge
        elif testIndex(x - 1, y + 1) and pixel[x - 1, y + 1] == edge:
            if show_przss3:
                plotL(x, y, 0, 0, 255, False)
            x -= 1
            y += 1
            dirct = 3

        # 4. possible position of next edge
        elif testIndex(x - 1, y - 1) and pixel[x - 1, y - 1] == edge:
            if show_przss3:
                plotL(x, y, 0, 0, 255, False)
            x -= 1
            y -= 1
            dirct = 4

        # 5. possible position of next edge
        elif testIndex(x + 1, y) and pixel[x + 1, y] == edge:
            if show_przss3:
                plotL(x, y, 0, 0, 255, False)
            x += 1
            y = y
            dirct = 5

        # 6. possible position of next edge
        elif testIndex(x - 1, y) and pixel[x - 1, y] == edge:
            if show_przss3:
                plotL(x, y, 0, 0, 255, False)
            x -= 1
            y = y
            dirct = 6

        # 7. possible position of next edge
        elif testIndex(x, y + 1) and pixel[x, y + 1] == edge:
            if show_przss3:
                plotL(x, y, 0, 0, 255, False)
            x = x
            y += 1
            dirct = 7

        # 8. possible position of next edge
        elif testIndex(x, y - 1) and pixel[x, y - 1] == edge:
            if show_przss3:
                plotL(x, y, 0, 0, 255, False)
            x = x
            y -= 1
            dirct = 8
        if dirct == 0:
            return closeCircle(x, y, subPath)  # returns end of path and created subPath,
            # also checks if path is a circle (ends where it starts)
        subPath.append((x, y, dirct))


def seachNextEdge(x, y, givenList):  # returns edge with smallest distance to the given one
    nearestEdge = givenList[0]  # note: version 1. Do not use for Entropy > 10% !!
    distance = math.sqrt(math.pow(nearestEdge[0] - x, 2) + math.pow(nearestEdge[0] - y, 2))
    for i in edgeList:  # iterates through a list that contains all edges.
        newDistance = math.sqrt(
            math.pow(i[0] - x, 2) + math.pow(i[1] - y, 2))  # calculates distance between given edge and current
        if newDistance < distance:
            distance = newDistance
            nearestEdge = i
    return nearestEdge


def searchInSquare(x, y):
    tmpList = []
    for i in xrange(square):
        ii = i - square * 0.5
        for j in xrange(square):
            jj = j - square * 0.5
            if testIndex(x + ii, y + jj) and pixel[x + ii, y + jj] == edge:
                tmpList.append(pixel[x + ii, y + jj])
    if len(tmpList) == 0:
        return seachNextEdge(lastPath[0], lastPath[1], edgeList)
    else:
        return seachNextEdge(lastPath[0], lastPath[1], tmpList)

def vect(path):
    path2 = [path[0]]
    i1 = 0
    if(path[0][:2] == path[-1][:2]): p2 = np.array(path[-2][:2])
    else: p2 = np.array(path[-2][:2])
    while(i1 < len(path)-1):
        p1 = np.array(path[i1][:2])
        k = i1
        for k in xrange(i1, len(path)):
            p3 = np.array(path[k][:2])
            d = np.linalg.norm(np.cross(p2 - p1, p1 - p3)) / np.linalg.norm(p2 - p1)
            if d > deltamax:
                break
        path2.append(path[k])
        i1 = k
    return path2


# Finally, create sub-paths and join them
lastPath = (0, 0, 0)
totalLen = len(edgeList)
joinedSubPaths = []
while len(edgeList) > 0:  # as long as there are edges left...
    # nextPath = seachNextEdge(lastPath[0],lastPath[1],edgeList) #...search for nearest edge, depending on last point of last path
    nextPath = searchInSquare(lastPath[0], lastPath[1])  # same, but searches for edges in a smaller area
    if show_connects:
        plotter.setColor(0, 50, 0)
        plotter.plotline(lastPath[0] / renderScale, lastPath[1] / renderScale, nextPath[0] / renderScale,
                         nextPath[1] / renderScale)
    lastPath = searchPath(nextPath[0], nextPath[1])  # search next path and save endpoint for next iteration
    if len(lastPath[2]) > 1:  # prevents artifacts (one-pixel-paths / path without direction))
        joinedSubPaths.append(vect(lastPath[2]))  # joins sub-paths and removes redundant pixels

    print "remaining edges: %s %.2f%s \r" % (len(edgeList), 100 - 100 * (len(edgeList) + 0.001) / totalLen, '%   '),
    stdout.flush()
    if show_przss3:
        plotter.show()

print "Total number of sub-pathes: %s%s" % (len(joinedSubPaths), ' ' * 20)

current_command = ""

def writeHPGL(nextPoint_x, nextPoint_y, laser):
    global current_command
    if laser > 0:
        if current_command == "PD":
            target.write(
                ',%d,%d' % ((nextPoint_x * pxScale + offset_x) * unit, (nextPoint_y * pxScale + offset_y) * unit))
        else:
            target.write(
                ';PD%d,%d' % ((nextPoint_x * pxScale + offset_x) * unit, (nextPoint_y * pxScale + offset_y) * unit))
            current_command = "PD"
    else:
        if current_command == "PU":
            target.write(
                ',d,%d' % ((nextPoint_x * pxScale + offset_x) * unit, (nextPoint_y * pxScale + offset_y) * unit))
        else:
            target.write(
                ';PU%d,%d' % ((nextPoint_x * pxScale + offset_x) * unit, (nextPoint_y * pxScale + offset_y) * unit))
            current_command = "PU"

def writeGcode(nextPoint_x, nextPoint_y, laser):
    if laser > 0:
        target.write(
            'G01 X%s Y%s S%s\n' % ((nextPoint_x * pxScale + offset_x), (nextPoint_y * pxScale + offset_y), laser))
    else:
        target.write(
            'G00 X%s Y%s S%s\n\n' % ((nextPoint_x * pxScale + offset_x), (nextPoint_y * pxScale + offset_y), laser))

for i in joinedSubPaths:
    lastDirct = 0
    lastPoint = [0, 0]
    target.flush()
    for j in xrange(len(i)):
        pathElement = i[j]
        if j == 0:
            if hpgl: writeHPGL(pathElement[0], pathElement[1], 0)
            if gcode: writeGcode(pathElement[0], pathElement[1], 0)
            lastDirct = pathElement[2]
            lastPoint = (pathElement[0], pathElement[1])
        else:
            if not (lastDirct == pathElement[2]) or True:  # simple run-length compression
                if hpgl: writeHPGL(pathElement[0], pathElement[1], 1)
                if gcode: writeGcode(pathElement[0], pathElement[1], 1000)
            elif j == len(i) - 1:
                if hpgl: writeHPGL(pathElement[0], pathElement[1], 1)
                if gcode: writeGcode(pathElement[0], pathElement[1], 1000)
            lastDirct = pathElement[2]

if hpgl:
    target.write(';SP0;PU0,0;IN;')
if gcode:
    target.write('S0 \n')
    target.write('M05 \n')
    target.write('G00 X0 Y0\n')
target.flush()
print "Elapsed time: %.4fs" % (float(time.time()) - timeStart)
print "Done :3"
print "Press Enter to exit."
im.save(output_path + filename, format="png")
raw_input()
