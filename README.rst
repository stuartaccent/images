Images
======

Description

What else is included?
----------------------

*  Awaiting

Documentation
-------------

To do

Example site with docker
------------------------

Clone the repo

.. code:: bash

    $ git clone https://github.com/stuartaccent/images.git

Run the docker container

.. code:: bash

    $ cd images
    $ docker-compose up

Create yourself a superuser

.. code:: bash

    $ docker-compose exec app bash
    $ python manage.py createsuperuser

Go to http://127.0.0.1:8000

Testing
-------

Install dependencies

You will need pyenv installed see https://github.com/pyenv/pyenv

Also tox needs to be installed

.. code:: bash

    $ pip install tox

Install python versions in pyenv

.. code:: bash

    $ pyenv install 3.4.4
    $ pyenv install 3.5.3
    $ pyenv install 3.6.2

Set local project versions

.. code:: bash

    $ pyenv local 3.4.4 3.5.3 3.6.2

Run the tests

.. code:: bash

    $ tox

or run for a single environment

.. code:: bash

    $ tox -e py36-dj200-wt200
