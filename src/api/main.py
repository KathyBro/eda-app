from datetime import datetime, time
from functools import partial
from typing import Optional
from fastapi import APIRouter, FastAPI, HTTPException, Depends, Response

from lib.schedule import Schedule, RoomSchedule, Lesson, Day
from .models import NewSchedule, NewRoom, NewLesson, UpdateLesson, UpdateRoom
from .dependencies import ScheduleManager, schedule_manager

app = FastAPI()


schedule_router = APIRouter(prefix="/schedules")
room_router = APIRouter(prefix="/schedules/{schedule_id}/rooms")


@schedule_router.get("/")
def get_schedules(
    manager: ScheduleManager = Depends(schedule_manager),
):
    return manager.get_schedules()


@schedule_router.post("/", status_code=201)
def create_schedule(
    schedule: NewSchedule,
    manager: ScheduleManager = Depends(schedule_manager),
):
    with manager.session():
        try:
            schedule.validate()
        except Exception as exc:
            raise HTTPException(400, detail=str(exc))

        instance = Schedule.model_validate(schedule.model_dump(mode="json"))
        manager.add_schedule(instance)
        return instance


@schedule_router.post("/{schedule_id}/rooms/", status_code=201)
def create_room(
    schedule_id: str,
    room: NewRoom,
    manager: ScheduleManager = Depends(schedule_manager),
) -> RoomSchedule:
    with manager.session():
        try:
            room.validate()
            room = RoomSchedule.model_validate(room.model_dump(mode="json"))
            possible_schedule = manager.get_schedule(schedule_id)
            if possible_schedule is None:
                raise ValueError("WTF schedule doesn't exist kathy!! WTF\nblame Milo")
            possible_schedule.add_room(room)
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))
        return room


@room_router.post("/{room_id}/lessons/", status_code=201)
def create_lesson(
    schedule_id: str,
    room_id: str,
    lesson: NewLesson,
    manager: ScheduleManager = Depends(schedule_manager),
) -> Lesson:
    with manager.session():
        try:
            lesson.validate()
            lesson = Lesson.model_validate(lesson.model_dump(mode="json"))
            possible_schedule = manager.get_schedule(schedule_id)
            for room in possible_schedule.rooms:
                if room.id == room_id:
                    break
            else:
                raise ValueError("Room not found")
            room.add_lesson(lesson)
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))
        return lesson


@room_router.get("/{room_id}/lessons/")
@room_router.get("/{room_id}")
def get_lessons(
    schedule_id: str,
    room_id: str,
    manager: ScheduleManager = Depends(schedule_manager),
) -> list[Lesson]:
    possible_sched = manager.get_schedule(schedule_id)
    for room in possible_sched.rooms:
        if room.id == room_id:
            return room.lessons
    raise HTTPException(404, detail="Could not find room")


@room_router.get("/{room_id}/lessons/{lesson_id}")
def get_specific_lesson(
    schedule_id: str,
    room_id: str,
    lesson_id: str,
    manager: ScheduleManager = Depends(schedule_manager),
) -> Lesson:
    possible_sched = manager.get_schedule(schedule_id)
    for room in possible_sched.rooms:
        if room.id == room_id:
            for lesson in room.lessons:
                if lesson.id == lesson_id:
                    return lesson
    raise HTTPException(404, detail="Could not find lesson")


@room_router.get("/")
@schedule_router.get("/{schedule_id}/")
def get_rooms(
    schedule_id: str,
    manager: ScheduleManager = Depends(schedule_manager),
) -> list[RoomSchedule]:
    possible_sched = manager.get_schedule(schedule_id)
    return possible_sched.rooms


@schedule_router.get("/{schedule_id}")
def get_schedule(
    schedule_id: str, manager: ScheduleManager = Depends(schedule_manager)
):
    try:
        possible_sched = manager.get_schedule(schedule_id)
        if not possible_sched:
            raise KeyError("Unrelated")
        return possible_sched
    except KeyError:
        raise HTTPException(404, detail="Could not find")


@schedule_router.delete("/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: str, manager: ScheduleManager = Depends(schedule_manager)
):
    try:
        possible_sched = manager.get_schedule(schedule_id)
        if not possible_sched:
            raise KeyError("Unrelated")
        manager._cache.pop(schedule_id)
        return Response(status_code=204)
    except KeyError:
        raise HTTPException(404, detail="Could not find")


@room_router.delete("/{room_id}", status_code=204)
def delete_room(
    schedule_id: str,
    room_id: str,
    manager: ScheduleManager = Depends(schedule_manager),
):
    possible_sched = manager.get_schedule(schedule_id)
    for room in possible_sched.rooms:
        if room.id == room_id:
            possible_sched.remove_room(room_id)
            return Response(status_code=204)
    raise HTTPException(404, detail="Could not find")


