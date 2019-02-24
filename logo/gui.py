
from tkinter import *
import turtle
import attr


@attr.s
class TurtleGui:
    root = attr.ib(default=None)
    frame = attr.ib(default=None)
    canvas = attr.ib(default=None)
    screen = attr.ib(default=None)
    
    @classmethod
    def make_gui(cls):
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
        button = Button(f, text="FROTZ")
        button.pack(side='bottom')
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
        
