from uuid import uuid4

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_create_notification(client):
    """Тест эндпоинта создания уведомления"""
    payload = {
        "user_id": str(uuid4()),
        "title": "Test Title",
        "text": "Test notification text",
    }

    response = client.post("/v1/notifications/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["text"] == payload["text"]
    assert data["user_id"] == payload["user_id"]


@pytest.mark.asyncio
async def test_get_notifications_list(client, db_session):
    """Тест эндпоинта получения списка уведомлений"""
    response = client.get("/v1/notifications/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert "limit" in data
    assert "offset" in data


@pytest.mark.asyncio
async def test_mark_notification_as_read(client, db_session):
    """Тест эндпоинта отметки уведомления как прочитанного"""
    payload = {
        "user_id": str(uuid4()),
        "title": "Test Title",
        "text": "Test notification text",
    }
    create_response = client.post("/v1/notifications/", json=payload)
    notification_id = create_response.json()["id"]

    response = client.post(f"/v1/notifications/{notification_id}/read")

    assert response.status_code == status.HTTP_204_NO_CONTENT
