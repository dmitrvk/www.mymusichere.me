MyMusicHere
###########


.. class:: no-web no-pdf

    |license|


The idea of MyMusicHere project is to automate the process
of publishing sheet music that was typeset with the `LilyPond`_ system.

The project includes two repositories.
This repository contains the source code of the `website`_.
The `mymusichere`_ repository contains the source code of sheet music.


.. class:: no-web no-pdf

    .. image:: https://raw.githubusercontent.com/dmitrvk/mymusichere.me/master/screenshot.jpg
        :alt: mymusichere.me screenshot
        :align: center
        :target: https://www.mymusichere.me


.. contents::

.. section-numbering::


How it works
============


Once uploaded to the master branch of `mymusichere`_ repository,
a source code in the LilyPond format is compiled with `GitHub Actions`_.
Resulting PDF files and PNG images are sent to the web server
where the application publishes new scores on the `website`_.

Each score has a unique
`slug <https://docs.djangoproject.com/en/3.1/glossary/#term-slug>`_.
This allows to create a simple and readable URL for each score, for example,
https://www.mymusichere.me/june.


Run locally
===========

1. Create a Python 3.8 virtualenv

2. Install dependencies:

.. code-block:: bash

    make install

3. Install `LilyPond`_

4. Provide the following environmental variables:

+------------------------+--------------------------------------------+
| Variable               | Description                                |
+========================+============================================+
| ``BASE_DIR``           | ``/absolute/path/to/project/root``         |
+------------------------+--------------------------------------------+
| ``MYMUSICHERE_REMOTE`` | ``https://github.com/dmitrvk/mymusichere`` |
+------------------------+--------------------------------------------+
| ``PUBLISH_TOKEN``      | Secret token for publishing scores         |
+------------------------+--------------------------------------------+
| ``SECRET_KEY``         | Django's app secret key                    |
+------------------------+--------------------------------------------+

5. Create a MySQL database

6. Create a ``secrets.json`` file in the project's root directory
   containing the information needed to connect to the database:

.. code-block:: json

    {
        "db_host": "localhost",
        "db_name": "mymusichere",
        "db_user": "mymusichere",
        "db_password": "secretpass"
    }

7. Apply migrations:

.. code-block:: bash

    ./manage.py migrate

8. Create a superuser:

.. code-block:: bash

    ./manage.py createsuperuser

9. Compile CSS:

.. code-block:: bash

    make css

10. Collect static files:

.. code-block:: bash

    make static

11. Run dev server:

.. code-block:: bash

    make run

The website should be available at http://localhost:8000/


Editing CSS
===========

*Sass* is used as a pre-processor for CSS.
To compile CSS from SCSS run ``make css``.

When editing SCSS sources, it might be useful to run ``make watch-scss``.
This enables auto-compilation every time SCSS is changed.


Contributing
============

You can contribute to the MyMusicHere project by
`creating an issue <https://github.com/dmitrvk/mymusichere.me/issues/new>`_
or submitting a pull request.

If you use LilyPond to create sheet music
and want to publish your scores on the `website`_,
please, visit the `mymusichere`_ repository
and create a pull request with your score.


Licensing
=========

This project is licensed under the `MIT License`_.


.. _GitHub Actions: https://github.com/dmitrvk/mymusichere/actions

.. _LilyPond: http://lilypond.org

.. _MIT License: https://github.com/dmitrvk/mymusichere.me/blob/master/LICENSE

.. _mymusichere: https://github.com/dmitrvk/mymusichere

.. _website: https://www.mymusichere.me

.. |license| image:: https://img.shields.io/github/license/dmitrvk/mymusichere.me?color=3e3e3e&style=flat-square
    :target: https://github.com/dmitrvk/mymusichere.me/blob/master/LICENSE
    :alt: GNU General Public License v3.0
