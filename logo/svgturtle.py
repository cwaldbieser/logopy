
import math
import sys
import attr
import svgwrite


@attr.s
class SVGScreen:
    """
    Screen abstraction for batch SVG turtles.
    """
    drawing = attr.ib(default=None)
    _mode = attr.ib(default=None)
    _colormode = attr.ib(default=None)
    _bgcolor = attr.ib(default=None)

    @classmethod
    def create_screen(cls, size=(1000, 1000), viewbox='-500 -500 1000 1000'):
        screen = cls()
        dwg = svgwrite.Drawing(size=size, viewBox=viewbox)
        screen.drawing = dwg
        return screen
        
    def mode(self, mode=None):
        if mode is None:
            return self._mode
        else:
            self._mode = mode 

    def colormode(self, colormode=None):
        if colormode is None:
            return self._colormode
        elif not colormode in (1.0, 255):
            raise Exception("Color mode must be `1.0` or `255`.")
        else:
            self._colormode = colormode

    def bgcolor(self, *args):
        """
        Get or set background color.
        """
        arg_count = len(args)
        if arg_count == 0:
            return self._bgcolor
        elif arg_count == 1:
            arg = args[0]
            self._bgcolor = arg
        elif arg_count == 3:
            self._bgcolor = tuple(*args)
        else:
            raise Exception("Invalid color specification `{}`.".format(tuple(*args)))

@attr.s
class SVGTurtle:
    """
    Turtle for drawing to an SVG image.
    """
    screen = attr.ib(default=None)
    _pendown = attr.ib(default=False)
    _pencolor = attr.ib(default='white')
    _pensize = attr.ib(default=1)
    _fillcolor = attr.ib(default='white')
    _pos = attr.ib(default=(0, 0))
    _heading = attr.ib(default=90)
    _visible = attr.ib(default=True)
    _speed = attr.ib(default=5)
    _paths = attr.ib(default=attr.Factory(list))

    @classmethod
    def create_turtle(cls, screen):
        turtle = cls()
        turtle.screen = screen
        return turtle
        
    def isdown(self):
        return self._pendown

    def pos(self):
        return self._pos

    def xcor(self):
        return self._pos[0]

    def ycor(self):
        return self._pos[1]

    def _get_xy(self, x, y=None):
        """
        Normalize X, Y coordinate inputs.
        """
        if y is None:
            if len(x) != 2:
                raise Exception("Expected coordinates `(x, y)` or `x, y`, but received `{}`.".format(x))
            else:
                x, y = x
        return (x, y)

    def setpos(self, x, y=None):
        pos = self._get_xy(x, y)
        self._pos = pos
        self._add_coord()

    def _add_coord(self):
        """
        If the pen is down, add a new coordinate to the current path.
        """
        if self._pendown:
            pos = self._pos
            coord_list = self._paths[-1]
            coord_list.append(pos)

    def heading(self):
        return self._heading 

    def setheading(self, heading):
        self._heading = heading

    def towards(self, x, y=None):
        x1, y1 = self._get_xy(x, y)
        x0, y0 = self._pos
        theta = math.atan2(y1-y0, x1-x0)
        return theta * 180.0 / math.pi

    def penup(self):
        if not self._pendown:
            return
        else:
            self._pendown = False

    def pendown(seld):
        if self._pendown:
            return
        else:
            coord_list = [self._pos]
            self._paths.append(coord_list)
            self._pendown = True 

    def right(self, angle):
        heading = _self.heading - angle
        self._heading = heading % 360

    def left(self, angle):
        heading = _self.heading + angle
        self._heading = heading % 360

    def forward(self, dist):
        dx, dy = calc_distance(self._heading, dist)
        x, y = self._pos
        x += dx
        y += dy
        self._pos = (x, y)
        self._add_coord() 

    def backward(self, dist):
        dx, dy = calc_distance(self._heading, -dist)
        x, y = self._pos
        x += dx
        y += dy
        self._pos = (x, y)
        self._add_coord() 

    def clear(self):
        paths = self._paths
        paths[:] = []
        if self._pendown:
            paths.append([self._pos])

    def home(self):
        self.setpos(0, 0)
        self.setheading(90)

    def pencolor(self, *args):
        arg_count = len(args)
        if arg_count == 0:
            return self._pencolor
        elif arg_count == 1:
            arg = args[0]
            self._pencolor = arg
        elif arg_count == 3:
            self._pencolor = tuple(*args)
        else:
            raise Exception("Invalid color specification `{}`.".format(tuple(*args)))

    def pensize(self, width=None):
        if width is None:
            return self._pensize
        else:
            self._pensize = width

    def fillcolor(self, color):
        arg_count = len(args)
        if arg_count == 0:
            return self._fillcolor
        elif arg_count == 1:
            arg = args[0]
            self._fillcolor = arg
        elif arg_count == 3:
            self._fillcolor = tuple(*args)
        else:
            raise Exception("Invalid color specification `{}`.".format(tuple(*args)))

    def begin_fill(self):
        pass

    def end_fill(self):
        pass
  
    def hideturtle(self):
        self._visible = False

    def showturtle(self):
        self._visible = True

    def isvisible(self):
        return self._visible

    def speed(self, num=None):
        if num is None:
            return self._speed
        else:
            self._speed = num

    def circle(self, radius, angle):
        pass

    def setundobuffer(self, num):
        pass

    def undo(self):
        pass

    def undobufferentries(self):
        return 0


def deg2rad(degrees):
    """
    Convert degrees to radians.
    """
    return degrees * (math.pi / 180.0)

def calc_distance(theta, dist):
    """
    Calculate x and y offsets for moving forward `dist` units at heading `theta`.
    `theta` is in degrees.
    """
    rad = deg2rad(theta)
    x = dist * math.cos(rad)
    y = dist * math.sin(rad)
    return (x, y) 

