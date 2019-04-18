
LogoPy Compatibility Commands
=============================

LogoPy has some commands that are valid in all backends, but unlikely
to be available in other Logo implementations.  They are different from
extension commands because they provide features that are necessary for
writing portable Logo programs.

.. note::

    Even in Logo implementations that do not provide these commands as
    primitives, it is not hard to provide implementations of these
    commands in the Logo language, itself.


CARTESIAN.HEADING
-----------------

.. code::

    to CARTESIAN.HEADING :heading

The *CARTESIAN.HEADING* command takes a heading for the current LogoPy backend
and maps it to a heading in the standard Cartesian coordinate system 
(North = 90 degrees, South = 270 degrees, East = 0 degrees, West = 180 degrees).

TURTLE.HEADING
--------------

.. code::

    to TURTLE.HEADING :heading

The *TURTLE.HEADING* command takes a Cartesian heading and outputs the corresponding
heading in the current LogoPy backend.

