WORKDIR = yatube
TEMPLATES-DIR = $(WORKDIR)/templates
MANAGE = python $(WORKDIR)/manage.py

style:
  black -S -l 79 $(WORKDIR)
  isort $(WORKDIR)
  djhtml -i -t 2 $(TEMPLATES-DIR)
  flake8 $(WORKDIR)
  mypy $(WORKDIR)

migrations:
  $(MANAGE) makemigrations

migrate:
  $(MANAGE) migrate

superuser:
  $(MANAGE) createsuperuser

run:
  $(MANAGE) runserver

shell:
  $(MANAGE) shell
