
Logo interpreter written in Python
==================================

logopy is a Logo interpreter written in Python3.  It aims to have some degree
of compatibility with UCBLogo, but I am open is open to adding new and 
interesting features.

Quick Start
-----------

To run using `pipenv`:

.. code:: bash

    $ pipenv run ./logopy.py -s ./test_scripts/ -s ~/git-repos/logo-procedures/logo-procs/ -f ./test_scripts/pysymbol.lg

To create an SVG image:

.. code:: bash

    $ pipenv run ./logopy.py -s ./test_scripts/ -s ~/git-repos/logo-procedures/logo-procs/ -f ./test_scripts/pysymbol.lg svg -o pysymbol.svg 

To create an animated SVG image that can be viewed in a web browser:

.. code:: bash

    $ pipenv run ./logopy.py -f ./test_scripts/pointy_star.lg svg --html /path/to/a/folder/for/web-files --html-title 'Pointy Star' --html-scale 50

Full docs at `Read the Docs <https://logopy.readthedocs.io/>`_ .    
