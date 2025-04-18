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
	CONFIG_FILE=./configs/config.test.yaml
	pytest ./tests -v

run_worker:
	celery -A src:worker_app worker --pool=prefork --loglevel=info

run_local:
	uvicorn src:rest_app --host 0.0.0.0 --port 8000 --no-access-log --log-level critical

docker_cleanup:
	echo "Stopping project containers..."
	docker ps -a | grep "notification_service" | awk '{print $$1}' | xargs -r docker stop

	echo "Removing project containers..."
	docker ps -a | grep "notification_service" | awk '{print $$1}' | xargs -r docker rm

	echo "Removing project images..."
	docker images | grep "notification_service" | awk '{print $$3}' | xargs -r docker rmi

	echo "Cleanup of project containers complete!"
