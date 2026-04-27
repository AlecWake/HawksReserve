from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database import get_db
from models import Reservation, Room, SystemConstraints

router = APIRouter(prefix="/admin")


@router.get("/rooms")
def get_all_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).order_by(Room.building, Room.room_num).all()
    return [{"id": r.id, "building": r.building, "room_num": r.room_num, "capacity": r.capacity} for r in rooms]


@router.get("/reservations")
def get_all_reservations(db: Session = Depends(get_db)):
    reservations = db.query(Reservation).order_by(Reservation.start_time).all()

    result = []
    for r in reservations:
        room = db.query(Room).filter(Room.id == r.room_id).first()
        result.append({
            "id": r.id,
            "student_id": r.student_id,
            "building": room.building if room else "Unknown",
            "room_num": room.room_num if room else "Unknown",
            "start_time": r.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": r.end_time.strftime("%Y-%m-%d %H:%M"),
            "status": r.status,
            "cancellation_reason": r.cancellation_reason,
        })

    return result


class BlockRequest(BaseModel):
    start_time: str  # "YYYY-MM-DD HH:MM"
    end_time: str


@router.post("/rooms/{room_id}/block")
def block_room(room_id: int, data: BlockRequest, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    start = datetime.strptime(data.start_time, "%Y-%m-%d %H:%M")
    end = datetime.strptime(data.end_time, "%Y-%m-%d %H:%M")

    if end <= start:
        raise HTTPException(status_code=400, detail="End time must be after start time.")

    block = Reservation(
        student_id=0,
        room_id=room_id,
        start_time=start,
        end_time=end,
        status="blocked",
    )
    db.add(block)
    db.commit()

    return {"success": True}


class CancelRequest(BaseModel):
    reason: str


@router.post("/reservations/{reservation_id}/cancel")
def admin_cancel(reservation_id: int, data: CancelRequest, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found.")

    reservation.status = "cancelled"
    reservation.cancellation_reason = data.reason
    db.commit()

    return {"success": True}


@router.get("/constraints")
def get_constraints(db: Session = Depends(get_db)):
    constraints = db.query(SystemConstraints).first()
    if not constraints:
        return {"max_weekly_min": 360, "max_session_min": 120}
    return {
        "max_weekly_min": constraints.max_weekly_min,
        "max_session_min": constraints.max_session_min,
    }


class ConstraintsUpdate(BaseModel):
    max_weekly_min: int
    max_session_min: int


@router.put("/constraints")
def update_constraints(data: ConstraintsUpdate, db: Session = Depends(get_db)):
    if data.max_weekly_min <= 0 or data.max_session_min <= 0:
        raise HTTPException(status_code=400, detail="Constraint values must be positive integers.")

    constraints = db.query(SystemConstraints).first()
    if not constraints:
        constraints = SystemConstraints()
        db.add(constraints)

    constraints.max_weekly_min = data.max_weekly_min
    constraints.max_session_min = data.max_session_min
    db.commit()

    return {
        "message": "System constraints updated successfully.",
        "max_weekly_min": constraints.max_weekly_min,
        "max_session_min": constraints.max_session_min,
    }
