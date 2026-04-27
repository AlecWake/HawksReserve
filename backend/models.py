from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    building = Column(String, nullable=False)
    room_num = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="active")  # active, cancelled, or blocked
    cancellation_reason = Column(String, nullable=True)


class SystemConstraints(Base):
    __tablename__ = "system_constraints"

    id = Column(Integer, primary_key=True)
    max_weekly_min = Column(Integer, default=360)   # 6 hours
    max_session_min = Column(Integer, default=120)  # 2 hours

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student")  # "student" or "admin"