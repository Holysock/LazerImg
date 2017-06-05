import plotlib
import sys

if len(sys.argv) < 3:
    print "Usage: python gcodeViewer.py <path to file> <pixel per mm>"
    exit()

gcode = open(sys.argv[1], 'r')
size_x = 5000
size_y = 5000
# renderScale = 5
pos_x = 0
pos_y = 0
color = (255, 255, 255)
pixelpermm = int(sys.argv[2])
skipAnimation = True

xmin = -1
xmax = -1
ymin = -1
ymax = -1

for line in gcode:
    if "G01" in line or "G1" in line:
        xi = line.find("X")
        yi = line.find("Y")
        if xi == -1 or yi == -1:
            continue
        i = xi + 1
        for char in line[xi + 1:]:
            if char.isdigit() or char == '.' or char == ',':
                i += 1
            else:
                break
        if i > xi + 1:
            x = float(line[xi + 1:i])
        else:
            continue

        i = yi + 1
        for char in line[yi + 1:]:
            if char.isdigit() or char == '.' or char == ',':
                i += 1
            else:
                break
        if i > yi + 1:
            y = float(line[yi + 1:i])
        else:
            continue

        if xmin < 0 or x < xmin:
            xmin = x
        if ymin < 0 or y < ymin:
            ymin = y
        if xmax < 0 or x > xmax:
            xmax = x
        if ymax < 0 or y > ymax:
            ymax = y
print xmin, xmax, ymin, ymax

plotter = plotlib.plot(int((xmax - xmin) * pixelpermm),
                       int((ymax - ymin) * pixelpermm))  # just for visualization and debugging
plotter.setBackground(0, 0, 0)


# plotter = plotlib.plot(int(size_x/renderScale), int(size_y/renderScale))  # just for visualization and debugging
# plotter.setBackground(0, 0, 0)

def step(x, y, dirx, diry):
    global color
    if x:
        global pos_x
        pos_x = pos_x + 1 if dirx else pos_x - 1
    if y:
        global pos_y
        pos_y = pos_y + 1 if diry else pos_y - 1
    plotter.setColor(color[0], color[1], color[2])
    plotter.plotdot(pos_x - xmin * pixelpermm, pos_y - ymin * pixelpermm)
    if not skipAnimation: plotter.show()


def home():
    # while motor.getEnd("x") or motor.getEnd("y"):
    #	step(1, 1, 0, 0)
    global pos_x, pos_y
    pos_x, pos_y = 0, 0


def step_line(x1, y1):
    x1 = round(x1)
    y1 = round(y1)
    global pos_x, pos_y
    x0 = pos_x
    y0 = pos_y
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    stpx, stpy, dirx, diry = 0, 0, 0, 0
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            stpx, stpy, dirx, diry = 0, 0, 0, 0
            err -= dy
            if err < 0:
                y += sy
                stpy = 1
                diry = 1 if sy > 0 else 0
                err += dx
            x += sx
            stpx = 1
            dirx = 1 if sx > 0 else 0
            step(stpx, stpy, dirx, diry)
    else:
        err = dy / 2.0
        while y != y1:
            stpx, stpy, dirx, diry = 0, 0, 0, 0
            err -= dx
            if err < 0:
                x += sx
                stpx = 1
                dirx = 1 if sx > 0 else 0
                err += dy
            y += sy
            stpy = 1
            diry = 1 if sy > 0 else 0
            step(stpx, stpy, dirx, diry)
    step(stpx, stpy, dirx, diry)


def gofast(x1, y1):
    x1 = round(x1)
    y1 = round(y1)
    dirx = 1 if x1 > pos_x else 0
    diry = 1 if y1 > pos_y else 0
    while pos_x != x1 or pos_y != y1:
        stpx, stpy = 0, 0
        if pos_x != x1:
            stpx = 1
        if pos_y != y1:
            stpy = 1
        step(stpx, stpy, dirx, diry)


def clearbuffer(stuff):
    global color
    if stuff[0] == "G1":
        if stuff[3] > -1:
            color = ((0, 0, (stuff[3])))
        if stuff[1] > -1 and stuff[2] > -1:
            step_line(stuff[1] * pixelpermm, stuff[2] * pixelpermm)
    elif stuff[0] == "G0":
        color = (0, 255, 0)
        gofast(stuff[1] * pixelpermm, stuff[2] * pixelpermm)
    elif stuff[0] == "G28":
        home()


gcode.seek(0)
for line in gcode:
    new_command, new_x, new_y, new_z = -1, -1, -1, -1
    if "G01" in line or "G1" in line:
        xi = line.find("X")
        yi = line.find("Y")
        zi = line.find("Z")
        if xi == -1 or yi == -1:
            continue
        if zi == -1:
            z = 0
        i = xi + 1
        for char in line[xi + 1:]:
            if char.isdigit() or char == '.' or char == ',':
                i += 1
            else:
                break
        if i > xi + 1:
            x = float(line[xi + 1:i])
        else:
            continue

        i = yi + 1
        for char in line[yi + 1:]:
            if char.isdigit() or char == '.' or char == ',':
                i += 1
            else:
                break
        if i > yi + 1:
            y = float(line[yi + 1:i])
        else:
            continue

        i = zi + 1
        for char in line[zi + 1:]:
            if char.isdigit() or char == '.' or char == ',':
                i += 1
            else:
                break
        if i > zi + 1:
            z = int(line[zi + 1:i])
        else:
            z = 0

        new_command = "G1"
        new_x = x
        new_y = y
        new_z = z

    elif "G00" in line or "G0" in line:
        xi = line.find("X")
        yi = line.find("Y")
        if xi == -1 or yi == -1:
            continue
        i = xi + 1
        for char in line[xi + 1:]:
            if char.isdigit() or char == '.' or char == ',':
                i += 1
            else:
                break
        if i > xi + 1:
            x = float(line[xi + 1:i])
        else:
            continue

        i = yi + 1
        for char in line[yi + 1:]:
            if char.isdigit() or char == '.' or char == ',':
                i += 1
            else:
                break
        if i > yi + 1:
            y = float(line[yi + 1:i])
        else:
            continue

        new_command = "G0"
        new_x = x
        new_y = y

    if not (new_x == -1 and new_y == -1 and new_z == -1):
        clearbuffer((new_command, new_x, new_y, new_z))

plotter.show()
raw_input()
