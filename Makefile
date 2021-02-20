# Licensed under the MIT License

APPS = mymusichere scores
SCSS = mymusichere/scss

.PHONY: css help install isort migrations-check build run static test watch-scss

help:
	@echo "Please, use \`make <target>\` where <target> is one of the following:"
	@echo "  css                 compile CSS from SCSS"
	@echo "  install             install dependencies with pip and npm"
	@echo "  isort               sort imports in .py files"
	@echo "  migrations-check    check migrations issues"
	@echo '  build               build with Docker Compose'
	@echo '  run                 run with Docker Compose'
	@echo "  static              collect static files for deployment"
	@echo "  test                run tests"
	@echo "  watch-scss          compile CSS every time SCSS is updated"

css:
	pysassc $(SCSS)/style.scss mymusichere/static/css/style.css -s compressed

install:
	@pip install -r requirements.txt
	@npm install

isort:
	isort --atomic $(APPS)

migrations-check:
	@./manage.py makemigrations --check --dry-run

build:
	docker-compose --file=deploy/docker-compose.yml build

run:
	docker-compose --file=deploy/docker-compose.yml up --detach

static:
	./manage.py collectstatic --noinput

test: migrations-check
	@coverage run --source=mymusichere,scores manage.py test $(APPS)
	@coverage xml
	@flake8 $(APPS) --exclude 'migrations'

watch-scss:
	watchmedo shell-command --patterns=*.scss --recursive --command="make scss" $(SCSS)

image:
	docker build -f deploy/Dockerfile -t ghcr.io/dmitrvk/mymusichere:latest .
	docker build -t ghcr.io/dmitrvk/mymusichere_caddy:latest deploy/caddy
	docker push ghcr.io/dmitrvk/mymusichere:latest
	docker push ghcr.io/dmitrvk/mymusichere_caddy:latest

deploy:
	docker stack deploy --with-registry-auth --compose-file=deploy/docker-stack.yml mymusichere

.PHONY: deploy
