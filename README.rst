
Logo interpreter written in Python
==================================

logopy is a Logo interpreter written in Python3.  It aims to have some degree
of compatibility with UCBLogo, but I am open is open to adding new and 
interesting features.

Quick Start
-----------

To run using `pipenv`:

.. code:: bash

    $ cd logopy/
    $ PYTHONPATH=. pipenv run ./bin/logopycli.py -s ./example_scripts/ -s ~/git-repos/logo-procedures/logo-procs/ -f ./test_scripts/pysymbol2.lg

To create an SVG image:

.. code:: bash

    $ cd logopy/
    $ PYTHONPATH=. pipenv run ./bin/logopycli.py -s ./example_scripts/ -s ~/git-repos/logo-procedures/logo-procs/ -f ./test_scripts/pysymbol2.lg svg -o pysymbol2.svg 

To create an animated SVG image that can be viewed in a web browser:

.. code:: bash

    $ cd logopy/
    $ PYTHONPATH=. pipenv run ./bin/logopycli.py -f ./example_scripts/pointy_star.lg svg --html /path/to/a/folder/for/web-files \
      --html-title 'Pointy Star' --html-scale 50 --animation-duration 400 --animation-type onebyone --animation-start automatic

Full docs at `Read the Docs <https://logopy.readthedocs.io/>`_ .    
