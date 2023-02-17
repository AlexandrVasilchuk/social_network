WORKDIR = yatube
TEMPLATES_DIR = $(WORKDIR)/templates
MANAGE = python $(WORKDIR)/manage.py

style:
	black -S -l 79 $(WORKDIR)
	isort $(WORKDIR)
	flake8 $(WORKDIR)
	mypy $(WORKDIR)
	djhtml -i -t 2 $(TEMPLATES_DIR)

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
