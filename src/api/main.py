from fastapi import APIRouter, FastAPI, HTTPException, Depends, Response

from lib.schedule import Schedule, RoomSchedule, Lesson, Day
from .models import NewSchedule, NewRoom, NewLesson
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


@room_router.get("/")
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


app.include_router(schedule_router)
app.include_router(room_router)

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # uvicorn api.main:app