@room_router.delete("/{room_id}/lessons/{lesson_id}", status_code=204)
def delete_lesson(
    schedule_id: str,
    room_id: str,
    lesson_id: str,
    manager: ScheduleManager = Depends(schedule_manager),
):
    possible_sched = manager.get_schedule(schedule_id)
    for room in possible_sched.rooms:
        if room.id == room_id:
            for lesson in room.lessons:
                if lesson.id == lesson_id:
                    room.remove_lesson(lesson_id)
                    return Response(status_code=204)
            raise HTTPException(404, detail="Could not find lesson")
    raise HTTPException(404, detail="Could not find")


@schedule_router.put("/{schedule_id}", status_code=204)
def update_schedule(
    schedule_id: str,
    schedule: NewSchedule,
    manager: ScheduleManager = Depends(schedule_manager),
):
    with manager.session():
        possible_sched = manager.get_schedule(schedule_id)
        if not possible_sched:
            raise HTTPException(404, detail="Could not find")
        try:
            schedule.validate()
        except Exception as exc:
            raise HTTPException(400, detail=str(exc))

        instance = Schedule.model_validate(schedule.model_dump(mode="json"))
        manager._cache[schedule_id] = instance


@schedule_router.put("/{schedule_id}/rooms/{room_id}", status_code=204)
def update_room(
    schedule_id: str,
    room_id: str,
    room: UpdateRoom,
    manager: ScheduleManager = Depends(schedule_manager),
):
    with manager.session():
        possible_sched = manager.get_schedule(schedule_id)
        if not possible_sched:
            raise HTTPException(404, detail="Could not find")
        try:
            room.validate()
        except Exception as exc:
            raise HTTPException(400, detail=str(exc))

        existing_room = next(
            (room for room in possible_sched.rooms if room.id == room_id), None
        )
        if not existing_room:
            raise HTTPException(404, detail="Could not find room")
        # Now change the existing_room to have the updated values
        if room.name is not None:
            existing_room.name = room.name
        if room.lessons is not None:
            existing_room.lessons = room.lessons
        instance = RoomSchedule.model_validate(existing_room.model_dump(mode="json"))
        for i, room in enumerate(possible_sched.rooms):
            if room.id == instance.id:
                possible_sched.rooms[i] = instance
                break


@room_router.put("/{room_id}/lessons/{lesson_id}", status_code=204)
def update_lesson(
    schedule_id: str,
    room_id: str,
    lesson_id: str,
    lesson: UpdateLesson,
    manager: ScheduleManager = Depends(schedule_manager),
):
    with manager.session():
        possible_sched = manager.get_schedule(schedule_id)
        if not possible_sched:
            raise HTTPException(404, detail="Could not find")
        existing_lesson = next(
            (
                lesson
                for lesson in next(
                    room for room in possible_sched.rooms if room.id == room_id
                ).lessons
                if lesson.id == lesson_id
            ),
            None,
        )
        try:
            lesson.validate()
        except Exception as exc:
            raise HTTPException(400, detail=str(exc))

        if not existing_lesson:
            raise HTTPException(404, detail="Could not find lesson")
        # Now change the existing_lesson to have the updated values
        if lesson.name is not None:
            existing_lesson.name = lesson.name
        if lesson.days is not None:
            existing_lesson.days = lesson.days
        if lesson.start is not None:
            if lesson.end is None:
                # Compare to existing end
                if (
                    existing_lesson.end
                    < datetime.strptime(lesson.start, "%H:%M").time()
                ):
                    raise HTTPException(400, detail="End time must be after start time")
                existing_lesson.start = datetime.strptime(lesson.start, "%H:%M").time()
        if lesson.end is not None:
            if lesson.start is None:
                if (
                    existing_lesson.start
                    > datetime.strptime(lesson.end, "%H:%M").time()
                ):
                    raise HTTPException(400, detail="End time must be after start time")
                existing_lesson.end = datetime.strptime(lesson.end, "%H:%M").time()
        if lesson.end is not None and lesson.start is not None:
            if (
                datetime.strptime(lesson.end, "%H:%M").time()
                < datetime.strptime(lesson.start, "%H:%M").time()
            ):
                raise HTTPException(400, detail="End time must be after start time")
            else:
                existing_lesson.end = datetime.strptime(lesson.end, "%H:%M").time()
                existing_lesson.start = datetime.strptime(lesson.start, "%H:%M").time()
        instance = Lesson.model_validate(existing_lesson.model_dump(mode="json"))
        instance.id = existing_lesson.id
        for i, room in enumerate(possible_sched.rooms):
            for j, lesson in enumerate(room.lessons):
                if lesson.id == instance.id:
                    possible_sched.rooms[i].lessons[j] = instance
                    break
        manager._cache[schedule_id] = possible_sched


app.include_router(schedule_router)
app.include_router(room_router)

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # uvicorn api.main:app
