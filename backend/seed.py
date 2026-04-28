# run once to set up the database: python seed.py

from database import engine, SessionLocal
from models import Base, Room, Reservation, SystemConstraints
from passlib.hash import bcrypt
from models import Base, Room, Reservation, SystemConstraints, User

Base.metadata.create_all(bind=engine)

db = SessionLocal()

db.query(Reservation).delete()
db.query(Room).delete()
db.query(SystemConstraints).delete()
db.add(SystemConstraints(max_weekly_min=360, max_session_min=120))
db.query(User).delete()
db.add_all([
    User(username="student", password_hash=bcrypt.hash("student"), role="student"),
    User(username="grant", password_hash=bcrypt.hash("meidinger"), role="student"),
    User(username="alexander", password_hash=bcrypt.hash("wake"), role="student"),
    User(username="anna", password_hash=bcrypt.hash("wille"), role="student"),
    User(username="maya", password_hash=bcrypt.hash("wyganowska"), role="student"),
    User(username="admin",   password_hash=bcrypt.hash("admin"),   role="admin"),
])
db.commit()

rooms = [
    # Memorial Union - 2nd floor (10 rooms)
    Room(building="Memorial Union", room_num="201", capacity=4),
    Room(building="Memorial Union", room_num="202", capacity=4),
    Room(building="Memorial Union", room_num="203", capacity=6),
    Room(building="Memorial Union", room_num="204", capacity=4),
    Room(building="Memorial Union", room_num="205", capacity=6),
    Room(building="Memorial Union", room_num="206", capacity=4),
    Room(building="Memorial Union", room_num="207", capacity=6),
    Room(building="Memorial Union", room_num="208", capacity=4),
    Room(building="Memorial Union", room_num="209", capacity=6),
    Room(building="Memorial Union", room_num="210", capacity=4),
    # Memorial Union - 3rd floor (8 rooms)
    Room(building="Memorial Union", room_num="301", capacity=6),
    Room(building="Memorial Union", room_num="302", capacity=8),
    Room(building="Memorial Union", room_num="303", capacity=6),
    Room(building="Memorial Union", room_num="304", capacity=10),
    Room(building="Memorial Union", room_num="305", capacity=8),
    Room(building="Memorial Union", room_num="306", capacity=6),
    Room(building="Memorial Union", room_num="307", capacity=8),
    Room(building="Memorial Union", room_num="308", capacity=10),
    # Chester Fritz Library - 1st floor
    Room(building="Chester Fritz Library", room_num="101", capacity=4),
    Room(building="Chester Fritz Library", room_num="102", capacity=6),
    Room(building="Chester Fritz Library", room_num="103", capacity=4),
    Room(building="Chester Fritz Library", room_num="104", capacity=6),
    Room(building="Chester Fritz Library", room_num="105", capacity=8),
    # Chester Fritz Library - 2nd floor
    Room(building="Chester Fritz Library", room_num="201", capacity=4),
    Room(building="Chester Fritz Library", room_num="202", capacity=6),
    Room(building="Chester Fritz Library", room_num="203", capacity=4),
    Room(building="Chester Fritz Library", room_num="204", capacity=10),
    # Chester Fritz Library - 3rd floor
    Room(building="Chester Fritz Library", room_num="301", capacity=6),
    Room(building="Chester Fritz Library", room_num="302", capacity=4),
    Room(building="Chester Fritz Library", room_num="303", capacity=8),
    Room(building="Chester Fritz Library", room_num="304", capacity=4),
    Room(building="Chester Fritz Library", room_num="305", capacity=4),

]
db.add_all(rooms)
db.commit()

db.close()
print("done")
