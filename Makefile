STATIC = scores/static/scores
SCSS = scores/scss

.PHONY: collectstatics scss run install test ci

install:
	@pip install -r requirements.txt
	@npm install

static: scss
	./manage.py collectstatic

scss:
	pysassc $(SCSS)/style.scss $(STATIC)/style.css -s compressed

run:
	./manage.py runserver 0:8000

test:
	@coverage run --source=hooks,mymusichere,scores manage.py test --verbosity 2
	@coverage xml
