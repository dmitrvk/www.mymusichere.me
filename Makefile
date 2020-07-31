# Licensed under the MIT License

APPS = mymusichere scores
SCSS = mymusichere/scss

.PHONY: css help install isort migrations-check run static test watch-scss

help:
	@echo "Please, use \`make <target>\` where <target> is one of the following:"
	@echo "  css                 compile CSS from SCSS"
	@echo "  install             install dependencies with pip and npm"
	@echo "  isort               sort imports in .py files"
	@echo "  migrations-check    check migrations issues"
	@echo "  run                 start development server"
	@echo "  static              collect static files for deployment"
	@echo "  test                run tests"
	@echo "  watch-scss          compile CSS every time SCSS is updated"

css:
	pysassc $(SCSS)/style.scss mymusichere/static/css/style.css -s compressed

install:
	@pip install -r requirements.txt
	@npm install

isort:
	isort -rc --atomic $(APPS)

migrations-check:
	@./manage.py makemigrations --check --dry-run

run:
	./manage.py runserver 0:8000

static:
	./manage.py collectstatic --clear --noinput

test: migrations-check
	@coverage run --source=mymusichere,scores manage.py test $(APPS)
	@coverage xml
	@flake8 $(APPS) --exclude 'migrations'

watch-scss:
	watchmedo shell-command --patterns=*.scss --recursive --command="make scss" $(SCSS)

