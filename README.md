# Notification Service (Test task)

![Tests](https://github.com/GAKiknadze/notification_service_test_task/actions/workflows/python-package.yml/badge.svg)

The test task "Notification service" from [AEZAKMI Group](https://aezakmi.group/)

### Task condition:

- [Russian](./docs/task_condition.ru.md)

## Launching the app

**Before launching:**
1. Specify the application settings in the `config.yml` file
2. Set the environment variables in the `.env` file to run the application in Docker

### Native

1. Make sure you have **Python 3.10+** installed.
2. Run in the terminal:

```bash
python main.py
```

or

```bash
python3 main.py
```

### Docker Compose

1. Make sure you have **Docker Compose** installed.
2. Run in the terminal:

```bash
docker compose up -d
```

or 

```bash
docker-compose up -d
```

## Launching tests (native)

1. Install test requirements:

```bash
pip install -r requirements.test.txt
```

2. Run tests:

```bash
pytest tests/ -v
```
