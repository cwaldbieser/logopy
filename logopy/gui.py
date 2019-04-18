
import collections
import functools
import io
import math
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import turtle
from logopy import errors
from logopy.trig import deg2rad, rotate_coords
import attr
import parsley


@attr.s
class TurtleGui:
    root = attr.ib(default=None)
    frame = attr.ib(default=None)
    canvas = attr.ib(default=None)
    screen = attr.ib(default=None)
    entry = attr.ib(default=None)
    output = attr.ib(default=None)
    input_var = attr.ib(default=None)
    halt = attr.ib(default=False)
    _prompt_label = attr.ib(default=None)
    _input_handler = attr.ib(default=None)
    _buffer = attr.ib(default=attr.Factory(list))
    _prompt = attr.ib(default="?")
    _io_outbuf = attr.ib(default=attr.Factory(io.StringIO))
    _command_history = attr.ib(default=attr.Factory(lambda : collections.deque([], 100)))
    _command_hist_idx = attr.ib(default=None)
    
    @classmethod
    def make_gui(cls, interactive=False):
        gui = cls()
        root = Tk()
        gui.root = root
        f = Frame(root)
        f.pack(side='top', expand=1, fill='both')
        gui.frame = f
        canvas = Canvas(f)
        canvas.bind("<Configure>", gui.configure_canvas)
        canvas.pack(side='top', expand=1, fill='both')
        gui.canvas = canvas
        screen = turtle.TurtleScreen(canvas)
        gui.screen = screen
        if interactive:
            output = ScrolledText(f, height=10, state='disabled')
            output.bind("<1>", lambda event: output.focus_set())
            output.pack(side='top', expand=0, fill='x')
            gui.output = output
            text_input = Frame(f) 
            prompt = Label(text_input, text="?")
            prompt.pack(side='left', expand=0)
            gui._prompt_label = prompt
            input_var = StringVar()
            gui.input_var = input_var
            entry = Entry(text_input, textvariable=input_var)
            entry.bind('<Return>', gui.handle_input)
            entry.bind('<Up>', gui.back_history)
            entry.bind('<Down>', gui.forward_history)
            entry.pack(side='left', expand=1, fill='x')
            text_input.pack(side='top', expand=0, fill='x')
        return gui

    def write(self, data):
        """
        Write to temporary output buffer.
        """
        buf = self._io_outbuf
        buf.write(data)
        self._flush_to_output()

    def _write(self, data):
        """
        Write to output widget.
        """
        output = self.output
        output.configure(state='normal')
        output.insert(END, data)
        output.configure(state='disabled')
        output.see(END)

    def _flush_to_output(self):
        """
        Flush temporary buffer to output widget.
        """
        buf = self._io_outbuf
        self._write(buf.getvalue())
        buf.seek(0)
        buf.truncate()

    def _flush_to_null(self):
        """
        Flush temporary buffer without displaying the output.
        """
        buf = self._io_outbuf
        buf.seek(0)
        buf.truncate()

    def _hist(self, direction=1):
        """
        Scroll back through line history.
        """
        idx = self._command_hist_idx
        if idx is None:
            idx = 0
        else:
            idx += direction
        history = self._command_history
        if idx < len(history) and idx >= 0:
            line = history[idx]
            self._command_hist_idx = idx
            self.input_var.set(line)
        elif idx == -1:
            self.input_var.set("")
            self._command_hist_idx = idx

    def back_history(self, event):
        """
        Scroll backward through line history.
        """
        self._hist(1)
    
    def forward_history(self, event):
        """
        Scroll forward through line history.
        """
        self._hist(-1)

    def configure_canvas(self, event):
        """
        Handle canvas size changes.
        """
        w, h = event.width, event.height
        canvas = self.canvas
        hh = h / 2.0
        hw = w / 2.0
        north = -hh
        south = hh
        east = hw
        west = -hw
        canvas.configure(scrollregion=(west, north, east, south))

    def set_input_handler(self, handler):
        """
        Set the input handler.
        """
        self._input_handler = handler

    def handle_input(self, event):
        """
        Handle data delivered from the input widget.
        """
        buf = self._buffer
        input_var = self.input_var
        input_data = input_var.get()
        input_var.set("")    
        handler = self._input_handler
        if len(buf) > 0:
            buf.append(input_data)
            data = ' '.join(buf)
            buf[:] = []
        else:
            data = input_data
        if handler is None:
            return
        prompt = self._prompt
        if data.strip().lower() == 'halt':
            self.halt = True
            return
        self._write("{} {}\n".format(prompt, input_data))
        result = None
        try:
            result = handler(data)
        except errors.ExpectedEndError as ex:
            buf.append(data)
            self._prompt_label.configure(text=">")
            self._prompt = ">"
        except (parsley.ParseError, parsley.EOFError) as ex:
            msg = str(ex)
            if msg.find("expected EOF") != -1:
                buf.append(data)
                self._prompt_label.configure(text=">")
                self._prompt = ">"
            else:
                raise
        except errors.LogoError as ex:
            self._prompt_label.configure(text="?")
            self._prompt = "?"
            self.write("{}\n".format(str(ex)))
        else:
            self._prompt_label.configure(text="?")
            self._prompt = "?"
        self._command_history.appendleft(input_data)
        self._command_hist_idx = None
        return result


def ext_ellipse(self, major, minor, angle=360, clockwise=True):
    """
    Extension method added to turtle instance.
    """
    backend = self.backend
    orig_heading = self.heading()
    theta = backend.cartesian_heading(orig_heading)
    orig_pos = self.pos()
    i = orig_pos[0]
    j = orig_pos[1]
    angle_count = int(angle)
    pos_fn = lambda frm, to, count, i: (to * i + frm * (count - i - 1)) / (count - 1)
    if clockwise:
        start_angle = 90
        p = functools.partial(pos_fn, start_angle, start_angle - angle + 1, angle_count)
        angles = list(map(p, range(angle_count)))
    else:
        start_angle = -90
        p = functools.partial(pos_fn, start_angle, start_angle + angle - 1, angle_count)
        angles = list(map(p, range(angle_count)))
    half_major = major / 2
    half_minor = minor / 2
    coords = [rotate_coords(0, 0, half_major * math.cos(deg2rad(alpha)), half_minor * math.sin(deg2rad(alpha)), theta) for alpha in angles]
    if not clockwise:
        xsign = -1
        ysign = 1
    else:
        xsign = 1
        ysign = -1
    i = half_minor * math.sin(deg2rad(theta)) * xsign + i
    j = half_minor * math.cos(deg2rad(theta)) * ysign + j 
    coords = [(i + x, j + y) for x, y in coords]
    self.pu()
    coord = coords[0]
    self.setpos(*coord)
    self.pd()
    for x, y in coords:
        self.setpos(x, y)
    if clockwise:
        turtle_heading = backend.turtle_heading_from_cartesian_heading(theta - angle)
    else:
        turtle_heading = backend.turtle_heading_from_cartesian_heading(theta + angle)
    self.setheading(turtle_heading)
        
