
import math
import sys
import uuid
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
        if output_file is not None:
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

    def cartesian_heading(self, theta):
        """
        Return the aubsolute Cartesian heading for the turtle in degrees.
        """
        return theta 

    def turtle_heading_from_cartesian_heading(self, theta):
        """
        Return an absolute turtle heading from a Cartesian heading.
        """
        return theta

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
    _current_polyline = attr.ib(default=None)
    # Fill attributes.
    # _fill_mode: off, fill, or unfill
    # _filled_components: index 0 is always a polygon
    # _hole components: index 0 is always a ploygon
    _fill_mode = attr.ib(default='off') # off, fill, or unfill
    _filled_components = attr.ib(default=None)
    _hole_components = attr.ib(default=None)

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
        vb = "{} {} {} {}".format(xmin, ymin, w, h)
        drawing['width'] = h
        drawing['height'] = w
        drawing['viewBox'] = vb
        components = self._components 
        for component in components:
            if hasattr(component, 'points') and len(component.points) == 0:
                continue
            drawing.add(component)
        drawing.write(fout)

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
        self._line_to(x, y)

    def _line_to(self, x1, y1):
        """
        Set the new pos.
        If the pen is down, add a new line.
        """
        x0, y0 = self._pos
        fill_mode = self._fill_mode
        if fill_mode != 'off':
            fill_container = self._filled_components[0]
            hole_container = self._hole_components[0]
            fill_container.points.append((y1, x1))
            if fill_mode == 'unfill':
                hole_container.points.append((y1, x1)) 
        if self._pendown:
            self._adjust_bounds(x0 + self._pensize * 0.5, -y0 + self._pensize * 0.5)
            self._adjust_bounds(x0 - self._pensize * 0.5, -y0 - self._pensize * 0.5)
            self._adjust_bounds(x1 + self._pensize * 0.5, -y1 + self._pensize * 0.5)
            self._adjust_bounds(x1 - self._pensize * 0.5, -y1 - self._pensize * 0.5)
            drawing = self.screen.drawing
            polyline = self._get_current_polyline()
            polyline.points.append((y1, x1))
        else:
            self._current_polyline = None
        self._pos = (x1, y1)

    def _get_current_polyline(self):
        """
        Get the current polyline or create a new one if it doesn't exist.
        """
        polyline = self._current_polyline
        if polyline is None:
            polyline = self.screen.drawing.polyline()
            polyline['transform'] = "rotate(-90)"
            polyline['stroke'] = self._pencolor
            polyline['stroke-width'] = self._pensize
            polyline['class'] = 'hole'
            polyline['fill-opacity'] = 0
            x, y = self._pos
            polyline.points.append((y, x))
            self._components.append(polyline)
            self._current_polyline = polyline
        return polyline

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
        heading = self._heading - angle
        self._heading = heading % 360

    def left(self, angle):
        heading = self._heading + angle
        self._heading = heading % 360

    def forward(self, dist):
        dx, dy = calc_distance(self._heading, dist)
        x, y = self._pos
        x += dx
        y += dy
        self._line_to(x, y)

    def backward(self, dist):
        dx, dy = calc_distance(self._heading, -dist)
        x, y = self._pos
        x += dx
        y += dy
        self._line_to(x, y) 

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
        self._current_polyline = None

    def pensize(self, width=None):
        if width is None:
            return self._pensize
        else:
            self._pensize = width
            self._current_polyline = None

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
        fill_mode = self._fill_mode 
        if fill_mode != 'off':
            raise Exception("`begin_fill()`: Fill mode is already enabled.")
        self._fill_mode = 'fill'
        self._filled_components = filled_components = []
        self._hole_components = hole_components = []
        fill_container = self.screen.drawing.polygon()
        fill_container['transform'] = 'rotate(-90)'
        filled_components.append(fill_container)
        self._components.append(fill_container)
        hole_polygon = self.screen.drawing.polygon()
        hole_polygon['transform'] = 'rotate(-90)'
        hole_components.append(hole_polygon)

    def end_fill(self):
        if self._fill_mode != 'fill':
            raise Exception("`end_fill()` can only be called in fill-mode and after any unfill mode has been cleared.  Fill mode was `{}`.".format(self._fill_mode))
        self._fill_mode = 'off'
        filled_components = self._filled_components
        fill_container = filled_components[0]
        self._filled_components = None
        hole_components = self._hole_components
        self._hole_components = None
        # If there are holes, create a mask.
        if len(hole_components) > 1 or len(hole_components[0].points) > 0:
            if len(fill_container.points) == 0 and len(filled_components) == 1:
                # No actual filled components; no mask needed to make holes.
                return
            dwg = self.screen.drawing
            mask_id = uuid.uuid4().hex
            mask = dwg.defs.add(dwg.mask(id=mask_id))
            for component in filled_components:
                if hasattr(component, 'points') and len(component.points) == 0:
                    continue
                allow_mask = component.copy()
                allow_mask['fill'] = 'white'
                if allow_mask.attribs.get('transform') is not None:
                    del allow_mask.attribs['transform']
                mask.add(allow_mask)
                component['fill'] = self._fillcolor
                component['fill-opacity'] = 1
                component['fill-rule'] = 'evenodd'
                component['mask'] = "url(#{})".format(mask_id)
                component['transform'] = 'rotate(-90)'
            for component in hole_components:
                if hasattr(component, 'points') and len(component.points) == 0:
                    continue
                deny_mask = component.copy()
                deny_mask['fill'] = 'black'
                if deny_mask.attribs.get('transform') is not None:
                    del deny_mask.attribs['transform']
                component['class'] = 'hole'
                component['fill-opacity'] = 0
                component['transform'] = 'rotate(-90)'
                mask.add(deny_mask)
        else:
            for component in filled_components:
                if hasattr(component, 'points') and len(component.points) == 0:
                    continue
                component['fill'] = self._fillcolor
                component['fill-opacity'] = 1
                component['fill-rule'] = 'evenodd'
                component['transform'] = 'rotate(-90)'

    def begin_unfilled(self):
        """
        Only valid within `begin_fill()` and `end_fill()` context.
        Shapes drawn in between inocations of this method and `end_unfilled()`
        will not be filled but instead will behave as holes in the current fill.
        """
        if self._fill_mode != 'fill':
            raise Exception("`begin_unfilled()` can only be called within `begin_fill()` ... `end_fill()` context.")
        self._fill_mode = 'unfill'

    def end_unfilled(self):
        """
        Only valid within `begin_fill()` and `end_fill()` context.
        Shapes drawn in between inocations of `begin_unfilled()` and this method
        will not be filled but instead will behave as holes in the current fill.
        """
        if self._fill_mode != 'unfill':
            raise Exception("`end_unfilled()` can only be called after `begin_unfilled()`.")
        self._fill_mode = 'fill'

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
        """
        The center of the circle with be `radius` units to 90 degrees left of
        the turtle's current heading.
        The turtle will trace out an arc that sweeps out `angle` degrees.
        """
        x, y = self._pos
        theta = (self._heading + 90) % 360
        xcenter = x + math.cos(deg2rad(theta)) * radius
        ycenter = y + math.sin(deg2rad(theta)) * radius
        self._adjust_bounds(xcenter - radius, ycenter - radius)
        self._adjust_bounds(xcenter + radius, ycenter + radius)
        if angle != 0 and (angle % 360 == 0):
            component = self.screen.drawing.circle((ycenter, xcenter), radius)
        else:
            rx = radius
            ry = radius
            xrot = 0
            if abs(angle) > 180.0:
                large_arc = 1
            else:
                large_arc = 0
            if angle < 0:
                sweep_flag = 1
            else:
                sweep_flag = 0
            theta = (theta - 180 + angle)
            xdest = xcenter + math.cos(deg2rad(theta)) * radius
            ydest = ycenter + math.sin(deg2rad(theta)) * radius
            component = self.screen.drawing.path()
            command = "M {} {}".format(y, x)
            component.push(command)
            command = "A {} {} {} {} {} {} {}".format(abs(radius), abs(radius), xrot, large_arc, sweep_flag, ydest, xdest)
            component.push(command)
        component['transform'] = 'rotate(-90)'
        component['stroke'] = self._pencolor
        component['stroke-width'] = self._pensize
        self._components.append(component)
        if self._fill_mode == 'unfill':
            self._hole_components.append(component)
        elif self._fill_mode == 'fill':
            self._filled_components.append(component)

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

def rad2deg(radians):
    """
    Convert radians to degrees.
    """
    return radians * (180.0 / math.pi)

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
    return ("0{}".format(hex(x)[2:]))[-2:]

def rgb2hex(r, g, b, mode=255):
    """
    Return a hex color suitble for SVG given RGB components.
    """
    return "#{}{}{}".format(hexpair(r), hexpair(g), hexpair(b)) 

