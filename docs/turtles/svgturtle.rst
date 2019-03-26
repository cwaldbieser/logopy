
SVG Turtle Back End
===================

The SVG turtle back end is used to produce `Scalable Vector Graphics <https://www.w3.org/Graphics/SVG/>`_
from turtle commands.  A line drawn by the turtle will be represented by the
appropriate markup in SVG.  

The SVG turtle is meant to be used in a non-interactive batch mode.  The
:option:`-f` command line argument should be used to select a Logo program that
contains turtle commands.  For interactive exploration while developing images,
use the GUI turtle back end.

The SVG turtle can be directed to write its results to a single SVG file using
the :option:`-o` command line option.  The SVG image can then be used in 
applications, such as web browsers, which support SVG.

Because SVG enjoys such robust web browser support, the turtle can also be
instructed to create a minimal web page that animates the SVG image so that
it appears to be drawn on the page.  The :option:`--html` command line option
can be used to specify a folder that the generated content will be placed
into.  The animation uses the `vivus.js <https://github.com/maxwellito/vivus>`_
JavaScript library to animate the content.

.. note::

    Vivus.js uses a different license than logopy.  While logopy uses the GPLv3
    license, vivus.js uses the MIT license.  As a user of the software, this
    probably won't make much difference to you.  If you plan on distributing the
    software, you may want to review your obligations under the different 
    licenses.

There are additional command line options that allow you to influence the behavior
of the animations:

* :option:`--html-title` allows you to set the web page title.
* :option:`--html-width` allows you to set the width of the image to be
  displayed in pixels.
* :option:`--html-scale` allows you to specify the width of the image as a
  percentage of the total screen width.
* :option:`--animation-duration` allows you to specify the animation
  duration in frames (see vivus documentation).
* :option:`--animation-type` allows you to specify the animation type (see the
  vivus documentation).

Examples of SVG images created with the SVG turtle can be seen in the 
`Logopy Gallery <https://cwaldbieser.github.io/logo-gallery/index.html>`_ .

