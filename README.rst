osprey
===============================

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
   :target: http://osprey.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://github.com/pacificclimate/osprey/workflows/Docker%20Publishing/badge.svg
   :target: https://github.com/pacificclimate/osprey
   :alt: Docker Publishing

.. image:: https://github.com/pacificclimate/osprey/workflows/Python%20CI/badge.svg
   :target: https://github.com/pacificclimate/osprey
   :alt: Python CI

.. image:: https://img.shields.io/github/license/nikola-rados/osprey.svg
    :target: https://github.com/nikola-rados/osprey/blob/master/LICENSE.txt
    :alt: GitHub license

.. image:: https://badges.gitter.im/bird-house/birdhouse.svg
    :target: https://gitter.im/bird-house/birdhouse?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
    :alt: Join the chat at https://gitter.im/bird-house/birdhouse


Osprey
  *The osprey or more specifically the western osprey — also called sea hawk (go hawks!), river hawk, and fish hawk — is a diurnal, fish-eating bird of prey with a cosmopolitan range. It is a large raptor, reaching more than 60 cm in length and 180 cm across the wings.*

A Web Processing Service for RVIC streamflow routing model.

Documentation
-------------

Learn more about osprey in its official documentation at
https://osprey.readthedocs.io.

Submit bug reports, questions and feature requests at
https://github.com/nikola-rados/osprey/issues

Installation
------------

Clone the repo onto the target machine. Python installation should be done in a python3 virtual environment created
and activated as follows (second `venv` can be replaced with environment name of your choice):

.. code:: bash

   $ python3 -m venv venv
   $ source venv/bin/activate
   (venv) $ pip install -i https://pypi.pacificclimate.org/simple/ -r requirements.txt -r requirements_dev.txt
   (venv) $ pip install -e .

Contributing
------------

You can find information about contributing in our `Developer Guide`_.

Testing
^^^^^^^

Upon installation, the tests for each process will fail due to issues in ``RVIC``. In order to fix them, two modules in the
``rvic`` site-package in your ``venv`` need to be modified as follows:

1. In line 188 of ``rvic/parameters.py``, change ``pour_points.ix`` to ``pour_points.loc``.

2. From lines 277 to 298 of ``rvic/core/share.py``, change each instance of ``max_range`` to ``range``.

After these changes, the tests can be run by running `pytest` on the command line.

Releasing
^^^^^^^^^

Please use bumpversion_ to release a new version.

License
-------

Free software: GNU General Public License v3

Credits
-------

This package was created with Cookiecutter_ and the `bird-house/cookiecutter-birdhouse`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`bird-house/cookiecutter-birdhouse`: https://github.com/bird-house/cookiecutter-birdhouse
.. _`Developer Guide`: https://osprey.readthedocs.io/en/latest/dev_guide.html
.. _bumpversion: https://osprey.readthedocs.io/en/latest/dev_guide.html#bump-a-new-version
