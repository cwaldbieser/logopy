
Extension Commands
==================

Extension commands are primitives that are available in logopy, but unlikely
to be available in other logo implementations.  Further, some extensions may
only be compatible with certain turtle backends.

Extensions provide interesting features at the expense of portability.  All
logopy extension commands begin with "EXT." to make it clear to the programmer
that this is an extension that is probably not available on a different Logo
interpreter.


EXT.ELLIPSE 
-----------

.. code::

    to EXT.ELLIPSE :major :minor [:angle 360] [:clockwise true]

The *EXT.ELLIPSE* command draws an ellipse with its major and minor axes set
to lengths `major` and `minor`.  The major axis will bisect the ellipse at
an angle equal to the current turtle heading.  The minor axis bisects the
ellipse at an angle perpendicular to the major axis.  The major axis may
be shorter than the minor axis.

The center of the ellipse will be located to the right of the turtle if the
ellipse is drawn clockwise.  If the ellipse is drawn anti-clockwise, the center
will be to the left of the turtle.  In both cases, the center of the ellipse
will be half the length of the minor axis from the turtle.

An optional parameter may be specified to indicate the angle that should be
swept out from the center of the ellipse when drawing its perimeter.  In this
manner, an elliptical arc can be drawn instead of a complete ellipse.  Drawing
starts at the turtle's starting position, and continues throughout `angle`
degrees around the perimeter of the ellipse.

The optional parameter `clockwise` determines whether the turtle will trace out
the ellipse in a clockwise or anti-clockwise direction.

The turtle moves as it draws the ellipse.  If a complete ellipse is drawn, the
turtle will end up at its original starting position and heading.  Otherwise,
the turtle will move to the end of the elliptical arc and have a heading
perpendicular to the curve at that point.

EXT.UNFILLED
------------

.. code::

    to EXT.UNFILLED :instrlist

The *EXT.UNFILLED* command behaves specially when used with the SVG turtle
backend.  It can be used inside a *FILLED* instruction to indicate that an
enclosed shape should not be filled.

When used with the TK GUI back end, the Logo instructions contained
in `instrlist` are processed normally by the interpreter.

When used with the SVG turtle backend, a number of special rules apply.  First,
the extension can only be used within an enclosing *FILLED* command.  When used
within a *FILLED* command, the path(s) traversed are masked.  The mask will
prevent those areas from being filled.

