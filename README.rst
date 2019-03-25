
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

Full docs at `Read the Docs <https://logopy.readthedocs.io/>`_ .    
