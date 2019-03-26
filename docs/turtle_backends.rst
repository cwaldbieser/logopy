
Turtle Back Ends
================

By default, when *logopy* is run, it will not activate any turtle graphics
unless one of the turtle sub-commands is used (`gui`, `svg`) or if the program
specified by the :option:`-f` option invokes any turtle commands.  In
the latter case, the default Python-TKinter turtle backend is launched.

Specific sub-commands can be used to activate individual turtle back ends.

Python-TKinter Turtle Graphics
------------------------------

This back end is a very simple `Tkinter <https://docs.python.org/3.7/library/tk.html>`_
application that incorporates the Python 
`turtle <https://docs.python.org/3.3/library/turtle.html?highlight=turtle#module-turtle>`_
module.  Commands may be typed in the entry input at the bottom of the application.
Output appears in the text widget above it.  The turtle will draw in the large
area at the top of the application.

The `HALT` command is not a Logo command, but is understood by this environment.  It
will cause the current command to abort as soon as possible.  This is useful
if the turtle is acting on a very time consuming series of commands.

SVG Turtle Backend
------------------

The Scalable Vector Graphics (SVG) turtle back end attempts to map turtle
geometry to SVG graphics.  This backend is not interactive.  It executes a
Logo program and writes the turtle output to an SVG file.  The SVG file
can be used directly in web pages or other applications that can use SVG.
It can also be animated in web pages using 
`Vivus <https://maxwellito.github.io/vivus/>`_ .

Detailed Turtle Back End Information
------------------------------------

.. toctree::
   :maxdepth: 2
   :glob:

   turtles/*


