
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import turtle
import attr
import parsley


@attr.s
class TurtleGui:
    root = attr.ib(default=None)
    frame = attr.ib(default=None)
    canvas = attr.ib(default=None)
    screen = attr.ib(default=None)
    output = attr.ib(default=None)
    input_var = attr.ib(default=None)
    _prompt_label = attr.ib(default=None)
    _input_handler = attr.ib(default=None)
    _buffer = attr.ib(default=attr.Factory(list))
    _prompt = attr.ib(default="?")
    
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
            entry.pack(side='left', expand=1, fill='x')
            text_input.pack(side='top', expand=0, fill='x')
        return gui

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
        result = None
        try:
            result = handler(data)
        except (parsley.ParseError, parsley.EOFError) as ex:
            msg = str(ex)
            if msg.find("expected EOF") != -1:
                buf.append(data)
                self._prompt_label.configure(text=">")
                self._prompt = ">"
            else:
                raise
        else:
            self._prompt_label.configure(text="?")
            self._prompt = "?"
        output = self.output
        output.configure(state='normal')
        output.insert(END, "{} ".format(prompt))
        output.insert(END, input_data)
        output.insert(END, "\n")
        output.configure(state='disabled')
        output.see(END)
        return result
