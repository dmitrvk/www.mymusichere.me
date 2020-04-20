STATIC = scores/static/scores
SCSS = scores/scss

.PHONY: install static scss watch-scss run install test migrations-check

install:
	@pip install -r requirements.txt
	@npm install

static:
	./manage.py collectstatic --clear --noinput

scss:
	pysassc $(SCSS)/style.scss $(STATIC)/style.css -s compressed

watch-scss:
	watchmedo shell-command --patterns=*.scss --recursive --command="make scss" $(SCSS)

run:
	./manage.py runserver 0:8000

test: migrations-check
	@coverage run --source=hooks,mymusichere,scores manage.py test --verbosity 2
	@coverage xml

migrations-check:
	@./manage.py makemigrations --check --dry-run
