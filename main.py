from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from methods import create_uuid
from schemas import UUID
from models import Base
from database import SessionLocal, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/get_uuid", response_model=UUID)
async def get_uuid(db: Session = Depends(get_db)):
    return create_uuid(db)
