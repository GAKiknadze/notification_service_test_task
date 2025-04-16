# Тестовое задание на позицию "Python Backend"

## Описание задания

Необходимо разработать небольшой сервис уведомлений для интеграции с
AI-моделями. Сервис должен предоставлять REST API на FastAPI и интегрироваться с
внешним AI API для анализа содержимого уведомлений.

## Требования

### Функциональные требования

1. Создание REST API для управления уведомлениями:
    - Создание нового уведомления
    - ​Получение списка уведомлений с фильтрацией и пагинацией
    - Получение детальной информации об уведомлении
    - Отметка уведомления как прочитанного

2. Интеграция с внешним AI API:
    - При создании уведомления необходимо отправить его текст в AI API для анализа
    - На основе анализа определить категорию уведомления (info, warning, critical)
    - Сохранить результат анализа вместе с уведомлением 

3. Асинхронная обработка​:
    - AI-анализ должен происходить асинхронно через очередь задач (Celery)
    - Реализовать эндпоинт для проверки статуса обработки уведомления

4. Кэширование и оптимизация:
    - Реализовать кэширование частых запросов
    - Оптимизировать работу с базой данных

### Технические требования

1. Стек технологий:​
    - Python 3.10+
    - FastAPI
    - PostgreSQL или SQLite (на выбор)
    - Redis (для кэширования и в качестве брокера сообщений)
    - Celery (для асинхронных задач)
    - Docker (для контейнеризации)
2. Структура проекта:​
    - Грамотная организация кода (разделение на слои: модели, репозитории, сервисы, контроллеры)
    - Применение принципов SOLID
    - Обработка ошибок и исключений
3. API:​
    - Документация API через Swagger/OpenAPI
    - Валидация входных данных через Pydantic
    - Реализация версионирования API
4. Тестирование:​
    - Написать unit-тесты для ключевой бизнес-логики
    - Добавить интеграционные тесты для API (минимум 3 теста)
5. Docker:​
    - Создать docker-compose.yml для запуска всех компонентов системы

### Мокап внешнего AI API

Поскольку реальное AI API может быть платным или недоступным, вы можете создать
мок-сервис со следующими характеристиками:

```python
async def analyze_text(text: str) -> dict:
    """
    Имитация работы AI API с задержкой 1-3 секунды
    """
    import random
    import asyncio

    await asyncio.sleep(random.uniform(1, 3))

    # Простая логика категоризации на основе ключевых слов
    if any(word in text.lower() for word in ["error", "exception", "failed"]):
        category = "critical"
        confidence = random.uniform(0.7, 0.95)
    elif any(word in text.lower() for word in ["warning", "attention", "careful"]):
        category = "warning"
        confidence = random.uniform(0.6, 0.9)
    else:
        category = "info"
        confidence = random.uniform(0.8, 0.99)
    return {
        "category": category,
        "confidence": confidence,"keywords": random.sample(text.split(), min(3, len(text.split())))
    }
```

### Модели данных

Примерная структура модели уведомления:

```python
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, nullable=False)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    # Результаты AI-анализа
    category = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    processing_status = Column(String, default="pending") # pending, processing,completed, failed
```

## Бонусные задания

1. Реализовать WebSocket API для получения уведомлений в реальном времени
2. Добавить метрики и мониторинг (Prometheus + Grafana)
3. Реализовать rate limiting для API
4. Создать простой веб-интерфейс для просмотра уведомлений
