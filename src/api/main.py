from fastapi import FastAPI
from schedule import Schedule, RoomSchedule, Lesson

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/schedule")
def get_schedule():
    schedule = Schedule()
    return schedule


@app.post("/schedule")
def create_room(room: RoomSchedule):
    return room


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # uvicorn api.main:app
