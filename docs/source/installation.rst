.. _installation:

Installation
============

.. contents::
    :local:
    :depth: 1

Install from Conda
------------------

.. warning::

   TODO: Prepare Conda package.

Install from GitHub
-------------------

Check out code from the osprey GitHub repo and start the installation:

.. code-block:: console

   $ git clone https://github.com/nikola-rados/osprey.git
   $ cd osprey

Create Python environment named `venv`:

.. code-block:: console

   $ python3 -m venv venv
   $ source venv/bin/activate

Install requirements:

.. code-block:: console

   (venv)$ pip install -r requirements.txt

Install osprey app:

.. code-block:: console

  (venv)$ pip install -e .
  OR
  make install

For development you can use this command:

.. code-block:: console

  (venv)$ pip install -e .[dev]
  OR
  $ make develop

Start osprey PyWPS service
--------------------------

After successful installation you can start the service using the ``osprey`` command-line.

.. code-block:: console

   (venv)$ osprey --help # show help
   (venv)$ osprey start  # start service with default configuration

   OR

   (venv)$ osprey start --daemon # start service as daemon
   loading configuration
   forked process id: 42

The deployed WPS service is by default available on:

http://localhost:5000/wps?service=WPS&version=1.0.0&request=GetCapabilities.

.. NOTE:: Remember the process ID (PID) so you can stop the service with ``kill PID``.

You can find which process uses a given port using the following command (here for port 5000):

.. code-block:: console

   $ netstat -nlp | grep :5000


Check the log files for errors:

.. code-block:: console

   $ tail -f  pywps.log

... or do it the lazy way
+++++++++++++++++++++++++

You can also use the ``Makefile`` to start and stop the service:

.. code-block:: console

  $ make start
  $ make status
  $ tail -f pywps.log
  $ make stop


Run osprey as Docker container
------------------------------

You can also run osprey as a Docker container.

.. code-block:: console

  $ docker-compose build
  $ docker-compose up

osprey will be available on port 8100.

Use Ansible to deploy osprey on your System
-------------------------------------------

Use the `Ansible playbook`_ for PyWPS to deploy osprey on your system.


.. _Ansible playbook: http://ansible-wps-playbook.readthedocs.io/en/latest/index.html
