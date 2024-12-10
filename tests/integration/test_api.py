import json
from fastapi.testclient import TestClient
import pytest
from api.main import app
from api.models import NewSchedule, NewLesson, NewRoom
from lib.schedule import Day


@pytest.fixture
def api_client():
    return TestClient(app)


__main_url__ = "/schedules/"


def create_schedule(api_client):
    request_body = NewSchedule(rooms=[]).model_dump(mode="json")
    response = api_client.post(__main_url__, json=request_body)
    return response


def create_room(api_client, schedule_id):
    request_body = NewRoom(lessons=[], name="Test Room").model_dump(mode="json")
    response = api_client.post(f"{__main_url__}{schedule_id}/rooms/", json=request_body)
    return response


def test_root__when_making_get__returns_list_of_schedules(api_client):
    response = api_client.get(__main_url__)
    response_body = response.json()
    assert response.status_code == 200
    assert isinstance(response_body, list)


def test_schedules__create_new_schedule__returns_new_schedule_with_empty_rooms(
    api_client,
):
    request_body = NewSchedule(rooms=[]).model_dump(mode="json")
    response = api_client.post(__main_url__, json=request_body)
    assert response.status_code == 201
    response_body = response.json()

    assert "id" in response_body
    assert isinstance(response_body["id"], str)

    assert "rooms" in response_body
    assert isinstance(response_body["rooms"], list)
    assert len(response_body["rooms"]) == 0


def test_schedules__create_new_schedule__new_schedule_appears_in_list_of_schedules(
    api_client,
):
    request_body = NewSchedule(rooms=[]).model_dump(mode="json")
    response = api_client.post(__main_url__, json=request_body)
    new_schedule_id = response.json()["id"]
    response = api_client.get(__main_url__)
    assert any(obj.get("id") == new_schedule_id for obj in response.json())


def test_schedules__create_new_schedule__missing_rooms__returns_422(api_client):
    request_body = "{}"
    response = api_client.post(__main_url__, json=request_body)
    assert response.status_code == 422


def test_schedules__create_new_room_but_schedule_does_not_exist__returns_400(
    api_client,
):
    request_body = NewRoom(lessons=[], name="Test Room").model_dump(mode="json")
    response = api_client.post(f"{__main_url__}123/rooms/", json=request_body)
    assert response.status_code == 400


def test_schedules__create_new_room__missing_lessons__returns_201_and_empty_lessons(
    api_client,
):
    request_body = NewRoom(name="Test Room").model_dump(mode="json")
    schedule_id = create_schedule(api_client).json()["id"]
    response = api_client.post(f"{__main_url__}{schedule_id}/rooms/", json=request_body)
    assert response.status_code == 201
    response_body = response.json()
    assert "id" in response_body
    assert isinstance(response_body["id"], str)

    assert "lessons" in response_body
    assert isinstance(response_body["lessons"], list)
    assert len(response_body["lessons"]) == 0

    assert response_body["name"] == "Test Room"


def test_schedules__create_new_room__missing_name__returns_422(api_client):
    request_body = '{"lessons": []}'
    schedule_id = create_schedule(api_client).json()["id"]
    response = api_client.post(f"{__main_url__}{schedule_id}/rooms/", json=request_body)
    assert response.status_code == 422


def test_schedules__create_new_room__room_exists__returns_200(api_client):
    request_body = NewRoom(name="Test Room").model_dump(mode="json")
    schedule_id = create_schedule(api_client).json()["id"]
    response = api_client.post(f"{__main_url__}{schedule_id}/rooms/", json=request_body)
    room_id = response.json()["id"]
    response = api_client.get(f"{__main_url__}{schedule_id}/rooms/{room_id}/lessons")
    assert response.status_code == 200


def test_schedules__create_new_lesson__missing_name__returns_422(api_client):
    request_body = '{"day": "monday", "start": "12:00", "end": "13:00"}'
    schedule_id = create_schedule(api_client).json()["id"]
    room_id = create_room(api_client, schedule_id).json()["id"]
    response = api_client.post(
        f"{__main_url__}{schedule_id}/rooms/{room_id}/lessons/", json=request_body
    )
    assert response.status_code == 422


def test_schedules__create_new_lesson__missing_day__returns_422(api_client):
    request_body = '{"name": "Test Lesson", "start": "12:00", "end": "13:00"}'
    schedule_id = create_schedule(api_client).json()["id"]
    room_id = create_room(api_client, schedule_id).json()["id"]
    response = api_client.post(
        f"{__main_url__}{schedule_id}/rooms/{room_id}/lessons/", json=request_body
    )
    assert response.status_code == 422


def test_schedules__create_new_lesson__missing_start__returns_422(api_client):
    request_body = '{"name": "Test Lesson", "day": "monday", "end": "13:00"}'
    schedule_id = create_schedule(api_client).json()["id"]
    room_id = create_room(api_client, schedule_id).json()["id"]
    response = api_client.post(
        f"{__main_url__}{schedule_id}/rooms/{room_id}/lessons/", json=request_body
    )
    assert response.status_code == 422


def test_schedules__create_new_lesson__missing_end__returns_422(api_client):
    request_body = '{"name": "Test Lesson", "day": "monday", "start": "12:00"}'
    schedule_id = create_schedule(api_client).json()["id"]
    room_id = create_room(api_client, schedule_id).json()["id"]
    response = api_client.post(
        f"{__main_url__}{schedule_id}/rooms/{room_id}/lessons/", json=request_body
    )
    assert response.status_code == 422


def test_schedules__create_new_lesson__missing_room__returns_400(api_client):
    request_body = NewLesson(
        name="Test Lesson", days=[Day.MONDAY], start="12:00", end="13:00"
    ).model_dump(mode="json")
    schedule_id = create_schedule(api_client).json()["id"]
    response = api_client.post(
        f"{__main_url__}{schedule_id}/rooms/123/lessons/", json=request_body
    )
    assert response.status_code == 400


def test_schedules__create_new_lesson__returns_new_lesson(api_client):
    request_body = NewLesson(
        name="Test Lesson", days=[Day.MONDAY], start="12:00", end="13:00"
    ).model_dump(mode="json")

    schedule_id = create_schedule(api_client).json()["id"]
    room_id = create_room(api_client, schedule_id).json()["id"]
    response = api_client.post(
        f"{__main_url__}{schedule_id}/rooms/{room_id}/lessons/", json=request_body
    )
    assert response.status_code == 201


def test_schedules__create_new_lesson__appears_in_list_of_lessons(api_client):
    request_body = NewLesson(
        name="Test Lesson", days=[Day.MONDAY], start="12:00", end="13:00"
    ).model_dump(mode="json")

    schedule_id = create_schedule(api_client).json()["id"]
    room_id = create_room(api_client, schedule_id).json()["id"]
    response = api_client.post(
        f"{__main_url__}{schedule_id}/rooms/{room_id}/lessons/", json=request_body
    )
    lesson_id = response.json()["id"]
    response = api_client.get(f"{__main_url__}{schedule_id}/rooms/{room_id}/lessons")
    assert any(obj.get("id") == lesson_id for obj in response.json())
