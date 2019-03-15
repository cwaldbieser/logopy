
import math
import sys
import attr
import svgwrite

@attr.s
class SVGTurtleEnv:

    initialized = attr.ib(default=False)
    screen = attr.ib(default=None)
    output_file = attr.ib(default=None)
    turtle = attr.ib(default=None)

    @classmethod
    def create_turtle_env(cls):
        """
        Create the Deferred TK turtle environment.
        """
        return cls()

    def initialize(self, **kwargs):
        """
        Initialize the turtle environment.
        """
        self.screen = SVGScreen.create_screen()
        self.output_file = kwargs.get('output_file')
        self.initialized = True

    def create_turtle(self):
        """
        Create a turtle.
        """
        turtle = self.turtle
        if turtle is None:
            turtle = SVGTurtle.create_turtle(self.screen)
            self.turtle = turtle 
        return turtle 

    def wait_complete(self):
        """
        The main program will wait until this turtle backend
        method returns.
        For a GUI backend, this could mean the user has exited the GUI.
        """
        output_file = self.output_file
        self.turtle.write_svg(output_file)

    @property
    def stdout(self):
        return sys.stdout

    @property
    def stderr(self):
        return sys.stderr

    @property
    def halt(self):
        return False

    @halt.setter
    def halt(self, value):
        raise NotImplemented("HALT is not implemented for the SVG Turtle environment.")

    def process_events(self):
        """
        Process any events for the turtle backend.
        """
        pass

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
            if isinstance(arg, tuple):
                arg = rgb2hex(*arg, mode=self._colormode)
            self._bgcolor = arg
        elif arg_count == 3:
            self._bgcolor = rgb2hex(*args, mode=self._colormode)
        else:
            raise Exception("Invalid color specification `{}`.".format(tuple(*args)))



@attr.s
class SVGTurtle:
    """
    Turtle for drawing to an SVG image.
    """
    screen = attr.ib(default=None)
    _pendown = attr.ib(default=True)
    _pencolor = attr.ib(default='white')
    _pensize = attr.ib(default=1)
    _fillcolor = attr.ib(default='white')
    _pos = attr.ib(default=(0, 0))
    home_heading = attr.ib(default=90)
    _heading = attr.ib(default=90)
    _visible = attr.ib(default=True)
    _speed = attr.ib(default=5)
    _components = attr.ib(default=attr.Factory(list))
    _bounds = attr.ib(default=(0, 0, 0, 0))

    @classmethod
    def create_turtle(cls, screen):
        turtle = cls()
        turtle.screen = screen
        return turtle

    def write_svg(self, fout):
        """
        Write SVG output to file object `fout`.
        """
        drawing = self.screen.drawing
        xmin, xmax, ymin, ymax = self._bounds
        w = xmax - xmin
        h = ymax - ymin
        #vb = "{} {} {} {}".format(xmin, ymin, w, h)
        #drawing['width'] = h
        #drawing['height'] = w
        vb = "-500 -500 1000 1000"
        drawing['width'] = 1000
        drawing['height'] = 1000
        drawing['viewBox'] = vb
        #transform='translate(0,{}) scale(1,-1)'.format(h)
        components = self._components 
        for component in components:
            #component['transform'] = transform
            drawing.add(component)
        drawing.write(fout)

    def _diagnostic(self):
        #print("POS:", self._pos, "HEADING:", self._heading)
        pass
 
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
        self._diagnostic()
        pos = self._get_xy(x, y)
        self._line_to(x, y)
        self._diagnostic()

    def _line_to(self, x1, y1, transform=False):
        """
        Set the new pos.
        If the pen is down, add a new line.
        """
        x0, y0 = self._pos
        self._pos = (x1, y1)
        if self._pendown:
            drawing = self.screen.drawing
            if transform:
                x0, y0 = y0, x0
                x1, y1 = y1, x1
                kwargs = dict(transform="rotate(-90)")
            else:
                kwargs = {}
            line = drawing.line((x0, y0), (x1, y1), stroke=self._pencolor, stroke_width=self._pensize, **kwargs)
            self._components.append(line)
            self._adjust_bounds(x0 + self._pensize * 0.5, -y0 + self._pensize * 0.5)
            self._adjust_bounds(x0 - self._pensize * 0.5, -y0 - self._pensize * 0.5)
            self._adjust_bounds(x1 + self._pensize * 0.5, -y1 + self._pensize * 0.5)
            self._adjust_bounds(x1 - self._pensize * 0.5, -y1 - self._pensize * 0.5)

    def _adjust_bounds(self, x, y):
        """
        Adjust the bounds of the drawing.
        """
        xmin, xmax, ymin, ymax = self._bounds
        xmin = min(x, xmin)
        xmax = max(x, xmax)
        ymin = min(y, ymin)
        ymax = max(y, ymax)
        self._bounds = (xmin, xmax, ymin, ymax)

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

    def pendown(self):
        if self._pendown:
            return
        else:
            self._pendown = True 

    def right(self, angle):
        self._diagnostic()
        heading = self._heading - angle
        self._heading = heading % 360
        self._diagnostic()

    def left(self, angle):
        self._diagnostic()
        heading = self._heading + angle
        self._heading = heading % 360
        self._diagnostic()

    def forward(self, dist):
        self._diagnostic()
        dx, dy = calc_distance(self._heading, dist)
        x, y = self._pos
        x += dx
        y += dy
        self._line_to(x, y, transform=True)
        self._diagnostic()

    def backward(self, dist):
        dx, dy = calc_distance(self._heading, -dist)
        x, y = self._pos
        x += dx
        y += dy
        self._line_to(x, y, transform=True) 

    def clear(self):
        self.components = []
        self._pos = (0, 0)
        self._heading = self.home_heading

    def home(self):
        self._pos = (0, 0)
        self._heading = self.home_heading

    def pencolor(self, *args):
        arg_count = len(args)
        if arg_count == 0:
            return self._pencolor
        elif arg_count == 1:
            arg = args[0]
            if isinstance(arg, tuple):
                arg = rgb2hex(*arg, mode=self.screen.colormode())
            self._pencolor = arg
        elif arg_count == 3:
            self._pencolor = rgb2hex(*args, mode=self.screen.colormode())
        else:
            raise Exception("Invalid color specification `{}`.".format(tuple(*args)))

    def pensize(self, width=None):
        if width is None:
            return self._pensize
        else:
            self._pensize = width

    def fillcolor(self, *args):
        arg_count = len(args)
        if arg_count == 0:
            return self._fillcolor
        elif arg_count == 1:
            arg = args[0]
            if isinstance(arg, tuple):
                arg = rgb2hex(*arg, mode=self.screen.colormode())
            self._fillcolor = arg
        elif arg_count == 3:
            self._fillcolor = rgb2hex(*args, mode=self.screen.colormode())
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

def hexpair(x): 
    """
    Return 2 hex digits for integers 0-255.
    """
    return ("0{}".format(hex(x)[2:])[-2:])

def rgb2hex(r, g, b, mode=255):
    """
    Return a hex color suitble for SVG given RGB components.
    """
    return "#{}{}{}".format(hexpair(r), hexpair(g), hexpair(g)) 

