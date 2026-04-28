from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import rooms, reservations, admin, auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# needed so the HTML files can call the API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms.router)
app.include_router(reservations.router)
app.include_router(admin.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "HawkReserve API is running"}
