
Install and Run logopy
======================

Currently, logopy is still in what I'd call "developer mode", and I haven't
made any actual releases.  That said, the code is on Github, and I've been
using `pipenv <https://pipenv.readthedocs.io/en/latest/>`_ to manage the
dependencies and run the software.  A typical command line might look like:

.. code:: shell

    $ pipenv run ./logopy.py -s ./test_scripts/ gui

Where I am running the interpreter in interactive mode and have set the 
folder where I can load my logo scripts from with the `load` command.

I tried to maintain compatibility with UCBLogo when I could.  There are some
times I decided to make some changes that had to do with the environment, but
most of the commands I've implemented at this time should behave the same as
documented in the `UCBLogo Manual <https://people.eecs.berkeley.edu/~bh/usermanual>`_ .


