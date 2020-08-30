MyMusicHere
###########


.. class:: no-web no-pdf

    |build| |coverage| |license|


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
Resulting PDF files and PNG images are sent to the webserver
where the application publishes new scores on the `website`_.

Each score has a unique
`slug <https://docs.djangoproject.com/en/3.1/glossary/#term-slug>`_.
This allows to create a simple and readable URL for each score, for example,
https://www.mymusichere.me/june.


Run locally
===========

1. Create a Python 3.8 virtualenv

2. Install dependencies with ``make install``

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

5. Create a superuser with ``./manage.py createsuperuser``

6. Set up the database with ``./manage.py migrate``

7. Compile CSS with ``make css``

8. Collect static files with ``make static``

9. Run dev server with ``make run``

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

This project is licensed runder the `MIT License`_.


.. _GitHub Actions: https://github.com/dmitrvk/mymusichere/actions

.. _LilyPond: http://lilypond.org

.. _MIT License: https://github.com/dmitrvk/mymusichere.me/blob/master/LICENSE

.. _mymusichere: https://github.com/dmitrvk/mymusichere

.. _website: https://www.mymusichere.me

.. |build| image:: https://img.shields.io/github/workflow/status/dmitrvk/mymusichere.me/build?color=3e3e3e&style=flat-square
    :target: https://github.com/dmitrvk/mymusichere.me/actions
    :alt: Build status

.. |coverage| image:: https://img.shields.io/codecov/c/github/dmitrvk/mymusichere.me?color=3e3e3e&style=flat-square&token=NH8F6U8988
    :target: https://codecov.io/gh/dmitrvk/mymusichere.me
    :alt: Test coverage

.. |license| image:: https://img.shields.io/github/license/dmitrvk/mymusichere.me?color=3e3e3e&style=flat-square
    :target: https://github.com/dmitrvk/mymusichere.me/blob/master/LICENSE
    :alt: GNU General Public License v3.0
