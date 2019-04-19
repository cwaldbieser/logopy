
Install and Run logopy
======================

Two ways to install and run.

In both examples, I am running the interpreter in interactive GUI mode and have
set the folder where I can load my logo scripts from with the `load` command.

Using `pip`
-----------

Install using `pip`:

.. code:: shell

    $ pip install logopy

Then, run using:

.. code:: shell

    $ logopycli.py -s ./example_scripts/ gui


Using `pipenv`
--------------

Information about `pipenv <https://pipenv.readthedocs.io/en/latest/>`_ .

Clone the repository from GitHub and install dependencies:

.. code:: shell

    $ git clone https://github.com/cwaldbieser/logopy.git
    $ cd logopy/
    $ pipenv install

Run logopy:

.. code:: shell

    $ cd logopy/
    $ PYTHONPATH=. pipenv run ./bin/logopycli.py -s ./example_scripts/ gui

You must explicitly set the PYTHONPATH to include the `logopy` package folder
when running the program using `pipenv` in this way since the library is not
installed into your python's :file:`site-packages` folder.


Logo Compatibility
------------------

I tried to maintain compatibility with UCBLogo when I could.  There are some
times I decided to make some changes that had to do with the environment, but
most of the commands I've implemented at this time should behave the same as
documented in the `UCBLogo Manual <https://people.eecs.berkeley.edu/~bh/usermanual>`_ .


