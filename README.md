# MyMusicHere

![build](https://github.com/dmitrvk/mymusichere-app/workflows/build/badge.svg)
[![codecov](https://codecov.io/gh/dmitrvk/mymusichere-app/branch/master/graph/badge.svg)](https://codecov.io/gh/dmitrvk/mymusichere-app)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

The idea of MyMusicHere project is to automate the process
of publishing sheet music that was typeset with the
[LilyPond](http://lilypond.org) system.

The project includes two repositories.
This repository contains the source code of the
[website](http://www.mymusichere.me).
The [second repository](http://github.com/dmitrvk/mymusichere)
contains the source code of sheet music.

Once uploaded to the master branch of
[mymusichere](http://github.com/dmitrvk/mymusichere)
repository, a source code in the LilyPond format
is compiled with
[GitHub Actions](https://github.com/dmitrvk/mymusichere/actions).
Resulting PDF files and PNG images are sent to the webserver
where the application publishes new scores on the
[website](http://www.mymusichere.me).

Each score has a unique 'slug'.
This allows to create a simple and readable URL for each score, for example,
[https://www.mymusichere.me/june](https://www.mymusichere.me/june).

## To run locally

1. Create a Python 3.8 virtualenv

2. Install dependencies with `make install`

3. Install [LilyPond](https://lilypond.org)

4. Provide the following environmental variables:

    | Variable             | Description                              |
    | :------------------- | :--------------------------------------- |
    | `BASE_DIR`           | `/absolute/path/to/project/root`         |
    | `PUBLISH_TOKEN`      | Secret token for publishing scores       |
    | `MYMUSICHERE_REMOTE` | `https://github.com/dmitrvk/mymusichere` |
    | `SECRET_KEY`         | Django's app secret key                  |

5. Create a superuser with `./manage.py createsuperuser`

6. Set up the database with `./manage.py migrate`

7. Compile CSS with `make css`

8. Collect static files with `make static`

9. Run dev server with `make run`

10. Publish sheet music with `./publish.py --force`

The website should be available at http://localhost:8000


## Editing CSS

*Sass* is used as a pre-processor for CSS.
To compile CSS from SCSS run `make css`.

When editing SCSS sources, it might be useful to run `make watch-scss`.
This enables auto-compilation every time SCSS is changed.


## Publishing sheet music

If you use LilyPond to create sheet music
and want to publish your scores on
[mymusichere.me](https://www.mymusichere.me),
please, visit
[this repository](https://github.com/dmitrvk/mymusichere)
and create pull request with your score.
