from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI()

EVENTS: dict[int, dict[str, str]] = {}


class EventRead(BaseModel):
    id: int
    note: str


class EventCreate(BaseModel):
    note: str = Field(min_length=1, max_length=200)


def _generate_next_event_id() -> int:
    return max(EVENTS, default=0) + 1


@app.get("/events")
def get_events(limit: Annotated[int, Query(ge=1)] = 10) -> list[EventRead]:
    events: list[EventRead] = []

    sorted_events = sorted(
        EVENTS.items(),
        key=lambda item: item[0],
        reverse=True,
    )

    for event_id, event_data in sorted_events[:limit]:
        events.append(
            EventRead(
                id=event_id,
                note=event_data["note"],
            )
        )

    return events


@app.get("/events/{event_id}")
def get_event(event_id: int) -> EventRead:
    event = EVENTS.get(event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event ID {event_id} not found!"
        )

    return EventRead(
        id=event_id,
        note=event["note"]
    )


@app.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(body: EventCreate) -> EventRead:
    next_event_id = _generate_next_event_id()

    EVENTS[next_event_id] = {
        "note": body.note,
    }

    return EventRead(
        id=next_event_id,
        note=body.note,
    )
