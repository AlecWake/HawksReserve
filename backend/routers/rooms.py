from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from database import get_db
from models import Room, Reservation

router = APIRouter()


@router.get("/rooms")
def get_available_rooms(building: str, date: str, start_time: str, end_time: str, db: Session = Depends(get_db)):
    requested_start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    requested_end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

    all_rooms = db.query(Room).filter(Room.building == building).all()

    # a room is taken if there's an active reservation overlapping the requested start
    booked_ids = {
        r.room_id for r in db.query(Reservation.room_id).filter(
            and_(
                Reservation.status.in_(["active", "blocked"]),
                Reservation.start_time < requested_end,
                Reservation.end_time > requested_start
            )
        ).all()
    }

    return [
        {
            "id": room.id,
            "building": room.building,
            "room_num": room.room_num,
            "capacity": room.capacity,
        }
        for room in all_rooms
        if room.id not in booked_ids
    ]
