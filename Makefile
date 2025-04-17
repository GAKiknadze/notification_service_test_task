
i_test:
	pip install -r requirements.test.txt

i_dev:
	pip install -r requirements.dev.txt

i:
	pip install -r requirements.txt

i_all: i_test i_dev i

check:
	mypy .
	flake8 ./src --max-line-length=127

format:
	isort .
	black .

test:
	pytest ./tests -v

run_worker:
	celery -A src:worker_app --pool=asyncio --loglevel=info

run_local:
	python ./app.py