# Notification Service (Test task)

![Tests](https://github.com/GAKiknadze/notification_service_test_task/actions/workflows/python-package.yml/badge.svg)

The test task "Notification service" from [AEZAKMI Group](https://aezakmi.group/)

### Task condition:

- [Russian](./docs/task_condition.ru.md)

## Launching the app

**Before launching:**
1. Create a configuration file based on `configs/config.example.yaml`
2. Set the environment variables in the `.env` file to run the application in Docker

### Native

1. Make sure you have **Python 3.10+** installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the REST API server with custom config:
```bash
CONFIG_FILE=./configs/config.yaml uvicorn src:rest_app --host 0.0.0.0 --port 8000
```

4. Run Celery worker in separate terminal:
```bash
CONFIG_FILE=./configs/config.yaml celery -A src:worker_app worker --pool=prefork --loglevel=info
```

### Docker Compose

1. Make sure you have **Docker Compose** installed
2. Run in the terminal:
```bash
docker compose up -d
```
or
```bash
docker-compose up -d
```

## Launching tests

1. Install test requirements:
```bash
pip install -r requirements.test.txt
```

2. Run tests (uses config.test.yaml by default):
```bash
CONFIG_FILE=./configs/config.test.yaml pytest tests/ -v
```
