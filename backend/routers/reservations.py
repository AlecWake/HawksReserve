from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from pydantic import BaseModel
from database import get_db
from models import Reservation, Room, SystemConstraints

router = APIRouter()


class ReservationCreate(BaseModel):
    student_id: int
    room_id: int
    start_time: str  # YYYY-MM-DD HH:MM
    end_time: str


@router.get("/reservations")
def get_reservations(student_id: int, db: Session = Depends(get_db)):
    now = datetime.now()

    reservations = db.query(Reservation).filter(
        and_(
            Reservation.student_id == student_id,
            Reservation.status == "active",
            Reservation.end_time >= now
        )
    ).all()

    result = []
    for r in reservations:
        room = db.query(Room).filter(Room.id == r.room_id).first()
        result.append({
            "id": r.id,
            "building": room.building if room else "Unknown",
            "room_num": room.room_num if room else "Unknown",
            "start_time": r.start_time.strftime("%Y-%m-%d %H:%M"),
            "end_time": r.end_time.strftime("%Y-%m-%d %H:%M"),
            "status": r.status,
        })

    return result


@router.post("/reservations")
def create_reservation(data: ReservationCreate, db: Session = Depends(get_db)):
    start = datetime.strptime(data.start_time, "%Y-%m-%d %H:%M")
    end = datetime.strptime(data.end_time, "%Y-%m-%d %H:%M")

    # make sure nobody else grabbed the room in the meantime
    conflict = db.query(Reservation).filter(
        and_(
            Reservation.room_id == data.room_id,
            Reservation.status.in_(["active", "blocked"]),
            Reservation.start_time < end,
            Reservation.end_time > start
        )
    ).first()

    if conflict:
        return JSONResponse(
            status_code=409,
            content={"success": False, "error": "Room is no longer available for that time slot."}
        )

    # enforce the weekly limit — read from DB so admin can change it
    constraints = db.query(SystemConstraints).first()
    max_weekly = constraints.max_weekly_min if constraints else 360

    week_start = (start - timedelta(days=start.weekday())).replace(hour=0, minute=0, second=0)
    week_end = week_start + timedelta(days=7)

    existing = db.query(Reservation).filter(
        and_(
            Reservation.student_id == data.student_id,
            Reservation.status == "active",
            Reservation.start_time >= week_start,
            Reservation.start_time < week_end
        )
    ).all()

    total_minutes = sum((r.end_time - r.start_time).seconds // 60 for r in existing)
    new_duration = (end - start).seconds // 60

    if total_minutes + new_duration > max_weekly:
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "You have exceeded your weekly reservation limit."}
        )

    reservation = Reservation(
        student_id=data.student_id,
        room_id=data.room_id,
        start_time=start,
        end_time=end,
        status="active"
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return JSONResponse(
        status_code=201,
        content={"success": True, "reservation_id": reservation.id}
    )


@router.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        return JSONResponse(status_code=404, content={"success": False, "error": "Reservation not found."})

    if reservation.status == "cancelled":
        return JSONResponse(status_code=400, content={"success": False, "error": "Reservation is already cancelled."})

    reservation.status = "cancelled"
    db.commit()

    return {"success": True}
