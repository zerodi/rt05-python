PY_FILES=main.py teplocom

prepare:
	pip install pip-tools

install-dev-deps: dev-deps
	pip-sync requirements.txt dev-requirements.txt

install-deps: deps
	pip-sync requirements.txt

deps:
	pip-compile requirements.in

dev-deps: deps
	pip-compile dev-requirements.in

lint:
	pflake8 ${PY_FILES} || mypy ${PY_FILES}

format:
	isort ${PY_FILES} && black ${PY_FILES}