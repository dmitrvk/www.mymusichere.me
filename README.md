# MyMusicHere

![build](https://github.com/dmitrvk/mymusichere-app/workflows/build/badge.svg)
[![codecov](https://codecov.io/gh/dmitrvk/mymusichere-app/branch/master/graph/badge.svg)](https://codecov.io/gh/dmitrvk/mymusichere-app)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

MyMusicHere is a web application
that compilies LilyPond sheet music from the
[Github repository](http://github.com/dmitrvk/mymusichere)
and publishes compiled scores on the
[website](http://www.mymusichere.me).


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

10. Publish sheet music with `./deploy-scores.py --force`

The website should be availabe at http://localhost:8000


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
